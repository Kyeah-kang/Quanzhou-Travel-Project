# 语料资产目录

`data/` 只保存项目的数据资产，不放 Python 脚本或运行环境。

## 目录

```text
data/
├─ raw_md/       # 站点与主题 Markdown 语料，含 YAML frontmatter
├─ eval/         # 离线检索评测集（D15 起）
├─ reports/      # 质检、入库和评测报告（D15/D17/D19）
└─ .cache/       # 本地缓存，不提交
```

## 命名规则

- 一个站点对应一个 `raw_md/*.md` 文件。
- 站点文件名使用小写英文蛇形，去掉 `.md` 后必须等于 frontmatter 的 `site_key`。
- 主题语料使用 `topic_*` 前缀。
- 新文件按 `_template.md` 的字段和固定六节正文结构编写。

## 工作流

1. 先使用权威来源核对事实，再在 frontmatter 的 `source` 中登记来源。
2. 没有可靠来源的数值填 `null`，文本填 `待校对`，并将字段加入 `pending_fields`。
3. 来源存在冲突时保留异说，并在正文中用统一格式标记，不擅自选边。
4. 在 `backend/` 下运行 `python -m app.ingest.corpus_check` 做结构校验。
5. D15 起再做内容质量检查；结构校验不代替事实审校。
