#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过 GitHub REST API 部署仓库。

用途：当执行环境无法直连 github.com:443（git push 超时）时，改用 GitHub
官方 API 通道发布。做法是把本地 HEAD 的完整文件树与远程 main 分支对齐：
内容哈希相同的文件跳过上传，只上传有差异/新增的文件，并把远程多出的文件删除，
最后在远程生成一个与本地工作区一致的提交。

用法：
    python3 scripts/deploy_api.py            # 部署当前 HEAD
    python3 scripts/deploy_api.py --dry-run  # 只列出差异，不推送

凭据从 git remote origin 的 URL 中读取（https://<user>:<token>@github.com/...），
不会打印到输出中。
"""

import base64
import http.client
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

API = "https://api.github.com"


def sh(*args):
    return subprocess.check_output(list(args)).decode("utf-8", "replace")


def api(path, method="GET", data=None, token=None, timeout=180):
    req = urllib.request.Request(
        API + path,
        method=method,
        data=json.dumps(data).encode() if data is not None else None,
        headers={
            "Authorization": "token " + token,
            "Accept": "application/vnd.github+json",
            "User-Agent": "buddhist-ontology-deploy",
        },
    )
    last_err = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                total = resp.length  # Content-Length, may be None
                chunks = []
                read = 0
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    read += len(chunk)
                body = b"".join(chunks)
                if total and read < total:
                    # 未读完
                    raise http.client.IncompleteRead(body, total - read)
                text = body.decode("utf-8", "replace")
                return resp.status, (json.loads(text) if text else None)
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")[:400]
        except (http.client.IncompleteRead, TimeoutError, socket.timeout, urllib.error.URLError, ConnectionError, json.JSONDecodeError) as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
            continue
    return 0, str(last_err)


def local_tree():
    """返回 {路径: git blob sha}，对应 HEAD 的完整文件树。"""
    out = sh("git", "ls-tree", "-r", "-z", "HEAD")
    tree = {}
    for item in out.split("\0"):
        if not item:
            continue
        meta, path = item.split("\t", 1)
        mode, otype, sha = meta.split()
        if otype == "blob":
            tree[path] = {"sha": sha, "mode": "100755" if mode == "100755" else "100644"}
    return tree


def main():
    dry = "--dry-run" in sys.argv
    root = sh("git", "rev-parse", "--show-toplevel").strip()
    os.chdir(root)

    url = sh("git", "remote", "get-url", "origin").strip()
    cred = re.search(r"://([^:]+):([^@]+)@", url)
    repo_m = re.search(r"github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$", url)
    if not cred or not repo_m:
        sys.exit("无法从 origin 地址解析出用户名/令牌或仓库名")
    token, owner, repo = cred.group(2), repo_m.group(1), repo_m.group(2)

    status, info = api(f"/repos/{owner}/{repo}", token=token, timeout=30)
    if status != 200:
        sys.exit(f"仓库不可访问（{status}）：{info}")
    branch = info.get("default_branch", "main")

    status, ref = api(f"/repos/{owner}/{repo}/git/ref/heads/{branch}", token=token)
    if status != 200:
        sys.exit(f"读取分支失败（{status}）：{ref}")
    remote_sha = ref["object"]["sha"]

    status, rcommit = api(f"/repos/{owner}/{repo}/git/commits/{remote_sha}", token=token)
    base_tree = rcommit["tree"]["sha"]

    status, rtree = api(f"/repos/{owner}/{repo}/git/trees/{base_tree}?recursive=1", token=token)
    remote_files = {
        t["path"]: t["sha"]
        for t in rtree.get("tree", [])
        if t["type"] == "blob"
    }

    locals_ = local_tree()

    changed = [p for p, v in locals_.items() if remote_files.get(p) != v["sha"]]
    removed = [p for p in remote_files if p not in locals_]

    print(f"仓库：{owner}/{repo}  分支：{branch}")
    print(f"远程 HEAD：{remote_sha[:10]}  本地 HEAD：{sh('git','rev-parse','HEAD').strip()[:10]}")
    print(f"需上传：{len(changed)} 个   需删除：{len(removed)} 个")
    for p in sorted(changed)[:20]:
        print("   +", p)
    if len(changed) > 20:
        print(f"   ...（其余 {len(changed)-20} 个）")
    for p in sorted(removed)[:20]:
        print("   -", p)

    if not changed and not removed:
        print("远程与本地一致，无需部署。")
        return
    if dry:
        print("（--dry-run，未推送）")
        return

    # 断点续传：进度文件记录 path -> {gitsha, blobsha}
    prog_path = ".deploy_progress.json"
    prog = {}
    if os.path.exists(prog_path):
        try:
            prog = json.load(open(prog_path, encoding="utf-8"))
        except Exception:
            prog = {}
    max_blobs = None
    for i, a in enumerate(sys.argv):
        if a == "--max-blobs" and i + 1 < len(sys.argv):
            max_blobs = int(sys.argv[i + 1])

    def _need(p):
        rec = prog.get(p)
        return not (rec and rec.get("gitsha") == locals_[p]["sha"])

    todo = [p for p in sorted(changed) if _need(p)]
    pending = 0
    if max_blobs is not None and len(todo) > max_blobs:
        pending = len(todo) - max_blobs
        todo = todo[:max_blobs]

    from concurrent.futures import ThreadPoolExecutor, as_completed

    def _up(p):
        try:
            content = open(p, "rb").read()
            status, blob = api(
                f"/repos/{owner}/{repo}/git/blobs",
                "POST",
                {"content": base64.b64encode(content).decode(), "encoding": "base64"},
                token=token,
                timeout=600,
            )
            return p, status, blob
        except Exception as e:
            return p, 0, str(e)

    uploaded = 0
    failed = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(_up, p) for p in todo]
        for f in as_completed(futs):
            p, status, blob = f.result()
            if status in (200, 201):
                prog[p] = {"gitsha": locals_[p]["sha"], "blobsha": blob["sha"]}
                uploaded += 1
            else:
                failed.append((p, status))
            if uploaded and uploaded % 100 == 0:
                json.dump(prog, open(prog_path, "w", encoding="utf-8"))
    json.dump(prog, open(prog_path, "w", encoding="utf-8"))
    if failed:
        print("部分上传失败：", failed[:5])

    items = []
    for p in sorted(changed):
        rec = prog.get(p)
        if rec and rec.get("gitsha") == locals_[p]["sha"]:
            items.append({"path": p, "mode": locals_[p]["mode"], "type": "blob", "sha": rec["blobsha"]})
    for p in sorted(removed):
        items.append({"path": p, "mode": "100644", "type": "blob", "sha": None})

    done = len(items)
    total = len(changed) + len(removed)
    print(f"本轮上传 {uploaded} 个；累计 {done}/{total}。")
    if pending or failed or done < total:
        print("尚未完成（等待续传上传），请再次运行。")
        return

    max_entries = None
    for i, a in enumerate(sys.argv):
        if a == "--max-entries" and i + 1 < len(sys.argv):
            max_entries = int(sys.argv[i + 1])
    truncated = False
    if max_entries and len(items) > max_entries:
        items = items[:max_entries]
        truncated = True

    status, tree = api(
        f"/repos/{owner}/{repo}/git/trees",
        "POST",
        {"base_tree": base_tree, "tree": items},
        token=token,
    )
    if status not in (200, 201):
        sys.exit(f"创建 tree 失败（{status}）：{tree}")

    message = sh("git", "log", "-1", "--pretty=%B", "HEAD").strip() or "deploy via API"
    status, commit = api(
        f"/repos/{owner}/{repo}/git/commits",
        "POST",
        {"message": message, "tree": tree["sha"], "parents": [remote_sha]},
        token=token,
    )
    if status not in (200, 201):
        sys.exit(f"创建提交失败（{status}）：{commit}")

    status, res = api(
        f"/repos/{owner}/{repo}/git/refs/heads/{branch}",
        "PATCH",
        {"sha": commit["sha"]},
        token=token,
    )
    if status not in (200, 201):
        sys.exit(f"更新分支失败（{status}）：{res}")

    print(f"✅ 已提交，远程提交：{commit['sha']}")
    if truncated:
        print(f"   本轮提交 {len(items)}/{total} 个文件，请再次运行继续剩余部分。")
    else:
        print("   ✅ 全部文件部署完成。")


if __name__ == "__main__":
    main()
