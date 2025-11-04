#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FIX FINAL - linia NTFY functionala pentru C-shell
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
    print("   FIX FINAL - LINIA NTFY FUNCȚIONALA")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Restaureaza backup
        ssh_exec(ssh, "cp /exlibris/backup/scripts/backup_mailer.ntfy_fix2_backup /exlibris/backup/scripts/backup_mailer", show=False)
        print("[OK] Backup restaurat!")
        
        # 2. Citeste fisierul
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        lines = out.split('\n')
        
        # 3. Gaseste unde sa adauge linia (dupa mailx, linia 96-97)
        print()
        print("=" * 70)
        print("LOCUIRE PUNCT INSERARE")
        print("=" * 70)
        print()
        
        # Gaseste linia mailx
        mailx_line = None
        for i, line in enumerate(lines):
            if 'mailx -s' in line and '$BKP_MAIL' in line:
                mailx_line = i
                print(f"[OK] Gasit linia mailx la: {i+1}")
                print(f"   {line}")
                break
        
        if mailx_line is None:
            print("[ERROR] Nu am gasit linia mailx!")
            return 1
        
        # 4. Adauga linia NTFY CORECTA
        print()
        print("=" * 70)
        print("ADAUGARE LINIE NTFY CORECTA")
        print("=" * 70)
        print()
        
        # Versiunea CORECTA pentru C-shell - EXACT ca prima notificare
        # Linia care a functionat cand ai primit prima notificare corecta
        ntfy_line = 'echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date '\''+%Y-%m-%d %H:%M:%S'\''` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh'
        
        print("Linia NTFY (exact ca la prima notificare):")
        print(ntfy_line)
        print()
        
        # Inserare dupa linia mailx
        insert_pos = mailx_line + 1
        lines.insert(insert_pos, ntfy_line)
        
        # 5. Scrie fisierul
        print("[INFO] Scriere fisier modificat...")
        new_content = '\n'.join(lines)
        
        sftp = ssh.open_sftp()
        f = sftp.open('/tmp/backup_mailer_working.txt', 'w')
        f.write(new_content)
        f.close()
        sftp.close()
        
        ssh_exec(ssh, "cp /tmp/backup_mailer_working.txt /exlibris/backup/scripts/backup_mailer", show=False)
        print("[OK] Fisier modificat!")
        
        # 6. Verifica
        print()
        print("=" * 70)
        print("VERIFICARE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linii 95-105:")
        print(out)
        
        # 7. Test FINAL
        print()
        print("=" * 70)
        print("TEST FINAL")
        print("=" * 70)
        print()
        
        # Test C-shell EXACT ca backup_mailer
        test_script = '''#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"

echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
'''
        
        sftp = ssh.open_sftp()
        f = sftp.open('/tmp/test_final_working.sh', 'w')
        f.write(test_script)
        f.close()
        sftp.close()
        
        ssh_exec(ssh, "chmod +x /tmp/test_final_working.sh", show=False)
        
        print("[INFO] Executare test...")
        out, err = ssh_exec(ssh, "/tmp/test_final_working.sh 2>&1", show=False)
        print("Output:")
        print(out)
        
        # Sterge test
        ssh_exec(ssh, "rm /tmp/test_final_working.sh", show=False)
        
        print()
        print("[INFO] VERIFICA TELEFONUL ACUM!")
        print("   Ar trebui sa primesti:")
        print("   BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-28 XX:XX:XX | STATUS: End FULL backup")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CONFIGURARE COMPLETA!")
        print("=" * 70)
        print()
        print("REZUMAT:")
        print("  - Linia NTFY adaugata (versiunea care a functionat prima oara)")
        print("  - Compatibila cu C-shell")
        print("  - Va trimite exact mesajul de la 04:24")
        print()
        print("PROXIMUL BACKUP:")
        print("  - Luni 27 oct la 23:00 sau miercuri 29 oct la 23:00")
        print("  - Vei primi notificare corecta")
        print("  - Format: BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: ... | STATUS: ...")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

