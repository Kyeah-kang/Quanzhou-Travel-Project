# 开发主课表 ｜ 刺桐智游（2026-09-04 → 2026-10-31）

> **教学日 = 周一~周六**；周日与国庆 10/1–10/8 为**复习/缓冲/赶超**（共约 15 天缓冲）。
> 这是**活文档**：每周校准一次；落后用缓冲日消化，未掌握的内容不往后堆叠。
> 提交规范：`docs|feat|mod|fix|test: 模块DNN-简述`。

## 里程碑总览

| 里程碑 | 范围 | 日期 | Tag |
|---|---|---|---|
| M0 启动与环境 | D01–D03 | 9/4–9/8 | — |
| M1 MySQL 数据层 + 认证 | D04–D10 | 9/9–9/16 | `m1-auth` |
| M2 数据工程 + 可评测检索基础 | D11–D19 | 9/17–9/26（**实际 9/12 开工**） | `m2-knowledge` |
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
| D06 | 9/11 (五) | M1 | 注册接口 POST /api/auth/register：bcrypt 哈希与加盐；唯一性校验 | ✅ |
| D07 | 9/12 (六) | M1 | 登录设计思路 + 登录接口：为何 REST 用 token 而非 session | ✅ |
| D08 | 9/14 (一) | M1 | JWT 精讲：签发/过期/校验；Header.Payload.Signature 与签名原理 | ✅ |
| D09 | 9/15 (二) | M1 | 认证依赖注入 + 受保护路由 GET /api/auth/me；鉴权链路完整复述 | ✅ |
| D10 | 9/16 (三) | M1 | pytest+httpx auth 测试 + 回归；M1 评审 | ✅ |
| D11 | 9/17 (四) | M2 | 语料合同 v2：frontmatter + 受控词表 + **溯源规则(pending_fields)** + **行程约束字段**；3 处样例；结构校验器 + 单测 | ✅ |
| D12 | 9/18 (五) | M2 | 批次A 录入校对「城市结构 · 机构保障」6 处（市舶司/南外宗正司/德济门/顺济桥/江口码头/府文庙） | ✅ |
| D13 | 9/19 (六) | M2 | 批次B 录入校对「多元社群：宗教/墓葬/石刻」6 处（天后宫/真武庙/开元寺/圣墓/草庵/老君岩） | ✅ |
| D14 | 9/21 (一) | M2 | 批次C 录入校对「交通网络 · 生产基地」7 处 → 22/22；Alembic 增补约束字段；corpus→MySQL 幂等落库；完整率 v1 | ⏳ |
| D15 | 9/22 (二) | M2 | 主题文化语料 6 篇 + 内容层质检（corpus_quality → 报告）+ 检索评测集 v1（六类分型，含 M5 约束型） | ⬜ |
| D16 | 9/23 (三) | M2 | 中文切分策略设计与**离线对比实验**（3 策略 × 参数网格，不花 API）+ chunk metadata 契约 + 单测 | ⬜ |
| D17 | 9/24 (四) | M2 | pgvector：documents 表 + HNSW；嵌入管线闭环（**幂等三态 / stale 清理 / 边界校验 / 报告 / 哈希缓存**）；不写 LangChain | ⬜ |
| D18 | 9/25 (五) | M2 | 手写检索器：余弦 SQL + metadata 硬过滤 + over-fetch + empty_reason 诊断；为何不能只靠相似度 | ⬜ |
| D19 | 9/26 (六) | M2 | 离线评测 Hit@K/Recall@K（3 策略 × 过滤 × K）+ 失败归类 + M2 评审 + M3/M5 移交清单 | ⬜ |
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

## M2（D11–D19）验收重点

> 计划 9/17–9/26；**实际 9/12 开工，提前约 5 天**，最早可 9/22 收口。完整逐日计划与文件边界见 `.plan/modules/M2.md`。
> M2 定位：**高保真旅游领域数据工程 + 可评测的检索基础 + 面向 M5 约束规划的数据准备**（不只是"把资料灌进向量库"）。

- **数据**：22/22 站点语料 + 主题语料 ≥6 篇；`corpus_check` 0 FAIL；`source` 全覆盖；`fact_status` 与 `pending_fields` 自洽；**词表覆盖 22 处**（扩表须有理由）；非空字段**无编造**
- **主数据**：22/22 入 MySQL（`site_key` 唯一；迁移可升可降）；`site_loader` **连跑两次幂等**；完整率报告（可得率 vs 待校对率**分开**统计）
- **质检 / 评测集**：质量报告数字可复算；评测集 ≥40 条、**六类覆盖**（单点/别名/跨主题/模糊/易混淆/约束型）、含 `planned_for=M5`
- **切分**：3 策略 × 参数网格的**结构对比表**；基线参数**有理由**（非凭感觉）
- **向量 / 检索**：`documents` + HNSW；**幂等三态**（skip/update/stale_deleted）实证；5 类边界各触发 1 次失败并计入报告；`search()` 支持硬过滤 + `over_fetch` + `empty_reason`
- **评测结论**：`Hit@K` / `Recall@K` 矩阵可复算；失败案例归类 ≥5 类；`docs/retrieval-eval.md` 含**选定基线** + **M3 改进项** + **M5 移交清单**
- **纪律**：无 LangChain / 对话模型 / SSE / 前端 / Agent 越界；依赖仅 `pyyaml` / `psycopg` / `httpx`(提升) 三项；`ruff` 干净、`pytest` 零回归
