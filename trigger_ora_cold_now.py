import os, paramiko

CFG = "CONFIG_FINAL_29OCT.txt"

def read_cfg():
    c={}
    with open(CFG,'r',encoding='utf-8',errors='ignore') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k,v=line.split('=',1)
            c[k.strip().upper()]=v.strip().strip("\"')")
    return c

cfg=read_cfg()
ssh=paramiko.SSHClient();ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(cfg['HOST'],username=cfg['USER'],password=cfg['PASSWORD'],port=int(cfg.get('PORT','22') or 22),timeout=30)
# start ora_cold in background
stdin,stdout,stderr=ssh.exec_command("/bin/date +%Y%m%d_%H%M%S")
ts=stdout.read().decode().strip()
log=f"/exlibris/backup/logs/manual_backup_{ts}.log"
cmd=("cd /exlibris/backup/scripts && "
     f"nohup /bin/csh exec_backup_main a1 > {log} 2>&1 & echo $!\n")
stdin,stdout,stderr=ssh.exec_command(cmd)
pid=stdout.read().decode().strip().splitlines()[-1] if stdout else ''
print(f"Started a1 pid={pid} log={log}")
ssh.close()
