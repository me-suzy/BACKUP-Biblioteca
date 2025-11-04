#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificare de ce nu s-a executat backup-ul
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
    print("   DE CE NU S-A EXECUTAT BACKUP?")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Test exec_backup_main direct
        print("=" * 70)
        print("1. TEST EXEC_BACKUP_MAIN")
        print("=" * 70)
        print()
        
        print("Test executare a5:")
        out, err = ssh_exec(ssh, "cd /exlibris/backup/scripts && /bin/csh exec_backup_main a5 2>&1 | head -50", show=False, timeout=30)
        print(out)
        if err:
            print(f"ERROR: {err}")
        
        # 2. Verificare cron log
        print()
        print("=" * 70)
        print("2. CRON LOG DETALIAT")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "tail -100 /var/log/cron 2>/dev/null || tail -100 /var/log/messages 2>/dev/null | grep cron", show=False)
        print(out)
        
        # 3. Verificare exec_backup_main exists
        print()
        print("=" * 70)
        print("3. VERIFICARE EXEC_BACKUP_MAIN")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -la /exlibris/backup/scripts/exec_backup_main", show=False)
        print(out)
        
        # 4. Read exec_backup_main
        print()
        print("=" * 70)
        print("4. CONTINUT EXEC_BACKUP_MAIN")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "head -30 /exlibris/backup/scripts/exec_backup_main", show=False)
        print(out)
        
        # 5. Verificare permisiuni
        print()
        print("=" * 70)
        print("5. PERMISIUNI")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -la /exlibris/backup/scripts/ | grep -E '(exec_backup|backup_mailer)'", show=False)
        print(out)
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("ANALIZA COMPLETA")
        print("=" * 70)
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

