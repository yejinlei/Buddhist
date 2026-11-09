#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
for i in $(seq 1 20); do
  echo "== push round $i $(date +%T) =="
  timeout 120 git push origin HEAD:main 2>&1 | tail -2
  if [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ]; then echo PUSH_OK; break; fi
  timeout 150 git fetch origin main 2>&1 | tail -1
  timeout 90 git merge origin/main --no-edit 2>&1 | tail -1
  sleep 10
done
echo DONE
