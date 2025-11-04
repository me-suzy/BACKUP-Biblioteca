import paramiko

CFG='CONFIG_FINAL_29OCT.txt'
TARGET='/exlibris/backup/scripts/exec_backup_main'

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
# backup and patch the BKP_STAT line to use tail -1
cmd=(
    f"cp {TARGET} {TARGET}.bak_$(date +%Y%m%d_%H%M%S); "
    f"perl -0777 -pe " + repr("s/set BKP_STAT =\s*`cat \$stat_file`/set BKP_STAT =  `tail -1 \$stat_file`/") + f" -i {TARGET}; "
    f"grep -n 'BKP_STAT' {TARGET} | sed -n '1,3p'"
)
stdin,stdout,stderr=ssh.exec_command(cmd)
print(stdout.read().decode('utf-8','ignore'))
ssh.close()
