#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificare simpla backup
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
    print("   VERIFICARE BACKUP - SIMPLA")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verificare executare azi
        print("=" * 70)
        print("1. PROCESE BACKUP ACTIVE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ps aux | grep exec_backup_main | grep -v grep")
        
        # 2. Verificare log cron
        print()
        print("=" * 70)
        print("2. LOG CRON 22:00")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/logs/cron_a5.log")
        
        # 3. Verificare log cron 23:00
        print()
        print("=" * 70)
        print("3. LOG CRON 23:00")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/logs/cron_a1.log")
        
        # 4. Verificare fisiere create azi
        print()
        print("=" * 70)
        print("4. FISIERE BACKUP 28 OCT")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "find /exlibris/backup -type f -newermt '2025-10-28 22:00' ! -newermt '2025-10-28 23:00' 2>/dev/null | head -20")
        
        # 5. Verificare ora cron
        print()
        print("=" * 70)
        print("5. CRON RULEAZA?")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ps aux | grep crond | grep -v grep")
        
        # 6. Test manual exec
        print()
        print("=" * 70)
        print("6. TEST EXEC (5 sec)")
        print("=" * 70)
        print()
        
        stdin, stdout, stderr = ssh.exec_command("cd /exlibris/backup/scripts && timeout 5 ./exec_backup_main a5 2>&1 || true", timeout=10)
        out = stdout.read().decode("utf-8", errors="ignore")
        err = stderr.read().decode("utf-8", errors="ignore")
        print(out)
        if err:
            print(f"ERROR: {err}")
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("GATA")
        print("=" * 70)
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

