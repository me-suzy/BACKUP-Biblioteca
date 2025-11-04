#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test problema cu pipe in C-shell
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
    print("   TEST PIPE ISSUE")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        print("[TEST 1] Test cu bash direct...")
        print()
        ssh_exec(ssh, """bash -c 'echo "BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: $(date "+%Y-%m-%d %H:%M:%S") | STATUS: End FULL backup test" | /usr/local/bin/ntfy_notify.sh'""")
        print()
        
        print("[TEST 2] Test prin fisier temporar (ca in csh)...")
        print()
        ssh_exec(ssh, """bash -c 'echo "BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: $(date "+%Y-%m-%d %H:%M:%S") | STATUS: End FULL backup test2" > /tmp/ntfy_msg.txt && cat /tmp/ntfy_msg.txt | /usr/local/bin/ntfy_notify.sh'""")
        print()
        
        print("[TEST 3] Verific ce primeste scriptul NTFY...")
        print()
        ssh_exec(ssh, """bash -c 'echo "Test mesaj special" | /usr/local/bin/ntfy_notify.sh 2>&1'""")
        print()
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("TEST FINALIZAT")
        print("=" * 70)
        print()
        print("Verifica telefonul pentru notificari!")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

