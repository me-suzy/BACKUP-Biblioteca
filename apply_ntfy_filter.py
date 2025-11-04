import paramiko
HOST='185.182.121.45'; USER='root'; PASS='YOUR-PASSWORD'; PORT=22
ssh=paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()); ssh.connect(HOST,PORT,USER,PASS,timeout=15)
script='''#!/bin/bash
TOPIC="bariasi-5f07b8571f7c"
URL="https://ntfy.sh/"
# Citește din pipe dacă există, altfel din argument
if [ -p /dev/stdin ] || [ -s /dev/stdin ]; then
  MSG=""
else
  MSG=""
fi
# Curăță spații
MSG=""; MSG=""; MSG=""
# NU trimite dacă mesajul e gol sau exact textul fallback
if [ -z "" ] || [ "" = "Server notification" ]; then
  exit 0
fi
curl -fsS -X POST -d "" "" >/dev/null || exit 1
'''
cmd="cat > /usr/local/bin/ntfy_notify.sh <<'EOF'\n"+script+"\nEOF"
ssh.exec_command(cmd)
ssh.exec_command('chmod +x /usr/local/bin/ntfy_notify.sh')
ssh.close()
print('Updated ntfy_notify.sh with empty-message filter.')
