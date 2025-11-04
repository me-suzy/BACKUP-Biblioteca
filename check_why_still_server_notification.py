#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica de ce inca trimite "Server notification"
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
    print("   CAUTARE CAUZA 'SERVER NOTIFICATION'")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Testeaza manual direct in bash
        print("=" * 70)
        print("1. TEST DIRECT CU VARIABILE DEFINITE")
        print("=" * 70)
        print()
        
        # Folosim parametri escape corect
        test_cmd = r'''bash -c 'export BACKUP_TYPE="FULL"; export ORACLE_SID="ALEPH"; export ERROR_NUMBER="00"; export ERROR_MESSAGE="End FULL backup"; echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: $(date +%Y-%m-%d\ %H:%M:%S) | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh' '''
        
        print("[INFO] Executare test bash...")
        out, err = ssh_exec(ssh, test_cmd, show=False)
        print("Output:")
        print(out)
        
        print()
        print("[INFO] Verifica telefonul - ce ai primit?")
        print()
        
        # 2. Testeaza C-shell direct
        print("=" * 70)
        print("2. TEST CU C-SHELL")
        print("=" * 70)
        print()
        
        csh_test = '''csh -c 'set BACKUP_TYPE="FULL"; set ORACLE_SID="ALEPH"; set ERROR_NUMBER="00"; set ERROR_MESSAGE="End FULL backup"; echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: \\`date +%Y-%m-%d\\ %H:%M:%S\\` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh' '''
        
        print("[INFO] Executare test C-shell...")
        out, err = ssh_exec(ssh, csh_test, show=False)
        print("Output:")
        print(out)
        
        print()
        print("[INFO] Verifica telefonul din nou!")
        print()
        
        # 3. Citeste backup_mailer actual
        print("=" * 70)
        print("3. BACKUP_MAILER ACTUAL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer | grep -A 5 -B 5 'ntfy'", show=False)
        print("Linii cu NTFY:")
        print(out)
        
        # 4. Test EXACT ce face backup_mailer
        print()
        print("=" * 70)
        print("4. TEST EXACT DIN BACKUP_MAILER")
        print("=" * 70)
        print()
        
        # Citeste linia exacta din backup_mailer
        out, _ = ssh_exec(ssh, "grep -n 'echo.*ntfy' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linia EXACTA din backup_mailer:")
        print(out)
        
        if out.strip():
            # Extrage linia completa
            line_num = out.split(':')[0]
            out, _ = ssh_exec(ssh, f"sed -n '{line_num}p' /exlibris/backup/scripts/backup_mailer", show=False)
            print("Continut:")
            print(out)
            print()
            
            # Testeaza EXACT acea linie
            print("[INFO] Executare linia EXACTA...")
            print("(setam variabilele mai intai)")
            
            test_exact = f'''#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"

{out.strip()}
'''
            
            sftp = ssh.open_sftp()
            f = sftp.open('/tmp/test_exact_line.sh', 'w')
            f.write(test_exact)
            f.close()
            sftp.close()
            
            ssh_exec(ssh, "chmod +x /tmp/test_exact_line.sh", show=False)
            out, err = ssh_exec(ssh, "/tmp/test_exact_line.sh 2>&1", show=False)
            print("Output:")
            print(out)
            
            print()
            print("[INFO] Verifica telefonul - acesta e mesajul EXACT care va fi trimis!")
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("DIAGNOSTIC COMPLET!")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

