#!/usr/bin/env python
"""
Diagnostic complet pentru problema notificari NTFY
"""

import paramiko
import sys
import re

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
    print("   DIAGNOSTIC COMPLET - PROBLEMA NOTIFICARI NTFY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica daca scriptul NTFY exista
        print("=" * 70)
        print("1. VERIFICARE SCRIPT NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -la /usr/local/bin/ntfy_notify.sh 2>&1", show=False)
        if "No such file" in out or "cannot access" in out:
            print("[ERROR] Scriptul /usr/local/bin/ntfy_notify.sh NU EXISTA!")
            print("   Asta e problema principala!")
        else:
            print("[OK] Scriptul exista!")
            print(out)
            
            # Verifica continutul
            print()
            print("Continutul scriptului:")
            out, _ = ssh_exec(ssh, "cat /usr/local/bin/ntfy_notify.sh", show=False)
            print(out)
        
        print()
        
        # 2. Testeaza trimiterea unei notificari
        print("=" * 70)
        print("2. TEST TRIMITERE NOTIFICARE")
        print("=" * 70)
        print()
        
        out, err = ssh_exec(ssh, "/usr/local/bin/ntfy_notify.sh 'TEST DIAGNOSTIC - DACA VEDEZI MESAJUL ASTA PE TELEFON, NTFY FUNCTIONEAZA' 2>&1", show=False)
        print(f"Output: {out}")
        if err:
            print(f"Error: {err}")
        
        print()
        print("[INFO] Verifica telefonul ACUM - trebuie sa primesti notificare!")
        print()
        
        # 3. Verifica backup_mailer - linia cu NTFY
        print("=" * 70)
        print("3. VERIFICARE BACKUP_MAILER - LINIA CU NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        if not out.strip():
            print("[ERROR] NU EXISTA linie cu NTFY in backup_mailer!")
            print("   Asta e problema - backup_mailer nu trimite NTFY!")
        else:
            print("[OK] Gasit linie cu NTFY in backup_mailer:")
            print(out)
        
        print()
        
        # 4. Afiseaza contextul complet pentru linia NTFY
        print("=" * 70)
        print("4. CONTINUT COMPLET - CONTEXT LINIA NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -B 5 -A 5 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Context linia NTFY:")
        print(out)
        
        print()
        
        # 5. Verifica daca linia NTFY este comentata
        print("=" * 70)
        print("5. VERIFICARE DACA LINIA ESTE ACTIVA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        if not out.strip():
            print("[ERROR] Linia NTFY nu exista!")
        else:
            lines = out.strip().split('\n')
            for line in lines:
                if 'ntfy_notify' in line:
                    if line.strip().startswith('#'):
                        print("[ERROR] Linia NTFY este COMENTATA!")
                        print(f"   {line}")
                    else:
                        print("[OK] Linia NTFY este ACTIVA!")
                        print(f"   {line}")
        
        print()
        
        # 6. Verifica cron jobs pentru backup
        print("=" * 70)
        print("6. VERIFICARE CRON JOBS BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l 2>&1", show=False)
        if "no crontab" in out.lower() or not out.strip():
            print("[WARN] Nu exista cron jobs!")
            print("   Posibil ca backup-ul sa ruleze prin alta modalitate")
        else:
            print("Cron jobs existente:")
            print(out)
            
            # Cauta cron jobs care apeleaza backup
            backup_cron = [l for l in out.split('\n') if 'backup' in l.lower()]
            if backup_cron:
                print()
                print("Cron jobs care pornesc backup:")
                for cron in backup_cron:
                    print(f"  {cron}")
        
        print()
        
        # 7. Verifica cand a rulat ultimul backup
        print("=" * 70)
        print("7. ULTIMUL BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -lt /exlibris/backup/logs/ | head -5", show=False)
        print("Ultimele fisiere de log backup:")
        print(out)
        
        print()
        
        # 8. Verifica log-urile pentru erori
        print("=" * 70)
        print("8. VERIFICARE LOGURI BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "tail -50 /exlibris/backup/logs/backup_mailer.log 2>/dev/null || echo 'Log nu exista'", show=False)
        print("Ultimele linii din log backup_mailer:")
        print(out)
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("DIAGNOSTIC COMPLET!")
        print("=" * 70)
        print()
        print("VERIFICAT:")
        print("  1. Script NTFY exista?")
        print("  2. Test notificare trimis!")
        print("  3. Linia NTFY in backup_mailer?")
        print("  4. Linia NTFY este activa?")
        print("  5. Cron jobs backup?")
        print("  6. Ultimul backup?")
        print("  7. Log-uri backup?")
        print()
        print("ACUM:")
        print("  - Verifica telefonul pentru test notificare")
        print("  - Daca ai primit notificare = NTFY functioneaza!")
        print("  - Daca NU ai primit = problema la aplicatie sau topic")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

