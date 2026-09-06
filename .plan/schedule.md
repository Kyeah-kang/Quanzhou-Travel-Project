# 开发主课表 ｜ 刺桐智游（2026-09-04 → 2026-10-31）

> **教学日 = 周一~周六**；周日与国庆 10/1–10/8 为**复习/缓冲/赶超**（共约 15 天缓冲）。
> 这是**活文档**：每周校准一次；落后用缓冲日消化，未掌握的内容不往后堆叠。
> 提交规范：`docs|feat|mod|fix|test: 模块DNN-简述`。

## 里程碑总览

| 里程碑 | 范围 | 日期 | Tag |
|---|---|---|---|
| M0 启动与环境 | D01–D03 | 9/4–9/8 | — |
| M1 MySQL 数据层 + 认证 | D04–D10 | 9/9–9/16 | `m1-auth` |
| M2 知识库数据工程 | D11–D19 | 9/17–9/26 | `m2-knowledge` |
| M3 RAG 问答闭环 | D20–D24 | 9/28–10/10（中间国庆） | `m3-qa` |
| M4 React 前端 | D25–D31 | 10/12–10/19 | `m4-frontend` |
| M5 LangGraph Agent | D32–D39 | 10/20–10/28 | `m5-agent` |
| M6 工程化 + 上线 + 简历 | D40–D42 | 10/29–10/31 | `m6-release` |

## 每日明细

| D# | 日期 | 里程碑 | 今日主题 / 讲解重点 | 状态 |
|---|---|---|---|---|
| D01 | 9/4 (五) | M0 | 项目总纲/架构全景/选型理由；git init + README + .gitignore + 建 .plan；Monorepo 与 Git 工作流 | ✅ |
| D02 | 9/7 (一) | M0 | Docker/compose 入门：起 mysql:8 与 pgvector:pg16；镜像/卷/网络/健康检查 | ✅ |
| D03 | 9/8 (二) | M0 | FastAPI 骨架：app 工厂 + .env(pydantic-settings) + CORS + /api/health + 日志 | ✅ |
| D04 | 9/9 (三) | M1 | SQLAlchemy 2.0：engine/session/Base + users 表；同步 vs 异步取舍 | ✅ |
| D05 | 9/10 (四) | M1 | 全表建模 + Alembic 迁移：users/sessions/messages/itineraries/heritage_sites/favorites | ✅ |
| D06 | 9/11 (五) | M1 | 注册接口 POST /api/auth/register：bcrypt 哈希与加盐；唯一性校验 | ⬜ |
| D07 | 9/12 (六) | M1 | 登录设计思路 + 登录接口：为何 REST 用 token 而非 session | ⬜ |
| D08 | 9/14 (一) | M1 | JWT 精讲：签发/过期/校验；Header.Payload.Signature 与签名原理 | ⬜ |
| D09 | 9/15 (二) | M1 | 认证依赖注入 + 受保护路由 GET /api/auth/me；鉴权链路完整复述 | ⬜ |
| D10 | 9/16 (三) | M1 | pytest+httpx auth 测试 + 回归；M1 评审 | ⬜ |
| D11 | 9/17 (四) | M2 | 语料规范：frontmatter 设计 + 首批 2–3 处高保真样例（老师协助） | ⬜ |
| D12 | 9/18 (五) | M2 | 语料批次A：海丝·港口·城市·市舶类 遗产点录入校对 | ⬜ |
| D13 | 9/19 (六) | M2 | 语料批次B：宗教/墓葬/石刻 类录入校对 | ⬜ |
| D14 | 9/21 (一) | M2 | 语料批次C：桥梁/码头/航标/窑址/冶铁 类录入校对，完成 22 处 v1 | ⬜ |
| D15 | 9/22 (二) | M2 | 主题背景语料（海丝史/闽南文化/非遗/美食）+ 质检脚本 | ⬜ |
| D16 | 9/23 (三) | M2 | 切分策略：naive vs Recursive 中文 vs 语义切块(overlap/metadata) | ⬜ |
| D17 | 9/24 (四) | M2 | pgvector：documents 表 + HNSW 索引；手写 切→嵌→入库 管线全量跑 | ⬜ |
| D18 | 9/25 (五) | M2 | 手写检索器：余弦相似度 SQL + topK + metadata 过滤；为何需要 rerank | ⬜ |
| D19 | 9/26 (六) | M2 | 离线检索评测 + 调优（切块/重叠/topK）；M2 评审 | ⬜ |
| D20 | 9/28 (一) | M3 | LangChain 版检索：OpenAIEmbeddings(siliconflow bge-m3) + PGVector store | ⬜ |
| D21 | 9/29 (二) | M3 | RAG QA 链：LCEL + 防幻觉 prompt（只依据语料 + 输出引用来源） | ⬜ |
| D22 | 9/30 (三) | M3 | DeepSeek v4-flash 接入 + LLM provider 抽象；核对真实 model id 与成本 | ⬜ |
| D23 | 10/9 (五) | M3 | SSE 流式问答接口：StreamingResponse 逐 token 推；SSE vs WebSocket | ⬜ |
| D24 | 10/10 (六) | M3 | 会话持久化 + 历史作为上下文；记忆截断策略；M3 评审 | ⬜ |
| D25 | 10/12 (一) | M4 | React/Vite/TS 基础精讲（组件/JSX/state/effect/hooks）；dev proxy | ⬜ |
| D26 | 10/13 (二) | M4 | 前端架构：axios 封装+拦截器(带 token)、路由守卫、全局状态(zustand) | ⬜ |
| D27 | 10/14 (三) | M4 | 登录/注册页 UI + 表单校验 + 打通后端 | ⬜ |
| D28 | 10/15 (四) | M4 | 世遗点 列表/搜索/详情页 → /api/sites | ⬜ |
| D29 | 10/16 (五) | M4 | 问答对话页：SSE 流式 markdown 渲染、停止生成、历史会话侧栏 | ⬜ |
| D30 | 10/17 (六) | M4 | 行程规划页(表单→时间线) + AI 讲解页 + 个人中心 | ⬜ |
| D31 | 10/19 (一) | M4 | 前端打磨(AntD/loading/空错态/响应式) + 端到端回归；M4 评审 | ⬜ |
| D32 | 10/20 (二) | M5 | LangGraph 概念：StateGraph/State/节点/边/条件路由；画 planner 状态图 | ⬜ |
| D33 | 10/21 (三) | M5 | 意图解析 + 参数抽取：Pydantic structured output；缺信息反问 | ⬜ |
| D34 | 10/22 (四) | M5 | 工具封装 tools：站点/开馆/检索/地理/贴士；tool schema 与 ReAct | ⬜ |
| D35 | 10/23 (五) | M5 | 行程编排节点：按 天/就近/主题 生成逐日行程草稿(JSON schema) | ⬜ |
| D36 | 10/24 (六) | M5 | 校验与自纠 + 落库；输出 JSON+markdown；保存 itineraries | ⬜ |
| D37 | 10/26 (一) | M5 | AI 讲解功能：site 检索 + 叙事大纲 + 带站点上下文追问闭环 | ⬜ |
| D38 | 10/27 (二) | M5 | 服务整合：chat 路由按 mode 分发 qa/itinerary/explain；统一流式 | ⬜ |
| D39 | 10/28 (三) | M5 | 上线前健康检查：越权/IDOR、prompt 注入、超时、logging/metrics；M5 评审 | ⬜ |
| D40 | 10/29 (四) | M6 | 容器化：backend 多阶段 Dockerfile + frontend→nginx + compose 生产编排 | ⬜ |
| D41 | 10/30 (五) | M6 | 上线冲刺（重新选型：学生云优先）+ 备份/日志/CI/HTTPS | ⬜ |
| D42 | 10/31 (六) | M6 | 简历与复盘：README 精修/亮点 bullet/演示/面试讲稿 | ⬜ |

> 富余缓冲：周日 9/6·9/13·9/20·9/27·10/11·10/18·10/25 与国庆 10/1–10/8。
