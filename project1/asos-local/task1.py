"""
Task 1: 抓取 ASOS 首页男女装分类链接
输出: ./data/gender_links.json
"""
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OUTPUT_DIR = './data'
os.makedirs(OUTPUT_DIR, exist_ok=True)


class AsosCategoryScraper:
    def __init__(self):
        print("正在初始化 Task 1 浏览器...")
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
        self.driver = webdriver.Chrome(options=opts)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        self.wait = WebDriverWait(self.driver, 15)

    def get_gender_links(self):
        print(">>> 访问 ASOS 首页...")
        self.driver.get("https://www.asos.com/")
        time.sleep(3)

        links = {}
        try:
            women_el = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//a[@data-testid='women-floor'] | //a[contains(@href, '/women')]")
            ))
            men_el = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//a[@data-testid='men-floor'] | //a[contains(@href, '/men')]")
            ))
            links['Women'] = women_el.get_attribute('href')
            links['Men'] = men_el.get_attribute('href')
            print("✅ 抓取成功")
        except Exception as e:
            print(f"❌ 抓取失败: {e}")
        return links

    def save_data(self, data, filename="gender_links.json"):
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"💾 已保存: {path}")

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    scraper = AsosCategoryScraper()
    try:
        results = scraper.get_gender_links()
        if results:
            scraper.save_data(results)
    finally:
        scraper.close()
