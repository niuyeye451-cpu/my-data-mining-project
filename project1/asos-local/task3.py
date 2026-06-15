"""
Task 3: ASOS 商品详情抓取（增强版 + 并行）
从 MySQL 队列取待抓取 URL，并发提取并在 DBeaver 可见
"""
import json
import os
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import mysql.connector
from mysql.connector import Error
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# ============ 配置 ============
DB_CONFIG = {
    'host': 'localhost', 'port': 3306,
    'user': 'root', 'password': 'rootpassword',
    'database': 'asos_local',
}
MAX_WORKERS = 2       # 并行数
PAGE_LOAD_WAIT = (3, 5)  # 每个商品页等待 (秒)
TOTAL_LIMIT = 10        # 先抓 10 条验证

ISOTIMEFORMAT = '%Y-%m-%d %X'
db_lock = threading.Lock()


def create_driver():
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    driver = webdriver.Chrome(options=opts)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


# ======================== 字段提取 ========================

def extract_pdp_config(driver):
    """从 window.asos.pdp.config.productDescription JSON 提取"""
    try:
        el = driver.find_element(
            By.XPATH, "//script[contains(text(), 'window.asos.pdp.config')]"
        )
        text = el.get_attribute("innerHTML")
        match = re.search(
            r'window\.asos\.pdp\.config\.productDescription\s*=\s*(\{.+?\});\s*\n',
            text, re.DOTALL
        )
        if match:
            return json.loads(match.group(1))
    except Exception:
        pass
    return {}


def extract_from_source(driver, key):
    try:
        match = re.search(rf'"{key}"\s*:\s*"([^"]*)"', driver.page_source)
        if match:
            return match.group(1)
    except Exception:
        pass
    return ''


def extract_title(driver):
    try:
        return driver.find_element(By.XPATH, "//h1").text.strip()
    except Exception:
        return "未获取到标题"


def extract_price(driver):
    try:
        return driver.find_element(
            By.XPATH,
            "//span[contains(@class, 'current-price')] | "
            "//span[contains(@data-testid, 'current-price')]"
        ).text.strip()
    except Exception:
        return ""


def extract_breadcrumb(driver):
    try:
        links = driver.find_elements(
            By.XPATH, "//nav//a[contains(@href, '/women') or contains(@href, '/men')]"
        )
        if links:
            return ' > '.join(el.text.strip() for el in links if el.text.strip())
    except Exception:
        pass
    return ''


def extract_sizes(driver):
    sizes = []
    try:
        for opt in driver.find_element(By.XPATH, "//select").find_elements(By.TAG_NAME, "option"):
            txt = opt.text.strip()
            if txt and txt.lower() != "please select":
                sizes.append(txt)
    except Exception:
        pass
    return ';'.join(sizes)


def extract_description(driver):
    try:
        return re.sub(r'\s+', ' ', driver.find_element(By.ID, "productDescription").text).strip()
    except Exception:
        return ''


def extract_main_image(driver):
    try:
        raw = driver.find_element(
            By.XPATH, "//img[contains(@src, 'images.asos-media.com')]"
        ).get_attribute("src")
        return raw.split('?')[0] + "?$n_640w$&wid=513&fit=constrain"
    except Exception:
        return ''


def extract_gallery(driver):
    seen = set()
    urls = []
    try:
        for img in driver.find_elements(By.XPATH, "//img[@class='gallery-image']"):
            src = img.get_attribute("src")
            if src and src not in seen:
                seen.add(src)
                urls.append(src)
    except Exception:
        pass
    return urls


# ======================== 单商品抓取 ========================

# ======================== 数据验证 ========================

ERROR_PAGE_PATTERNS = [
    "page isn't",
    "page isn’t",
    "this page isn",
    "http error",
    "access denied",
    "are you a robot",
    "captcha",
    "bot detected",
    "redirecting",
    "javascript is disabled",
    "enable javascript",
]

PRICE_PATTERN = re.compile(r'[\$\£\€]?\s*\d+\.?\d{0,2}')


def validate_data(data):
    """
    多维度校验抓取结果，返回 (is_valid, fail_reason)
    """
    # 1. 标题校验
    title = (data.get("title") or "").strip()
    if not title:
        return False, "标题为空"
    if title == "未获取到标题":
        return False, "标题提取失败"
    title_lower = title.lower()
    for pat in ERROR_PAGE_PATTERNS:
        if pat in title_lower:
            return False, f"错误页: {title[:60]}"

    # 2. 标题长度（正常商品标题至少 10 个字符）
    if len(title) < 10:
        return False, f"标题过短: {title[:60]}"

    # 3. 价格校验
    price = (data.get("price") or "").strip()
    if not price:
        return False, "价格为空"
    if not PRICE_PATTERN.search(price):
        return False, f"价格格式异常: {price}"
    # 价格不应超过 5 位数（正常单件 < £9999）
    price_nums = re.findall(r'\d+\.?\d*', price)
    if price_nums and float(price_nums[0]) > 99999:
        return False, f"价格异常偏高: {price}"

    # 4. 页面 URL 校验（加载后不应跳转到首页或搜索页）
    url = (data.get("url") or "").lower()
    if url:
        if "/prd/" not in url:
            return False, "URL 不含 product 标识"
        skip_patterns = ["asos.com/?" , "asos.com/search", "asos.com/cart"]
        for sp in skip_patterns:
            if sp in url:
                return False, f"页面跳转至: {url[:60]}"

    # 5. 品牌 -- 可以为空（部分 ASOS 商品无品牌字段），但不能是超长字符串
    brand = data.get("brand") or ""
    if len(brand) > 150:
        return False, "品牌字段异常"

    # 6. 图片 -- 至少有一张主图是正常的
    img = data.get("image_url") or ""
    if img and "images.asos-media.com" not in img:
        return False, "主图 URL 非 ASOS CDN"

    return True, "ok"


def scrape_one_product(url):
    """抓取单个商品详情（线程安全，独立 WebDriver）"""
    driver = create_driver()
    try:
        code_match = re.search(r'/prd/(\d+)', url)
        product_code = code_match.group(1) if code_match else "unknown"

        driver.get(url)
        time.sleep(random.uniform(*PAGE_LOAD_WAIT))

        # 检查加载后的实际 URL（防止跳转到错误页/首页）
        actual_url = driver.current_url

        breadcrumb = extract_breadcrumb(driver)
        gender = 1 if 'Men' in breadcrumb else 0

        # 基础字段
        title = extract_title(driver)
        price = extract_price(driver)
        brand = extract_from_source(driver, "brandName")
        colour = extract_from_source(driver, "colour")
        description = extract_description(driver)

        # pdp.config JSON
        pdp = extract_pdp_config(driver)
        material = re.sub(r'<br\s*/?>', '\n', pdp.get("aboutMe", ""))
        care_info = re.sub(r'<br\s*/?>', '\n', pdp.get("careInfo", ""))

        sizes = extract_sizes(driver)
        main_img = extract_main_image(driver)
        gallery = extract_gallery(driver)

        return {
            "product_code": product_code,
            "url": actual_url,           # 实际加载后的 URL
            "title": title,
            "price": price,
            "brand": brand,
            "colour": colour,
            "description": description,
            "material": material,
            "size_options": sizes,
            "care_info": care_info,
            "gender": gender,
            "image_url": main_img,
            "images_dir": json.dumps(gallery) if gallery else "",
            "crawled_at": time.strftime(ISOTIMEFORMAT, time.localtime()),
            "gallery_count": len(gallery),
        }
    except Exception as e:
        return {"product_code": "error", "title": None, "error": str(e)}
    finally:
        driver.quit()


# ======================== 主流程 ========================

def main():
    print("=" * 50)
    print(f"Task 3: 并行详情抓取 (并发 {MAX_WORKERS}, 限 {TOTAL_LIMIT} 条)")
    print("=" * 50)

    db = mysql.connector.connect(**DB_CONFIG)
    print("✅ 已连接 MySQL (asos_local)")

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT product_code, url FROM asos_dresses WHERE status = 0 LIMIT %s",
        (TOTAL_LIMIT,)
    )
    tasks = cursor.fetchall()
    cursor.close()

    if not tasks:
        print("🎉 无待抓取任务")
        db.close()
        return

    print(f"📦 共 {len(tasks)} 个任务，开始并行抓取...\n")

    success = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(scrape_one_product, t['url']): t['product_code']
            for t in tasks
        }
        for future in as_completed(futures):
            code = futures[future]
            try:
                data = future.result(timeout=60)
            except Exception as e:
                print(f"  ❌ {code}: 超时或异常 - {e}")
                with db_lock:
                    c = db.cursor()
                    c.execute("UPDATE asos_dresses SET status=2 WHERE product_code=%s", (code,))
                    db.commit()
                    c.close()
                failed += 1
                continue

            is_valid, reason = validate_data(data)
            if is_valid:
                with db_lock:
                    c = db.cursor()
                    c.execute("""
                        UPDATE asos_dresses SET
                            title=%s, price=%s, brand=%s, colour=%s, description=%s,
                            image_url=%s, status=1,
                            material=%s, size_options=%s, care_info=%s,
                            gender=%s, images_dir=%s, crawled_at=%s
                        WHERE product_code=%s
                    """, (
                        data['title'], data['price'], data['brand'],
                        data['colour'], data['description'], data['image_url'],
                        data['material'], data['size_options'], data['care_info'],
                        data['gender'], data['images_dir'], data['crawled_at'],
                        data['product_code']
                    ))
                    db.commit()
                    c.close()
                extras = f"🖼️x{data['gallery_count']}" if data.get('gallery_count') else ""
                if data.get('material'):
                    extras += " 🧵"
                if data.get('size_options'):
                    extras += f" 📏{data['size_options'][:30]}"
                print(f"  ✅ {data['title'][:40]}... 💰{data['price']} {extras}")
                success += 1
            else:
                with db_lock:
                    c = db.cursor()
                    c.execute("UPDATE asos_dresses SET status=2 WHERE product_code=%s", (code,))
                    db.commit()
                    c.close()
                print(f"  ⚠️ {code}: 失败 — {reason}")
                failed += 1

    print(f"\n✅ Task 3 完成！成功 {success}, 失败 {failed}")
    db.close()


if __name__ == "__main__":
    main()
