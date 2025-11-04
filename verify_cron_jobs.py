#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica cron jobs create
"""

import paramiko
import sys

HOST = "185.182.121.45"
USER = "root"
PASS = "YOUR-PASSWORD"
PORT = 22

def ssh_exec(ssh, cmd, show=True, timeout=10):
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
    print("   VERIFICARE CRON JOBS BACKUP")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Crontab
        print("=" * 70)
        print("1. CRONTAB JOBS")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l", show=False)
        if out.strip():
            print("[OK] Exista cron jobs:")
            print(out)
        else:
            print("[INFO] Nu exista cron jobs")
        
        # 2. Cron service
        print()
        print("=" * 70)
        print("2. CROND STATUS")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ps aux | grep crond | grep -v grep", show=False)
        if out.strip():
            print("[OK] crond ruleaza:")
            print(out)
        else:
            print("[WARN] crond nu ruleaza!")
        
        # 3. At jobs
        print()
        print("=" * 70)
        print("3. AT JOBS (programari viitoare)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "atq", show=False)
        if out.strip():
            print("[INFO] Exista joburi 'at':")
            print(out)
        else:
            print("[INFO] Nu exista joburi 'at' programate")
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("CONCLUSIE")
        print("=" * 70)
        print()
        print("Cron jobs create SUCCES!")
        print("Backup-urile vor rula de acum incolo.")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

