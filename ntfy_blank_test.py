import paramiko
HOST='185.182.121.45'; USER='root'; PASS='YOUR-PASSWORD'; PORT=22
ssh=paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()); ssh.connect(HOST,PORT,USER,PASS,timeout=15)
# 1) apel fara mesaj (nu trebuie sa trimita nimic)
ssh.exec_command('/usr/local/bin/ntfy_notify.sh')
# 2) apel cu mesaj clar
ssh.exec_command('echo "TEST: Filtru NTFY activ" | /usr/local/bin/ntfy_notify.sh')
ssh.close()
print('Trimis test: gol + mesaj explicit')
