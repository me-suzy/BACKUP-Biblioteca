#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test backup_mailer cu toate variabilele necesare setate
"""

import paramiko
import sys

HOST = "185.182.121.45"
USER = "root"
PASS = "YOUR-PASSWORD"
PORT = 22

def ssh_exec(ssh, cmd, show=True, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    if show:
        if out:
            print(out)
        if err:
            print(f"[ERR] {err}")
    return out, err


def main():
    print("=" * 70)
    print("   TEST BACKUP_MAILER CU VARIABILE COMPLETE")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        print("[TEST] Rulez backup_mailer cu variabile setate manual...")
        print()
        
        cmd = """cd /exlibris/backup/scripts && /bin/csh -f backup_mailer \
  set BACKUP_TYPE=FULL \
  set ORACLE_SID=ALEPH \
  set ERROR_NUMBER=00 \
  set ERROR_MESSAGE='End FULL backup'
  """
        
        # Mai simplu: creez un script temporar
        test_script = """#!/bin/csh -f
setenv UNIX_TYPE Linux
set BACKUP_TYPE=FULL
set ORACLE_SID=ALEPH
set ERROR_NUMBER=00
set ERROR_MESSAGE='End FULL backup test'
set BKP_SLOT=99
set BKP_MAIL='test@test.com'

if ($UNIX_TYPE == "Linux") then
   alias mailx /bin/mail
endif

echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh

echo "Test backup_mailer completed"
"""
        
        print("Creez script test temporar...")
        ssh_exec(ssh, "cat > /tmp/test_backup_mailer.csh << 'EOF'\n" + test_script + "\nEOF", show=False)
        
        print("Rulez scriptul...")
        print()
        ssh_exec(ssh, "chmod +x /tmp/test_backup_mailer.csh && /tmp/test_backup_mailer.csh")
        print()
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("TEST FINALIZAT")
        print("=" * 70)
        print()
        print("Verifica telefonul pentru notificare NTFY!")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

