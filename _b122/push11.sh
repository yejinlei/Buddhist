#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
for i in $(seq 1 8); do
  echo "=== round $i $(date +%H:%M:%S) ==="
  git fetch origin main 2>&1 | tail -2
  git merge origin/main --no-edit -X ours 2>&1 | tail -3
  if git push origin HEAD:main 2>&1 | tail -3; then
    if git rev-list --left-right --count origin/main...HEAD | grep -q '^0\s*0$'; then
      echo "PUSH_OK"; break
    fi
  fi
  echo "retry..."; sleep 20
done
git rev-list --left-right --count origin/main...HEAD
