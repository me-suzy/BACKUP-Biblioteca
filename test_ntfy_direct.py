#!/usr/bin/env python
"""
Test direct NTFY cu curl vechi din server
"""

import paramiko
import sys

HOST = "185.182.121.45"
USER = "root"
PASS = "YOUR-PASSWORD"
PORT = 22
TOPIC = "bariasi-5f07b8571f7c"


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
    print("   TEST DIRECT NTFY")
    print("=" * 70)
    print()
    
    print(f"[INFO] Topic: {TOPIC}")
    print()
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Test cu base64 (compatibil cu OpenSSL vechi)
        print("=" * 70)
        print("TEST BASE64")
        print("=" * 70)
        print()
        
        # Mesaj simplu
        message = "Test 123"
        
        # Folosim curl cu HTTP simplu (fara HTTPS)
        print(f"[INFO] Mesaj: {message}")
        print()
        
        cmd = f'curl -s -X POST -d "{message}" "http://ntfy.sh/{TOPIC}"'
        
        print("[INFO] Trimitere...")
        out, err = ssh_exec(ssh, cmd, show=False, timeout=5)
        
        print("Output:")
        print(out)
        
        if err:
            print("Error:")
            print(err)
        
        print()
        
        # Test cu telnet pentru HTTP simplu
        print("=" * 70)
        print("TEST TELNET")
        print("=" * 70)
        print()
        
        print("[INFO] Test telnet cu ntfy.sh...")
        
        telnet_cmd = f'''telnet ntfy.sh 80 <<EOF
POST /{TOPIC} HTTP/1.1
Host: ntfy.sh
Content-Length: {len(message)}

{message}
EOF
'''
        
        out, _ = ssh_exec(ssh, telnet_cmd, show=False, timeout=5)
        
        print("Output:")
        print(out[:500])
        
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("TEST COMPLET!")
        print("=" * 70)
        print()
        print(">> VERIFICA TELEFONUL:")
        print("   - Deschide aplicatia NTFY")
        print("   - Tema: {TOPIC}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

