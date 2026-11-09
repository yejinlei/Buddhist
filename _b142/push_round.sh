#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
for i in $(seq 1 10); do
  echo "=== attempt $i $(date '+%H:%M:%S') ==="
  git fetch origin main 2>&1 | tail -2
  git merge origin/main --no-edit 2>&1 | tail -3
  if git push origin HEAD:main 2>&1 | tail -5; then
    echo "PUSH_DONE"
    break
  fi
  sleep 20
done
echo "=== final ==="
git rev-list --left-right --count HEAD...origin/main
