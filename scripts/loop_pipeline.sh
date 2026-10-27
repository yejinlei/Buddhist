#!/bin/bash
cd "$(dirname "$0")/.."

echo "=== 循环全量处理开始 $(date) ===" >> loop.log

BATCH=1
while true; do
    echo "=== 第$BATCH批开始 $(date) ===" >> loop.log
    
    # 1. 下载50部
    python3 scripts/pipeline_full.py download 50 2>&1 | tail -20 >> loop.log
    
    # 2. 解析所有已下载未解析的
    python3 scripts/pipeline_full.py parse 2>&1 | tail -20 >> loop.log
    
    # 3. 重建索引
    python3 scripts/pipeline_full.py index 2>&1 | tail -5 >> loop.log
    
    # 4. 统计当前进度
    DOWNLOADED=$(ls .xmlcache/*.xml 2>/dev/null | wc -l)
    PARSED=$(ls sutras/n*.json 2>/dev/null | wc -l)
    echo "进度：已下载 $DOWNLOADED / 2459，已解析入库 $PARSED 部" >> loop.log
    
    # 5. 提交推送
    if [ $PARSED -gt 0 ]; then
        git add sutras/ 2>&1 >> loop.log
        if ! git diff --cached --quiet; then
            git commit -m "🚀 第$BATCH批：大正藏佛经批量入库，当前累计$PARSED部" 2>&1 >> loop.log
            git push 2>&1 >> loop.log
            echo "提交推送完成" >> loop.log
        fi
    fi
    
    # 检查是否全部完成
    if [ $DOWNLOADED -ge 2459 ] && [ $PARSED -ge 2459 ]; then
        echo "=== 全部完成！共$PARSED部经入库 $(date) ===" >> loop.log
        git add sutras/
        git commit -m "✅ 大正藏全量2459部经全部完成入库"
        git push
        break
    fi
    
    BATCH=$((BATCH+1))
    sleep 15
done
