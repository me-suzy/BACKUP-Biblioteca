#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica de ce apare "DB: ALEPH | DB: ALEPH" de doua ori
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
    print("   VERIFICARE DUPLICAT 'DB: ALEPH'")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica linia NTFY in backup_mailer
        print("=" * 70)
        print("1. LINIA NTFY IN BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linia NTFY:")
        print(out)
        
        print()
        
        # 2. Cauta TOATE liniile care contin "DB:" sau "ORACLE_SID"
        print("=" * 70)
        print("2. CAUTARE TOATE APARITIILE 'DB:' SI 'ORACLE_SID'")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'DB:\|ORACLE_SID' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linii care contin DB: sau ORACLE_SID:")
        print(out)
        
        # 3. Verifica daca exista MULTE linii NTFY
        print()
        print("=" * 70)
        print("3. NUMAR LINII NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -c 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        count = int(out.strip()) if out.strip() else 0
        print(f"Numar linii cu 'ntfy_notify': {count}")
        
        if count > 1:
            print("[ERROR] EXISTA MAI MULTE LINII!")
            print("   Toate liniile:")
            out, _ = ssh_exec(ssh, "grep -n 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
            print(out)
        else:
            print("[OK] Doar o singura linie!")
        
        print()
        
        # 4. Verifica daca backup_mailer a avut probleme cu forma
        print("=" * 70)
        print("4. VERIFICARE FORMA LINIE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep 'ntfy_notify' /exlibris/backup/scripts/backup_mailer | cat -A", show=False)
        print("Linia NTFY cu marcatori (spatii, newline):")
        print(out)
        
        # 5. Verifica contextul liniei
        print()
        print("=" * 70)
        print("5. CONTEXT LINIE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linii 95-105:")
        print(out)
        
        # 6. Verifica NOTIFICAREA RECE_PRIMITA
        print()
        print("=" * 70)
        print("6. ANALIZA NOTIFICARE")
        print("=" * 70)
        print()
        
        print("Notificarea pe care ai primit-o la 04:24:")
        print("  BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-28 01:23:45 | STATUS: End FULL backup")
        print()
        print("[INFO] Daca ai vazut 'DB: ALEPH | DB: ALEPH' de doua ori,")
        print("   posibil ca linia NTFY sa aiba o greseala de sintaxa.")
        print("   Sau exista mai multe linii care trimit NTFY.")
        print()
        print("CODE: 00 = Backup completat cu succes")
        print("CODE: 01-14 = Erori diferite in backup")
        
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

