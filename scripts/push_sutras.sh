#!/bin/bash
# 大正藏经文 JSON 分批提交推送（每批 200 部），规避单次过大导致 408
set -u
cd "$(dirname "$0")/.."
LOG=push_sutras.log
: > "$LOG"
say(){ echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

git config http.postBuffer 524288000
git config http.version HTTP/1.1
git config http.lowSpeedLimit 0
git config http.lowSpeedTime 999999

push_retry(){
  local i=1
  while [ $i -le 6 ]; do
    if git push >>"$LOG" 2>&1; then say "  推送成功"; return 0; fi
    say "  推送失败，重试 $i/6"; i=$((i+1)); sleep 8
  done
  return 1
}

ls sutras/t*.json | sort > /tmp/all_json.txt
split -l 200 -d -a 3 /tmp/all_json.txt /tmp/sc_
i=0
for f in /tmp/sc_*; do
  i=$((i+1))
  N=$(wc -l < "$f")
  git add $(sed 's#^#sutras/#' "$f") sutras/index.json >/dev/null 2>&1
  if git diff --cached --quiet; then say "批次 $i 无变更，跳过"; continue; fi
  git commit -q -m "🚀 大正藏经文库入库 第${i}批"
  say "批次 ${i}: ${N} 部，推送中"
  push_retry || say "  !! 批次 ${i} 最终失败"
done

git add sutras/index.json >/dev/null 2>&1
if ! git diff --cached --quiet; then
  git commit -q -m "✅ 大正藏经文库索引更新"
  push_retry || say "  !! 收尾推送失败"
fi
say "=== 完成，本地未推送数: $(git rev-list --count origin/main..HEAD) ==="
