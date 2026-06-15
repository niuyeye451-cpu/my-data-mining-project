import time
import re
import os
import threading
import mysql.connector
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 线程锁，保护 MySQL 写入（mysql-connector-python 非线程安全）
db_lock = threading.Lock()


def create_driver():
    """每个线程独立创建一个 WebDriver 实例"""
    print(f"  [Thread-{threading.current_thread().name}] 正在初始化浏览器...")
    chrome_options = Options()

    # 反爬配置
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


def get_db_connection():
    """建立数据库连接"""
    return mysql.connector.connect(
        host='db', user='root', password='rootpassword', database='asos_db'
    )


def save_link_to_db(db_conn, url):
    """解析 product_code 并存入数据库（线程安全）"""
    code_match = re.search(r'/prd/(\d+)', url)
    if not code_match:
        return
    product_code = code_match.group(1)

    with db_lock:
        cursor = db_conn.cursor()
        sql = "INSERT IGNORE INTO asos_dresses (product_code, url, status) VALUES (%s, %s, 0)"
        try:
            cursor.execute(sql, (product_code, url))
            db_conn.commit()
            if cursor.rowcount > 0:
                print(f"  🔗 新链接入库: {product_code}")
        except Exception as e:
            print(f"  ❌ 入库失败: {e}")
        finally:
            cursor.close()


def scrape_page(page_num):
    """爬取单个列表页，返回发现的商品 URL 列表"""
    target_url = (
        "https://www.asos.com/women/sale/dresses/cat/?cid=5235"
        "&page=" + str(page_num)
    )
    print(f"\n📄 [第 {page_num} 页] 正在访问: {target_url}")

    driver = create_driver()
    found_urls = []

    try:
        driver.get(target_url)
        time.sleep(3)
        print(f"  [第 {page_num} 页] 页面标题: {driver.title}")

        # 模拟真人向下滚动，触发懒加载
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(2)

        # 显式等待商品加载
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/prd/')]"))
            )
        except Exception:
            print(f"  ⚠️ [第 {page_num} 页] 等待超时，直接提取...")

        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/prd/')]")
        found_urls = list(set([link.get_attribute('href') for link in links]))

        if not found_urls:
            debug_dir = "/app/data"
            driver.save_screenshot(
                os.path.join(debug_dir, f"error_page{page_num}.png")
            )
            with open(
                os.path.join(debug_dir, f"error_page{page_num}.html"), "w", encoding="utf-8"
            ) as f:
                f.write(driver.page_source)
            print(f"  ⚠️ [第 {page_num} 页] 未抓到链接，已保存截图")
        else:
            print(f"  🎉 [第 {page_num} 页] 发现 {len(found_urls)} 个商品链接")
    finally:
        driver.quit()

    return found_urls


def main():
    print("=" * 50)
    print("Task 2: 多线程商品链接收割 (页 1-5)")
    print("=" * 50)

    # 先建立数据库连接（每个线程独立用，但共享同一个连接加锁）
    db_conn = get_db_connection()
    print("✅ 已连接 MySQL 数据库")

    # 使用线程池并发抓取 5 页
    pages = [1, 2, 3, 4, 5]
    all_urls = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_page = {executor.submit(scrape_page, p): p for p in pages}
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                urls = future.result()
                all_urls.extend(urls)
            except Exception as e:
                print(f"❌ [第 {page} 页] 线程异常: {e}")

    # 去重后统一入库
    unique_urls = list(set(all_urls))
    print(f"\n📊 多线程爬取完毕，共发现 {len(unique_urls)} 个不重复商品链接")
    print("正在写入数据库...")
    for url in unique_urls:
        save_link_to_db(db_conn, url)

    db_conn.close()
    print("✅ Task 2 执行完毕！")


if __name__ == "__main__":
    main()
