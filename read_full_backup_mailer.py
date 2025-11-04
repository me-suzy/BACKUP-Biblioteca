#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Citeste fisierul backup_mailer COMPLET pentru a intelege structura
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
    print("   CITIRE BACKUP_MAILER COMPLET")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Numara linii
        print("=" * 70)
        print("1. NUMAR LINII")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "wc -l /exlibris/backup/scripts/backup_mailer", show=False)
        print(f"Numar total linii: {out.strip()}")
        
        # 2. Citeste sectiunea relevanta (90-110)
        print()
        print("=" * 70)
        print("2. LINII 90-110")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '90,110p' /exlibris/backup/scripts/backup_mailer", show=False)
        print(out)
        
        # 3. Citeste doar linia 99
        print()
        print("=" * 70)
        print("3. LINIA 99 EXACTA (cu numar octeti)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '99p' /exlibris/backup/scripts/backup_mailer | od -c", show=False)
        print("Linia 99 in octeti:")
        print(out)
        
        # 4. Verifica in jurul liniei 99
        print()
        print("=" * 70)
        print("4. LINII 97-103")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '97,103p' /exlibris/backup/scripts/backup_mailer | cat -A", show=False)
        print("Cu marcatori caracter:")
        print(out)
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("ANALIZA COMPLETA!")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

