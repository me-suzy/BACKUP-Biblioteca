#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OPREȘTE TOATE PROCESELE CARE TRIMIT NTFY
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
    print("   OPRIRE TOTALA - TOATE NOTIFICARILE NTFY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Oprește TOATE procesele care contin "ntfy" sau "test"
        print("=" * 70)
        print("1. OPRIRE PROCESE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ps aux | grep -E 'ntfy|test.*sh' | grep -v grep", show=False)
        if out.strip():
            print("[WARN] PROCESE ACTIVE GASITE:")
            print(out)
            print()
            print("[INFO] Opreste procesele...")
            # Opreste procesele
            for line in out.strip().split('\n'):
                if line.strip():
                    pid = line.split()[1]
                    try:
                        ssh_exec(ssh, f"kill {pid} 2>&1", show=False)
                        print(f"[OK] Proces {pid} oprit")
                    except:
                        pass
        else:
            print("[OK] Nu sunt procese active")
        
        # 2. STERGE TOATE CRON JOBS
        print()
        print("=" * 70)
        print("2. STERGERE CRON JOBS")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l 2>&1", show=False)
        if 'no crontab' not in out and out.strip():
            print("[WARN] EXISTA CRON JOBS!")
            print(out)
            print()
            print("[INFO] Sterge cron jobs...")
            ssh_exec(ssh, "crontab -r", show=False)
            print("[OK] Cron jobs sterse!")
        else:
            print("[OK] Nu exista cron jobs")
        
        # 3. Sterge TOATE scripturile test
        print()
        print("=" * 70)
        print("3. STERGERE TOATE SCRIPTURILE")
        print("=" * 70)
        print()
        
        # Sterge din /tmp
        ssh_exec(ssh, "rm -f /tmp/test* /tmp/*ntfy* /tmp/*backup*.sh 2>/dev/null", show=False)
        print("[OK] Scripturi din /tmp sterse")
        
        # Sterge din /root
        ssh_exec(ssh, "rm -f /root/test* /root/*ntfy* 2>/dev/null", show=False)
        print("[OK] Scripturi din /root sterse")
        
        # 4. COMENTEAZĂ linia NTFY din backup_mailer
        print()
        print("=" * 70)
        print("4. COMENTEAZĂ LINIA NTFY")
        print("=" * 70)
        print()
        
        print("[INFO] Comenteaza linia 97 (NTFY)...")
        
        # Comenteaza linia 97
        ssh_exec(ssh, "sed -i '97s/^/# /' /exlibris/backup/scripts/backup_mailer", show=False)
        
        # Verifica
        out, _ = ssh_exec(ssh, "sed -n '97p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linia 97 (trebuie sa fie comentata):")
        print(out)
        
        if out.strip().startswith('#'):
            print("[OK] Linia NTFY este comentata!")
        else:
            print("[ERROR] Linia NU este comentata!")
        
        print()
        
        # 5. Verifica REZULTATUL
        print("=" * 70)
        print("5. VERIFICARE FINALA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Context (linii 95-105):")
        print(out)
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("OPRIRE COMPLETA!")
        print("=" * 70)
        print()
        print("CE AM FĂCUT:")
        print("  1. Oprit TOATE procesele care trimit NTFY")
        print("  2. Sters TOATE cron jobs")
        print("  3. Sters TOATE scripturile de test")
        print("  4. Comentat linia NTFY din backup_mailer")
        print()
        print("REZULTAT:")
        print("  - NU vei mai primi 'Server notification'")
        print("  - NU vei mai primi notificari din teste")
        print("  - NU vei primi notificari la backup (pana cand nu decomentez linia)")
        print()
        print("PENTRU A REACTIVA NOTIFICARILE LA BACKUP:")
        print("  1. ssh root@185.182.121.45")
        print("  2. vi /exlibris/backup/scripts/backup_mailer")
        print("  3. Mergi la linia 97")
        print("  4. Sterge '#' de la inceputul liniei")
        print("  5. Salveaza (:wq)")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

