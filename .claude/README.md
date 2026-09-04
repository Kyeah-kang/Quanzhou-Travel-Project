# .claude/ —— Claude Code 仓库级配置

> 与仓库根的 `CLAUDE.md` / `AGENTS.md` **互补**而非重复：
> 那两个文件是给人+Codex 读的「契约文本」（怎么想、怎么写、红线在哪）；
> 这个目录是给「工具」的机器配置——**自动执行 / 强制拦截 / 一键复用**。

## 布局

| 路径 | 作用 | 生效方式 |
|---|---|---|
| `settings.json` | 权限白名单（常用只读 git 免弹窗） | Claude Code 读入（新会话或 `/hooks` 后生效） |
| `githooks/commit-msg` | 提交规范强制：`类型: 模块DNN-简述` | **git 层拦截**，任何提交者（含 Codex）都绕不开 |
| `skills/review-dnn/` | 评审技能：按 CLAUDE.md §9 过 Codex 交付 | `/review-dnn` 或会话里触发 |
| `skills/teach-module/` | 带教技能：按 CLAUDE.md §8 六段讲透模块 | `/teach-module` 或会话里触发 |

## 一次性安装（当前机器已执行，新 clone 需重跑）

```powershell
git config core.hooksPath .claude/githooks   # 启用 commit-msg 提交钩子
```

## 约定与豁免

- 提交信息不达标会被 `commit-msg` 拒绝；紧急豁免用 `git commit --no-verify`。
- 类型白名单取 AGENTS.md §6：`feat|mod|fix|docs|test`；merge/revert 系统提交自动放行。
- 权限白名单可随时在 `settings.json` 增删；个人偏好放 `.claude/settings.local.json`（已 gitignore，不入库）。

## M1（有真实后端代码）之后待办

- `agents/architect-review.md` —— 独立「架构评审」子代理，与主会话做 four-eyes 分工，把 CLAUDE.md §7 分层约束 + §9 清单固化为只读评审角色。
- 视需要再加 hooks：如提交前自动跑 `ruff check`、扫描 `.env` 是否误入暂存区。
- 语料上线（M2）后加语料质检技能。
