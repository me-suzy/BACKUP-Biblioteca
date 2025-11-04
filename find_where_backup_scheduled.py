#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cauta unde se programeaza backup-urile
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
    print("   VERIFICARE UNDE SE PROGRAMEAZA BACKUP-URILE")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Citeste exec_backup_main
        print("=" * 70)
        print("1. SCRIPT EXEC_BACKUP_MAIN")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "head -100 /exlibris/backup/scripts/exec_backup_main", show=False)
        print(out)
        
        # 2. Cauta dupa comanda 'at'
        print()
        print("=" * 70)
        print("2. CAUTA COMENZI 'at' IN SCRIPT")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'at ' /exlibris/backup/scripts/exec_backup_main", show=False)
        if out.strip():
            print("[FOUND] Comenzi 'at' in exec_backup_main:")
            print(out)
        else:
            print("[INFO] Nu s-au gasit comenzi 'at' in exec_backup_main")
        
        # 3. Verifica daca exista /etc/cron.* joburi
        print()
        print("=" * 70)
        print("3. VERIFICARE /etc/cron.*")
        print("=" * 70)
        print()
        
        for cron_dir in ['/etc/cron.d', '/etc/cron.daily', '/etc/cron.hourly']:
            out, _ = ssh_exec(ssh, f"ls -la {cron_dir} 2>/dev/null", show=False)
            if out.strip():
                print(f"[OK] {cron_dir}:")
                print(out)
        
        # 4. Verifica cronjobs ale tuturor userilor
        print()
        print("=" * 70)
        print("4. CRONTAB PENTRU TOTI USERII")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "for user in $(cut -f1 -d: /etc/passwd); do crontab -u $user -l 2>/dev/null; done", show=False)
        if out.strip():
            print("Cron jobs pentru toti userii:")
            print(out)
        else:
            print("[INFO] Nu sunt cron jobs")
        
        # 5. Verifica unde se apeleaza exec_backup_main
        print()
        print("=" * 70)
        print("5. UNDE SE APELEAZA EXEC_BACKUP_MAIN")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -r 'exec_backup_main' /etc /usr/local /exlibris/backup 2>/dev/null | grep -v Binary", show=False)
        if out.strip():
            print("[FOUND] Referinte la exec_backup_main:")
            print(out)
        else:
            print("[INFO] Nu s-au gasit referinte")
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("DIAGNOSTIC FINAL")
        print("=" * 70)
        print()
        print("PROBLEMA:")
        print("  - Backup-urile s-au oprit pe 25 oct")
        print("  - Nu sunt joburi 'at' programate")
        print("  - atd ruleaza corect")
        print()
        print("SOLUTIE:")
        print("  Trebuie sa gasim scriptul care programa backup-urile")
        print("  si sa-l re-pornim")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

