#!/usr/bin/env python
"""
Trimitere email simplu prin sendmail direct
"""

import paramiko
import sys
from datetime import datetime

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
    print("   TRIMITERE EMAIL TEST")
    print("=" * 70)
    print()
    
    email = input("Adresa de email pentru test (sau 'skip'): ").strip()
    
    if email.lower() == "skip":
        return 0
    
    print()
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[INFO] Trimitere email la: {email}")
        print()
        
        subject = "Test Notificare Server Linux"
        body = f"""Test notificare de pe serverul Linux!

Timestamp: {timestamp}
Server: {HOST}
Status: SUCCESS

Acesta este un mesaj de test pentru a confirma ca notificarile functioneaza!
"""
        
        cmd = f'''(
echo "To: {email}"
echo "From: root@{HOST}"
echo "Subject: {subject}"
echo ""
echo "{body}"
) | sendmail -t -v
'''
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=15)
        
        print("Output:")
        print(out)
        print()
        
        print("[OK] Email trimis!")
        print()
        
        ssh.close()
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

