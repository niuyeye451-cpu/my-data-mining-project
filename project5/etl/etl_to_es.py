#!/usr/bin/env python3
"""
MySQL → Elasticsearch 数据导入脚本
从 gyy_mall 表读取商品数据，关联 gyy_category 获取类别名，批量索引到 ES
"""
import os
import time
import pymysql
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# ========== 配置 ==========
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'port': int(os.environ.get('MYSQL_PORT', 3306)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DATABASE', 'gyy'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,  # 返回字典格式
}

ES_HOST = os.environ.get('ES_HOST', 'http://localhost:9200')
INDEX_NAME = 'gyy_mall'

# ========== ES 索引映射（Mapping） ==========
INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                # ik_max_word: 索引时细粒度切分，最大化召回率
                # 例如"不锈钢螺丝" -> ["不锈钢", "不锈", "钢", "螺丝"]
                "ik_index": {
                    "type": "custom",
                    "tokenizer": "ik_max_word"
                },
                # ik_smart: 搜索时粗粒度切分，提升精准度
                # 例如"不锈钢螺丝" -> ["不锈钢", "螺丝"]
                "ik_search": {
                    "type": "custom",
                    "tokenizer": "ik_smart"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "itemid":    {"type": "integer"},
            "title":     {
                "type": "text",
                "analyzer": "ik_index",
                "search_analyzer": "ik_search",
                "fields": {
                    "keyword": {"type": "keyword", "ignore_above": 500}
                }
            },
            "price":     {"type": "float"},
            "picture":   {"type": "keyword", "index": False},
            "catid":     {"type": "integer"},
            "catname":   {"type": "keyword"},
            "companyid": {"type": "integer"},
            "company":   {"type": "keyword"},
            "areaid":    {"type": "integer"},
            "areaname":  {"type": "keyword"},
            "parentid":  {"type": "integer"},
            "vip":       {"type": "integer"},
        }
    }
}


def get_es_client():
    """创建 ES 客户端，等待连接就绪"""
    es = Elasticsearch(ES_HOST)
    # 等待 ES 就绪
    for _ in range(30):
        try:
            if es.ping():
                print(f"✅ ES 连接成功: {ES_HOST}")
                return es
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError("❌ ES 连接超时，请检查 docker compose up -d 是否成功")


def create_index(es: Elasticsearch):
    """创建 ES 索引（如果已存在则先删除）"""
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"  已删除旧索引: {INDEX_NAME}")

    es.indices.create(index=INDEX_NAME, body=INDEX_MAPPING)
    print(f"✅ 索引创建成功: {INDEX_NAME}")


def fetch_products_from_mysql():
    """从 MySQL 读取商品数据，JOIN 类别表获取 catname"""
    conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()

    # JOIN gyy_category 获取类别名称
    sql = """
        SELECT
            m.itemid,
            m.title,
            m.price,
            m.picture,
            m.catid,
            c.catname,
            m.companyid,
            m.company,
            m.areaid,
            m.areaname,
            m.parentid,
            m.vip
        FROM gyy_mall m
        LEFT JOIN gyy_category c ON m.catid = c.catid
        ORDER BY m.itemid
    """
    cursor.execute(sql)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    print(f"  从 MySQL 读取 {len(products)} 条商品数据")
    return products


def generate_actions(products):
    """生成 bulk API 的 actions 生成器"""
    for p in products:
        yield {
            "_index": INDEX_NAME,
            "_id": p["itemid"],
            "_source": {
                "itemid": p["itemid"],
                "title": p["title"],
                "price": p["price"],
                "picture": p["picture"] or "",
                "catid": p["catid"],
                "catname": p.get("catname") or "",
                "companyid": p["companyid"],
                "company": p["company"],
                "areaid": p["areaid"],
                "areaname": p["areaname"],
                "parentid": p["parentid"],
                "vip": p["vip"],
            }
        }


def index_products(es: Elasticsearch, products):
    """批量索引商品到 ES"""
    success, errors = bulk(es, generate_actions(products), chunk_size=200, raise_on_error=False)
    print(f"  成功索引: {success} 条")
    if errors:
        print(f"  失败: {len(errors)} 条")
        for err in errors[:3]:  # 只打印前3条错误
            print(f"    {err}")
    # 刷新索引，使文档立即可搜索
    es.indices.refresh(index=INDEX_NAME)


def verify(es: Elasticsearch):
    """验证索引结果，执行几个测试查询"""
    count = es.count(index=INDEX_NAME)["count"]
    print(f"\n✅ ES 索引文档总数: {count}")

    # 测试1：全量查询
    total = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}, "size": 0})["hits"]["total"]["value"]
    print(f"  match_all 命中数: {total}")

    # 测试2：中文全文搜索
    test_queries = ["螺丝", "不锈钢", "轴承"]
    for q in test_queries:
        resp = es.search(index=INDEX_NAME, body={
            "query": {"match": {"title": q}},
            "size": 0
        })
        hit_count = resp["hits"]["total"]["value"]
        print(f"  搜索 '{q}' 命中数: {hit_count}")

    # 测试3：聚合查询 - 分类分布
    resp = es.search(index=INDEX_NAME, body={
        "size": 0,
        "aggs": {
            "categories": {
                "terms": {"field": "catname", "size": 35}
            }
        }
    })
    cat_count = len(resp["aggregations"]["categories"]["buckets"])
    print(f"  类别聚合 buckets: {cat_count}（共33个类别）")


def main():
    print("=" * 50)
    print("MySQL → Elasticsearch 数据导入")
    print("=" * 50)

    # 1. 连接 ES
    print("\n1. 连接 Elasticsearch...")
    es = get_es_client()

    # 2. 创建索引
    print("\n2. 创建索引...")
    create_index(es)

    # 3. 从 MySQL 读取数据
    print("\n3. 读取 MySQL 数据...")
    products = fetch_products_from_mysql()

    if not products:
        print("  警告：MySQL 中没有数据，请先运行 generate_data.py")
        return

    # 4. 批量索引到 ES
    print("\n4. 索引文档到 ES...")
    index_products(es, products)

    # 5. 验证
    print("\n5. 验证索引结果...")
    verify(es)

    print("\n" + "=" * 50)
    print("🎉 数据导入完成！")
    print("=" * 50)


if __name__ == '__main__':
    main()
