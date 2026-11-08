import subprocess,time,sys
files=sys.argv[1:]
pending=list(files)
for attempt in range(3):
    if not pending: break
    nxt=[]
    for f in pending:
        r=subprocess.run(['timeout','9','python3','scripts/deploy_contents.py',f],capture_output=True,text=True)
        out=r.stdout+r.stderr
        if r.returncode==0 and '失败 0' in out:
            print('OK',f,flush=True)
        else:
            nxt.append(f)
    pending=nxt
    if pending: time.sleep(2)
print('PENDING',pending,flush=True)
