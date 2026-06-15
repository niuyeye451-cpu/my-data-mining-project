from contextlib import asynccontextmanager
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Query, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import ES_HOST, ES_INDEX
from app.models import SearchParams, SearchResponse
from app.search import search_products

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"  🔗 连接 Elasticsearch: {ES_HOST}")
    app.state.es = AsyncElasticsearch(ES_HOST)
    if not await app.state.es.ping():
        print("  ⚠️ 警告：ES 连接失败，请确认 docker compose up -d")
    else:
        print("  ✅ ES 连接成功")
    yield
    await app.state.es.close()
    print("  👋 ES 连接已关闭")

app = FastAPI(
    title="工业商城搜索引擎",
    description="中文全文检索，支持分类/地区/VIP/价格过滤",
    version="2.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ========== 元数据 ==========
CATEGORIES = [
    (0, "全部"), (1, "摩托车配件"), (2, "装备制造"), (3, "电子制造"),
    (4, "材料/新材料"), (5, "生物医药"), (6, "食品/农副产品"),
    (7, "化工/塑料"), (8, "服装鞋靴"), (9, "软件/信息服务"),
    (10, "高新技术"), (11, "特色轻工/仪表"), (12, "五金制品"),
    (13, "钢铁冶金"), (14, "环保科技"), (15, "新能源"),
    (16, "电子信息"), (17, "铝加工"), (18, "家居建材/照明"),
    (19, "精密加工"), (20, "煤炭采洗"), (21, "再生资源"),
    (22, "黑色金属"), (23, "木材加工"), (24, "管道管件"),
    (25, "机械制造"), (26, "信息技术"), (27, "汽车制造及配件"),
    (28, "现代服务业"), (29, "消费品工业"), (30, "显示器产业集群"),
    (31, "大数据产业"), (32, "5G产业集群"), (33, "工业楼和总部经济"),
]

AREAS = [
    (0, "全部", 0), (1, "北京市", 1), (2, "天津市", 2),
    (3, "上海市", 9), (4, "重庆市", 22), (5, "广东省", 19),
    (6, "浙江省", 11), (7, "江苏省", 10), (8, "山东省", 15),
    (9, "河南省", 16), (10, "四川省", 23), (11, "湖北省", 17),
    (12, "湖南省", 18), (13, "福建省", 13), (14, "安徽省", 12),
    (15, "河北省", 3), (16, "辽宁省", 6), (17, "陕西省", 27),
    (18, "江西省", 14), (19, "广西壮族自治区", 20), (20, "山西省", 4),
    (21, "吉林省", 7), (22, "黑龙江省", 8), (23, "云南省", 25),
    (24, "贵州省", 24), (25, "甘肃省", 28), (26, "海南省", 21),
    (27, "内蒙古自治区", 5), (28, "宁夏回族自治区", 30),
    (29, "青海省", 29), (30, "西藏自治区", 26),
    (31, "新疆维吾尔族自治区", 31), (32, "台湾省", 32),
    (33, "香港特别行政区", 33), (34, "澳门特别行政区", 34),
    (35, "海外", 35), (36, "其他", 36),
]

def _parse_float(v: str) -> float | None:
    if v is None or v.strip() == "":
        return None
    return float(v)

def _current(request: Request):
    """simple cookie-based user lookup"""
    return None  # TODO: real session


# ========== 搜索页 ==========
@app.get("/")
async def search_page(
    request: Request,
    q: str = Query(default=""),
    areaid: int = Query(default=0),
    catid: int = Query(default=0),
    vip: int = Query(default=0),
    price_min: str = Query(default=""),
    price_max: str = Query(default=""),
    sort: str = Query(default="default"),
    page: int = Query(default=1, ge=1),
):
    pm = _parse_float(price_min)
    px = _parse_float(price_max)
    params = SearchParams(q=q, areaid=areaid, catid=catid, vip=vip,
                          price_min=pm, price_max=px, sort=sort, page=page)
    result = await search_products(app.state.es, params, ES_INDEX)

    current_location, current_category = "", ""
    for idx, name, aid in AREAS:
        if aid == areaid and idx != 0:
            current_location = name; break
    for cid, cname in CATEGORIES:
        if cid == catid and cid != 0:
            current_category = cname; break

    return templates.TemplateResponse("index.html", {
        "request": request, "user": _current(request),
        "q": q, "areaid": areaid, "catid": catid, "vip": vip,
        "price_min": pm, "price_max": px, "sort": sort, "page": page,
        "categories": CATEGORIES, "areas": AREAS,
        "products": result["products"], "total": result["total"],
        "page_count": result["page_count"], "query_time_ms": result["query_time_ms"],
        "cat_counts": result.get("cat_counts", {}),
        "area_counts": result.get("area_counts", {}),
        "current_location": current_location, "current_category": current_category,
    })


# ========== JSON API ==========
@app.get("/api/search")
async def search_api(
    q: str = Query(default=""),
    areaid: int = Query(default=0),
    catid: int = Query(default=0),
    vip: int = Query(default=0),
    price_min: str = Query(default=""),
    price_max: str = Query(default=""),
    sort: str = Query(default="default"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
):
    pm = _parse_float(price_min); px = _parse_float(price_max)
    params = SearchParams(q=q, areaid=areaid, catid=catid, vip=vip,
                          price_min=pm, price_max=px, sort=sort, page=page, size=size)
    result = await search_products(app.state.es, params, ES_INDEX)
    return SearchResponse(
        products=[{
            "itemid": p["itemid"], "title": p["title"], "price": p["price"],
            "picture": p["picture"], "catid": p["catid"], "catname": p["catname"],
            "companyid": p["companyid"], "company": p["company"],
            "areaid": p["areaid"], "areaname": p["areaname"],
            "parentid": p["parentid"], "vip": p["vip"],
        } for p in result["products"]],
        total=result["total"], page=page,
        page_count=result["page_count"], query_time_ms=result["query_time_ms"],
    )


# ========== Auth Pages ==========
@app.get("/login")
async def login_page(request: Request, error: str | None = None):
    return templates.TemplateResponse("login.html", {
        "request": request, "user": _current(request), "error": error
    })

@app.post("/auth/login")
async def login_action(request: Request, username: str = Form(...), password: str = Form(...)):
    # TODO: real auth — for now redirect to search
    return RedirectResponse("/?q=", status_code=303)

@app.post("/auth/logout")
async def logout_action():
    return RedirectResponse("/", status_code=303)

@app.get("/register")
async def register_page(request: Request, error: str | None = None, success: str | None = None):
    return templates.TemplateResponse("register.html", {
        "request": request, "user": _current(request), "error": error, "success": success
    })

@app.post("/auth/register")
async def register_action(
    request: Request,
    username: str = Form(...), password: str = Form(...),
    email: str = Form(...), gender: str = Form(""),
):
    # TODO: real register — for now redirect to login
    return RedirectResponse("/login?success=注册成功", status_code=303)


# ========== Company Page ==========
@app.get("/company/{companyid}")
async def company_page(request: Request, companyid: int, page: int = Query(default=1, ge=1)):
    params = SearchParams(q="", page=page)
    # Search with companyid filter
    body = {
        "query": {"bool": {"filter": [{"term": {"companyid": companyid}}]}},
        "from": (page - 1) * params.size,
        "size": params.size,
        "track_total_hits": True,
    }
    resp = await app.state.es.search(index=ES_INDEX, body=body)
    total = resp["hits"]["total"]["value"]
    hits = resp["hits"]["hits"]

    products = []
    company_info = {"companyid": companyid, "company": "", "areaname": "", "business": "", "vip": 0}
    for hit in hits:
        src = hit["_source"]
        products.append({
            "itemid": src.get("itemid"), "title": src.get("title", ""),
            "price": src.get("price", 0), "picture": src.get("picture", ""),
            "catid": src.get("catid", 0), "catname": src.get("catname", ""),
            "companyid": src.get("companyid", 0), "company": src.get("company", ""),
            "areaid": src.get("areaid", 0), "areaname": src.get("areaname", ""),
            "vip": src.get("vip", 0),
        })
        if not company_info["company"]:
            company_info = {
                "companyid": src.get("companyid", companyid),
                "company": src.get("company", ""),
                "areaname": src.get("areaname", ""),
                "business": "",
                "vip": src.get("vip", 0),
            }

    page_count = max(1, (total + params.size - 1) // params.size)

    return templates.TemplateResponse("company.html", {
        "request": request, "user": _current(request),
        "company": company_info, "products": products,
        "total": total, "page": page, "page_count": page_count,
    })
