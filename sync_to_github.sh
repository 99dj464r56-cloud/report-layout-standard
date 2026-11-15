#!/bin/bash
# 同步 report-layout-standard 到 GitHub（单一来源）
# 用 gh api 走 contents 接口，绕过 git push 在本机网络环境下的限制。
# 用法：bash sync_to_github.sh [提交说明]
set -e

REPO="99dj464r56-cloud/report-layout-standard"
SKILL_DIR="$HOME/.workbuddy/skills/report-layout-standard"
MSG="${1:-sync: 更新排版规范}"

cd "$SKILL_DIR"

for f in README.md SKILL.md "scripts/终版排版验收.py" "scripts/检测裸数字.py"; do
  # 取当前文件的 sha（若已存在）
  sha=$(gh api "repos/$REPO/contents/$f" --jq '.sha' 2>/dev/null || true)
  content=$(base64 < "$f" | tr -d '\n')
  if [ -n "$sha" ]; then
    gh api -X PUT "repos/$REPO/contents/$f" \
      -f message="$MSG" -f content="$content" -f sha="$sha" --jq '.content.path' 2>/dev/null
  else
    gh api -X PUT "repos/$REPO/contents/$f" \
      -f message="$MSG" -f content="$content" --jq '.content.path' 2>/dev/null
  fi
  echo "✓ 已同步 $f"
done
echo "完成：$REPO"
