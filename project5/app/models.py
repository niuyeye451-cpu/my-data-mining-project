"""
Pydantic 数据模型：搜索参数 + 响应结构
"""
from pydantic import BaseModel, Field


class SearchParams(BaseModel):
    """搜索请求参数"""
    q: str = Field(default="", description="搜索关键词")
    areaid: int = Field(default=0, description="地区ID（省级 parentid），0=全部")
    catid: int = Field(default=0, description="类别ID，0=全部")
    vip: int = Field(default=0, description="只看会员：0=否，1=是")
    price_min: float | None = Field(default=None, description="最低价格")
    price_max: float | None = Field(default=None, description="最高价格")
    sort: str = Field(default="default", description="排序：default / asc / desc")
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    size: int = Field(default=10, ge=1, le=50, description="每页条数")


class ProductItem(BaseModel):
    """单条商品"""
    itemid: int
    title: str
    price: float
    picture: str
    catid: int
    catname: str
    companyid: int
    company: str
    areaid: int
    areaname: str
    parentid: int
    vip: int


class SearchResponse(BaseModel):
    """搜索响应"""
    products: list[ProductItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_count: int = 0
    query_time_ms: int = 0
