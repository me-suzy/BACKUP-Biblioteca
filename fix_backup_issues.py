#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix backup issues:
1. Check backup_mailer permissions
2. Check what backup actually ran
3. See if backup_mailer was called at all
"""

import paramiko
import sys

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
    print("   DIAGNOSTIC PROBLEME BACKUP")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        print("[1] Verific permisiuni backup_mailer...")
        print()
        ssh_exec(ssh, "ls -l /exlibris/backup/scripts/backup_mailer")
        print()
        
        print("[2] Verific daca exista linia NTFY in backup_mailer...")
        print()
        ssh_exec(ssh, "grep -n 'ntfy_notify' /exlibris/backup/scripts/backup_mailer | head -5")
        print()
        
        print("[3] Verific exact ce comanda NTFY este in backup_mailer...")
        print()
        ssh_exec(ssh, "grep -A2 -B2 'ntfy_notify' /exlibris/backup/scripts/backup_mailer | head -10")
        print()
        
        print("[4] Verific daca backup_mailer a fost apelat din cron...")
        print()
        ssh_exec(ssh, "grep backup_mailer /exlibris/backup/logs/user_data_a5_Detail_251028_23*.log | tail -5")
        print()
        
        print("[5] Verific daca mailx a fost apelat...")
        print()
        ssh_exec(ssh, "grep -i mailx /exlibris/backup/logs/user_data_a5_Detail_251028_23*.log | tail -3")
        print()
        
        print("[6] TEST: Rulez backup_mailer manual cu parametri corecti...")
        print()
        print("Va simula un backup reusit...")
        ssh_exec(ssh, "cd /exlibris/backup/scripts && /bin/csh -f backup_mailer FULL ALEPH 00 'End FULL backup' test")
        print()
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("DIAGNOSTIC FINALIZAT")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

