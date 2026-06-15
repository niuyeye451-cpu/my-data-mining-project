# Stitch 前端生成提示词

> 项目背景：工业商城搜索引擎，后端 FastAPI + Elasticsearch + Jinja2 模板引擎，前端 Pico.css + 少量自定义 CSS，服务端渲染（SSR），所有交互通过 GET 表单或 POST 请求实现，无需前端路由。

---

## Prompt 1：更新 base.html ——添加顶部导航栏

```
请你生成一个 Jinja2 模板文件 base.html。

这是整个搜索应用的页面骨架，所有其他页面通过 {% extends "base.html" %} 继承它。

═══════════════════════════════════════
技术约束
═══════════════════════════════════════
- 模板引擎：Jinja2（Python），使用 {% block content %}{% endblock %} 作为子页面插槽
- CSS 框架：Pico.css v2.0.6，从 CDN 加载：https://cdn.jsdelivr.net/npm/@picocss/pico@2.0.6/css/pico.min.css
- 自定义 CSS：<link rel="stylesheet" href="/static/style.css">
- JS：<script src="/static/app.js"></script>（放在 </body> 前）
- 语言：简体中文，<html lang="zh-CN" data-theme="light">
- 视口：<meta name="viewport" content="width=device-width, initial-scale=1">
- 编码：UTF-8

═══════════════════════════════════════
模板变量（由后端传入）
═══════════════════════════════════════
- user: dict | None  — 当前登录用户，{username: "xxx"}；None 表示未登录

═══════════════════════════════════════
设计要求
═══════════════════════════════════════
1. 顶部导航栏（<nav> 或 <header>），Pico.css 风格，水平布局：
   - 左侧：Logo + 标题 "🏭 工业商城"（点击跳转 /）
   - 右侧：
     - 如果 user 非空：显示 "👤 {user.username}" + "登出" 按钮（POST /auth/logout）
     - 如果 user 为空：显示 "登录" 链接（跳转 /login）

2. 导航栏下方是 <main class="container"> 包裹的 {% block content %}{% endblock %}

3. 最底部是 <footer>：小字居中 "Data Mining Project 5 · Elasticsearch + FastAPI + Jinja2"

4. 导航栏样式建议：
   - 白色背景，底部有细分割线
   - 左侧标题加粗
   - 右侧按钮/链接使用 Pico 的 outline 风格
   - 登出按钮用一个小表单（POST 方法，因为登出是状态变更操作）

═══════════════════════════════════════
参考：旧版 base.html（需要在此基础上改造）
═══════════════════════════════════════
旧版没有导航栏，只有居中标题 header，现在要保留标题区域但加上导航功能。
旧版代码：
---
<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>工业商城搜索引擎</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2.0.6/css/pico.min.css">
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <header class="container">
        <h1 style="text-align:center;">🏭 工业商城搜索引擎</h1>
        <p style="text-align:center; color:var(--pico-muted-color);">
            Elasticsearch + IK 中文分词 · 全文检索 · 多条件过滤
        </p>
    </header>
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    <footer class="container" style="text-align:center; margin-top:3rem;">
        <small>Data Mining Project 5 · Elasticsearch + FastAPI + Jinja2</small>
    </footer>
    <script src="/static/app.js"></script>
</body>
</html>
---

请在旧版基础上增加顶部导航栏（含登录态显示），保持其他部分不变。只输出完整的 base.html 代码，不要额外说明。
```

---

## Prompt 2：新增 login.html ——登录页

```
请你生成一个 Jinja2 模板文件 login.html。

这是工业商城搜索引擎的登录页面，继承自 base.html。

═══════════════════════════════════════
技术约束
═══════════════════════════════════════
- 继承 {% extends "base.html" %}
- 内容放在 {% block content %}{% endblock %} 中
- CSS 框架：Pico.css v2.0.6
- 模板变量：
  - error: str | None  — 登录失败时的错误消息，如 "账号或密码错误"
  - user: dict | None  — 当前登录用户（如果已登录则自动跳转搜索页）

═══════════════════════════════════════
设计要求
═══════════════════════════════════════
1. 页面居中，卡片式布局，宽度约 420px，上下留白足够（margin-top: 8vh 左右）

2. 卡片内容：
   - 标题："🔐 用户登录"（居中，h2）
   - 表单 <form method="post" action="/auth/login">：
     - 用户名输入框 <input name="username" type="text" required placeholder="请输入用户名">
     - 密码输入框 <input name="password" type="password" required placeholder="请输入密码">
     - 登录按钮 <button type="submit"> 登 录
   - 下方链接："还没有账号？立即注册" 跳转 /register

3. 错误提示：如果 error 不为空，在表单上方显示红色提示条（Pico 不支持原生的 alert，用带样式的 div）

4. 视觉风格：
   - 卡片用 Pico 的 <article> 标签包裹
   - 表单元素用 Pico 默认样式（自带圆角和间距）
   - 整体色调偏工业蓝（var(--pico-primary-background)）

5. 交互细节：
   - 输入框带 label，label 和 input 上下排列
   - 登录按钮占满宽度（display:block; width:100%）

只输出完整的 login.html 代码，不要额外说明。
```

---

## Prompt 3：新增 register.html ——注册页

```
请你生成一个 Jinja2 模板文件 register.html。

这是工业商城搜索引擎的用户注册页面，继承自 base.html。

═══════════════════════════════════════
技术约束
═══════════════════════════════════════
- 继承 {% extends "base.html" %}
- 内容放在 {% block content %}{% endblock %} 中
- CSS 框架：Pico.css v2.0.6
- 模板变量：
  - error: str | None  — 注册失败时的错误消息
  - success: str | None  — 注册成功时的提示消息

═══════════════════════════════════════
设计要求
═══════════════════════════════════════
1. 页面居中，卡片式布局，宽度约 440px

2. 卡片内容：
   - 标题："📝 用户注册"（居中，h2）
   - 表单 <form method="post" action="/auth/register">：
     - 用户名 <input name="username" type="text" required placeholder="请输入用户名">
     - 密码 <input name="password" type="password" required placeholder="请输入密码（至少6位）">
     - 确认密码 <input name="confirm_password" type="password" required placeholder="请再次输入密码">
     - 邮箱 <input name="email" type="email" required placeholder="请输入邮箱地址">
     - 性别：两个 radio button 或 select（男/女）
       <select name="gender">
         <option value="">请选择</option>
         <option value="男">男</option>
         <option value="女">女</option>
       </select>
     - 注册按钮 <button type="submit"> 注 册

3. 成功/错误提示：
   - 如果 success 不为空，显示绿色提示条，内容为 {{ success }}，并显示 "去登录" 链接
   - 如果 error 不为空，在表单上方显示红色提示条

4. 表单下方链接："已有账号？去登录" 跳转 /login

5. 前端 JS 校验（内嵌或放在 app.js）：
   - 密码长度 >= 6
   - 两次密码一致
   - 用户名、邮箱非空

只输出完整的 register.html 代码，不要额外说明。
```

---

## Prompt 4：新增 company.html ——公司详情页

```
请你生成一个 Jinja2 模板文件 company.html。

这是工业商城搜索引擎的公司详情页，显示某家公司的基本信息和该公司发布的所有商品。

═══════════════════════════════════════
技术约束
═══════════════════════════════════════
- 继承 {% extends "base.html" %}
- 内容放在 {% block content %}{% endblock %} 中
- CSS 框架：Pico.css v2.0.6
- 复用现有的商品卡片样式（results-grid, product-card, card-body, card-img, card-info, product-title, price 等 class），这些 CSS 已经在 /static/style.css 中定义好

═══════════════════════════════════════
模板变量（后端传入）
═══════════════════════════════════════
- company: dict = {
    "companyid": 123,
    "company": "龙智造机械制造有限公司",
    "business": "五金制品、机械制造",
    "areaname": "重庆市",
    "vip": 1
  }
- products: list[dict]  每个元素：
  {
    "itemid": 1,
    "title": "高品质螺丝",
    "price": 123.45,
    "picture": "https://...jpg" 或 "",
    "catname": "五金制品",
    "company": "龙智造机械制造有限公司",
    "areaname": "重庆市",
    "vip": 1
  }
- total: int  — 商品总数
- page: int  — 当前页码
- page_count: int  — 总页数

═══════════════════════════════════════
设计要求
═══════════════════════════════════════
1. 公司信息卡片（顶部，用 <article> 包裹）：
   - 公司名称（h2，若 vip==1 则旁边显示金色 VIP 徽章）
   - 所在地：📍 {{ company.areaname }}
   - 主营业务：{{ company.business }}
   - 商品数：共 {{ total }} 件

2. 商品列表区域：
   - 标题："📦 该公司商品（共 X 件）"
   - 复用 index.html 中的商品卡片网格（results-grid + product-card + card-body），完全相同的结构：
     - 左侧图片（有图片显示 img，无图片显示 📦 占位）
     - 右侧：标题 + 价格 + 类别名
   - 若商品数为 0，显示 "该公司暂无商品"

3. 分页导航（复用 index.html 中相同的分页逻辑）：
   - URL 格式：/company/{{ company.companyid }}?page={{ pn }}
   - 上一页 / 页码（当前页高亮）/ 下一页
   - 显示最多当前页±2 的页码，首尾加 "…"

4. 面包屑导航：
   - 顶部放一个返回链接：← 返回搜索

只输出完整的 company.html 代码，不要额外说明。
```

---

## Prompt 5：更新 index.html ——关键词高亮 + 标签计数 + 公司名可点击

```
请你修改 Jinja2 模板 index.html，在现有搜索页面基础上增加三个功能：
关键词高亮、标签商品计数、公司名可点击跳转。

═══════════════════════════════════════
现有上下文
═══════════════════════════════════════
- 模板引擎：Jinja2（Python）
- CSS 框架：Pico.css v2.0.6 + /static/style.css
- 该模板被 / 路由渲染，支持 GET 参数：q, areaid, catid, vip, price_min, price_max, sort, page
- 现有功能：搜索框、类别/地区标签筛选（可展开收起）、排序下拉、VIP开关、价格区间、商品卡片网格、分页

═══════════════════════════════════════
新增模板变量（后端传入，以下是新增的）
═══════════════════════════════════════
- highlighted: bool  — 是否有搜索关键词（q 不为空时 = true）
- 每个商品 p 新增字段：
  - p.highlight: str | None  — ES 返回的高亮 HTML，如 "高品质<mark>螺丝</mark>"；无高亮时为 None

- cat_counts: dict[int, int]  — 类别商品计数，如 {1: 15, 2: 23, 12: 8, ...}，key 是 catid，value 是商品数
- area_counts: dict[int, int]  — 地区商品计数，如 {22: 10, 19: 42, ...}，key 是 parentid，value 是商品数

═══════════════════════════════════════
要做的三项改动
═══════════════════════════════════════

【改动1】关键词高亮
商品标题渲染逻辑改为：
  {% if highlighted and p.highlight %}
    <h4 class="product-title">{{ p.highlight | safe }}</h4>
  {% else %}
    <h4 class="product-title" title="{{ p.title }}">{{ p.title }}</h4>
  {% endif %}
对应的 CSS（在 style.css 中补充）：
  mark { background: #FFF176; padding: 1px 3px; border-radius: 2px; color: #333; }

【改动2】标签商品计数
类别标签渲染改为：
  {% for cid, cname in categories %}
    <a ... class="tag {% if catid == cid %}tag-active{% endif %}">
      {{ cname }}
      {% if cat_counts and cat_counts.get(cid, 0) > 0 %}
        <small>({{ cat_counts.get(cid, 0) }})</small>
      {% endif %}
    </a>
  {% endfor %}

地区标签类似：
  {% for idx, aname, aid in areas %}
    <a ... class="tag {% if areaid == aid and aid != 0 %}tag-active{% endif %}">
      {{ aname }}
      {% if area_counts and area_counts.get(aid, 0) > 0 %}
        <small>({{ area_counts.get(aid, 0) }})</small>
      {% endif %}
    </a>
  {% endfor %}

【改动3】公司名可点击
商品卡片中 "公司名：{{ p.company }}" 改为链接：
  <a href="/company/{{ p.companyid }}" class="company-link">{{ p.company }}</a>

═══════════════════════════════════════
请你基于以上三项改动，输出完整更新后的 index.html 代码（保留现有的所有其他功能）。
不要写解释，只输出完整的 index.html。
```

---

## Prompt 6：更新 style.css ——补充新功能样式

```
请在现有 style.css 文件基础上，追加以下新样式规则。保留全部现有 CSS 不变，只追加新内容。

═══════════════════════════════════════
要追加的样式
═══════════════════════════════════════

1. 导航栏样式（配合 base.html 的新导航栏）：
```css
/* ====== 导航栏 ====== */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 1rem;
    background: #fff;
    border-bottom: 2px solid var(--pico-primary-background);
    margin-bottom: 1.5rem;
}
.navbar-brand {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-decoration: none;
    font-size: 1.25rem;
    font-weight: bold;
    color: var(--pico-color);
}
.navbar-brand:hover { text-decoration: none; color: var(--pico-primary-background); }
.navbar-user {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 0.9rem;
}
.navbar-user .username { color: var(--pico-muted-color); }
.logout-btn {
    background: none;
    border: 1px solid var(--pico-muted-border-color);
    border-radius: var(--pico-border-radius);
    padding: 0.25rem 0.75rem;
    cursor: pointer;
    font-size: 0.85rem;
    color: var(--pico-muted-color);
}
.logout-btn:hover { background: var(--pico-primary-hover-background); color: #fff; }
```

2. 关键词高亮样式：
```css
/* ====== 关键词高亮 ====== */
mark {
    background: #FFF176;
    padding: 1px 3px;
    border-radius: 2px;
    color: #333;
}
```

3. 公司名链接样式：
```css
/* ====== 公司名链接 ====== */
.company-link {
    color: var(--pico-primary-background);
    text-decoration: none;
    font-size: 0.85rem;
}
.company-link:hover {
    text-decoration: underline;
}
```

4. 登录/注册页面卡片样式：
```css
/* ====== 认证页面 ====== */
.auth-card {
    max-width: 420px;
    margin: 6vh auto;
    padding: 2rem;
}
.auth-card h2 {
    text-align: center;
    margin-bottom: 1.5rem;
}
.auth-card form label {
    margin-top: 0.75rem;
}
.auth-card form button {
    width: 100%;
    margin-top: 1rem;
}
.auth-links {
    text-align: center;
    margin-top: 1rem;
    font-size: 0.9rem;
}
.auth-error {
    background: #FFF0F0;
    color: #C62828;
    padding: 0.5rem 1rem;
    border-radius: var(--pico-border-radius);
    margin-bottom: 1rem;
    font-size: 0.9rem;
    border: 1px solid #FFCDD2;
}
.auth-success {
    background: #F0FFF0;
    color: #2E7D32;
    padding: 0.5rem 1rem;
    border-radius: var(--pico-border-radius);
    margin-bottom: 1rem;
    font-size: 0.9rem;
    border: 1px solid #C8E6C9;
}
```

5. 公司详情页样式：
```css
/* ====== 公司详情页 ====== */
.company-hero {
    margin-bottom: 1.5rem;
}
.company-hero h2 {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.company-info {
    display: flex;
    gap: 2rem;
    color: var(--pico-muted-color);
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}
```

只输出要追加到 style.css 末尾的所有新 CSS 规则，不要删除任何现有规则，不要写解释。
```

---

## 后端对应改动速查

这些提示词生成前端模板后，后端 `app/main.py` 需要新增以下路由来支撑：

```python
# 1. 登录页
@app.get("/login")
async def login_page(request: Request, error: str | None = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error, "user": get_current_user(request)})

@app.post("/auth/login")
async def login_action(request: Request, ...):  # 读取表单，验证，设置 session
    ...

@app.post("/auth/logout")
async def logout_action(request: Request):  # 清除 session
    ...

# 2. 注册页
@app.get("/register")
async def register_page(request: Request, ...):
    ...

@app.post("/auth/register")
async def register_action(request: Request, ...):  # 读取表单，写入 MySQL
    ...

# 3. 公司详情页
@app.get("/company/{companyid}")
async def company_page(request: Request, companyid: int, page: int = 1):
    # ES filter by companyid，返回 company 信息 + products 列表
    ...

# 4. 搜索页路由需要新增模板变量：
# - highlighted: True if q else False
# - cat_counts / area_counts 来自 ES aggs
# - 每个 product 带 highlight 字段
```

---

## Stitch 使用顺序

按依赖关系依次提交：

1. **Prompt 6**（style.css）— 纯 CSS，无依赖，先追加样式
2. **Prompt 2**（login.html）— 新页面，依赖 base.html 和 style.css
3. **Prompt 3**（register.html）— 新页面，同上
4. **Prompt 4**（company.html）— 新页面，复用商品卡片样式
5. **Prompt 5**（index.html）— 改造现有搜索页，依赖后端新传的 variable
6. **Prompt 1**（base.html）— 最后改造骨架（因为 login/register 都 extends 它，base 改完它们才能验证）

每个 Prompt 生成的文件名：
- `app/templates/base.html`
- `app/templates/login.html`
- `app/templates/register.html`
- `app/templates/company.html`
- `app/templates/index.html`
- `app/static/style.css`
