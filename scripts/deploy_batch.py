# -*- coding: utf-8 -*-
"""批量 API 部署（带节流，避免触发 GitHub 二级写限流）。
用法：python3 scripts/deploy_batch.py <file1> <file2> ...
日志：stdout（可用 nohup 重定向）。
"""
import base64, json, os, re, subprocess, sys, time, urllib.request, urllib.error


def sh(*a):
    return subprocess.check_output(list(a)).decode("utf-8", "replace")


def api(path, method="GET", data=None, token=None):
    req = urllib.request.Request(
        "https://api.github.com" + path, method=method,
        data=json.dumps(data).encode() if data is not None else None,
        headers={"Authorization": "token " + token,
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "buddhist-deploy"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            b = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(b) if b else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:200]
    except Exception as e:
        return 0, str(e)[:200]


def main():
    root = sh("git", "rev-parse", "--show-toplevel").strip()
    os.chdir(root)
    url = sh("git", "remote", "get-url", "origin").strip()
    cred = re.search(r"://([^:]+):([^@]+)@", url)
    repo_m = re.search(r"github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$", url)
    token = cred.group(2)
    repo = f"{repo_m.group(1)}/{repo_m.group(2)}"
    files = [f.strip() for f in sys.argv[1:] if f.strip()]
    ok, fail = [], []
    for idx, f in enumerate(files, 1):
        rel = os.path.relpath(os.path.abspath(f), root)
        content = base64.b64encode(open(f, "rb").read()).decode()
        done = False
        for attempt in range(3):
            st, cur = api(f"/repos/{repo}/contents/{rel}?ref=main", token=token)
            sha = cur.get("sha") if isinstance(cur, dict) else None
            payload = {"message": f"deploy {rel}", "content": content, "branch": "main"}
            if sha:
                payload["sha"] = sha
            st2, r2 = api(f"/repos/{repo}/contents/{rel}", method="PUT", data=payload, token=token)
            if st2 in (200, 201):
                print(f"[{idx}/{len(files)}] OK {rel}", flush=True)
                ok.append(rel); done = True; break
            print(f"[{idx}/{len(files)}] retry({attempt+1}) {rel} st={st2} {str(r2)[:80]}", flush=True)
            time.sleep(3)
        if not done:
            print(f"[{idx}/{len(files)}] FAIL {rel}", flush=True); fail.append(rel)
        time.sleep(0.7)
    print(f"=== 完成 成功{len(ok)} 失败{len(fail)} ===", flush=True)
    if fail:
        print("失败:", " ".join(fail), flush=True)


if __name__ == "__main__":
    main()
