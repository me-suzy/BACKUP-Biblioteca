#!/usr/bin/env python
"""
Analizeaza backup_mailer pentru a vedea UNDE si CUM este apelat
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
    print("   ANALIZA BACKUP_MAILER - UNDE TRIMITE NTFY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Citeste backup_mailer COMPLET
        print("=" * 70)
        print("1. CONTINUT BACKUP_MAILER (aproximativ)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "head -50 /exlibris/backup/scripts/backup_mailer", show=False)
        print("Primele 50 de linii:")
        print(out)
        
        print()
        
        # 2. Cauta TOATE apelurile la backup_mailer
        print("=" * 70)
        print("2. UNDE SE APELEAZA BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "find /exlibris/backup -type f -exec grep -l 'backup_mailer' {} \\; 2>/dev/null", show=False)
        print("Fisiere care contin 'backup_mailer':")
        print(out)
        
        print()
        
        # 3. Verifica in ce context este linia NTFY
        print("=" * 70)
        print("3. CONTEXT LINIA NTFY (in jurul liniei 99)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '85,110p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Context linia NTFY:")
        print(out)
        
        print()
        
        # 4. Verifica daca backup_mailer este executat cu parametri
        print("=" * 70)
        print("4. CARE SUNT PARAMETRII BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "head -20 /exlibris/backup/scripts/backup_mailer | grep -E 'BACKUP_TYPE|ORACLE_SID|ERROR'", show=False)
        print("Variabile definite:")
        print(out)
        
        print()
        
        # 5. Verifica daca exista un test simplu
        print("=" * 70)
        print("5. SIMULARE APEL BACKUP_MAILER")
        print("=" * 70)
        print()
        
        print("[INFO] Vom simula executia liniei NTFY manual...")
        
        # Simuleaza variabilele
        test_cmd = '''
        export BACKUP_TYPE="FULL"
        export ORACLE_SID="ALEPH"
        export ERROR_NUMBER="00"
        export ERROR_MESSAGE="End FULL backup"
        
        echo "BACKUP: ${BACKUP_TYPE} | DB: ${ORACLE_SID} | CODE: ${ERROR_NUMBER} | TIME: `/bin/date '+%Y-%m-%d %H:%M:%S'` | STATUS: ${ERROR_MESSAGE}" | /usr/local/bin/ntfy_notify.sh
        '''
        
        out, err = ssh_exec(ssh, test_cmd, show=False)
        print("Rezultat simulare:")
        print(out)
        if err:
            print(f"Error: {err}")
        
        print()
        print("[INFO] Verifica telefonul ACUM - ar trebui sa primesti notificare!")
        print()
        
        ssh.close()
        
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

