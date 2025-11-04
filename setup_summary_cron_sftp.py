import paramiko
h='185.182.121.45';u='root';p='YOUR-PASSWORD'
ssh=paramiko.SSHClient();ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy());ssh.connect(h,22,u,p,timeout=15)
sftp=ssh.open_sftp()
script='''#!/bin/bash
SUM="/exlibris/backup/logs/Summary.log"
NTFY="/usr/local/bin/ntfy_notify.sh"
MSG=$(awk '/^Start/{blk=$0;next}/^  End/{print blk"\n"$0}' "$SUM" | tail -4)
[ -n "$MSG" ] && echo "$MSG" | $NTFY
'''
f=sftp.open('/usr/local/bin/backup_summary_ntfy.sh','w'); f.write(script); f.close()
ssh.exec_command('chmod +x /usr/local/bin/backup_summary_ntfy.sh')
ssh.exec_command("(crontab -l 2>/dev/null | grep -v backup_summary_ntfy; echo '10 3 * * * /usr/local/bin/backup_summary_ntfy.sh >/dev/null 2>&1') | crontab -")
ssh.close()
print('Summary NTFY cron setat la 03:10 (scris via SFTP).')
