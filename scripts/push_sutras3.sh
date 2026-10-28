#!/bin/bash
# 大正藏经文分批入库（小批次 60 部 + 无限重试，适应 github 时通时断）
set -u
cd "$(dirname "$0")/.."
LOG=push3.log
: > "$LOG"
say(){ echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

git config http.postBuffer 524288000
git config http.version HTTP/1.1
git config http.lowSpeedLimit 0
git config http.lowSpeedTime 999999

git checkout -- sutras/ 2>>"$LOG" || true

CHUNK=200
round=0
MAXROUND=1000
last_push_ok=0

while [ $round -lt $MAXROUND ]; do
  round=$((round+1))

  # 1) 有待推送提交则先推送
  if [ "$(git rev-list --count origin/main..HEAD)" -gt 0 ]; then
    if timeout 240 git push >>"$LOG" 2>&1; then
      last_push_ok=$round
      say "✅ 推送成功（已同步到远程）"
    else
      say "✗ 推送失败，20s 后重试"
      sleep 8
      continue
    fi
  fi

  # 2) 收集未跟踪经文
  git ls-files -o --exclude-standard sutras/ | grep -E '^sutras/t[0-9].*\.json$' | sort > /tmp/su.txt
  N=$(wc -l < /tmp/su.txt)
  if [ "$N" -eq 0 ]; then
    git add -- sutras/index.json 2>>"$LOG" || true
    if ! git diff --cached --quiet; then
      git commit -q -m "✅ 大正藏经文库索引更新"
      continue
    fi
    say "🎉 全部经文已提交并推送完成"
    break
  fi

  # 3) 提交一小批
  head -n $CHUNK /tmp/su.txt > /tmp/su_chunk.txt
  mapfile -t arr < /tmp/su_chunk.txt
  if ! git add -- "${arr[@]}" 2>>"$LOG"; then say "add 失败，重试"; sleep 5; continue; fi
  if git diff --cached --quiet; then say "无变更，继续"; continue; fi
  if ! git commit -q -m "🚀 大正藏经文库入库（${#arr[@]}部）"; then say "commit 失败"; sleep 5; continue; fi
  say "已提交 ${#arr[@]} 部，剩余未跟踪 $((N-${#arr[@]})) 部，准备推送"
done

say "=== 结束：未推送提交 $(git rev-list --count origin/main..HEAD) | 已跟踪经文 $(git ls-files sutras/ | wc -l) ==="
