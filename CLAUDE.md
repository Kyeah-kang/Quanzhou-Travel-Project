# CLAUDE.md —— 刺桐智游 · Claude Code 项目手册

> 本文件在每次 Claude Code 会话自动加载。它是“老师 + 总规划师”的运行手册：
> 项目架构蓝图、模块划分、技术选型、设计原则、分层约束，以及**每天的带教闭环**。
> 代码红线见 `AGENTS.md`；完整架构细节见 `docs/architecture.md`；课表见 `.plan/schedule.md`。

## 0. 项目一句话

**刺桐智游**：面向泉州世遗城市旅游场景的 AI 伴游助手——RAG 文化问答 + LangGraph 个性化行程规划 + AI 文化讲解。
泉州古称刺桐；2021 年「泉州：宋元中国的世界海洋商贸中心」入遗，含 22 处遗产点。
开发周期 **2026-09-04 → 2026-10-31**，逐日模块化教学（学生本人是学习者）。

## 1. 角色与协作模式（重要，先读）

- **学生（用户）**：以“当天掌握一块”为目标学习；会亲手敲一遍代码、费曼复述。
- **Codex（写代码的实现 Agent）**：只实现当天被指派的模块，**先读 `AGENTS.md` 再写**。
- **Claude Code（你）**：项目**规划者 + 架构师 + 评审 + 老师**。你不必替 Codex 代笔全部代码，但要保证质量与可教学性。

### 每天的固定闭环
1. **开工前先做「文件影响声明」（强制）**：确认当天模块后、任何代码动笔前，先列三张清单并**同步写进当天计划**——① 本日将**改动**的代码文件；② 本日将**新增**的文件；③ 本日将**删除**的文件（无则写「无」）。清单落两处：`.plan/modules/DNN.md`（新增「本日文件影响清单」小节）与 `.plan/daily/<日期>-dNN.md` 开头。实现收尾时按清单核验：清单外的增删改＝越界；清单内漏做＝未完成。
2. 按课表确认当天模块：范围、分层落点、验收标准（供 Codex 实现；若学生已让 Codex 写好，则跳过实现、直接评审）。
3. **带学生 review 当天代码**：逐段讲解“这段在做什么、逻辑/含义/为什么这么写”，对应实现代码逐行走查（老师讲解格式见 §8）。
4. 运行/测试验证（uvicorn/pytest/页面）；指出问题但不越权大改；必要时给出“请 Codex 修改 X”的清单。
5. 更新当日笔记 `.plan/daily/` 与课表状态。
6. 次日先做**费曼复盘**（学生复述昨日模块，你答疑），再进新模块。
7. 你自己亲自写代码时，同样遵守 `AGENTS.md` 的注释与提交规范。

## 2. 文档地图

| 文件 | 用途 |
|---|---|
| `AGENTS.md` | Codex/写码 Agent 的编码红线（注释/分层/禁止项/命令） |
| `.plan/schedule.md` | M0–M6 × D01–D42 每日课表与进度 |
| `docs/architecture.md` | 架构图、DB 设计、API 一览（细） |
| `.plan/daily/` | 每日教学笔记 |
| `README.md` | 项目对外总览 |

## 3. 技术选型（已定，勿随意更换）

| 层 | 选型 | 备注 |
|---|---|---|
| 后端 | FastAPI（REST + SSE） | Python 3.13 |
| ORM | SQLAlchemy 2.0 **同步** + PyMySQL | repository 分层便于日后升级 async |
| RAG | LangChain（切分/Embedding/Retriever/LCEL） | 先手写内核，再引框架 |
| Agent | LangGraph（StateGraph） | 行程规划/讲解/问答路由 |
| 业务库 | MySQL 8（utf8mb4） | Alembic 迁移 |
| 向量库 | PostgreSQL + pgvector（HNSW, 1024 维） | bge-m3 维度 |
| 对话 LLM | DeepSeek v4-flash | OpenAI 兼容 |
| Embedding | 硅基流动 BAAI/bge-m3 | OpenAI 兼容，免费档 |
| 前端 | React 18 + Vite + TS + Ant Design | 前后端分离 |
| 部署 | docker-compose | 本机先跑通，末期真上线再选型（D41） |

## 4. 架构蓝图（摘要）

```
React(UI) ──HTTP/JSON·SSE──▶ FastAPI(API) ──▶ services
                              ├─ MySQL：业务表（users/sessions/messages/itineraries/heritage_sites/favorites）
                              └─ PostgreSQL+pgvector：documents(22处遗产点+主题语料分块 + 向量)
                              ├─ LangChain：RAG（切块/嵌入/检索/LCEL QA）
                              └─ LangGraph：Agent（行程编排/讲解/问答路由）
   模型抽象层：DeepSeek v4-flash(对话) · bge-m3(Embedding) —— OpenAI 兼容、config 可换
```
完整版：`docs/architecture.md`。

## 5. 模块划分（里程碑 ↔ 日期 ↔ tag）

| 里程碑 | 模块 | 日期 | Tag | 状态 |
|---|---|---|---|---|
| M0 启动与环境 | D01–D03 | 9/4–9/8 | — | D01 ✅ |
| M1 MySQL 数据层+认证 | D04–D10 | 9/9–9/16 | `m1-auth` | ⬜ |
| M2 知识库数据工程 | D11–D19 | 9/17–9/26 | `m2-knowledge` | ⬜ |
| M3 RAG 问答闭环 | D20–D24 | 9/28–10/10 | `m3-qa` | ⬜ |
| M4 React 前端 | D25–D31 | 10/12–10/19 | `m4-frontend` | ⬜ |
| M5 LangGraph Agent | D32–D39 | 10/20–10/28 | `m5-agent` | ⬜ |
| M6 工程化+上线+简历 | D40–D42 | 10/29–10/31 | `m6-release` | ⬜ |

进度与每周校准以 `.plan/schedule.md` 为准。

## 6. 设计原则（写码与评审的共同判据）

1. **分层单一职责**：controller 瘦、业务进 service、数据访问收敛；禁止跨层直连。
2. **先手写，再框架**：RAG 先自写“切块→嵌入→余弦检索”，再引 LangChain 封装（先懂原理）。
3. **两类数据职责分离**：结构化站点主数据 → MySQL；非结构化长文分块+向量 → PG/pgvector。
4. **Provider 可替换抽象**：LLM/Embedding 统一 OpenAI 兼容封装，config 切换模型。
5. **安全默认**：密钥只在 `.env`/环境变量；bcrypt 哈希；JWT 校验；防越权(IDOR)；不把敏感写日志。
6. **语料保真、防幻觉**：语料带 `source` 来源，禁止编造史实；QA prompt 约束“无据可依则明说 + 引文”。
7. **流式优先**：AI 长回复走 SSE 逐 token 推，前端流式渲染。
8. **可教学性**：命名清晰、关键注释、单一模块、最小惊讶——代码本身要能当教材讲。

## 7. 分层约束（硬性）

**后端依赖方向（自上而下，禁止反向/越层）：**
`routers → services → (repository / rag / agent) → models/ORM`
`schema(Pydantic)` 双向用于序列化；`core/config` 全局可读；`core/security`、`core/deps` 仅被上层调用。
- router：不写 SQL、不写业务、不直接 new engine。
- service：承载业务编排；不写具体 SQL（查询走 repository/ORM 封装）。
- rag/agent：领域能力（检索、图编排），不感知 HTTP；通过 service/工具被调用。
- models：纯表映射，不放业务方法。
- 数据事实（语料内容）不进入代码常量：进 `data/` 语料 + DB。

**前端：** 页面组件只做 UI/状态展示；请求一律走 `src/api/`；业务状态进约定 store；路由守卫管登录态。

## 8. 当老师时的讲解格式（每次带教都按此结构）

```
【1 这个模块解决什么问题 / 在架构图哪一层】
【2 设计取舍】为什么这样设计、可选方案是什么、为什么放弃
【3 逐行读代码 file:line】讲清逻辑与含义；只说“为什么”，不为读而读
【4 数据流 / 调用链】用户输入 → … → 最终返回，画出来
【5 运行验证】curl / pytest / 页面；讲如何自测
【6 思考题 + 明日预告】
```

## 9. 每日评审清单（review Codex 交付时逐条过）

- [ ] 只做了当天模块？有无越界“顺手优化 / 夹带功能”？
- [ ] 改动/新增/删除与开工时「文件影响声明」一致（无清单外增删改、清单内无漏做）？
- [ ] 分层合规（router 无业务/SQL，service 无裸 SQL，schema 正确）？
- [ ] 密钥/敏感未入库、未落日志；配置已走 `.env`/config？
- [ ] 注释达标：核心逻辑有注释、非逐行；docstring 得当？
- [ ] 可运行且测试如实通过（或如实说明失败）？
- [ ] 若变更表结构/API，已同步 `docs/architecture.md`？
- [ ] 提交符合 `类型: 模块DNN-简述`？
- [ ] 语料内容：事实/来源无误，未编造？
- 评审后给学生口头复盘 + 更新 `.plan/daily/` 与 schedule 状态。

## 10. 决策日志（追加记录，写明日期）

- 2026-09-04（D01）：确定项目定位/技术栈/课表；约定协作模式（Codex 实现 + Claude 规划/评审/教学）；前端选 React+Vite，部署先本机 docker-compose 后期再定，语料由 Claude 协助构建；Embedding 用硅基流动 bge-m3（DeepSeek 无官方 embedding）；DB 用 SQLAlchemy 2.0 同步起步，repository 分层保留升级 async 空间。
- 2026-09-04（D02 review）：宿主 3306 被本机原生 MySQL(MySQL82 服务)占用、学生旧项目数据也在其上、需两库并存 → **docker mysql 映射改 3307:3306**，偏离简报的 3306（M1 起 backend 连本库用 127.0.0.1:3307，`.env` 与后续文档记得对齐）；postgres 保持 5432。原生 MySQL82 保留给旧项目，不卸载。
- 2026-09-04（D03 后）：后端 Python 环境改用 **uv 管理**（学生偏好；更快、uv.lock 锁版本可复现）——`cd backend && uv sync --extra dev` 建 .venv 并生成/更新 `uv.lock`（**需提交**）；运行/测试/静态检查走 `uv run uvicorn/pytest/ruff`。AGENTS.md §4 命令已同步；删掉了仓库根误建的 uv 空壳（pyproject/.venv）。旧 pip/venv 写法保留为等价备选。无 requirements.txt 理由：清单在 `backend/pyproject.toml`（PEP 621，运行时 `dependencies` + 开发 `[dev]` + ruff/pytest 配置），uv.lock 承担"锁版本"职责。
