#!/bin/bash
cd /home/user/workspace/13511660557912876654/buddhist-ontology
for i in $(seq 1 8); do
  echo "== attempt $i =="
  git fetch origin main 2>&1 | tail -2
  b=$(git rev-list --count HEAD..origin/main 2>/dev/null)
  echo "behind=$b"
  if [ "$b" -gt 0 ]; then
    git merge origin/main --no-edit -m "merge remote ($i)" 2>&1 | tail -4
    if [ -f .git/MERGE_HEAD ]; then echo "MERGE_CONFLICT"; break; fi
  fi
  out=$(git push origin HEAD:main 2>&1)
  echo "$out" | tail -3
  if echo "$out" | grep -qE "-> main|Everything up-to-date"; then
    echo "PUSH_OK"; break
  fi
  echo "PUSH_RETRY$i"; sleep 20
done
echo "== final =="
git log --oneline -1
git status -sb | head -3
