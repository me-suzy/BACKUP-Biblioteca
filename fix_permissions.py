#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix permissions pentru backup_mailer
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
    print("   FIX PERMISSIONS BACKUP_MAILER")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verificare permisiuni curente
        print("=" * 70)
        print("1. PERMISIUNI CURENTE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -l /exlibris/backup/scripts/backup_mailer", show=False)
        print(out)
        
        # 2. Fix permisiuni
        print()
        print("=" * 70)
        print("2. SETARE PERMISIUNI")
        print("=" * 70)
        print()
        
        ssh_exec(ssh, "chmod 755 /exlibris/backup/scripts/backup_mailer")
        print("[OK] Permisiuni setate!")
        
        # 3. Verificare dupa
        print()
        print("=" * 70)
        print("3. PERMISIUNI NOI")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -l /exlibris/backup/scripts/backup_mailer", show=False)
        print(out)
        
        # 4. Test manual
        print()
        print("=" * 70)
        print("4. TEST MANUAL BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "head -5 /exlibris/backup/scripts/backup_mailer", show=False)
        print(out)
        
        # 5. Verificare shebang
        print()
        print("=" * 70)
        print("5. VERIFICARE SHEBANG")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "head -1 /exlibris/backup/scripts/backup_mailer", show=False)
        print(out)
        if not out.strip().startswith("#!"):
            print("\n[PROBLEMA] Lipseste shebang!")
            print("Adaug shebang...")
            
            # Read full file
            out_full, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
            
            # Check if already has shebang
            if not out_full.strip().startswith("#!/"):
                ssh_exec(ssh, "echo '#!/bin/csh' > /tmp/backup_mailer_fixed && cat /exlibris/backup/scripts/backup_mailer >> /tmp/backup_mailer_fixed && mv /tmp/backup_mailer_fixed /exlibris/backup/scripts/backup_mailer")
                print("[OK] Shebang adaugat!")
        
        # 6. Test exec
        print()
        print("=" * 70)
        print("6. TEST EXECUTARE")
        print("=" * 70)
        print()
        
        ssh_exec(ssh, "cd /exlibris/backup/scripts && /bin/csh -c 'source backup_mailer' 2>&1 | head -20", show=False)
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("FIX COMPLETAT")
        print("=" * 70)
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

