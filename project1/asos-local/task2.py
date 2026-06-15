"""
Task 2: 多线程爬取 ASOS 打折裙装商品链接，存入 MySQL
并发 3 线程，错峰启动防封
"""
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ============ 配置 ============
DB_CONFIG = {
    'host': 'localhost', 'port': 3306,
    'user': 'root', 'password': 'rootpassword',
    'database': 'asos_local',
}
BASE_URL = "https://www.asos.com/women/sale/dresses/cat/?cid=5235"
PAGES = [1, 2, 3, 4, 5]
MAX_WORKERS = 3  # 降低并发，避免冲垮代理
DELAY_BETWEEN_THREADS = 3  # 线程间隔启动(秒)

db_lock = threading.Lock()


def create_driver():
    tname = threading.current_thread().name
    print(f"  [{tname}] 初始化浏览器...")
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--window-size=1920,1080')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    driver = webdriver.Chrome(options=opts)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


def scrape_page(page_num):
    """抓取单页，返回 URL 列表"""
    url = f"{BASE_URL}&page={page_num}"
    print(f"\n📄 [第 {page_num} 页] {url}")

    driver = create_driver()
    try:
        driver.get(url)
        time.sleep(3)
        print(f"  [第 {page_num} 页] 标题: {driver.title}")

        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(2)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//a[contains(@href, '/prd/')]")
                )
            )
        except Exception:
            print(f"  ⚠️ [第 {page_num} 页] 等待超时")

        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/prd/')]")
        urls = list(set([l.get_attribute('href') for l in links]))

        if not urls:
            driver.save_screenshot(f"./data/error_page{page_num}.png")
            print(f"  ⚠️ [第 {page_num} 页] 未抓到链接")
        else:
            print(f"  🎉 [第 {page_num} 页] 发现 {len(urls)} 个链接")
        return urls
    finally:
        driver.quit()


def main():
    print("=" * 50)
    print(f"Task 2: 多线程商品链接收割 (并发 {MAX_WORKERS})")
    print("=" * 50)

    db = mysql.connector.connect(**DB_CONFIG)
    print("✅ 已连接 MySQL (asos_local)")

    # 清空旧数据重新开始
    cursor = db.cursor()
    cursor.execute("TRUNCATE TABLE asos_dresses")
    db.commit()
    cursor.close()
    print("🧹 已清空旧数据")

    all_urls = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for i, page in enumerate(PAGES):
            if i > 0:
                time.sleep(DELAY_BETWEEN_THREADS)  # 错峰提交
            futures[executor.submit(scrape_page, page)] = page

        for future in as_completed(futures):
            page = futures[future]
            try:
                all_urls.extend(future.result())
            except Exception as e:
                print(f"❌ [第 {page} 页] 线程异常: {e}")

    unique_urls = list(set(all_urls))
    print(f"\n📊 共 {len(unique_urls)} 个不重复链接，正在入库...")

    for url in unique_urls:
        m = re.search(r'/prd/(\d+)', url)
        if not m:
            continue
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT IGNORE INTO asos_dresses (product_code, url, status) VALUES (%s, %s, 0)",
                (m.group(1), url)
            )
            db.commit()
        except Exception:
            pass
        finally:
            cursor.close()

    # 统计
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM asos_dresses")
    total = cursor.fetchone()[0]
    cursor.close()

    db.close()
    print(f"✅ Task 2 完成！共 {total} 条链接入库")


if __name__ == "__main__":
    main()
