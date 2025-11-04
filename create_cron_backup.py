#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Creaza cron job pentru backup-uri
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
    print("   CREEZ CRON JOB PENTRU BACKUP-URI")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica daca exista deja cron job
        print("=" * 70)
        print("1. VERIFIC CRON JOBS EXISTENTE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l", show=False)
        if out.strip():
            print("[INFO] Exista cron jobs:")
            print(out)
        else:
            print("[INFO] Nu exista cron jobs")
        
        # 2. Adauga noile cron jobs
        print()
        print("=" * 70)
        print("2. ADAUGA CRON JOBS PENTRU BACKUP")
        print("=" * 70)
        print()
        
        # Read existing crontab
        existing = out.strip() if out.strip() else ""
        
        # Add backup jobs
        new_jobs = """# Backup jobs
00 22 * * * /exlibris/backup/scripts/exec_backup_main a5 >> /exlibris/backup/logs/cron_a5.log 2>&1
00 23 * * * /exlibris/backup/scripts/exec_backup_main a1 >> /exlibris/backup/logs/cron_a1.log 2>&1
"""
        
        # Combine
        full_crontab = existing
        if existing:
            full_crontab += "\n"
        full_crontab += new_jobs
        
        # Write to temp file
        print("Creez fisiere temporare...")
        ssh_exec(ssh, "cat > /tmp/new_crontab << 'EOFEOF'\n" + full_crontab + "EOFEOF", show=False)
        
        # Install crontab
        print("Instalez crontab...")
        ssh_exec(ssh, "crontab /tmp/new_crontab")
        
        # 3. Verifica
        print()
        print("=" * 70)
        print("3. VERIFICARE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l", show=False)
        print("Crontab final:")
        print(out)
        
        # 4. Info
        print()
        print("=" * 70)
        print("GATA!")
        print("=" * 70)
        print()
        print("Am creat cron jobs pentru:")
        print("  - Backup user_data: zilnic la 22:00 (slot a5)")
        print("  - Backup ora_cold: zilnic la 23:00 (slot a1)")
        print()
        print("Log-uri:")
        print("  - /exlibris/backup/logs/cron_a5.log")
        print("  - /exlibris/backup/logs/cron_a1.log")
        print()
        print("URMATORUL BACKUP:")
        print("  - Astazi (28 oct) la 22:00 si 23:00")
        print("  - NU A MIERS INCĂ! Asadar urmatorul REAL")
        print("  - este mâine (29 oct) la 22:00 si 23:00")
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

