#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
for i in $(seq 1 10); do
  echo "=== round $i $(date +%H:%M:%S) ==="
  git fetch origin main 2>&1 | tail -1
  git merge origin/main --no-edit -X ours 2>&1 | tail -2
  out=$(git push origin HEAD:main 2>&1); echo "$out" | tail -3
  if echo "$out" | grep -qiE 'pre-receive|rejected|error|fatal|timed out|Connection|TLS'; then
    echo "retry..."; sleep 15
  else
    echo "PUSH_DONE"; break
  fi
done
git rev-list --left-right --count origin/main...HEAD
