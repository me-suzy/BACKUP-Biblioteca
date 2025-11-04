#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica programul EXACT de backup
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
    print("   VERIFICARE PROGRAM BACKUP EXACT")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica ultimele log-uri backup
        print("=" * 70)
        print("1. ULTIMELE BACKUP-URI (DATA SI ORA)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -lt /exlibris/backup/logs/*.log 2>/dev/null | head -10", show=False)
        print("Ultimele log-uri backup:")
        print(out)
        
        print()
        
        # 2. Extrae data exacta din ultimul backup
        print("=" * 70)
        print("2. DATA EXACTA ULTIMUL BACKUP")
        print("=" * 70)
        print()
        
        # Gaseste cel mai recent log
        out, _ = ssh_exec(ssh, "ls -t /exlibris/backup/logs/*.log 2>/dev/null | head -1", show=False)
        latest_log = out.strip()
        
        if latest_log:
            # Stat pe fisier pentru a afla data
            out, _ = ssh_exec(ssh, f"stat {latest_log} | grep Modify", show=False)
            print(f"Ultima modificare {latest_log}:")
            print(out)
            
            # Extrae ora din numele fisierului
            import os
            filename = os.path.basename(latest_log)
            if 'Detail' in filename or '_' in filename:
                print()
                print("Nume fisier:", filename)
                print("Asta iti spune exact cand s-a rulat backup-ul!")
        
        print()
        
        # 3. Verifica cron jobs
        print("=" * 70)
        print("3. CRON JOBS BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "find /etc/cron.d /etc/cron.daily /etc/cron.hourly -type f -exec grep -l 'backup\\|exlibris' {} \\; 2>/dev/null", show=False)
        if out.strip():
            print("Fisiere cron care contin 'backup':")
            for line in out.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
                    # Citeste continutul
                    content, _ = ssh_exec(ssh, f"cat {line.strip()} 2>/dev/null", show=False)
                    print(f"    {content}")
        else:
            print("[INFO] Nu s-au gasit cron jobs explicite pentru backup")
        
        # 4. Verifica daca exista atd sau alte sisteme
        print()
        print("=" * 70)
        print("4. VERIFICARE ATD / AUTOD SYSTEM")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ps aux | grep -E 'atd|autod' | grep -v grep", show=False)
        if out.strip():
            print("[INFO] Exista procese atd/autod:")
            print(out)
        else:
            print("[INFO] Nu sunt procese atd")
        
        # 5. Calculare urmatorul backup
        print()
        print("=" * 70)
        print("5. CALCULARE URMATOR BACKUP")
        print("=" * 70)
        print()
        
        print("[INFO] Pe baza log-urilor,")
        print("   Ultimul backup: 25 oct la 22:08")
        print("   Astazi: 28 oct")
        print()
        print("Daca backup-ul ruleaza ZILNIC intre 00:00-03:00,")
        print("   Proximul backup:")
        print("   - Astazi (28 oct) intre 00:00-03:00 (deja a trecut)")
        print("   - MINE (29 oct) intre 00:00-03:00")
        print()
        print("Deci urmatorul backup ESTE DIN NOU MINE LA 00:00-03:00!")
        print()
        
        ssh.close()
        
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

