#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ruleaza backup manual ACUM pentru azi (28 oct)
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
    print("   TRIGGER BACKUP MANUAL - 28 OCT 23:52")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        print("[1/2] Rulez backup a5 (user_data)...")
        print("      (asteapta 10 secunde pentru inceput...)")
        print()
        
        # Ruleaza in background
        stdin, stdout, stderr = ssh.exec_command(
            "cd /exlibris/backup/scripts && nohup /bin/csh exec_backup_main a5 > /exlibris/backup/logs/manual_backup_$(date +%Y%m%d_%H%M%S).log 2>&1 &"
        )
        
        import time
        time.sleep(2)
        
        print("[OK] Backup pornit in background!")
        print()
        print("[2/2] Verific procese active...")
        print()
        
        out, _ = ssh_exec(ssh, "ps aux | grep exec_backup_main | grep -v grep", show=False)
        print(out)
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("BACKUP PORNIT!")
        print("=" * 70)
        print()
        print("Notificarea NTFY va veni in ~10-15 minute")
        print("cand backup-ul se va finaliza!")
        print()
        print("Verifica telefonul pentru:")
        print("  BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: ... | STATUS: ...")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

