---
site_key:            # 必填，小写英文蛇形，必须与文件名一致
name:                # 必填，官方名称
alias: []            # 别名/俗称，列表，可为空
category:            # 必填，受控词表
key_element:         # 六大关键要素之一（属事实字段，未核到原文须列入 pending_fields）
unesco_group:        # 主题分组，便于行程编排
area:                # 必填，县市区
lat:                 # 纬度，无可靠来源时填 null
lng:                 # 经度，无可靠来源时填 null
address:             # 地址
open_hours:          # 开放时间；无来源填「待校对」
tags: []             # 检索标签，列表
intro_short:         # 一句话简介（列表页展示，≤60 字）
visit_duration_min:  # 建议参观时长（分钟，整数）；无来源填 null 并列入 pending_fields
theme: []            # 适合的行程主题，受控词表（编辑归类，不要求来源）
notice:              # 游览注意事项（预约/闭馆日/交通/安全）；无来源填「待校对」
source:              # 必填，来源列表（见下）
  - title:
    url:
    publisher:
    accessed:        # 访问日期 YYYY-MM-DD
pending_fields: []   # 尚无可靠来源、仍待校对的字段名列表；fact_status=已核对 时必须为空
fact_status: 待校对   # 已核对 | 待校对
updated:             # 最后更新 YYYY-MM-DD
---

## 概述
## 历史沿革
## 遗产价值
## 看点与细节
## 实用信息
## 常见问答
