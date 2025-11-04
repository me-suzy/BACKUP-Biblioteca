#!/usr/bin/env python
"""
Debug script NTFY pe server pentru a verifica ca functioneaza
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
    print("   DEBUG SCRIPT NTFY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica ca scriptul exista
        print("=" * 70)
        print("1. VERIFICARE SCRIPT NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -la /usr/local/bin/ntfy_send.sh", show=False)
        if "/usr/local/bin/ntfy_send.sh" in out:
            print("[OK] Script NTFY exista")
            print(out)
        else:
            print("[ERROR] Script NTFY nu exista!")
        
        print()
        
        # 2. Verifica continutul scriptului
        print("=" * 70)
        print("2. CONTINUT SCRIPT NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /usr/local/bin/ntfy_send.sh", show=False)
        print(out)
        print()
        
        # 3. Verifica curl
        print("=" * 70)
        print("3. VERIFICARE CURL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "which curl", show=False)
        if "curl" in out:
            print(f"[OK] Curl gasit: {out.strip()}")
            out, _ = ssh_exec(ssh, "curl --version", show=False)
            print(out)
        else:
            print("[ERROR] Curl nu este instalat!")
        
        print()
        
        # 4. Test direct curl cu NTFY
        print("=" * 70)
        print("4. TEST DIRECT CURL CU NTFY")
        print("=" * 70)
        print()
        
        topic = "bariasi-5f07b8571f7c"
        message = "Test direct curl cu NTFY de pe serverul Linux!"
        
        print(f"[INFO] Test curl cu topic: {topic}")
        print(f"[INFO] Message: {message}")
        print()
        
        cmd = 'curl -H "Title: Test Direct" -H "Priority: default" -d "{}" "https://ntfy.sh/{}" 2>&1'.format(message, topic)
        
        print("[INFO] Executare comanda curl...")
        print(f"[INFO] Comanda: {cmd[:80]}...")
        print()
        
        out, err = ssh_exec(ssh, cmd, show=False, timeout=10)
        
        print("Output:")
        print(out)
        
        if err:
            print("Error:")
            print(err)
        
        print()
        
        # 5. Test simplu
        print("=" * 70)
        print("5. TEST SIMPLU")
        print("=" * 70)
        print()
        
        print("[INFO] Test simplu cu echo...")
        out, _ = ssh_exec(ssh, 'echo "test simplu"', show=False)
        print(out)
        
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("DEBUG COMPLET!")
        print("=" * 70)
        print()
        print("Verifica output-ul de mai sus pentru detalii!")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Eroare: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[WARN] Script intrerupt.")
        sys.exit(130)

