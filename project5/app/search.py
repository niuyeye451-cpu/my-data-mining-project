"""
Elasticsearch 查询构建与执行
支持：bool查询(must/filter) + 高亮 + 分类/地区聚合计数
"""
import time
from elasticsearch import AsyncElasticsearch
from app.models import SearchParams


async def search_products(es: AsyncElasticsearch, params: SearchParams, index: str) -> dict:
    """
    构建 ES 查询并返回解析后的结果
    返回: {"products": [...], "total": int, "page_count": int, "query_time_ms": int,
           "cat_counts": dict, "area_counts": dict}
    """
    start = time.time()

    must_clauses: list[dict] = []
    filter_clauses: list[dict] = []

    # 1. 全文搜索
    if params.q.strip():
        must_clauses.append({"match": {"title": params.q}})
    else:
        must_clauses.append({"match_all": {}})

    # 2. 地区过滤
    if params.areaid > 0:
        filter_clauses.append({"term": {"parentid": params.areaid}})

    # 3. 类别过滤
    if params.catid > 0:
        filter_clauses.append({"term": {"catid": params.catid}})

    # 4. VIP 过滤
    if params.vip == 1:
        filter_clauses.append({"term": {"vip": 1}})

    # 5. 价格区间过滤
    price_range: dict = {}
    if params.price_min is not None:
        price_range["gte"] = params.price_min
    if params.price_max is not None:
        price_range["lte"] = params.price_max
    if price_range:
        filter_clauses.append({"range": {"price": price_range}})

    # 排序
    sort_clause: list[dict] | None = None
    if params.sort == "asc":
        sort_clause = [{"price": {"order": "asc"}}]
    elif params.sort == "desc":
        sort_clause = [{"price": {"order": "desc"}}]

    # 组装请求体
    body: dict = {
        "query": {"bool": {"must": must_clauses, "filter": filter_clauses}},
        "from": (params.page - 1) * params.size,
        "size": params.size,
        "track_total_hits": True,
        # 高亮
        "highlight": {
            "fields": {"title": {"fragment_size": 100, "number_of_fragments": 1}},
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"]
        },
        # 聚合：分类计数 + 地区计数
        "aggs": {
            "cat_counts": {"terms": {"field": "catid", "size": 35}},
            "area_counts": {"terms": {"field": "parentid", "size": 40}}
        }
    }
    if sort_clause:
        body["sort"] = sort_clause

    response = await es.search(index=index, body=body)

    total = response["hits"]["total"]["value"]
    hits = response["hits"]["hits"]

    products = []
    for hit in hits:
        src = hit["_source"]
        hl = hit.get("highlight", {}).get("title", [None])[0]
        products.append({
            "itemid": src.get("itemid"),
            "title": src.get("title", ""),
            "highlight": hl,  # 高亮 HTML 或 None
            "price": src.get("price", 0),
            "picture": src.get("picture", ""),
            "catid": src.get("catid", 0),
            "catname": src.get("catname", ""),
            "companyid": src.get("companyid", 0),
            "company": src.get("company", ""),
            "areaid": src.get("areaid", 0),
            "areaname": src.get("areaname", ""),
            "parentid": src.get("parentid", 0),
            "vip": src.get("vip", 0),
        })

    # 解析聚合计数
    cat_counts: dict[int, int] = {}
    for bucket in response.get("aggregations", {}).get("cat_counts", {}).get("buckets", []):
        cat_counts[bucket["key"]] = bucket["doc_count"]

    area_counts: dict[int, int] = {}
    for bucket in response.get("aggregations", {}).get("area_counts", {}).get("buckets", []):
        area_counts[bucket["key"]] = bucket["doc_count"]

    elapsed = int((time.time() - start) * 1000)

    return {
        "products": products,
        "total": total,
        "page_count": max(1, (total + params.size - 1) // params.size),
        "query_time_ms": elapsed,
        "cat_counts": cat_counts,
        "area_counts": area_counts,
    }
