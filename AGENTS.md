# AGENTS.md —— 项目编码契约（Codex 等写代码的 Agent **先读、再写**）

> 这是「刺桐智游」（泉州世遗文化 AI 伴游助手）的编码约束文件。**任何在动笔写代码前，先完整读一遍本文件。**
> 你的职责：**只实现当天被指派的模块**（见 `.plan/schedule.md` 的 DNN）。
> 规划、架构取舍、教学与最终评审由 **Claude Code（老师）** 负责——不要越权替它做决定。

## 0. 开工前阅读顺序

1. `AGENTS.md`（本文件，编码红线）
2. `CLAUDE.md`（架构蓝图 / 设计原则 / 分层约束）
3. `.plan/schedule.md`（今天做到哪个模块）
4. `docs/architecture.md`（架构与数据库细节）
5. `README.md`（项目总览）

## 1. 工作模式

- **每天只做一个模块**。不要顺手把“下一个/以后的功能”也做掉，不要顺手重构无关代码。
- 模块交付标准：**可运行 + 可验证 + 主要逻辑有中文注释 + 不破坏 main 的可运行性**。
- 交付时在提交说明里附一段给老师的 **「改动清单 + 关键设计决定 + 希望重点 review 的点」**（供评审与讲解）。

## 2. 编码规范

### 2.1 注释规范（重点，务必遵守）
- **不为每一行写注释。**
- 只为三类写**中文注释**：① 主要/核心逻辑；② 非显而易见的“为什么这样写”；③ 易错边界。
- **“为什么这样做”优先于“做了什么”**；同一句代码如无价值就不写。
- 文件/模块/类/公共函数写简短 docstring（一句话职责，必要时说明参数与返回）。

### 2.2 后端（Python 3.13 · FastAPI · SQLAlchemy 2.0 同步 · PyMySQL · Pydantic v2）
- **分层铁律**：`routers` 只做参数接收/校验/响应组装；业务逻辑在 `services`；数据访问收敛在 repository/ORM 查询封装。
  **禁止在 router 里写 SQL 或业务逻辑**（controller 要瘦）。
- 类型注解齐全（参数与返回都要）；用 `list[...]`/`Optional[...]` 内置泛型，不写无类型标注的公共函数。
- 命名：类 `PascalCase`、函数/变量 `snake_case`、常量 `UPPER_CASE`；缩写克制、可读优先。
- import 分组：标准库 → 三方 → 项目内部；禁止 `*` 导入。
- 用模块级 `logging`，**禁止残留 `print` 调试**。
- 一切可配置项（密钥/URL/模型名/DB 地址…）都从 `app/core/config.py`（pydantic-settings 读 `.env`）读取；**禁止硬编码密钥或地址**。
- Pydantic schema 用 v2 风格；命名：请求 `XxxIn`、响应 `XxxOut`。
- 错误处理：用 `HTTPException` + 可读 message；不裸抛堆栈给前端；敏感错误不落日志明文。
- SQLAlchemy 模型：字符串类型带长度，外键/唯一约束在模型层声明；不隐藏隐式 commit。

### 2.3 语料 / 数据（M2 起）
- 世遗内容**必须保真**：来源写入 frontmatter 的 `source`；**禁止编造史实/数据**；拿不准写「待校对」而不是硬编。
- 结构化站点主数据与长文语料分离存放（见 CLAUDE.md 设计原则 3）。

### 2.4 前端（M4 起）
- React 18 函数组件 + Hooks；TypeScript strict。
- 组件只做 UI/展示；请求统一走 `src/api/` client；状态用约定好的全局 store；**禁止在组件里拼业务 HTTP 逻辑**。

## 3. 目录结构（必须遵循）

```
├─ .plan/          # 课表 schedule.md · 每日笔记 daily/
├─ docs/           # architecture.md · API.md · 简历亮点.md
├─ data/           # 语料 raw_md(带 frontmatter) + ingest/质检脚本
├─ backend/
│  ├─ app/
│  │  ├─ main.py            # app 工厂 + 路由注册 + 中间件
│  │  ├─ core/              # config · security · deps · llm_provider
│  │  ├─ db/                # engine · session · base · alembic
│  │  ├─ models/            # SQLAlchemy 模型
│  │  ├─ schemas/           # Pydantic v2
│  │  ├─ routers/           # auth · sites · chat · itinerary · favorites
│  │  ├─ services/          # 业务逻辑
│  │  ├─ rag/               # splitter · embed · vector_search · qa_chain
│  │  ├─ agent/             # langgraph: state · graph · nodes · tools
│  │  └─ utils/
│  ├─ tests/                # pytest（镜像 app 目录）
│  └─ pyproject.toml
├─ frontend/       # Vite + React + TS（src/api · pages · components · store · router）
├─ docker-compose.yml
├─ .env.example    # 可提交的配置样例
└─ .env            # 真实密钥，禁止提交
```

## 4. 构建 / 测试命令（规范入口，随脚手架更新）

```powershell
# 后端（uv 管理；uv.lock 需提交，锁版本供可复现）
cd backend
uv sync --extra dev                     # 首次/依赖变动：装 pyproject 全部依赖，生成/更新 uv.lock
uv run uvicorn app.main:app --reload    # 开发服务器 http://127.0.0.1:8000
uv run pytest                           # 测试
uv run ruff check .                     # 静态检查
# 旧等价（pip/venv，二选一）：python -m venv .venv && .\.venv\Scripts\Activate.ps1 → pip install -e ".[dev]"

# 前端
cd frontend
npm install
npm run dev                      # Vite dev（proxy 到后端）
npm run build                    # 产物到 frontend/dist
npm run typecheck                # tsc --noEmit
npm run lint

# Docker（全套本地环境）
docker compose up -d             # mysql · postgres(pgvector) · backend · frontend
docker compose down
```

> 某命令尚未就绪说明该模块未到；不要为“看起来缺文件”私自造命令入口之外的结构。

## 5. 禁止事项（红线，违者返工）

- ❌ 提交 `.env`、密钥、token、敏感日志；`.env` 永不入库，配置只进 `.env.example`。
- ❌ 一次实现多个模块 / “顺手优化”无关代码 / 大范围重构现有可运行代码。
- ❌ 引入当天任务之外的依赖；确需新增，先说明理由（会评审，安装前后都要报备）。
- ❌ 每行/每 token 写注释、用 `print` 调试、拼音变量名、裸 `except`。
- ❌ 在 `routers` 里写 SQL / 业务逻辑，或绕过既有分层直接调底层。
- ❌ 未经老师确认改动：DB 表结构、API 契约、语料事实口径、已交付模块的行为。
- ❌ 编造/臆测不存在的函数、环境变量、第三方接口参数或返回；不确定就查文档或问，不许“猜一个能编译的”。
- ❌ 谎报验证结果：测试或运行失败要如实说明，不得声称通过。
- ❌ 一个提交里夹带多个模块内容；不直接改写已共享的历史 commit。

## 6. Git / 提交

- 提交规范：`类型: 模块DNN-简述`，类型取 `feat | mod | fix | docs | test`。
- 每完成一个模块即做一次原子提交，不积压多天。
- 保持 `main` 可运行：若在分支上开发，验证通过后再合回；直接在 main 上提交前必须先本地跑通。
- 每里程碑由老师打 tag（`m1-auth`、`m2-knowledge` …）。
