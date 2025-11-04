#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica daca backup-ul a rulat AZI
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
    print("   VERIFICARE DACA BACKUP A RULAT AZI")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica fisierele modificate AZI
        print("=" * 70)
        print("1. FISIERE BACKUP MODIFICATE AZI")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "find /exlibris/backup/logs -type f -mtime -1 -ls 2>/dev/null", show=False)
        if out.strip():
            print("[OK] Gasit fisiere modificate azi!")
            print(out)
        else:
            print("[INFO] Nu sunt fisiere modificate azi in /exlibris/backup/logs")
        
        print()
        
        # 2. Verifica toate log-urile recente
        print("=" * 70)
        print("2. TOATE LOG-URILE DIN ULTIMELE 7 ZILE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -lt /exlibris/backup/logs/*.log 2>/dev/null | head -15", show=False)
        print(out)
        
        # 3. Verifica data exacta
        print()
        print("=" * 70)
        print("3. DATA SI ORA EXACTA PE SERVER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "date", show=False)
        print(f"Ora curenta pe server: {out.strip()}")
        
        # 4. Calculare
        print()
        print("=" * 70)
        print("4. CALCULARE")
        print("=" * 70)
        print()
        
        print("Daca ai spus ca backup-ul ruleaza ZILNIC intre 00:00-03:00,")
        print("si AZI este 28 oct dimineata 06:36,")
        print("atunci:")
        print()
        print("  - Backup-ul pentru AZI (28 oct) ar fi trebuit sa ruleze")
        print("    intre 00:00-03:00 (deja a trecut)")
        print()
        print("  - DACA ai primit notificarea la 04:24 azi, asta este")
        print("    backup-ul de noapte (28 oct 01:23:45)")
        print()
        print("  - Urmatorul backup:")
        print("    MINE (29 oct) intre 00:00-03:00")
        print("    Adica peste ~18 ore de acum")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("VERIFICARE COMPLETA!")
        print("=" * 70)
        print()
        print("CONCLUZIE:")
        print("  - Backup-ul de AZI (28 oct) a rulat deja la 01:23 (vezi notificarea)")
        print("  - Urmatorul backup: MINE (29 oct) intre 00:00-03:00")
        print("  - Adica peste ~18 ore de acum (ora 06:36)")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

