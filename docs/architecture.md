# 刺桐智游 · 架构设计（v1）

> 一句话定位：泉州世遗场景的 AI 伴游助手 —— RAG 文化问答 + LangGraph 个性化行程规划 + AI 叙事讲解。
> 本文是项目的地基文档，随模块演进持续更新（**v0.2 @ 2026-09-12 / M2 重规划**：数据工程与检索评测定稿）。

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
2. **两类数据职责分离（M2 细化到字段级）**：
   - MySQL `heritage_sites` 存**可硬过滤 / 可约束**的结构化字段：`name/alias/area/category/key_element/lat/lng/address/open_hours/visit_duration_min/theme/notice/tags/intro_short` → 支撑列表筛选、地理就近、**行程硬约束**（M5）。
   - PG `documents`(含 vector) 存**非结构化长文分块 + 检索期 metadata 镜像** → 支撑语义召回与"先硬过滤再召回"。
   - **同一份语料 frontmatter 被两个消费者消费**：MySQL 只存**短引文** `source`，完整来源列表留在语料与 PG metadata（不在两处重复存大字段）；字段口径以 `data/raw_md/` 为唯一事实源。字段 × 消费者分工表见 `docs/corpus-spec.md`。
3. **先手写，再框架**：RAG 检索先手写 pgvector 余弦 SQL 一遍，再引入 LangChain PGVector store——先懂原理，再学封装。
4. **OpenAI 兼容协议统一抽象**：DeepSeek 与硅基流动都兼容 OpenAI 协议；`core/llm_provider` 集中管理，可随时换模型/Embedding。面试高频考点。
5. **同步 ORM 起步 + repository 分层**：SQLAlchemy 2.0 同步 + PyMySQL（Windows 免编译、易调试）；业务逻辑经 repository/service 封装，日后可平滑升级 async。取舍点会专题讲解。
6. **流式优先**：AI 长回复一律走 SSE 逐 token 推送，前端流式渲染，交互接近真实产品。
7. **Alembic 管 schema 演进**：上线必需，避免"手改表结构"。

## 3. 目录结构（Monorepo）

```
├─ .plan/            # 课表 schedule.md · 模块简报 modules/ · 每日笔记 daily/
├─ docs/             # 本文档 / corpus-spec.md / corpus-quality.md / retrieval-eval.md
├─ data/             # 纯数据资产：raw_md(frontmatter+六节语料) / eval(评测集) / reports(生成报告) / .cache(嵌入缓存,gitignore)
├─ backend/
│  ├─ app/
│  │  ├─ main.py            # app 工厂 + 路由 + 中间件
│  │  ├─ core/              # config / security / deps / llm_provider
│  │  ├─ db/                # engine / session / base / alembic
│  │  ├─ models/            # SQLAlchemy 模型（业务表）
│  │  ├─ schemas/           # Pydantic v2 请求/响应
│  │  ├─ routers/           # auth · sites · chat · itinerary · favorites
│  │  ├─ services/          # 业务逻辑
│  │  ├─ rag/               # 领域能力：corpus(解析) · splitter · embedder · vector_store(检索) 〔M3 加 qa_chain〕
│  │  ├─ ingest/            # 离线管线 CLI：corpus_check · corpus_quality · site_loader · indexer · evaluator
│  │  ├─ agent/             # langgraph: state · graph · nodes · tools（M5）
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
- `heritage_sites`（M2-D14 增列后）: id · `site_key`(uq) · name · alias(json) · area(索引) · category(索引) · `key_element` · unesco_group · lat · lng · address · open_hours · **`visit_duration_min`(int，M5 时间预算)** · **`theme`(json，M5 主题匹配)** · **`notice`(M5/前端游览提示)** · tags(json) · intro_short · **source(字符串，仅"短引文"；完整来源列表在语料与 PG metadata)** · **`fact_status` / `pending_fields`(json，数据可信度标注)** · created_at/updated_at
  - 迁移：`backend/alembic/versions/<rev>_add_site_constraint_fields.py`（可升可降）
  - 落库：`app/ingest/site_loader.py` 按 `site_key` **幂等 upsert**（见 §6.2）
- `chat_sessions`: id · user_id(FK) · title · mode(qa|itinerary|explain) · site_key(null) · created_at
- `chat_messages`: id · session_id(FK) · role(user|assistant|tool) · content · sources(json 引用来源) · created_at
- `itineraries`: id · user_id(FK) · params(json) · content(json 逐日行程 + md) · created_at
- `favorites`: id · user_id(FK) · site_key · created_at；唯一(user_id, site_key)

### 4.2 PostgreSQL + pgvector（知识库，M2-D17 定稿）

- `documents`（**派生索引**：可从 `data/raw_md/` 完整重建）
  - id · `doc_type`(site|topic) · `doc_key`（站点文档 == `heritage_sites.site_key`；主题文档 `topic_*`）· `section`（六节标题之一，**跨切分策略稳定的评测锚点**）· `chunk_index` · `chunk_strategy`(naive|recursive|semantic) · `title` · `content` · `content_hash`(sha256，幂等判定) · `char_len` · `metadata`(jsonb：`source` 完整列表 / category / area / theme / open_hours / visit_duration_min / fact_status / pending_fields …) · `embedding vector(1024)` · created_at
  - **唯一键 `(doc_key, chunk_strategy, chunk_index)`** → 多策略并存 + 幂等 upsert + stale 尾巴清理（见 §6.2）
  - 索引：`HNSW (embedding vector_cosine_ops)`；btree on `doc_key` / `section` / `chunk_strategy` / `doc_type`
- **建表方式**：`app/rag/vector_store.ensure_schema()` 幂等 DDL，**不纳入 Alembic** —— 理由：PG 在此是**派生索引而非权威数据**，可随时重建；避免在单项目内维护两套迁移体系。
  （技术债登记：一旦 PG 承载权威数据，须补 Alembic。）

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

## 6. M2 数据工程与检索评测（2026-09-12 定稿）

### 6.1 离线管线（`backend/app/ingest/`）

> 分层约定：**Python 全部收在 `backend/`**（单一 venv、无 `sys.path` 技巧、可被 pytest 直接测）；`data/` 只放**数据资产**（语料 / 评测集 / 生成报告 / 嵌入缓存）。

```
语料 .md ─[corpus_check 结构校验]→ ─[site_loader 幂等 upsert]→ MySQL heritage_sites
                                  └[indexer: 解析 → splitter(3 策略) → embedder(bge-m3,1024) → upsert]→ PG documents
评测 .jsonl ─[evaluator]→ Hit@K / Recall@K → docs/retrieval-eval.md + data/reports/
```

- `app/rag/` = **可复用领域能力**（corpus / splitter / embedder / vector_store），离线管线与 M3/M5 服务共用同一份实现；该层**不依赖 FastAPI 请求上下文**（允许作为外部模型 API 的客户端）。
- **不引入 LangChain**：M2 全部手写（呼应设计原则 2：先手写再框架）。

### 6.2 幂等与 stale 清理（"重复运行不产生失控重复数据"）

- 判定键 `(doc_key, chunk_strategy, chunk_index)` + `content_hash`：
  - hash 未变 → `skip`；内容变 → `update`（重写 content + embedding）
  - **新块数 < 旧块数 → 删除尾部 `chunk_index >= new_count` 的行**（`stale_deleted`）
- 报告字段：`total_files / total_chunks / embedded / skipped / updated / stale_deleted / failed(+reasons)`
- 边界校验（各计一次失败）：空内容、缺 `source`、`section` 缺失、维度不符（≠1024）、重复 chunk
- **嵌入缓存**：`data/.cache/embeddings/<content_hash>.json`（已 gitignore）→ 重跑 / 换策略 / 重评测趋近零 API 调用

### 6.3 chunk metadata 契约（D16 定稿）

`doc_type · doc_key · section · title · chunk_index · chunk_strategy · content_hash`
→ `section` 让评测集（`expected: [{doc_key, section}]`）在 3 种切分策略下**通用**（`chunk_index` 会随策略变，不能作锚点）。

### 6.4 检索：先硬过滤，再向量召回

- **硬过滤**（结构化）：`doc_key / doc_type / area / category / theme`
- **向量召回**：`ORDER BY embedding <=> %s::vector LIMIT k`（相似度 = `1 - distance`）
- **注意**：过滤后 ANN 可能**不足 K 行**（pgvector 已知行为）→ 用 `over_fetch`（多取再过滤/截断）应对；D18 实证、D19 量化
- **诊断**：`empty_reason ∈ {no_vector_match, filtered_out, low_similarity}` —— 把"没检索到"与"被过滤掉"分开
- **为什么不能只靠相似度**：硬约束（开放时间/时长/区域）不该交给相似度；别名与专名对向量不敏感；多意图问题（"三天怎么安排"）没有单一语义答案 → 分别交给 M3（查询改写/提示词）与 M5（约束编排）

### 6.5 评测协议（D15 建集 / D19 出数）

- 评测集 `data/eval/retrieval_eval_v1.jsonl`：`{id, query, intent_type, expected[{doc_key, section}], difficulty, planned_for?}`
- 六类分型：单点事实 / 别名 / 跨主题 / 模糊表达 / 易混淆站点 / 约束型（标 `planned_for: M5`）
- 指标：`Hit@K`（Top-K 是否命中任一期望项）与 `Recall@K`（期望项被召回比例）；实验矩阵 = 3 策略 × 过滤开/关 × `K∈{3,5,10}`
- 产出：结果矩阵 + **失败归类**（别名 / 主题混淆 / chunk 不完整 / metadata 缺失 / 语料不足 / 约束型）+ 选定基线 + **M3 改进项** + **M5 移交清单**

## 7. 非功能要点
- **安全**：bcrypt 加盐哈希；JWT 过期；越权/IDOR 防护复查（D39）。
- **防幻觉**：RAG prompt 约束"只依据语料作答，无据可依则明说"；作答附引用来源。
- **可观测**：结构化日志 + 简单请求耗时指标雏形（D39）。
- **部署**：docker-compose（mysql/pg/backend/frontend-nginx），本地先跑通，末期真上线选型（见课表 D41）。
