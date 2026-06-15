"""
Task 4: ASOS 商品图片批量下载
从 MySQL 读取 images_dir 字段，逐个下载到 ./data/images/{product_code}/
"""
import json
import os
import sys
import time
import urllib.request

import mysql.connector

# ============ 配置 ============
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'rootpassword',
    'database': 'asos_local',
}

OUTPUT_DIR = './data/images'

# 浏览器请求头（绕过 Akamai 防盗链的关键）
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

# 下载配置
REQUEST_TIMEOUT = 20       # 单张超时 (秒)
REQUEST_INTERVAL = 0.8     # 请求间隔 (秒)，防速率限制
MAX_RETRIES = 3            # 最大重试次数
MAX_PER_PRODUCT = 72       # 单次最多处理的商品数


class ImageDownloader:
    def __init__(self):
        self.db = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.db.cursor(dictionary=True)
        self.stats = {"total_products": 0, "total_images": 0, "downloaded": 0, "skipped": 0, "failed": 0}

    # ======================== 下载核心 ========================

    def download_one(self, url, save_path):
        """单张图片下载，含指数退避重试"""
        for attempt in range(MAX_RETRIES):
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                    data = resp.read()
                    if len(data) < 1000:
                        continue  # 太小，重试

                    with open(save_path, 'wb') as f:
                        f.write(data)
                    return True
            except Exception:
                pass

            if attempt < MAX_RETRIES - 1:
                time.sleep(3 ** attempt)  # 1s → 3s → 9s

        return False

    def download_product_images(self, product_code, images_json):
        """下载单个商品的所有图片"""
        try:
            urls = json.loads(images_json)
        except (json.JSONDecodeError, TypeError):
            return 0, 0

        if not urls:
            return 0, 0

        img_dir = os.path.join(OUTPUT_DIR, str(product_code))
        os.makedirs(img_dir, exist_ok=True)

        downloaded = 0
        for i, url in enumerate(urls):
            save_path = os.path.join(img_dir, f'{i}.jpg')

            # 已下载过的跳过
            if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
                self.stats["skipped"] += 1
                downloaded += 1
                continue

            if self.download_one(url, save_path):
                self.stats["downloaded"] += 1
                downloaded += 1
            else:
                self.stats["failed"] += 1

            time.sleep(REQUEST_INTERVAL)

        return downloaded, len(urls)

    # ======================== 主流程 ========================

    def run(self, limit=None, product_code=None):
        """运行下载任务

        Args:
            limit: 限制下载商品数量
            product_code: 指定单个商品编号
        """
        print("=" * 50)
        print("Task 4: 商品图片批量下载")
        print("=" * 50)

        # 查询待下载商品
        if product_code:
            self.cursor.execute(
                "SELECT product_code, images_dir FROM asos_dresses "
                "WHERE product_code = %s AND images_dir != '' AND images_dir != '[]'",
                (product_code,)
            )
        else:
            limit = limit or MAX_PER_PRODUCT
            self.cursor.execute(
                "SELECT product_code, images_dir FROM asos_dresses "
                "WHERE images_dir IS NOT NULL AND images_dir != '' AND images_dir != '[]' "
                "LIMIT %s", (limit,)
            )

        tasks = self.cursor.fetchall()

        if not tasks:
            print("🎉 没有需要下载图片的商品")
            return

        print(f"📦 共 {len(tasks)} 件商品待下载\n")

        for i, task in enumerate(tasks, 1):
            code = task['product_code']
            img_data = task['images_dir']

            print(f"[{i}/{len(tasks)}] {code} ", end="", flush=True)

            try:
                urls = json.loads(img_data)
                total_urls = len(urls) if urls else 0
            except Exception:
                total_urls = 0

            downloaded, total = self.download_product_images(code, img_data)
            self.stats["total_products"] += 1
            self.stats["total_images"] += total

            print(f"→ {downloaded}/{total} 张")

        self._print_summary()

    # ======================== 统计 ========================

    def _print_summary(self):
        print(f"\n{'=' * 50}")
        print(f"📊 下载统计")
        print(f"{'=' * 50}")
        print(f"  商品数:     {self.stats['total_products']}")
        print(f"  图片总数:   {self.stats['total_images']}")
        print(f"  ✅ 新下载:  {self.stats['downloaded']}")
        print(f"  ⏭️ 已跳过:  {self.stats['skipped']}")
        print(f"  ❌ 失败:    {self.stats['failed']}")
        print(f"\n  存储路径:   {os.path.abspath(OUTPUT_DIR)}")

    def close(self):
        self.cursor.close()
        self.db.close()


# ======================== 入口 ========================

if __name__ == "__main__":
    # 用法:
    #   python task4.py              → 下载所有（上限 72 件）
    #   python task4.py 5            → 下载前 5 件
    #   python task4.py 209733038    → 下载指定商品
    downloader = ImageDownloader()
    try:
        arg = sys.argv[1] if len(sys.argv) > 1 else None
        if arg:
            if arg.isdigit() and len(arg) >= 8:
                # 像 product_code
                downloader.run(product_code=arg)
            else:
                downloader.run(limit=int(arg))
        else:
            downloader.run()
    finally:
        downloader.close()
