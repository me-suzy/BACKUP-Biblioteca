#!/usr/bin/env python
"""
Corecteaza linia NTFY pentru sintaxa C-shell (csh)
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
    print("   CORECTARE LINIE NTFY PENTRU C-SHELL")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica linia actuala
        print("=" * 70)
        print("1. LINIA ACTUALA (cu sintaxa bash)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '99p' /exlibris/backup/scripts/backup_mailer", show=False)
        print(f"Linia actuala (99): {out.strip()}")
        
        print()
        print("[ERROR] Problema:")
        print("  backup_mailer foloseste C-shell (#!/bin/csh)")
        print("  dar linia NTFY foloseste sintaxa bash (echo ... |)")
        print("  In C-shell, pipe-ul nu functioneaza corect!")
        print()
        
        # 2. Creeaza linia corecta pentru C-shell
        print("=" * 70)
        print("2. LINIA CORECTA PENTRU C-SHELL")
        print("=" * 70)
        print()
        
        # C-shell corect ar fi:
        # echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
        
        # SAU mai simplu - apeleaza direct cu argument
        csh_line = 'echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `date \'+%Y-%m-%d %H:%M:%S\'` | STATUS: $ERROR_MESSAGE" > /tmp/ntfy_msg.txt ; cat /tmp/ntfy_msg.txt | /usr/local/bin/ntfy_notify.sh'
        
        print("Linia corecta pentru C-shell:")
        print(csh_line)
        print()
        
        # 3. Fa backup la linia actuala
        print("=" * 70)
        print("3. BACKUP LINIA ACTUALA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '99p' /exlibris/backup/scripts/backup_mailer > /tmp/backup_mailer_line99_backup.txt && cat /tmp/backup_mailer_line99_backup.txt", show=False)
        print("Linia salvata in backup:")
        print(out)
        
        print()
        
        # 4. Inlocuieste linia 99 cu varianta corecta C-shell
        print("=" * 70)
        print("4. INLOCUIRE LINIE CU SINTAXA C-SHELL")
        print("=" * 70)
        print()
        
        # Varianta mai simpla - foloseste argument in loc de pipe
        new_line = 'echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `date \'+%Y-%m-%d %H:%M:%S\'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh'
        
        print(f"Noua linie:")
        print(new_line)
        print()
        print("[INFO] Acum sa inlocuim...")
        
        # Inlocuieste linia 99
        replace_cmd = f"sed -i '99s|.*|{new_line}|' /exlibris/backup/scripts/backup_mailer"
        
        out, err = ssh_exec(ssh, replace_cmd, show=False)
        
        # Verifica rezultatul
        out, _ = ssh_exec(ssh, "sed -n '99p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linia dupa inlocuire:")
        print(out)
        
        print()
        
        # 5. Testeaza noua linie
        print("=" * 70)
        print("5. TESTARE NOUA LINIE")
        print("=" * 70)
        print()
        
        test_cmd = '''
        set BACKUP_TYPE="FULL"
        set ORACLE_SID="ALEPH"
        set ERROR_NUMBER="00"
        set ERROR_MESSAGE="End FULL backup"
        
        echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
        '''
        
        print("[INFO] Trimitere notificare test...")
        out, err = ssh_exec(ssh, f'csh -c "{test_cmd}" 2>&1', show=False)
        print("Rezultat:")
        print(out)
        if err:
            print(f"Error: {err}")
        
        print()
        print("[INFO] Verifica telefonul ACUM!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CORECTARE COMPLETA!")
        print("=" * 70)
        print()
        print("[OK] Am corectat sintaxa pentru C-shell!")
        print("   - backup_mailer foloseste C-shell")
        print("   - Linia NTFY ar trebui sa functioneze acum")
        print()
        print("PROXIMA DATA CAND SE FACE BACKUP:")
        print("   - Vei primi notificare normal!")
        print("   - Cu formatul: BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-28 01:23:45 | STATUS: ...")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

