#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
for f in data/modern-translation/t2783.json data/modern-translation/t1136.json \
         data/modern-translation/t2817.json data/modern-translation/t2841.json \
         data/modern-translation/t1186.json pages/sutras.html PROGRESS.md; do
  for try in 1 2 3; do
    out=$(python3 scripts/deploy_contents.py "$f" 2>&1)
    echo "$out" | tail -1
    if echo "$out" | grep -q "^OK"; then break; fi
    echo "  retry $try for $f"; sleep 3
  done
done
echo "ALL-DONE"
