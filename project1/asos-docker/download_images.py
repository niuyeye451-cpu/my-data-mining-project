#!/usr/bin/env python3
"""
ASOS 商品图片下载脚本 (WSL 端运行)
从 MySQL 读取 images_dir 中的图片 URL 列表，通过代理下载到本地。

使用方法:
  python download_images.py --limit 5          # 下载 5 件商品的图片
  python download_images.py --product 209733038 # 下载指定商品
  python download_images.py --all               # 下载全部
"""

import argparse
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
    'database': 'asos_db',
}
OUTPUT_DIR = './data/images'

# 代理配置（Clash 默认端口）
PROXY = 'http://127.0.0.1:7897'

# 下载请求头
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ),
    'Referer': 'https://www.asos.com/',
    'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
}


def download_images(product_code, images_json, output_dir, use_proxy=True):
    """下载指定商品的所有图片"""
    try:
        urls = json.loads(images_json)
    except (json.JSONDecodeError, TypeError):
        print(f"  ⚠️ {product_code}: 无法解析图片 URL 列表")
        return 0

    if not urls:
        print(f"  ⚠️ {product_code}: 无图片 URL")
        return 0

    img_dir = os.path.join(output_dir, str(product_code))
    os.makedirs(img_dir, exist_ok=True)

    downloaded = 0
    for i, url in enumerate(urls):
        try:
            save_path = os.path.join(img_dir, f'{i}.jpg')
            if os.path.exists(save_path):
                downloaded += 1
                continue  # 跳过已下载

            req = urllib.request.Request(url, headers=HEADERS)
            if use_proxy:
                req.set_proxy(PROXY, 'https')

            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(save_path, 'wb') as f:
                    f.write(resp.read())
            downloaded += 1
        except Exception as e:
            print(f"    ❌ {product_code} 图片 {i}: {e}")

    return downloaded


def main():
    parser = argparse.ArgumentParser(description='ASOS 商品图片下载')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--limit', type=int, help='下载前 N 件商品')
    group.add_argument('--product', type=str, help='下载指定 product_code')
    group.add_argument('--all', action='store_true', help='下载全部')
    parser.add_argument('--no-proxy', action='store_true', help='不使用代理')
    parser.add_argument('--proxy', type=str, default=PROXY, help=f'代理地址 (默认: {PROXY})')
    args = parser.parse_args()

    if not any([args.limit, args.product, args.all]):
        args.limit = 5  # 默认下载 5 件

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    if args.product:
        cursor.execute(
            "SELECT product_code, images_dir FROM asos_dresses WHERE product_code = %s",
            (args.product,)
        )
    else:
        limit = args.limit if args.limit else 999999
        cursor.execute(
            "SELECT product_code, images_dir FROM asos_dresses "
            "WHERE images_dir IS NOT NULL AND images_dir != '' AND images_dir != '[]' "
            "LIMIT %s", (limit,)
        )

    tasks = cursor.fetchall()
    print(f"📦 共 {len(tasks)} 件商品待下载")
    use_proxy = not args.no_proxy

    total = 0
    for task in tasks:
        code = task['product_code']
        img_json = task['images_dir']
        print(f"\n🚀 正在下载: {code}")
        n = download_images(code, img_json, OUTPUT_DIR, use_proxy)
        total += n
        print(f"  ✅ {code}: 下载 {n} 张图片")
        time.sleep(0.5)  # 礼貌间隔

    print(f"\n🎉 完成！共下载 {total} 张图片 → {os.path.abspath(OUTPUT_DIR)}")
    cursor.close()
    conn.close()


if __name__ == '__main__':
    main()
