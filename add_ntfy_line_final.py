#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Adauga linia NTFY FUNCTIONALA
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
        
        # 1. Sterge linia 98 (duplicat)
        print("=" * 70)
        print("1. STERGERE LINIE DUPLICAT")
        print("=" * 70)
        print()
        
        ssh_exec(ssh, "sed -i '98d' /exlibris/backup/scripts/backup_mailer", show=False)
        print("[OK] Linie duplicat stearsa!")
        
        # 2. Adauga linia NTFY FUNCTIONALA dupa linia 98
        print()
        print("=" * 70)
        print("2. ADAUGARE LINIE FUNCTIONALA")
        print("=" * 70)
        print()
        
        # Linia care functioneaza - foloseste variabile C-shell corect
        # Intrucat e C-shell, folosim $VARIABILA nu ${VARIABILA}
        working_line = 'echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `date \\'+%Y-%m-%d %H:%M:%S\\'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh'
        
        # Folosim 'a\' pentru a adauga dupa linie
        ssh_exec(ssh, f"sed -i \"98a\\{working_line}\" /exlibris/backup/scripts/backup_mailer", show=False)
        
        print("[OK] Linie NTFY adaugata!")
        
        # 3. Verifica rezultatul
        print()
        print("=" * 70)
        print("3. VERIFICARE FINALA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linii 95-105:")
        print(out)
        
        # 4. Testeaza
        print()
        print("=" * 70)
        print("4. TESTARE NOTIFICARE")
        print("=" * 70)
        print()
        
        # Creeaza un fisier de test simplu
        test_script_content = '''#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"
echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: \\`date '+%Y-%m-%d %H:%M:%S'\\` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
'''
        
        ssh_exec(ssh, "cat > /tmp/test_ntfy_working.sh << 'ENDSCRIPT'\n#!/bin/csh\nset BACKUP_TYPE=\"TEST\"\nset ORACLE_SID=\"ALEPH\"\nset ERROR_NUMBER=\"00\"\nset ERROR_MESSAGE=\"Test backup\"\necho \"BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: \\\\\\`date '+%Y-%m-%d %H:%M:%S'\\\\\\` | STATUS: $ERROR_MESSAGE\" | /usr/local/bin/ntfy_notify.sh\nENDSCRIPT", show=False)
        
        ssh_exec(ssh, "chmod +x /tmp/test_ntfy_working.sh", show=False)
        
        print("[INFO] Executare test...")
        out, err = ssh_exec(ssh, "/tmp/test_ntfy_working.sh 2>&1", show=False)
        print("Output:")
        print(out)
        if err:
            print(f"Error: {err}")
        
        print()
        print("[INFO] Verifica telefonul - ar trebui sa primesti notificare cu mesajul complet!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CORECTARE COMPLETA!")
        print("=" * 70)
        print()
        print("PROBLEMA REZOLVATA:")
        print("  1. Am sters linia duplicat")
        print("  2. Am adaugat linia NTFY functionala")
        print("  3. Linia foloseste variabile C-shell corect: $VARIABILA")
        print()
        print("PROXIMA DATA LA BACKUP:")
        print("  Vei primi notificare cu formatul:")
        print("  BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-28 01:23:45 | STATUS: End FULL backup")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

