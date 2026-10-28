#!/bin/bash
# 修正版：分批提交并推送大正藏经文 JSON（每批 120 部）
# 修复上一版 bug：ls 输出自带 sutras/ 前缀，二次加前缀导致 git add 路径不存在而静默失败
set -u
cd "$(dirname "$0")/.."
LOG=push_sutras2.log
: > "$LOG"
say(){ echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

git config http.postBuffer 524288000
git config http.version HTTP/1.1
git config http.lowSpeedLimit 0
git config http.lowSpeedTime 999999

# 恢复被误删的旧版 JSON
git checkout -- sutras/ 2>>"$LOG" || true
say "已恢复工作区旧文件"

wait_git(){
  local t=0
  while ! timeout 25 git ls-remote origin HEAD >/dev/null 2>&1; do
    t=$((t+1)); say "  github 暂不可达，等待第 $t 次"; sleep 15
    [ $t -ge 20 ] && return 1
  done
  return 0
}

push_retry(){
  local i=1
  while [ $i -le 8 ]; do
    if timeout 400 git push >>"$LOG" 2>&1; then say "  ✅ 推送成功"; return 0; fi
    say "  ✗ 推送失败，重试 $i/8"; i=$((i+1)); sleep 10
    wait_git || return 1
  done
  return 1
}

wait_git || { say "github 长时间不可达，退出"; exit 1; }

git ls-files -o --exclude-standard sutras/ | grep -E '^sutras/t[0-9].*\.json$' | sort > /tmp/sutras_untracked.txt
TOTAL=$(wc -l < /tmp/sutras_untracked.txt)
say "待提交经文: $TOTAL 部"

split -l 120 -d -a 3 /tmp/sutras_untracked.txt /tmp/sj_
i=0
for f in /tmp/sj_*; do
  i=$((i+1))
  N=$(wc -l < "$f")
  mapfile -t arr < "$f"
  if ! git add -- "${arr[@]}" 2>>"$LOG"; then say "批次 $i add 失败"; continue; fi
  if git diff --cached --quiet; then say "批次 $i 无变更，跳过"; continue; fi
  git commit -q -m "🚀 大正藏经文库入库 第${i}批（${N}部）" || { say "批次 $i commit 失败"; continue; }
  say "批次 ${i}: ${N} 部，推送中"
  if ! push_retry; then say "  !! 批次 ${i} 推送最终失败，停止"; break; fi
done

git add -- sutras/index.json 2>>"$LOG" || true
if ! git diff --cached --quiet; then
  git commit -q -m "✅ 大正藏经文库索引更新"
  push_retry || say "  !! 收尾推送失败"
fi
say "=== 完成，本地未推送提交: $(git rev-list --count origin/main..HEAD) ==="
