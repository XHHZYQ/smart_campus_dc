# 智慧校园数据中心管理软件

面向**小学、初中、高中**学校的校园数据管理后台：管住人（学生学籍 / 教职工档案）、管住事（课程 / 排课 / 成绩 / 考勤）、管住物（资产台账 / 宿舍），并用图表与数据大屏呈现结果。

- 前端：Vue 3 + TypeScript + Vite + Element Plus + Pinia + ECharts
- 后端：Python + FastAPI + SQLAlchemy 2.0 + Pydantic v2
- 数据库：PostgreSQL
- 认证：账号密码 + JWT

设计依据见 [设计概要](docs/设计概要.md)。

---

## 一、仓库结构

```
smart-campus-dc/
├── frontend/          # 前端工程（Vue 3 + TS + Vite）
│   └── src/
│       ├── api/       # 按模块封装的接口调用
│       ├── layout/    # 主框架（侧边菜单 + 顶栏）
│       ├── router/    # 路由、菜单配置、登录守卫
│       ├── stores/    # Pinia（登录用户、令牌、菜单）
│       ├── styles/    # 全局样式
│       ├── types/     # api.ts 接口类型（与后端 schemas.py 对齐）
│       ├── utils/     # axios 统一封装
│       └── views/     # 页面（按模块分目录）
├── backend/           # 后端工程（FastAPI）
│   └── app/
│       ├── routers/   # 按模块分的路由
│       ├── config.py  # 配置（数据库、JWT、跨域）
│       ├── database.py# 引擎、会话、建表
│       ├── models.py  # SQLAlchemy 表模型（17 张表）
│       ├── schemas.py # Pydantic 请求/响应模型（前后端契约事实源）
│       ├── security.py# 密码哈希、JWT 签发校验
│       ├── deps.py    # 公共依赖（当前用户、角色校验）
│       ├── init_data.py # 初始化演示数据
│       └── main.py    # 应用入口
└── docs/              # 设计概要、操作手册、截图
```

---

## 二、环境要求

| 项 | 要求 |
| --- | --- |
| 操作系统 | Windows（也可在 macOS / Linux 运行） |
| Node.js | 18 及以上 |
| Python | 3.11 ~ 3.13（推荐） |
| PostgreSQL | 12 及以上（本地安装或用 Docker 启动） |

---

## 三、启动步骤

### 1. 启动 PostgreSQL（使用 Docker）

在已安装 Docker 的终端（Windows 上通常为 WSL）执行：

```bash
docker run -d \
  --name postgresql-container \
  -e POSTGRES_USER=smart_campus_dc \
  -e POSTGRES_PASSWORD=smart_campus_dc \
  -e POSTGRES_DB=smart_campus_dc_db \
  -p 5433:5432 \
  postgres:16
```

> 容器名为 `postgresql-container`，会自动创建数据库 `smart_campus_dc_db` 和用户 `smart_campus_dc`，无需手动建库。
> 已存在的容器直接启动：`docker start postgresql-container`

### 2. 启动后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.init_data
uvicorn app.main:app --reload --port 8000
```

启动后可访问：

- 接口文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/v1/health

### 3. 启动前端

另开一个终端：

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 http://localhost:5173 ，前端已配置 `/api` 代理到后端 8000 端口。

---

## 四、演示账号

密码统一为 `admin123`。

| 账号 | 姓名 | 角色 |
| --- | --- | --- |
| admin | 张建国 | 系统管理员（全部模块） |
| jiaowu | 李文娟 | 教务管理员 |
| banzhuren | 王海燕 | 班主任 |
| laoshi | 陈志强 | 任课教师 |
| zongwu | 刘明辉 | 总务管理员 |

---

## 五、说明

- 数据库表由后端启动时自动创建（`init_db`），无需手工执行建表 SQL。
- `python -m app.init_data` 可重复执行，已存在的数据会自动跳过。
- 后续批次将陆续补充：系统管理、基础数据管理、教学管理、校务管理、数据看板与演示数据。
