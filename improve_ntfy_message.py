#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Imbunatateste mesajul NTFY pentru claritate mai mare
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
    print("   IMBUNATATIRE MESAJ NTFY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Backup
        ssh_exec(ssh, "cp /exlibris/backup/scripts/backup_mailer /exlibris/backup/scripts/backup_mailer.before_improvement", show=False)
        print("[OK] Backup creat!")
        
        # 2. Inlocuieste linia cu o versiune mai clar
        print()
        print("=" * 70)
        print("IMBUNATATIRE MESAJ")
        print("=" * 70)
        print()
        
        # Versiunea NOUA - mai clara si fara duplicari
        new_line = 'echo "BACKUP: $BACKUP_TYPE | Database: $ORACLE_SID | Result: $ERROR_NUMBER | Completed: `/bin/date \'"+%Y-%m-%d %H:%M:%S"\'` | $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh'
        
        print("Linia NOUA mai clara:")
        print(new_line)
        print()
        
        # Inlocuieste linia 97
        print("[INFO] Inlocuire linie 97...")
        
        # Folosim metod veche - citim, modificam, scriem
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        lines = out.split('\n')
        
        # Inlocuieste linia 97 (index 96)
        if len(lines) > 96 and 'ntfy_notify' in lines[96]:
            lines[96] = new_line
            
            # Scrie fisierul
            new_content = '\n'.join(lines)
            sftp = ssh.open_sftp()
            f = sftp.open('/tmp/backup_mailer_improved.txt', 'w')
            f.write(new_content)
            f.close()
            sftp.close()
            
            ssh_exec(ssh, "cp /tmp/backup_mailer_improved.txt /exlibris/backup/scripts/backup_mailer", show=False)
            print("[OK] Linie inlocuita!")
        else:
            print("[ERROR] Nu am gasit linia 97 cu NTFY!")
            return 1
        
        # 3. Verifica rezultatul
        print()
        print("=" * 70)
        print("VERIFICARE FINALA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linii 95-105:")
        print(out)
        
        # 4. Testeaza
        print()
        print("=" * 70)
        print("TEST NOTIFICARE IMBUNATATITA")
        print("=" * 70)
        print()
        
        test_content = '''#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"

echo "BACKUP: $BACKUP_TYPE | Database: $ORACLE_SID | Result: $ERROR_NUMBER | Completed: `/bin/date '+%Y-%m-%d %H:%M:%S'` | $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
'''
        
        sftp = ssh.open_sftp()
        f = sftp.open('/tmp/test_improved.sh', 'w')
        f.write(test_content)
        f.close()
        sftp.close()
        
        ssh_exec(ssh, "chmod +x /tmp/test_improved.sh", show=False)
        
        print("[INFO] Executare test...")
        out, err = ssh_exec(ssh, "/tmp/test_improved.sh 2>&1", show=False)
        print("Output:")
        print(out)
        
        # Sterge test
        ssh_exec(ssh, "rm /tmp/test_improved.sh", show=False)
        
        print()
        print("[INFO] Verifica telefonul!")
        print("   Ar trebui sa primesti:")
        print("   BACKUP: FULL | Database: ALEPH | Result: 00 | Completed: 2025-10-28 XX:XX:XX | End FULL backup")
        print()
        print("[INFO] PROVOCARE: Sa NU mai existe 'DB: ALEPH' de doua ori!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("IMBUNATATIRE COMPLETA!")
        print("=" * 70)
        print()
        print("SCHIMBARI:")
        print("  - 'DB:' -> 'Database:' (mai clar)")
        print("  - 'CODE:' -> 'Result:' (mai clar)")
        print("  - 'TIME:' -> 'Completed:' (mai clar)")
        print("  - 'STATUS:' -> eliminat (EROARE era dublat)")
        print()
        print("PROXIMUL BACKUP:")
        print("  Vei primi notificare fara duplicate!")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

