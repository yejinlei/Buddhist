#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
OLD=a6944b5ddbb5d8a2945061847552636c64f51c47
for i in $(seq 1 15); do
  echo "== round $i $(date +%T) =="
  timeout 150 git fetch origin main 2>&1 | tail -1
  NEW=$(git rev-parse origin/main 2>/dev/null)
  echo "origin/main=$NEW"
  if [ "$NEW" != "$OLD" ]; then
    echo "FETCH_GOT_REMOTE -> merge & push"
    timeout 90 git merge origin/main --no-edit 2>&1 | tail -3
    timeout 150 git push origin HEAD:main 2>&1 | tail -3
    if [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ]; then echo PUSH_OK; break; fi
  fi
  sleep 15
done
echo ALL_DONE
