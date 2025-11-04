#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Citeste ultimul log de backup pentru detalii
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
    print("   CITIRE LOG BACKUP FINAL")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        print("[1] Citire manual_backup log (23:54)...")
        print()
        ssh_exec(ssh, "cat /exlibris/backup/logs/manual_backup_20251028_235406.log")
        print()
        
        print("[2] Citire ultimele 100 linii din user_data log (23:54)...")
        print()
        ssh_exec(ssh, "tail -100 /exlibris/backup/logs/user_data_a5_Detail_251028_2354.log")
        print()
        
        print("[3] Verific cron log a5...")
        print()
        ssh_exec(ssh, "cat /exlibris/backup/logs/cron_a5.log")
        print()
        
        print("[4] Verific cron log a1...")
        print()
        ssh_exec(ssh, "cat /exlibris/backup/logs/cron_a1.log")
        print()
        
        ssh.close()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

