#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Trimite test NTFY acum
"""

import paramiko

HOST = "185.182.121.45"
USER = "root"
PASS = "YOUR-PASSWORD"
PORT = 22

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, PORT, USER, PASS, timeout=15)

print("Trimit test NTFY...")
stdin, stdout, stderr = ssh.exec_command("/usr/local/bin/ntfy_notify.sh 'Test urgent - 23:49 - Backup in desfasurare!'")
out = stdout.read().decode("utf-8", errors="ignore")
print(out)

ssh.close()
print("\n[OK] Mesaj trimis!")

