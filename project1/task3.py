import time
import re
import random
import mysql.connector
from mysql.connector import Error
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class AsosScraperTask3:
    def __init__(self):
        print("正在初始化 Task 3 进阶版...")
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.db_conn = self.connect_to_db()

    def connect_to_db(self):
        try:
            conn = mysql.connector.connect(
                host='db', database='asos_db', user='root', password='rootpassword'
            )
            return conn
        except Error as e:
            print(f"❌ 数据库连接失败: {e}")
            return None

    def scrape_product_details(self, url):
        """解析页面获取商品详细信息，含主图提取"""
        print(f"\n🚀 正在抓取: {url}")
        try:
            self.driver.get(url)
            # 随机休眠防封
            time.sleep(random.uniform(3, 5)) 
            
            data = {"url": url}
            code_match = re.search(r'/prd/(\d+)', url)
            data["product_code"] = code_match.group(1) if code_match else "unknown"
            
            # 基础信息提取
            try: data["title"] = self.driver.find_element(By.XPATH, "//h1").text.strip()
            except: data["title"] = "未获取到标题"
            
            try: data["price"] = self.driver.find_element(By.XPATH, "//span[contains(@class, 'current-price')] | //span[contains(@data-testid, 'current-price')]").text.strip()
            except: data["price"] = ""

            try: data["colour"] = self.driver.find_element(By.XPATH, "//span[contains(translate(text(), 'COLOUR', 'colour'), 'colour')]/following-sibling::span").text.strip()
            except: data["colour"] = ""
            
            try: data["description"] = re.sub(r'\s+', ' ', self.driver.find_element(By.ID, "productDescriptionDetails").get_attribute("textContent")).strip()
            except: data["description"] = ""

            try: data["brand"] = self.driver.find_element(By.XPATH, "//a[contains(@data-testid, 'brand')]").text.strip()
            except: data["brand"] = data["title"].split()[0] if data["title"] else ""

            # 【新增】主图提取逻辑 (寻找包含 asos-media 的高清图)
            try:
                img_element = self.driver.find_element(By.XPATH, "//img[contains(@src, 'images.asos-media.com')]")
                # 把缩略图参数去掉，获取高清原图
                raw_img_url = img_element.get_attribute("src")
                data["image_url"] = raw_img_url.split('?')[0] + "?$n_640w$&wid=513&fit=constrain"
            except: 
                data["image_url"] = ""

            return data
        except Exception as e:
            print(f"❌ 抓取商品异常: {e}")
            return None

    def update_db_details(self, data):
        cursor = self.db_conn.cursor()
        sql = """
            UPDATE asos_dresses 
            SET title=%s, price=%s, brand=%s, colour=%s, description=%s, image_url=%s, status=1 
            WHERE product_code=%s
        """
        cursor.execute(sql, (
            data['title'], data['price'], data['brand'], 
            data['colour'], data['description'], data['image_url'], data['product_code']
        ))
        self.db_conn.commit()
        print(f"  ✅ 成功入库: {data['title'][:20]}... 💰 {data['price']}")
        cursor.close()

    def mark_as_failed(self, product_code):
        cursor = self.db_conn.cursor()
        cursor.execute("UPDATE asos_dresses SET status=2 WHERE product_code=%s", (product_code,))
        self.db_conn.commit()
        print(f"  ⚠️ 抓取失败，已标记为状态2: {product_code}")
        cursor.close()

    def run_task3(self, limit=72):
        if not self.db_conn or not self.db_conn.is_connected(): return

        cursor = self.db_conn.cursor(dictionary=True)
        # 每次取1条锁定，这是为了后续开多个终端同时爬取做准备
        cursor.execute("SELECT product_code, url FROM asos_dresses WHERE status = 0 LIMIT %s", (limit,))
        tasks = cursor.fetchall()
        
        if not tasks:
            print("🎉 任务队列空空如也，所有商品已抓取完毕！")
            return
            
        print(f"📦 发现 {len(tasks)} 个待抓取任务，开始干活！")
        for task in tasks:
            data = self.scrape_product_details(task['url'])
            if data and data.get("title") != "未获取到标题":
                self.update_db_details(data)
            else:
                self.mark_as_failed(task['product_code'])

    def close(self):
        if self.db_conn and self.db_conn.is_connected():
            self.db_conn.close()
        self.driver.quit()

if __name__ == "__main__":
    scraper = AsosScraperTask3()
    try:
        # 这里设置为 72，直接一口气把刚才爬到的链接全消化掉
        scraper.run_task3(limit=72) 
    finally:
        scraper.close()