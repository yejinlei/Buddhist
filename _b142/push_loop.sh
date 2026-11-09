#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
for i in $(seq 1 10); do
  echo "=== attempt $i $(date +%T) ==="
  timeout 90 git push origin main 2>&1 && { echo PUSH_OK; break; }
  timeout 60 git fetch origin 2>&1 | tail -2
  timeout 60 git merge origin/main --no-edit 2>&1 | tail -3
  sleep 15
done
echo "=== done $(date +%T) ==="
