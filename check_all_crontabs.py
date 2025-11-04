#!/usr/bin/env python
"""
Verifica TOATE crontab-urile si fisierele cron
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
    print("   VERIFICARE TOATE CRONTAB-URILE")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica /var/spool/cron/root direct
        print("=" * 70)
        print("1. CONTINUT /var/spool/cron/root")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /var/spool/cron/root 2>&1", show=False)
        if out.strip():
            print("Continut /var/spool/cron/root:")
            print(out)
        else:
            print("[WARN] Fisier este GOL")
        
        print()
        
        # 2. Verifica /etc/crontab
        print("=" * 70)
        print("2. CONTINUT /etc/crontab")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /etc/crontab", show=False)
        print(out)
        
        print()
        
        # 3. Cauta fisiere care contin "backup" in /etc/cron
        print("=" * 70)
        print("3. CAUTARE 'BACKUP' IN /ETC/CRON")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -r 'backup' /etc/cron* 2>/dev/null", show=False)
        if out:
            print("Rezultate:")
            print(out)
        else:
            print("[INFO] Niciun rezultat")
        
        print()
        
        # 4. Verifica procese oracle si rman
        print("=" * 70)
        print("4. PROCESE ORACLE/RMAN")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ps aux | grep -E 'rman|oracle|backup' | grep -v grep", show=False)
        if out:
            print("Procese relevante:")
            print(out)
        else:
            print("[INFO] Nu sunt procese relevante active")
        
        print()
        
        # 5. Verifica cand a rulat ultimul backup
        print("=" * 70)
        print("5. DATA ULTIMUL BACKUP (din log)")

        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -lt /exlibris/backup/logs/*.log | head -3", show=False)
        print("Ultimele log-uri backup:")
        print(out)
        
        # Extrage data din primul log
        if out:
            lines = out.strip().split('\n')
            if len(lines) > 2:
                log_file = lines[1].split()[-1]
                print()
                print(f"Data ultimul log: {log_file}")
                
                # Verifica data
                out, _ = ssh_exec(ssh, f"tail -5 {log_file} 2>&1", show=False)
                print("Ultimele linii din log:")
                print(out)
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("VERIFICARE COMPLETA!")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

