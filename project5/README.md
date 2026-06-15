# 工业商城搜索引擎

基于 **Elasticsearch + FastAPI + Jinja2** 的工业商品中文全文搜索引擎。

## 技术栈

| 层 | 技术 | 说明 |
|---|---|---|
| 搜索引擎 | Elasticsearch 8.17 | IK 中文分词（ik_max_word + ik_smart） |
| 后端 | FastAPI | 异步 ES 查询，Pydantic 数据验证 |
| 前端 | Jinja2 + Pico.css | 服务端渲染，classless CSS 框架 |
| 数据库 | MySQL 8.0 | 源数据存储 |
| 容器 | Docker Compose | 一键启动 MySQL + ES |

## 架构

```
init_data.sql → MySQL ← generate_data.py (模拟数据生成)
                    ↓
              etl_to_es.py (数据导入)
                    ↓
            Elasticsearch (IK 中文分词)
                    ↓
            FastAPI (search.py)
                    ↓
          Jinja2 HTML 页面
```

## 快速启动

### 1. 启动 Docker 服务

```bash
docker compose up -d
```

等待 ES 就绪（约30秒）：

```bash
curl http://localhost:9200
```

### 2. 生成模拟数据

```bash
pip install pymysql
python3 data/generate_data.py
```

### 3. 导入数据到 ES

```bash
pip install elasticsearch
python3 etl/etl_to_es.py
```

### 4. 启动搜索应用

```bash
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 打开浏览器

- 搜索页面：http://localhost:8000
- API 文档：http://localhost:8000/docs
- JSON API：http://localhost:8000/api/search?q=螺丝

## 功能

- **中文全文搜索**：IK 分词器，支持细粒度中文检索
- **类别过滤**：33 个工业商品类别标签
- **地区过滤**：36 个省/直辖市/地区
- **价格区间**：最低/最高价格过滤
- **VIP 筛选**：只看会员商品
- **排序**：相关度 / 价格升序 / 价格降序
- **分页**：支持翻页浏览
- **URL 书签**：所有筛选条件通过 URL 参数传递

## API

### `GET /` 搜索页面

```
/?q=螺丝&areaid=22&catid=12&vip=1&price_min=10&price_max=500&sort=asc&page=1
```

### `GET /api/search` JSON API

```json
{
  "products": [
    {
      "itemid": 1,
      "title": "高品质螺丝",
      "price": 123.45,
      "company": "龙智造机械制造有限公司",
      "areaname": "重庆市",
      "catname": "五金制品",
      "vip": 1
    }
  ],
  "total": 42,
  "page": 1,
  "page_count": 5,
  "query_time_ms": 15
}
```

## 文件结构

```
project5/
├── docker-compose.yml       # MySQL + ES
├── Dockerfile.es             # ES + IK 插件
├── requirements.txt
├── data/
│   ├── init_data.sql         # 建表 DDL
│   └── generate_data.py      # 模拟数据生成
├── etl/
│   └── etl_to_es.py          # MySQL → ES 导入
├── app/
│   ├── config.py             # 配置
│   ├── models.py             # Pydantic 模型
│   ├── search.py             # ES 查询构建
│   ├── main.py               # FastAPI 入口
│   ├── templates/
│   │   ├── base.html         # 页面骨架
│   │   └── index.html        # 搜索页面
│   └── static/
│       ├── style.css         # 自定义样式
│       └── app.js            # 前端交互
└── test_e2e.sh               # 端到端测试
```
