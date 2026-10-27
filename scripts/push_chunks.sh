#!/bin/bash
# 分批提交并推送大正藏经文库，规避单次推送过大导致的 HTTP 408
set -u
cd "$(dirname "$0")/.."
LOG=push_chunks.log
: > "$LOG"
say(){ echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

git config http.postBuffer 524288000
git config http.version HTTP/1.1
git config http.lowSpeedLimit 0
git config http.lowSpeedTime 999999
git config user.name "yejinlei"
git config user.email "yejinlei@users.noreply.github.com"

BASE=5fe6d56   # 远程当前 HEAD

say "=== 分批推送开始，基线 $BASE ==="

# 把此前的大提交折叠为未暂存改动，工作区不动
git reset --mixed "$BASE" >/dev/null 2>&1
say "已折叠历史提交，工作区保持完整"

push_retry(){
  local i=1
  while [ $i -le 4 ]; do
    git push >>"$LOG" 2>&1
    local rc=$?
    if [ $rc -eq 0 ]; then say "  推送成功"; return 0; fi
    say "  推送失败(rc=$rc)，重试 $i/4"; i=$((i+1)); sleep 6
  done
  return 1
}

# 1) 非经文文件（站点/脚本/数据）
git add -A -- . ':(exclude)sutras/' >/dev/null 2>&1
if ! git diff --cached --quiet; then
  git commit -q -m "chore: 站点与抓取脚本更新（分批入库流程）"
  say "已提交：站点与脚本"
  push_retry || say "  !! 站点提交推送失败"
fi

# 2) 经文 JSON 分批（每批 200 部）
ls sutras/t*.json | sort > /tmp/all_json.txt
TOTAL=$(wc -l < /tmp/all_json.txt)
say "待推送经文: $TOTAL 部"
split -l 200 -d -a 3 /tmp/all_json.txt /tmp/chunk_
i=0
for f in /tmp/chunk_*; do
  i=$((i+1))
  N=$(wc -l < "$f")
  git add $(sed 's#^#sutras/#' "$f") sutras/index.json >/dev/null 2>&1
  git commit -q -m "🚀 大正藏经文库入库 第${i}批（累计约 $((i*200)) 部）"
  say "批次 ${i}：提交 ${N} 部，开始推送"
  push_retry || say "  !! 批次 ${i} 推送失败"
done

# 3) 收尾（索引等）
git add sutras/index.json >/dev/null 2>&1
if ! git diff --cached --quiet; then
  git commit -q -m "✅ 大正藏索引更新"
  push_retry || say "  !! 收尾推送失败"
fi

say "=== 全部完成，本地未推送数: $(git rev-list --count origin/main..HEAD) ==="
