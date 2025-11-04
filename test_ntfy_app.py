#!/usr/bin/env python
"""
Test NTFY - trimite notificare si verifica
"""

import paramiko
import sys
import time

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
    print("   TEST NOTIFICARE NTFY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Trimite 3 notificari diferite
        print("=" * 70)
        print("   TRIMITERE 3 NOTIFICARI DE TEST")
        print("=" * 70)
        print()
        
        for i in range(1, 4):
            msg = f"TEST {i} - Backup system notification - Timestamp: {int(time.time())}"
            print(f"[INFO] Trimitere mesaj {i}...")
            out, err = ssh_exec(ssh, f"/usr/local/bin/ntfy_notify.sh '{msg}' 2>&1", show=False)
            print(f"Output: {out}")
            if err:
                print(f"Error: {err}")
            print()
            time.sleep(2)
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("TEST COMPLET!")
        print("=" * 70)
        print()
        print("[INFO] Am trimis 3 notificari!")
        print()
        print("VERIFICA TELEFONUL ACUM:")
        print("  1. Deschide aplicatia NTFY")
        print("  2. Verifica daca esti subscribe la topic: bariasi-5f07b8571f7c")
        print("  3. Verifica daca primesti 3 notificari")
        print()
        print("DACA NU PRIMESTI NOTIFICARI:")
        print("  - Aplicația NTFY nu e instalata pe telefon?")
        print("  - Nu esti subscribe la topic-ul corect?")
        print("  - Telefonul nu are internet?")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

