#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
for i in $(seq 1 8); do
  echo "== attempt $i =="
  timeout 110 git push origin main 2>&1 | tail -3
  if [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main 2>/dev/null)" ]; then echo PUSH_OK; break; fi
  timeout 60 git fetch origin main 2>&1 | tail -1
  sleep 15
done
echo "== final =="; git log --oneline -1; git status -sb | head -1
