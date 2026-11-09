#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
for i in $(seq 1 12); do
  echo "=== attempt $i $(date +%T) ==="
  timeout 60 git fetch origin main 2>&1 | tail -1
  timeout 60 git merge origin/main --no-edit 2>&1 | tail -2
  if timeout 90 git push origin HEAD:main 2>&1 | tail -2; then
    if [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ]; then echo PUSH_OK; break; fi
  fi
  sleep 20
done
echo ALL_DONE
