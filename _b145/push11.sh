cd /home/user/workspace/13511660557912876654/buddhist-ontology
for i in $(seq 1 10); do
  git fetch origin -q 2>/dev/null
  git merge origin/main -X ours --no-edit -q 2>/dev/null
  if git push origin HEAD:main 2>&1 | tail -2; then
    if git rev-parse HEAD | grep -q "$(git rev-parse origin/main)"; then echo PUSH_OK; exit 0; fi
  fi
  echo "retry $i"; sleep 20
done
echo PUSH_FAIL
