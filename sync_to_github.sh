#!/bin/bash
# 本仓库是公开指针，不再是独立排版技能。
# 唯一来源：私有仓库 99dj464r56-cloud/company-research-skill（技能「公司课题研究」）。
#
# 本脚本原先会把 ~/.workbuddy/skills/report-layout-standard 里的旧 SKILL.md、
# README.md 和门禁脚本用 gh api 推回本仓库。那会覆盖指针，把这里变回一套
# 平行的、只含排版的技能，因此已停用。
#
# 不要从旧的 report-layout-standard 技能目录覆盖：
#   SKILL.md
#   README.md
# 排版细则与门禁脚本的权威文本在 company-research-skill：
#   references/layout-rules.md
#   scripts/终版排版验收.py   （--expect-pages N，不得写死 EXPECT_PAGES）
#   scripts/检测裸数字.py
# 公开副本只从那份技能同步，且不得覆盖上面两个指针文件。
set -euo pipefail

echo "已停止：本脚本不再把旧的 report-layout-standard 技能推回本仓库。" >&2
echo "唯一来源是「公司课题研究」：https://github.com/99dj464r56-cloud/company-research-skill" >&2
echo "SKILL.md 与 README.md 是指针，不得被旧排版技能覆盖。" >&2
exit 1
