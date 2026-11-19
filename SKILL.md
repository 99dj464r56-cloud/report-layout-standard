---
name: report-layout-standard
description: >-
  本仓库不再作为独立排版技能使用。研究报告的排版已于 2026-11-19 并入「公司课题研究」。
  若要写或验收研究报告、图表、表格或交付 PDF，请改用技能「公司课题研究」（私有仓库
  https://github.com/99dj464r56-cloud/company-research-skill 的 SKILL.md）。
  本目录仅保留公开可读的排版细则与验收脚本副本，与那份唯一技能同步，不是平行模板。
---

# 排版规范（已并入「公司课题研究」）

**请改用「公司课题研究」。** 排版是该课题的表面标准，只为研究服务，写在那份技能里，不在这里另维护一套。本仓库保持公开，只放排版细则和门禁脚本的公开副本，避免把研究框架一并公开。

- 完整技能（须有权限）：https://github.com/99dj464r56-cloud/company-research-skill
- 本仓库公开副本：`references/layout-rules.md`（排版细则）、`scripts/终版排版验收.py`、`scripts/检测裸数字.py`
- 交稿前跑门禁：`python3 scripts/终版排版验收.py <报告.pdf> [附录页码.json] [--expect-pages N]`，以及 `python3 scripts/检测裸数字.py`
- `--expect-pages N` 仅在已约定总页数时使用；未指定则只报告实际页数，不因此 FAIL。不要写死页数。

颜色与版式以 `references/layout-rules.md` 为准（与「公司课题研究」同一份）。评价色（红绿黄）只用于借鉴/评价标注；图表用方向色与指标色，不要再另起一套模板。

以后若有其他目的的排版，再单独立一份；不要把更新写回这份已退役的平行技能。
