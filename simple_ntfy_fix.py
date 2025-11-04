#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple fix - foloseste raw bytes
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
    print("   SIMPLE FIX - SCRIE FISIER DIRECT")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Scriem direct linia intr-un fisier temporar
        print("=" * 70)
        print("1. CREARE LINIE NTFY CORECTA")
        print("=" * 70)
        print()
        
        # Linia care functioneaza
        ntfy_line = r'echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date '\''+%Y-%m-%d %H:%M:%S'\''` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh'
        
        # Scriem intr-un fisier temporar
        sftp = ssh.open_sftp()
        with sftp.open('/tmp/ntfy_line_new.txt', 'w') as f:
            f.write(ntfy_line + '\n')
        sftp.close()
        
        # 2. Citeste backup_mailer
        print("[INFO] Citire backup_mailer...")
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        lines = out.split('\n')
        
        # 3. Insereaza linia NTFY dupa linia 98 (comentariu)
        print("[INFO] Inserare linie NTFY...")
        new_lines = []
        for i, line in enumerate(lines, start=1):
            new_lines.append(line)
            if i == 98:  # Dupa linia 98 (comentariu)
                new_lines.append(ntfy_line)
        
        # 4. Scrie fisierul modificat
        print("[INFO] Scriere fisier modificat...")
        sftp = ssh.open_sftp()
        with sftp.open('/tmp/backup_mailer_new.txt', 'w') as f:
            f.write('\n'.join(new_lines))
        sftp.close()
        
        # 5. Inlocuieste originalul
        print("[INFO] Inlocuire backup_mailer...")
        ssh_exec(ssh, "cp /exlibris/backup/scripts/backup_mailer /exlibris/backup/scripts/backup_mailer.before_ntfy_final", show=False)
        ssh_exec(ssh, "cp /tmp/backup_mailer_new.txt /exlibris/backup/scripts/backup_mailer", show=False)
        
        # 6. Verifica rezultatul
        print()
        print("=" * 70)
        print("2. VERIFICARE FINALA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linii 95-105:")
        print(out)
        
        # 7. Testeaza
        print()
        print("=" * 70)
        print("3. TESTARE NOTIFICARE")
        print("=" * 70)
        print()
        
        # Creeaza script de test care simuleaza exact ce face backup_mailer
        test_script = '''#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"

# Aceasta e linia exacta din backup_mailer
echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
'''
        
        sftp = ssh.open_sftp()
        with sftp.open('/tmp/test_exact_backup.sh', 'w') as f:
            f.write(test_script)
        sftp.close()
        
        ssh_exec(ssh, "chmod +x /tmp/test_exact_backup.sh", show=False)
        out, err = ssh_exec(ssh, "/tmp/test_exact_backup.sh 2>&1", show=False)
        print("Output:")
        print(out)
        
        print()
        print("[INFO] Verifica telefonul ACUM!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CORECTARE COMPLETA!")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

