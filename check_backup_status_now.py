#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica status backup si loguri acum
"""

import paramiko
import sys
from datetime import datetime

HOST = "185.182.121.45"
USER = "root"
PASS = "YOUR-PASSWORD"
PORT = 22

def ssh_exec(ssh, cmd, show=True, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    if show:
        if out:
            print(out)
        if err and "warning" not in err.lower():
            print(f"[WARN] {err}")
    return out, err


def main():
    print("=" * 70)
    print("   VERIFICARE STATUS BACKUP - 29 OCT 00:44")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica procese exec_backup_main
        print("[1/6] Verific procese exec_backup_main active...")
        print()
        out, _ = ssh_exec(ssh, "ps aux | grep exec_backup_main | grep -v grep")
        if not out.strip():
            print("[OK] Nu exista procese backup active")
        else:
            print("[!] EXISTA PROCESE BACKUP ACTIVE!")
            print(out)
        print()
        
        # 2. Verifica logurile recente
        print("[2/6] Verific loguri backup din ultimele ore...")
        print()
        ssh_exec(ssh, "ls -lht /exlibris/backup/logs/ | head -10")
        print()
        
        # 3. Cauta mesaje in loguri de azi
        print("[3/6] Cauta in loguri mesaje de azi (28 oct)...")
        print()
        ssh_exec(ssh, "grep -l '28/10/2025\\|Oct 28' /exlibris/backup/logs/*.log 2>/dev/null | head -5", timeout=30)
        print()
        
        # 4. Verifica backup_mailer pentru erori
        print("[4/6] Verifica daca backup_mailer a rulat...")
        print()
        ssh_exec(ssh, "grep -i 'backup_mailer' /var/log/cron 2>/dev/null | tail -10", timeout=30)
        print()
        
        # 5. Verifica log sistem pentru erori
        print("[5/6] Verifica log sistem pentru erori cron recente...")
        print()
        ssh_exec(ssh, "tail -50 /var/log/messages 2>/dev/null | grep -i cron", timeout=20)
        print()
        
        # 6. Verifica daca NTFY a fost apelat
        print("[6/6] Verifica ultimele apeluri la scriptul NTFY...")
        print()
        ssh_exec(ssh, "grep -i 'ntfy_notify' /var/log/*.log 2>/dev/null | tail -5", timeout=20)
        print()
        
        # 7. Verifica cron jobs active
        print("[INFO] Cron jobs active pentru backup:")
        print()
        ssh_exec(ssh, "crontab -l")
        print()
        
        ssh.close()
        print()
        print("=" * 70)
        print("VERIFICARE FINALIZATA")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

