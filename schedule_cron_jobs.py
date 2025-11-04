import paramiko

CFG='CONFIG_FINAL_29OCT.txt'

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
# create root crontab lines idempotently
cron_lines=[
    "00 22 * * * /exlibris/backup/scripts/exec_backup_main a5 >> /exlibris/backup/logs/cron_a5.log 2>&1",
    "00 23 * * * /exlibris/backup/scripts/exec_backup_main a1 >> /exlibris/backup/logs/cron_a1.log 2>&1",
]
cmd=(
    "(crontab -l 2>/dev/null | grep -v 'exec_backup_main a5' ; echo '{l1}') | crontab -; ".format(l1=cron_lines[0])+
    "(crontab -l 2>/dev/null | grep -v 'exec_backup_main a1' ; echo '{l2}') | crontab -; crontab -l".format(l2=cron_lines[1])
)
stdin,stdout,stderr=ssh.exec_command(cmd)
print(stdout.read().decode('utf-8','ignore'))
ssh.close()
