import paramiko
h='185.182.121.45';u='root';p='YOUR-PASSWORD'
ssh=paramiko.SSHClient();ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy());ssh.connect(h,22,u,p,timeout=15)
script='''#!/bin/bash
SUM="/exlibris/backup/logs/Summary.log"
NTFY="/usr/local/bin/ntfy_notify.sh"
# extrage ultimele doua inregistrari complete (user_data si ora_cold)
MSG=
[ -n "" ] && echo "" | 
'''
ssh.exec_command("cat > /usr/local/bin/backup_summary_ntfy.sh <<'EOF'\n"+script+"\nEOF")
ssh.exec_command('chmod +x /usr/local/bin/backup_summary_ntfy.sh')
# adaug cron la 03:10 daca nu exista
ssh.exec_command("(crontab -l 2>/dev/null | grep -v backup_summary_ntfy; echo '10 3 * * * /usr/local/bin/backup_summary_ntfy.sh >/dev/null 2>&1') | crontab -")
ssh.close()
print('Summary NTFY cron setat la 03:10.')
