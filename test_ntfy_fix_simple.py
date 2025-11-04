#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test simplu NTFY fixat cu timeout mai mare
"""

import paramiko
import sys

HOST = "185.182.121.45"
USER = "root"
PASS = "YOUR-PASSWORD"
PORT = 22

def main():
    print("=" * 70)
    print("   TEST NTFY FIXAT")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        print("Test 1: cu argument...")
        stdin, stdout, stderr = ssh.exec_command("/usr/local/bin/ntfy_notify.sh 'BACKUP FIX - Argument test'", timeout=30)
        out = stdout.read().decode("utf-8", errors="ignore")
        print(out)
        print()
        
        print("Test 2: cu pipe stdin...")
        stdin, stdout, stderr = ssh.exec_command("echo 'BACKUP FIX - Pipe stdin test' | /usr/local/bin/ntfy_notify.sh", timeout=30)
        out = stdout.read().decode("utf-8", errors="ignore")
        print(out)
        print()
        
        print("Test 3: comanda exacta din backup_mailer...")
        cmd = """bash -c 'echo "BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: $(date "+%Y-%m-%d %H:%M:%S") | STATUS: End FULL backup TEST FINAL" | /usr/local/bin/ntfy_notify.sh'"""
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
        out = stdout.read().decode("utf-8", errors="ignore")
        print(out)
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("TEST FINALIZAT")
        print("=" * 70)
        print()
        print("Verifica telefonul pentru toate cele 3 notificari!")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

