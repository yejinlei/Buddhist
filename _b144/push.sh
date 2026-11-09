#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
for i in $(seq 1 10); do
  echo "=== attempt $i ==="
  if git push origin main 2>&1; then echo "PUSH_OK"; exit 0; fi
  git fetch origin main 2>&1 | tail -1
  git merge origin/main --no-edit 2>&1 | tail -2
  sleep 20
done
echo "PUSH_FAIL"
