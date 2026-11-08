#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
for i in 1 2 3 4 5; do
  echo "=== attempt $i ==="
  if git push origin HEAD:main 2>&1; then echo "PUSH_OK"; break; fi
  sleep 5
done
