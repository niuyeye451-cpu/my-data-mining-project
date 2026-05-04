import time
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AsosScraperTask1:
    def __init__(self):
        print("正在初始化 Task 1 浏览器...")
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        self.wait = WebDriverWait(self.driver, 15)

    def get_gender_links(self):
        """爬取首页分类链接"""
        print(">>> 访问 ASOS 首页...")
        self.driver.get("https://www.asos.com/")
        time.sleep(3)

        links = {}
        try:
            xpath_women = "//a[@data-testid='women-floor'] | //a[contains(@href, '/women')]"
            xpath_men = "//a[@data-testid='men-floor'] | //a[contains(@href, '/men')]"

            women_element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_women)))
            men_element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_men)))

            links['Women'] = women_element.get_attribute('href')
            links['Men'] = men_element.get_attribute('href')
            print(f"✅ 成功抓取分类链接")
        except Exception as e:
            print(f"❌ 抓取失败: {e}")
        return links

    def save_data(self, data, filename="gender_links.json"):
        """保存数据到指定挂载目录"""
        save_dir = "/app/data"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        full_path = os.path.join(save_dir, filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"💾 数据已保存至容器内路径: {full_path}")

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    scraper = AsosScraperTask1()
    try:
        results = scraper.get_gender_links()
        if results:
            scraper.save_data(results)
    finally:
        scraper.close()
