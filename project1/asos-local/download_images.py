"""
ASOS 商品图片下载脚本
借鉴老师 urlretrieve 简洁思路 + 浏览器请求头绕过 Akamai 防盗链 + 指数退避重试
"""
import json
import os
import sys
import time
import urllib.request

import mysql.connector

DB_CONFIG = {
    'host': 'localhost', 'port': 3306,
    'user': 'root', 'password': 'rootpassword',
    'database': 'asos_local',
}
OUTPUT_DIR = './data/images'

# 老师的方法无法绕过 Akamai → 补上完整浏览器请求头
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.asos.com/",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "cross-site",
}


def download_one(image_url, save_path, max_retries=3):
    """
    借鉴老师的 urlretrieve 思路，加上请求头 + 指数退避重试
    老师原版: urllib.request.urlretrieve(image_url, save_path)
    改进版: urlopen + headers + 重试
    """
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(image_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                if len(data) > 1000:
                    with open(save_path, 'wb') as f:
                        f.write(data)
                    return True
            # 如果太小，重试
        except Exception:
            pass
        # 指数退避：1s → 3s → 9s
        if attempt < max_retries - 1:
            time.sleep(3 ** attempt)
    return False


def download_product_images(product_code, images_json):
    """下载单个商品的所有图片"""
    try:
        urls = json.loads(images_json)
    except (json.JSONDecodeError, TypeError):
        print(f"  ⚠️ 无法解析图片列表")
        return 0

    if not urls:
        return 0

    img_dir = os.path.join(OUTPUT_DIR, str(product_code))
    os.makedirs(img_dir, exist_ok=True)

    downloaded = 0
    for i, url in enumerate(urls):
        save_path = os.path.join(img_dir, f'{i}.jpg')
        if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
            downloaded += 1
            continue

        if download_one(url, save_path):
            downloaded += 1

        time.sleep(0.5)  # 请求间隔

    return downloaded


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    print(f"📦 下载前 {limit} 件商品图片\n")

    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT product_code, images_dir FROM asos_dresses "
        "WHERE images_dir IS NOT NULL AND images_dir != '' AND images_dir != '[]' "
        "LIMIT %s", (limit,)
    )
    tasks = cursor.fetchall()
    db.close()

    total = 0
    for task in tasks:
        code = task['product_code']
        print(f"  {code} ... ", end="", flush=True)
        n = download_product_images(code, task['images_dir'])
        total += n
        print(f"{n} 张")

    print(f"\n🎉 共 {total} 张 → {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()
