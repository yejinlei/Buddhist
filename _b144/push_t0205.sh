#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
for i in $(seq 1 8); do
  echo "== attempt $i =="
  if timeout 90 git fetch origin main 2>&1 | tail -2; then :; fi
  git merge origin/main --no-edit -q 2>&1 | tail -2
  if timeout 110 git push origin main 2>&1 | tail -3; then
    if git rev-parse HEAD | grep -q "$(git rev-parse origin/main 2>/dev/null)"; then
      echo PUSH_OK; break
    fi
  fi
  sleep 20
done
echo "== final =="; git log --oneline -2; git status -sb | head -1
