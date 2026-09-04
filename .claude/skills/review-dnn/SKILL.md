---
name: review-dnn
description: review-dnn —— Review Codex 交付的当天模块（DNN）代码，把交付挑到能当教材。按 CLAUDE.md §9 清单逐条对代码验证（分层/越权/密钥/注释/验证如实/文档同步/提交格式/语料保真），产出 per-file 问题表 +「请 Codex 修改 X」清单，落每日笔记与课表状态。当学生说 review / 评审 / 检查今天或某天 Codex 写的代码时使用。
---

# 任务：Review Codex 当天交付（DNN）

你是本项目的「老师 + 评审」。目标：在**不改 Codex 代码**的前提下，把交付审查到可以当教材的程度。

## 步骤

1. **定位当天模块**
   - 读 `.plan/schedule.md`：确认要评审的 DNN（状态 ⬜ 且最靠前，或用户指定）。
   - 若 `.plan/modules/DNN.md` 存在则读它，以拿到当天范围与验收标准——**只有当天模块算数**。

2. **拿改动**
   - `git status` 看未提交改动；`git log --oneline -8` + `git show --stat HEAD` 定位 Codex 的提交。
   - 从 router → service → repository/rag/agent → models/ORM 分层往下读，验证依赖方向没有反。

3. **逐条过 CLAUDE.md §9 评审清单**（对代码验证，不是照念）
   - 只做了当天模块？有无越界「顺手优化 / 夹带功能 / 大范围重构」？
   - 分层合规：router 无业务/SQL；service 无裸 SQL（查询走 repository/ORM 封装）；schema 类型正确、命名 XxxIn/XxxOut？
   - 密钥/敏感：配置只走 `.env`/config；未入库未落日志；不裸抛堆栈给前端？
   - 注释：核心逻辑有注释、非逐行；docstring 得当（对照 AGENTS.md §2.1）？
   - 可运行且验证**如实**：确有 pytest/ruff/uvicorn 等结果，没有谎报通过？
   - 变更表结构/API 是否同步了 `docs/architecture.md`？
   - 提交信息符合 `类型: 模块DNN-简述`？（现有 commit-msg 钩子会拦）
   - 语料内容（M2 起）：来源/事实无误、未编造、拿不准标「待校对」？

4. **实测验证**（如环境允许）：跑 pytest / ruff 等确认；结果如实写进发现，失败就写失败。

5. **产出评审单**（给学生的口头 + 笔记格式）
   - 总体结论：✅ 通过 / ⚠️ 改完可过 / ❌ 需返工
   - per-file 问题表：`文件:行 | 严重度(高/中/低) | 问题 | 依据（AGENTS/CLAUDE 哪一条）`
   - 「请 Codex 修改 X」清单：逐条、可执行、不替它改。

6. **落笔记**
   - 更新 `.plan/daily/<当日日期>-dNN.md`（评审结论 + 问题清单 + 复盘要点）。
   - 仅当判定通过时，在 `.plan/schedule.md` 把该 DNN 状态改为 ✅。

## 不要做
- 不要直接改 Codex 的代码「顺手修掉」——问题以清单给出（学生本人明确要求你修除外）。
- 不要给清单之外的「风格偏好」；每条问题必须能对到 AGENTS.md / CLAUDE.md 的具体条款。
- 不要越过当天模块去评审未来功能。
