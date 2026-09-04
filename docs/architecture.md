# 刺桐智游 · 架构设计（v1）

> 一句话定位：泉州世遗场景的 AI 伴游助手 —— RAG 文化问答 + LangGraph 个性化行程规划 + AI 叙事讲解。
> 本文是项目的地基文档，随模块演进持续更新（draft v0.1 @ 2026-09-04 / D01）。

## 1. 系统架构

```
React(Vite+TS+AntD) ──HTTP/JSON·SSE──▶ FastAPI(REST + 流式) ──▶ 服务层
  pages: 登录/注册·首页·世遗点·问答·行程·讲解·个人中心          │
                                           ┌────────────────────┴─────────────┐
                                           ▼                                ▼
                                  MySQL(SQLAlchemy 2.0)          PostgreSQL + pgvector
                                users/sessions/messages/          documents + vector(1024)
                                itineraries/heritage_sites      (22 遗产点+主题语料分块, HNSW)
                                           │
                            LangChain(RAG)：切分/Embedding/Retriever/LCEL chain
                            LangGraph(Agent)：StateGraph 行程编排/讲解/问答路由
                            模型抽象层：DeepSeek v4-flash(对话) · SiliconFlow bge-m3(向量)
```

## 2. 关键设计决策（含理由）

1. **前后端分离**：React 只消费 API，FastAPI 不渲染页面 → 可独立部署、便于 Docker/nginx 组合、贴近企业形态。
2. **两类数据职责分离**：
   - MySQL `heritage_sites` 存**结构化主数据**（名称/坐标/开馆/分类/标签）→ 支撑列表、筛选、行程工具。
   - PG `documents`(含 vector) 存**非结构化长文分块** → 支撑语义检索。数据库各司其职是教学点。
3. **先手写，再框架**：RAG 检索先手写 pgvector 余弦 SQL 一遍，再引入 LangChain PGVector store——先懂原理，再学封装。
4. **OpenAI 兼容协议统一抽象**：DeepSeek 与硅基流动都兼容 OpenAI 协议；`core/llm_provider` 集中管理，可随时换模型/Embedding。面试高频考点。
5. **同步 ORM 起步 + repository 分层**：SQLAlchemy 2.0 同步 + PyMySQL（Windows 免编译、易调试）；业务逻辑经 repository/service 封装，日后可平滑升级 async。取舍点会专题讲解。
6. **流式优先**：AI 长回复一律走 SSE 逐 token 推送，前端流式渲染，交互接近真实产品。
7. **Alembic 管 schema 演进**：上线必需，避免"手改表结构"。

## 3. 目录结构（Monorepo）

```
├─ .plan/            # 课表 + 每日教学笔记
├─ docs/             # 本文档 / API.md / 简历亮点.md
├─ data/             # 语料 raw_md(frontmatter) + ingest/质检脚本
├─ backend/
│  ├─ app/
│  │  ├─ main.py            # app 工厂 + 路由 + 中间件
│  │  ├─ core/              # config / security / deps / llm_provider
│  │  ├─ db/                # engine / session / base / alembic
│  │  ├─ models/            # SQLAlchemy 模型（业务表）
│  │  ├─ schemas/           # Pydantic v2 请求/响应
│  │  ├─ routers/           # auth · sites · chat · itinerary · favorites
│  │  ├─ services/          # 业务逻辑
│  │  ├─ rag/               # splitter / embed / vector_search / qa_chain
│  │  ├─ agent/             # langgraph: state · graph · nodes · tools
│  │  └─ utils/
│  ├─ tests/
│  └─ pyproject.toml
├─ frontend/         # Vite + React + TS
├─ docker-compose.yml
└─ .env.example
```

## 4. 数据库设计（draft）

### 4.1 MySQL（业务数据，utf8mb4）
- `users`: id · username(uq) · email(uq) · hashed_password · nickname · avatar · created_at/updated_at
- `heritage_sites`: id · site_key(uq) · name · alias(json) · area(县市区) · category(功能分区) · unesco_group · lat/lng · address · open_hours · tags(json) · intro_short · source
- `chat_sessions`: id · user_id(FK) · title · mode(qa|itinerary|explain) · site_key(null) · created_at
- `chat_messages`: id · session_id(FK) · role(user|assistant|tool) · content · sources(json 引用来源) · created_at
- `itineraries`: id · user_id(FK) · params(json) · content(json 逐日行程 + md) · created_at
- `favorites`: id · user_id(FK) · site_key · created_at；唯一(user_id, site_key)

### 4.2 PostgreSQL + pgvector（知识库）
- `documents`: id · site_key/topic · chunk_index · title · content(text) · metadata(jsonb:来源/段…) · embedding vector(1024) · created_at
- 索引：HNSW（1024 维，bge-m3）
- 迁移工具：Alembic

## 5. REST API 一览（v1）

```
POST   /api/auth/register          # 注册（bcrypt）
POST   /api/auth/login             # 登录 → {access_token}
GET    /api/auth/me                # JWT
GET    /api/sites                  # 世遗点列表（搜索/筛选/分页）
GET    /api/sites/{site_key}       # 详情
GET/POST /api/chat/sessions        # 会话列表 / 新建(mode=qa|itinerary|explain)
GET    /api/chat/sessions/{id}/messages
POST   /api/chat/stream            # SSE：逐 token 推送（问答/行程/讲解统一出口）
GET/POST /api/itineraries          # 我的行程 / 生成；GET /{id}
GET/POST/DELETE /api/favorites
GET    /api/health
```

## 6. 非功能要点
- **安全**：bcrypt 加盐哈希；JWT 过期；越权/IDOR 防护复查（D39）。
- **防幻觉**：RAG prompt 约束"只依据语料作答，无据可依则明说"；作答附引用来源。
- **可观测**：结构化日志 + 简单请求耗时指标雏形（D39）。
- **部署**：docker-compose（mysql/pg/backend/frontend-nginx），本地先跑通，末期真上线选型（见课表 D41）。
