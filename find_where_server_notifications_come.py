#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gaseste de unde vin "Server notification" messages
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
    print("   CAUTARE: DE UNDE VIN 'SERVER NOTIFICATION'")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica cron jobs
        print("=" * 70)
        print("1. CRON JOBS")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l", show=False)
        if out and 'no crontab' not in out:
            print("Cron jobs root:")
            print(out)
            
            if 'ntfy' in out.lower() or 'ntfy_notify' in out.lower():
                print()
                print("[ERROR] FOUND! Cron job care trimite 'Server notification'!")
        else:
            print("[OK] Nu exista cron jobs")
        
        print()
        
        # 2. Verifica scriptul NTFY
        print("=" * 70)
        print("2. SCRIPT NTFY - MESAJ DEFAULT")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /usr/local/bin/ntfy_notify.sh", show=False)
        print("Continut script NTFY:")
        print(out)
        
        # Extrage linia cu "Server notification"
        if 'Server notification' in out:
            print()
            print("[INFO] Scriptul trimite 'Server notification' daca mesajul e gol")
        
        print()
        
        # 3. Cauta scripturi de test
        print("=" * 70)
        print("3. SCRIPTURI TEST CARE FOLOSESC NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "find /tmp -name '*ntfy*' -o -name '*test*' | grep -i 'ntfy' 2>/dev/null", show=False)
        if out.strip():
            print("Scripturi gasite:")
            print(out)
        else:
            print("[INFO] Nu sunt scripturi in /tmp")
        
        # 4. Verifica backup_mailer pentru probleme
        print()
        print("=" * 70)
        print("4. BACKUP_MAILER - LINIA NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linii 95-105:")
        print(out)
        
        # 5. Testeaza DACA variabilele sunt definite
        print()
        print("=" * 70)
        print("5. TEST: SUNT VARIABILELE DEFINITE?")
        print("=" * 70)
        print()
        
        # Creeaza un test care simuleaza ce face backup_mailer
        test_script = '''#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"

echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
'''
        
        # Scriem testul
        sftp = ssh.open_sftp()
        f = sftp.open('/tmp/test_backup_ntfy.sh', 'w')
        f.write('''#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"

echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
''')
        f.close()
        sftp.close()
        
        ssh_exec(ssh, "chmod +x /tmp/test_backup_ntfy.sh", show=False)
        
        print("[INFO] Testare backup_mailer...")
        out, err = ssh_exec(ssh, "/tmp/test_backup_ntfy.sh 2>&1", show=False)
        print("Output:")
        print(out)
        
        print()
        print("[INFO] Verifica telefonul - ar trebui sa primesti UN SINGUR mesaj detaliat!")
        print()
        
        # 6. Verifica sa nu existe alte linii NTFY
        print("=" * 70)
        print("6. TOATE LINIILE CU NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linii cu NTFY:")
        print(out)
        
        count = out.strip().count('\n') + 1 if out.strip() else 0
        print()
        print(f"Numar linii cu NTFY: {count}")
        
        if count > 1:
            print("[ERROR] EXISTA MAI MULTE LINII CU NTFY!")
            print("   Asta inseamna ca se trimit notificari multiple!")
        
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

