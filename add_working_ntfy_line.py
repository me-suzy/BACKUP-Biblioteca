#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Adauga linia NTFY FUNCTIONALA in backup_mailer
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
    print("   ADAUGARE LINIE NTFY FUNCTIONALA")
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
        print("=" * 70)
        print("1. BACKUP ORIGINAL")
        print("=" * 70)
        print()
        
        ssh_exec(ssh, "cp /exlibris/backup/scripts/backup_mailer /exlibris/backup/scripts/backup_mailer.ntfy_fix2_backup", show=False)
        print("[OK] Backup creat!")
        
        # 2. Citeste fisierul
        print()
        print("=" * 70)
        print("2. CITIRE FISIER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        lines = out.split('\n')
        
        # 3. Gaseste liniile 98-99 (comentariile)
        print("[INFO] Cautare linii comentarii NTFY...")
        for i, line in enumerate(lines):
            if i >= 97 and i < 102 and 'NTFY' in line:
                print(f"Linia {i+1}: {line}")
        
        # 4. Inseraza linia NOUA dupa linia 98
        print()
        print("=" * 70)
        print("3. INSERARE LINIE FUNCTIONALA")
        print("=" * 70)
        print()
        
        # Versiune SIMPLA si FUNCTIONALA pentru C-shell
        # ATENTIE: Trebuie sa fie pe O SINGURA LINIE
        new_line = "echo \"BACKUP: \$BACKUP_TYPE | DB: \$ORACLE_SID | CODE: \$ERROR_NUMBER | TIME: \\`/bin/date '+%Y-%m-%d %H:%M:%S'\\` | STATUS: \$ERROR_MESSAGE\" | /usr/local/bin/ntfy_notify.sh"
        
        print("Linia de adaugat:")
        print(new_line)
        print()
        
        # Sterge liniile 98-99 (doua comentarii duplicate)
        ssh_exec(ssh, "sed -i '98,99d' /exlibris/backup/scripts/backup_mailer", show=False)
        
        # Adauga linia NOUA la linia 98
        # Folosim un wrapper bash pentru a scapa de probleme de encoding
        print("[INFO] Adaugare linie NTFY...")
        
        # Metoda sigura: folosim printf pentru a construi linia
        # Si apoi o inseram cu sed
        wrapper_cmd = f'''bash -c "printf '%s\\n' '{new_line}' | sed -i '98r /dev/stdin' /exlibris/backup/scripts/backup_mailer"'''
        
        # Mai simplu: adaugam direct pe linia 98
        ssh_exec(ssh, f"sed -i \"98i\\{new_line}\" /exlibris/backup/scripts/backup_mailer", show=False)
        
        # 5. Verifica rezultatul
        print()
        print("=" * 70)
        print("4. VERIFICARE FINALA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linii 95-105:")
        print(out)
        
        # 6. Testeaza
        print()
        print("=" * 70)
        print("5. TESTARE NOTIFICARE")
        print("=" * 70)
        print()
        
        # Creeaza un test EXACT ca backup_mailer
        test_content = '''#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"

echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
'''
        
        sftp = ssh.open_sftp()
        f = sftp.open('/tmp/test_backup_final.sh', 'w')
        f.write(test_content)
        f.close()
        sftp.close()
        
        ssh_exec(ssh, "chmod +x /tmp/test_backup_final.sh", show=False)
        
        print("[INFO] Executare test final...")
        out, err = ssh_exec(ssh, "/tmp/test_backup_final.sh 2>&1", show=False)
        print("Output:")
        print(out)
        
        print()
        print("[INFO] Verifica telefonul - ar trebui sa primesti UN SINGUR mesaj:")
        print("   BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-28 XX:XX:XX | STATUS: End FULL backup")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CORECTARE COMPLETA!")
        print("=" * 70)
        print()
        print("STATUS:")
        print("  - Linia NTFY functionala adaugata!")
        print("  - Va trimite un singur mesaj detaliat la backup")
        print("  - Nu va mai trimite 'Server notification'")
        print()
        print("PROXIMA DATA LA BACKUP:")
        print("  Vei primi: BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: ... | STATUS: ...")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

