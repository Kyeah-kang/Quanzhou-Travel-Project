# 🌺 刺桐智游 —— 泉州世遗文化 AI 伴游助手

> 刺桐（Zayton）是泉州古称。2021 年「**泉州：宋元中国的世界海洋商贸中心**」列入《世界遗产名录》，含 **22 处遗产点**。
> 刺桐智游是一款面向泉州世遗城市旅游场景的 **AI 伴游助手**：以 RAG 知识库与 Agent 编排为核心，陪你读懂一座「世遗之城」。

## ✨ 三大核心功能

| 功能 | 说明 | 技术主线 |
|---|---|---|
| 🧭 **文化问答** | 围绕泉州世遗/海丝史/闽南文化自由提问，作答**带引用来源**，多轮会话落库 | RAG：pgvector 向量检索 + LLM 依据语料作答 |
| 🗺 **个性化行程规划** | 输入天数/兴趣/节奏，Agent 逐日编排行程（地理就近·主题分组·开馆时间·餐饮交通） | LangGraph 有状态多步编排 + 工具调用 |
| 📖 **AI 文化讲解** | 选中某遗产点，生成分节叙事讲解，并支持带站点上下文的追问 | 单站点 RAG + 长文生成 |

配套：用户注册/登录（JWT）、22 处世遗点主数据浏览、会话历史、行程收藏、个人中心。

## 🧱 技术栈

| 层 | 选型 |
|---|---|
| 后端 | Python · **FastAPI**（REST + SSE 流式） |
| RAG | **LangChain**（切分/Embedding/Retriever/LCEL） |
| Agent | **LangGraph**（StateGraph 编排） |
| 业务库 | **MySQL 8**（SQLAlchemy 2.0 + Alembic 迁移） |
| 向量库 | **PostgreSQL + pgvector**（HNSW，1024 维） |
| 大模型 | **DeepSeek v4-flash**（对话）· 硅基流动 **bge-m3**（中文 Embedding，可替换抽象层） |
| 前端 | **React 18 + Vite + TypeScript + Ant Design** |
| 部署 | Docker / docker-compose · GitHub Actions（CI） |

## 🗂 项目结构（Monorepo）

```
├─ .plan/          # 规划文档：课表 schedule.md · 每日笔记 daily/
├─ docs/           # architecture.md / API.md / 简历亮点.md
├─ data/           # 泉州世遗知识库原始语料(raw_md) + ingest 脚本
├─ backend/        # FastAPI 应用（app/core·db·models·schemas·routers·services·rag·agent）
├─ frontend/       # React 前端（Vite + TS + AntD）
├─ docker-compose.yml   # mysql · postgres(pgvector) · backend · frontend
└─ README.md
```

## 🚀 快速开始

> 随模块开发逐步补全（D03 后可起 `/api/health`；D40 后提供 `docker compose up` 一键启动说明）。

```bash
# 后端（本地开发）
cd backend && python -m pip install -e ".[dev]" && python -m uvicorn app.main:app --reload

# 前端（本地开发）
cd frontend && npm install && npm run dev
```

## 🗺 开发路线图（2026-09-04 → 2026-10-31）

- [ ] **M0** 启动与环境：仓库骨架 / Docker+compose(mysql+pgvector) / FastAPI 骨架
- [ ] **M1** MySQL 数据层 + 用户认证（注册·登录·JWT·受保护路由）
- [ ] **M2** 知识库数据工程：22 处遗产点语料 · 切块 · pgvector 入库 · 手写检索器
- [ ] **M3** RAG 文化问答闭环（LangChain + DeepSeek + SSE + 会话持久化）
- [ ] **M4** React 前端（登录注册/世遗点/问答/行程/讲解/个人中心）
- [ ] **M5** LangGraph Agent：行程规划 + AI 讲解 + 安全健康检查
- [ ] **M6** 容器化 + 上线冲刺 + 简历包装

## 📄 文档

- 开发课表与进度：[`.plan/schedule.md`](.plan/schedule.md)
- 架构设计：[`docs/architecture.md`](docs/architecture.md)
- 编码 Agent（Codex）契约：[`AGENTS.md`](AGENTS.md)
- Claude Code 项目手册（架构/模块/原则/分层）：[`CLAUDE.md`](CLAUDE.md)

## 📌 说明

语料内容来自官方申遗文本及权威公开资料，逐条在语料 frontmatter 的 `source` 字段标注来源，仅供学习交流。
