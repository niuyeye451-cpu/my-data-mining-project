#!/bin/bash
# =============================================
# 端到端测试脚本
# 使用：bash test_e2e.sh
# =============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "===== 1. 启动 Docker 服务 ====="
docker compose up -d

echo ""
echo "===== 2. 等待服务就绪 ====="
echo "等待 MySQL 就绪..."
for i in $(seq 1 30); do
    if docker compose exec -T mysql mysqladmin ping -h localhost --silent 2>/dev/null; then
        echo "✅ MySQL 就绪"
        break
    fi
    sleep 2
done

echo "等待 Elasticsearch 就绪..."
for i in $(seq 1 40); do
    if curl -sf http://localhost:9200/_cluster/health > /dev/null 2>&1; then
        echo "✅ Elasticsearch 就绪"
        break
    fi
    sleep 3
done

echo ""
echo "===== 3. 检查 MySQL 建表 ====="
TABLE_COUNT=$(docker compose exec -T mysql mysql -u root gyy -e "SHOW TABLES;" 2>/dev/null | wc -l)
echo "  gyy 数据库表数量: $TABLE_COUNT"

echo ""
echo "===== 4. 生成模拟数据 ====="
pip install -q pymysql
python3 data/generate_data.py

echo ""
echo "===== 5. 验证 MySQL 数据 ====="
MALL_COUNT=$(docker compose exec -T mysql mysql -u root gyy -e "SELECT COUNT(*) FROM gyy_mall;" -N 2>/dev/null)
echo "  gyy_mall 记录数: $MALL_COUNT"
if [ "$MALL_COUNT" != "500" ]; then
    echo "  ⚠️  期望 500 条，实际 $MALL_COUNT 条"
    exit 1
fi
echo "  ✅ 数据生成正确"

echo ""
echo "===== 6. 数据导入 ES ====="
pip install -q elasticsearch
python3 etl/etl_to_es.py

echo ""
echo "===== 7. 验证 ES 数据 ====="
ES_COUNT=$(curl -s http://localhost:9200/gyy_mall/_count | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])")
echo "  ES 文档数: $ES_COUNT"
if [ "$ES_COUNT" != "500" ]; then
    echo "  ⚠️  期望 500 条，实际 $ES_COUNT 条"
    exit 1
fi
echo "  ✅ ES 索引正确"

echo ""
echo "===== 8. 测试中文搜索 ====="
RESULT=$(curl -s "http://localhost:9200/gyy_mall/_search" -H "Content-Type: application/json" -d '{"query":{"match":{"title":"螺丝"}},"size":0}' | python3 -c "import sys,json; print(json.load(sys.stdin)['hits']['total']['value'])")
echo "  搜索'螺丝'命中: $RESULT 条"
if [ "$RESULT" -eq 0 ]; then
    echo "  ⚠️  中文搜索无结果，请检查 IK 分词器"
    exit 1
fi
echo "  ✅ 中文搜索正常"

echo ""
echo "===== 9. 启动 FastAPI ====="
pip install -q fastapi uvicorn jinja2 python-multipart aiofiles
# 后台启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
sleep 3
echo "  FastAPI PID: $API_PID"

echo ""
echo "===== 10. 测试搜索 API ====="
API_RESULT=$(curl -s "http://localhost:8000/api/search?q=螺丝&size=5")
API_TOTAL=$(echo "$API_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['total'])")
API_ITEMS=$(echo "$API_RESULT" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['products']))")
echo "  API 搜索结果: total=$API_TOTAL, items=$API_ITEMS"
if [ "$API_TOTAL" -eq 0 ]; then
    echo "  ⚠️  API 搜索无结果"
    kill $API_PID 2>/dev/null
    exit 1
fi
echo "  ✅ API 搜索正常"

echo ""
echo "===== 11. 测试 HTML 页面 ====="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/?q=螺丝")
echo "  页面 HTTP 状态码: $HTTP_CODE"
if [ "$HTTP_CODE" != "200" ]; then
    echo "  ⚠️  页面返回异常"
    kill $API_PID 2>/dev/null
    exit 1
fi
echo "  ✅ HTML 页面正常"

# 清理
kill $API_PID 2>/dev/null

echo ""
echo "========================================="
echo "  🎉 所有测试通过！"
echo "========================================="
echo ""
echo "  启动方式："
echo "    docker compose up -d"
echo "    python3 data/generate_data.py"
echo "    python3 etl/etl_to_es.py"
echo "    python3 -m uvicorn app.main:app --reload"
echo "    浏览器打开 http://localhost:8000"
echo ""
