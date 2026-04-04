import time
import re
import os
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AsosScraperTask2:
    def __init__(self):
        print("正在初始化 Task 2 浏览器...")
        chrome_options = Options()
        
        # 【核心优化 1】使用最新版无头模式，极大降低被拦截概率
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 【核心优化 2】添加防爬虫隐藏参数
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # 【核心优化 3】在 Chrome 底层抹除 webdriver 标记
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        # 连接数据库
        try:
            self.db_conn = mysql.connector.connect(
                host='db', user='root', password='rootpassword', database='asos_db'
            )
            print("✅ 成功连接到 MySQL 数据库")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            self.db_conn = None

    def save_link_to_db(self, url):
        """解析 product_code 并存入数据库"""
        if not self.db_conn: return
        
        code_match = re.search(r'/prd/(\d+)', url)
        if not code_match: return
        product_code = code_match.group(1)

        cursor = self.db_conn.cursor()
        sql = "INSERT IGNORE INTO asos_dresses (product_code, url, status) VALUES (%s, %s, 0)"
        try:
            cursor.execute(sql, (product_code, url))
            self.db_conn.commit()
            if cursor.rowcount > 0:
                print(f"  🔗 新链接入库: {product_code}")
        except Exception as e:
            print(f"  ❌ 入库失败: {e}")
        finally:
            cursor.close()

    def run(self):
        # 【核心优化 4】修正 URL 路径 (把 ctas 改成了正确的 cat)
        target_url = "https://www.asos.com/women/sale/dresses/cat/?cid=5235"
        print(f"正在访问商品列表页: {target_url}")
        self.driver.get(target_url)
        
        time.sleep(3)
        print(f"📄 当前浏览器页面标题: {self.driver.title}")
        
        # 模拟真人分段向下滚动，触发商品图片的懒加载
        print("⏬ 正在模拟真人向下滚动页面...")
        for _ in range(3):
            self.driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(2)
        
        # 显式等待商品加载出来
        try:
            print("⏳ 正在等待商品数据渲染...")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/prd/')]"))
            )
        except:
            print("⚠️ 警告：显式等待商品链接超时，将直接尝试提取...")
        
        links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/prd/')]")
        found_urls = list(set([link.get_attribute('href') for link in links]))
        
        if len(found_urls) == 0:
            print("\n⚠️ 警告：依然未能抓取到任何链接！")
            debug_dir = "/app/data"
            self.driver.save_screenshot(os.path.join(debug_dir, "error_screenshot.png"))
            with open(os.path.join(debug_dir, "error_source.html"), "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("👉 已更新截图，请查看新的 error_screenshot.png")
        else:
            print(f"\n🎉 成功突破！发现 {len(found_urls)} 个商品链接，准备存入数据库...")
            for url in found_urls:
                self.save_link_to_db(url)
            print("✅ Task 2 执行完毕！链接已全部入库。")

    def close(self):
        self.driver.quit()
        if self.db_conn and self.db_conn.is_connected():
            self.db_conn.close()

if __name__ == "__main__":
    scraper = AsosScraperTask2()
    try:
        scraper.run()
    finally:
        scraper.close()