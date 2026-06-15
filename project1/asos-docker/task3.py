import time
import re
import json
import os
import random
import mysql.connector
from mysql.connector import Error
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

ISOTIMEFORMAT = '%Y-%m-%d %X'


class AsosScraperTask3:
    def __init__(self):
        print("正在初始化 Task 3 增强版浏览器...")
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        self.wait = WebDriverWait(self.driver, 8)
        self.db_conn = self._connect_db()

    # ======================== 数据库 ========================

    def _connect_db(self):
        try:
            conn = mysql.connector.connect(
                host='db', database='asos_db',
                user='root', password='rootpassword'
            )
            print("✅ 数据库连接成功")
            return conn
        except Error as e:
            print(f"❌ 数据库连接失败: {e}")
            return None

    # ======================== JSON 配置提取（ASOS 新架构） ========================

    def _extract_pdp_config(self):
        """从页面中提取 window.asos.pdp.config JSON，包含品牌/材质/洗护等"""
        try:
            script_el = self.driver.find_element(
                By.XPATH,
                "//script[contains(text(), 'window.asos.pdp.config')]"
            )
            text = script_el.get_attribute("innerHTML")
            # 提取 JSON 对象：从 productDescription 开始到最近的 };
            match = re.search(
                r'window\.asos\.pdp\.config\.productDescription\s*=\s*(\{.+?\});\s*\n',
                text, re.DOTALL
            )
            if match:
                return json.loads(match.group(1))
        except Exception:
            pass
        return {}

    def _extract_brand_from_meta(self):
        """从 meta 标签或页面 JSON 提取品牌名"""
        # 方法1：从 JSON-LD 结构化数据提取
        try:
            script = self.driver.find_element(
                By.XPATH, "//script[@type='application/ld+json']"
            )
            ld_json = json.loads(script.get_attribute("innerHTML"))
            if isinstance(ld_json, dict):
                brand = ld_json.get('brand', {}).get('name', '')
                if brand:
                    return brand
        except Exception:
            pass

        # 方法2：从页面 config JSON 提取 brandName
        try:
            text = self.driver.page_source
            match = re.search(r'"brandName"\s*:\s*"([^"]+)"', text)
            if match:
                return match.group(1)
        except Exception:
            pass
        return ''

    def _extract_colour_from_config(self):
        """从页面 JSON 提取颜色"""
        try:
            text = self.driver.page_source
            match = re.search(r'"colour"\s*:\s*"([^"]+)"', text)
            if match:
                return match.group(1)
        except Exception:
            pass
        return ''

    # ======================== XPath 字段提取 ========================

    def _extract_breadcrumb(self):
        """面包屑导航（仅用于性别判断，不存库）"""
        try:
            links = self.driver.find_elements(
                By.XPATH, "//nav//a[contains(@href, '/women') or contains(@href, '/men')]"
            )
            if links:
                texts = [el.text.strip() for el in links if el.text.strip()]
                if texts:
                    return ' > '.join(texts)
        except Exception:
            pass
        return ''

    def _extract_gender(self, breadcrumb):
        return 1 if 'Men' in breadcrumb else 0

    def _extract_size_options(self):
        """提取可选尺码"""
        sizes = []
        try:
            select_el = self.driver.find_element(By.XPATH, "//select")
            for opt in select_el.find_elements(By.TAG_NAME, "option"):
                txt = opt.text.strip()
                if txt and txt.lower() != "please select":
                    sizes.append(txt)
        except Exception:
            pass
        return ';'.join(sizes)

    def _extract_description(self):
        """从 productDescription 区块提取描述"""
        try:
            el = self.driver.find_element(By.ID, "productDescription")
            return re.sub(r'\s+', ' ', el.text).strip()
        except Exception:
            return ''

    def _extract_main_image_url(self):
        """商品主图高清 URL"""
        try:
            img = self.driver.find_element(
                By.XPATH, "//img[contains(@src, 'images.asos-media.com')]"
            )
            raw = img.get_attribute("src")
            return raw.split('?')[0] + "?$n_640w$&wid=513&fit=constrain"
        except Exception:
            return ''

    def _extract_gallery_image_urls(self):
        """提取 gallery 图片 URL 列表"""
        seen = set()
        urls = []
        try:
            for img in self.driver.find_elements(
                By.XPATH, "//img[@class='gallery-image']"
            ):
                src = img.get_attribute("src")
                if src and src not in seen:
                    seen.add(src)
                    urls.append(src)
        except Exception:
            pass
        return urls

    # ======================== 详情抓取 ========================

    def scrape_product_details(self, url):
        print(f"\n🚀 正在抓取: {url}")
        try:
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))

            data = {"url": url}

            # product_code
            code_match = re.search(r'/prd/(\d+)', url)
            data["product_code"] = code_match.group(1) if code_match else "unknown"

            # 面包屑 → 仅用于性别判断
            breadcrumb = self._extract_breadcrumb()
            data["gender"] = self._extract_gender(breadcrumb)

            # ---- 基础字段 ----
            try:
                data["title"] = self.driver.find_element(
                    By.XPATH, "//h1"
                ).text.strip()
            except Exception:
                data["title"] = "未获取到标题"

            try:
                data["price"] = self.driver.find_element(
                    By.XPATH,
                    "//span[contains(@class, 'current-price')] | "
                    "//span[contains(@data-testid, 'current-price')]"
                ).text.strip()
            except Exception:
                data["price"] = ""

            # 品牌：优先从 JSON-LD，兜底从页面正则
            data["brand"] = self._extract_brand_from_meta()

            # 颜色：从页面 JSON 提取
            data["colour"] = self._extract_colour_from_config()

            # 描述：productDescription 区块
            data["description"] = self._extract_description()

            # ---- 新增字段：从 pdp.config JSON 提取 ----
            pdp = self._extract_pdp_config()
            data["material"] = pdp.get("aboutMe", "")
            data["care_info"] = pdp.get("careInfo", "")

            # 如果 JSON 描述有 HTML 标签，清理一下
            if data["material"]:
                data["material"] = re.sub(r'<br\s*/?>', '\n', data["material"])
            if data["care_info"]:
                data["care_info"] = re.sub(r'<br\s*/?>', '\n', data["care_info"])

            # 尺码
            data["size_options"] = self._extract_size_options()

            # 图片
            data["image_url"] = self._extract_main_image_url()
            gallery_urls = self._extract_gallery_image_urls()
            # 存图片 URL 列表（JSON 格式），方便后续下载
            data["images_dir"] = json.dumps(gallery_urls) if gallery_urls else ""
            if gallery_urls:
                print(f"    🖼️ 发现 {len(gallery_urls)} 张 gallery 图片")

            # 时间戳
            data["crawled_at"] = time.strftime(ISOTIMEFORMAT, time.localtime())

            return data

        except Exception as e:
            print(f"❌ 抓取异常: {e}")
            return None

    # ======================== 数据库更新 ========================

    def update_db_details(self, data):
        cursor = self.db_conn.cursor()
        sql = """
            UPDATE asos_dresses
            SET title=%s, price=%s, brand=%s, colour=%s, description=%s,
                image_url=%s, status=1,
                material=%s, size_options=%s, care_info=%s,
                gender=%s, images_dir=%s, crawled_at=%s
            WHERE product_code=%s
        """
        cursor.execute(sql, (
            data['title'], data['price'], data['brand'],
            data['colour'], data['description'], data['image_url'],
            data['material'], data['size_options'],
            data['care_info'], data['gender'], data['images_dir'],
            data['crawled_at'], data['product_code']
        ))
        self.db_conn.commit()
        extras = []
        if data.get('size_options'):
            extras.append(f"📏 {data['size_options']}")
        if data.get('material'):
            extras.append("🧵 有材质")
        if data.get('brand'):
            extras.append(f"🏷️ {data['brand']}")
        print(f"  ✅ 入库: {data['title'][:35]}... 💰 {data['price']} {' | '.join(extras)}")
        cursor.close()

    def mark_as_failed(self, product_code):
        cursor = self.db_conn.cursor()
        cursor.execute(
            "UPDATE asos_dresses SET status=2 WHERE product_code=%s",
            (product_code,)
        )
        self.db_conn.commit()
        print(f"  ⚠️ 已标记失败: {product_code}")
        cursor.close()

    # ======================== 主流程 ========================

    def run_task3(self, limit=72):
        if not self.db_conn or not self.db_conn.is_connected():
            print("❌ 数据库不可用")
            return

        cursor = self.db_conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT product_code, url FROM asos_dresses WHERE status = 0 LIMIT %s",
            (limit,)
        )
        tasks = cursor.fetchall()

        if not tasks:
            print("🎉 任务队列空空如也，所有商品已抓取完毕！")
            return

        print(f"📦 发现 {len(tasks)} 个待抓取任务，开始干活！")
        success, failed = 0, 0
        for task in tasks:
            data = self.scrape_product_details(task['url'])
            if data and data.get("title") != "未获取到标题":
                self.update_db_details(data)
                success += 1
            else:
                self.mark_as_failed(task['product_code'])
                failed += 1
        print(f"\n✅ 完成: {success} 成功, {failed} 失败")

    def close(self):
        if self.db_conn and self.db_conn.is_connected():
            self.db_conn.close()
        self.driver.quit()


if __name__ == "__main__":
    scraper = AsosScraperTask3()
    try:
        scraper.run_task3(limit=72)
    finally:
        scraper.close()
