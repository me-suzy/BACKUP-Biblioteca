#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificare backup de azi si de ce nu s-a trimis mesaj NTFY
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
    print("   VERIFICARE BACKUP 28 OCT 22:00")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Ora server
        print("=" * 70)
        print("1. ORA SERVER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "date", show=False)
        print(out)
        
        # 2. Log cron a5 (22:00 backup)
        print()
        print("=" * 70)
        print("2. LOG BACKUP 22:00 (a5)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "tail -50 /exlibris/backup/logs/cron_a5.log", show=False)
        print(out)
        
        # 3. Log cron a1 (23:00 backup)
        print()
        print("=" * 70)
        print("3. LOG BACKUP 23:00 (a1)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "tail -50 /exlibris/backup/logs/cron_a1.log", show=False)
        print(out)
        
        # 4. Lista backup-uri de azi
        print()
        print("=" * 70)
        print("4. FISIERE BACKUP DE AZI")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -lth /exlibris/backup/*/*$(date +%Y%m%d)* 2>/dev/null | head -20", show=False)
        print(out)
        
        # 5. Verificare cron
        print()
        print("=" * 70)
        print("5. CRON JOBS")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l", show=False)
        print(out)
        
        # 6. Test manual NTFY
        print()
        print("=" * 70)
        print("6. TEST MANUAL NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "/usr/local/bin/ntfy_notify.sh 'Test verificare - ora 23:45'", show=False)
        print(out)
        
        # 7. Verificare backup_mailer
        print()
        print("=" * 70)
        print("7. BACKUP_MAILER - LINIA NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        print(out)
        
        # 8. Verificare procese backup
        print()
        print("=" * 70)
        print("8. PROCESE BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ps aux | grep -i backup | grep -v grep", show=False)
        print(out)
        
        # 9. Ultimele log-uri exec_backup_main
        print()
        print("=" * 70)
        print("9. LOG EXEC_BACKUP_MAIN")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -lt /exlibris/backup/logs/*exec* 2>/dev/null | head -5", show=False)
        print(out)
        
        if out:
            first_log = out.split()[8]
            print(f"\nContinut {first_log}:")
            out2, _ = ssh_exec(ssh, f"tail -100 {first_log}", show=False)
            print(out2)
        
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

