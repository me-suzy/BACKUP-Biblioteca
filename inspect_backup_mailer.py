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
# show file
for c in [
    "ls -l /exlibris/backup/scripts/backup_mailer",
    "nl -ba /exlibris/backup/scripts/backup_mailer | sed -n '1,120p'",
]:
    stdin,stdout,stderr=ssh.exec_command(c)
    print(stdout.read().decode('utf-8','ignore'))

# run a test invoking backup_mailer similarly to success branch
cmd=(
    "setenv BACKUP_TYPE user_data; setenv ORACLE_SID ALEPH; setenv ERROR_NUMBER 00; setenv ERROR_MESSAGE 'End user_data backup test'; "
    "/bin/csh -f /exlibris/backup/scripts/backup_mailer user_data 00 || true"
)
stdin,stdout,stderr=ssh.exec_command(cmd)
print(stdout.read().decode('utf-8','ignore') or stderr.read().decode('utf-8','ignore'))
ssh.close()
