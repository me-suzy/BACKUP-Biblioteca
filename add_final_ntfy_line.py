#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Adauga linia NTFY FINALA in backup_mailer
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
    print("   ADAUGARE LINIE NTFY FINALA")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Backup original
        ssh_exec(ssh, "cp /exlibris/backup/scripts/backup_mailer /exlibris/backup/scripts/backup_mailer.final_backup", show=False)
        print("[OK] Backup creat!")
        
        # 2. Citeste fisierul
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        lines = out.split('\n')
        
        # 3. Gaseste unde sa insereze (dupa mailx)
        print()
        print("=" * 70)
        print("CAUTARE LOCATIE INSERARE")
        print("=" * 70)
        print()
        
        found = False
        for i, line in enumerate(lines):
            if 'mailx -s' in line and '$BKP_MAIL' in line:
                print(f"[OK] Gasit locatie la linia {i+1}")
                insert_pos = i + 1
                
                # Verifica daca urmeaza spatiu sau comment
                next_line = lines[insert_pos] if insert_pos < len(lines) else ""
                print(f"Linia urmatoare: '{next_line}'")
                
                if next_line.strip() == "" or next_line.strip().startswith("#"):
                    # Adauga linia NTFY aici
                    # Linia care functioneaza 100% in C-shell
                    ntfy_line = 'echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date \'"+%Y-%m-%d %H:%M:%S"\'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh'
                    
                    print()
                    print("Linia de adaugat:")
                    print(ntfy_line)
                    print()
                    
                    # Inserare linie
                    lines.insert(insert_pos, ntfy_line)
                    found = True
                    break
        
        if not found:
            print("[ERROR] Nu am gasit locul de inserare!")
            return 1
        
        # 4. Scrie fisierul modificat
        print()
        print("=" * 70)
        print("SCRIIRE FISIER MODIFICAT")
        print("=" * 70)
        print()
        
        new_content = '\n'.join(lines)
        
        sftp = ssh.open_sftp()
        f = sftp.open('/tmp/backup_mailer_modified.txt', 'w')
        f.write(new_content)
        f.close()
        sftp.close()
        
        # Copiaza inapoi
        ssh_exec(ssh, "cp /tmp/backup_mailer_modified.txt /exlibris/backup/scripts/backup_mailer", show=False)
        
        print("[OK] Fisier modificat!")
        
        # 5. Verifica rezultatul
        print()
        print("=" * 70)
        print("VERIFICARE FINALA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linii 95-105:")
        print(out)
        
        # 6. Verifica ca exista O SINGURA linie
        out, _ = ssh_exec(ssh, "grep -n 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        print()
        print("Linii cu NTFY:")
        print(out)
        
        lines_count = len([l for l in out.strip().split('\n') if l.strip()])
        print(f"Numar linii NTFY: {lines_count}")
        
        if lines_count > 1:
            print("[WARN] EXISTA MAI MULTE LINII!")
        else:
            print("[OK] DOAR o singura linie NTFY!")
        
        # 7. Test final
        print()
        print("=" * 70)
        print("TEST FINAL")
        print("=" * 70)
        print()
        
        test_content = '''#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"

echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
'''
        
        sftp = ssh.open_sftp()
        f = sftp.open('/tmp/test_final_backup_ntfy.sh', 'w')
        f.write(test_content)
        f.close()
        sftp.close()
        
        ssh_exec(ssh, "chmod +x /tmp/test_final_backup_ntfy.sh", show=False)
        
        print("[INFO] Executare test final...")
        out, err = ssh_exec(ssh, "/tmp/test_final_backup_ntfy.sh 2>&1", show=False)
        print("Output:")
        print(out)
        
        # Sterge script de test
        ssh_exec(ssh, "rm /tmp/test_final_backup_ntfy.sh", show=False)
        
        print()
        print("[INFO] Verifica telefonul ACUM!")
        print("   Ar trebui sa primesti mesajul complet de backup!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CONFIGURARE COMPLETA!")
        print("=" * 70)
        print()
        print("REZUMAT:")
        print("  - Linia NTFY adaugata in backup_mailer")
        print("  - Scripturile de test sterse")
        print("  - La urmatorul backup vei primi:")
        print("    BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: ... | STATUS: ...")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

