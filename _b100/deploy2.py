import subprocess,time,sys
budget=float(sys.argv[1]); files=sys.argv[2:]
deadline=time.time()+budget
pending=list(files); done=[]
while pending and time.time()<deadline:
    for f in list(pending):
        if time.time()>=deadline: break
        r=subprocess.run(['timeout','14','python3','scripts/deploy_contents.py',f],capture_output=True,text=True)
        if r.returncode==0 and '失败 0' in (r.stdout+r.stderr):
            pending.remove(f); done.append(f); print('OK',f,flush=True)
    if pending: time.sleep(1)
print('已完成:',done,flush=True)
print('待续:',pending,flush=True)
