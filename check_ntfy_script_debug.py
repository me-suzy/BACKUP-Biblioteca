#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica exact ce primeste ntfy_notify.sh
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
    print("   DEBUG NTFY SCRIPT")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        print("[1] Verific continutul ntfy_notify.sh...")
        print()
        ssh_exec(ssh, "cat /usr/local/bin/ntfy_notify.sh")
        print()
        
        print("[2] TEST: Rulez direct echo cu comanda exacta din backup_mailer...")
        print()
        ssh_exec(ssh, """echo "BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: `/bin/date '+%Y-%m-%d %H:%M:%S'` | STATUS: End FULL backup test" | /usr/local/bin/ntfy_notify.sh""")
        print()
        
        print("[3] Verific daca exista probleme cu pipe in csh...")
        print()
        ssh_exec(ssh, """echo "Test direct NTFY" | curl -d @- http://ntfy.sh/bariasi-5f07b8571f7c""")
        print()
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("DEBUG FINALIZAT")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

