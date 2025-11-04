#!/usr/bin/env python
"""
Citeste backup_mailer si creeaza un script modificat cu detalii complete
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
    print("   CITESTE BACKUP_MAILER SI CREEZ SCRIPT DETALIAT")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Citeste scriptul backup_mailer
        print("=" * 70)
        print("1. CITESTE BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        
        print("Continut script:")
        print(out[:2000])
        print()
        
        # Analizeaza variabilele disponibile
        print("=" * 70)
        print("2. ANALIZEZ VARIABILE DISPONIBILE")
        print("=" * 70)
        print()
        
        variables = []
        lines = out.split('\n')
        for line in lines:
            if 'BKP_' in line or 'BACKUP_' in line or 'ERROR_' in line or 'SUBJECT' in line:
                variables.append(line.strip())
        
        print("Variabile gasite:")
        for v in variables[:20]:
            print(f"  {v}")
        
        print()
        
        # Creez script nou cu detalii complete
        print("=" * 70)
        print("3. CREEZ SCRIPT DETALIAT CU NTFY")
        print("=" * 70)
        print()
        
        # Gaseste linia unde se trimite email
        # de obicei este ceva de genul: mailx -s "$SUBJECT  $BACKUP_TYPE " "$BKP_MAIL"
        
        # Creez mesajul NTFY cu detalii
        ntfy_message = '''#!/bin/bash
# Trimitere NTFY cu detalii complete
DETAILS="${SUBJECT} - ${BACKUP_TYPE}\\n\\nStatus: ${ERROR_MESSAGE}\\nEroare: ${ERROR_NUMBER}\\nMail: ${BKP_MAIL}\\nSlot: ${BKP_SLOT}\\nTimestamp: $(date)"
echo -e "$DETAILS" | /usr/local/bin/ntfy_notify.sh'''
        
        print("Mesaj NTFY cu detalii:")
        print(ntfy_message)
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("VERIFICARE COMPLETA!")
        print("=" * 70)
        print()
        print(">> URMARAREA: Modific scriptul backup_mailer")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
