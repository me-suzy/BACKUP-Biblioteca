#!/usr/bin/env python
"""
Trimitere multiple mesaje NTFY pentru test
"""

import paramiko
import sys
import time
from datetime import datetime

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
    print("   TRIMITERE MESAJE TEST NTFY")
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
        
        messages = [
            "Test 1: Notificare de pe serverul Linux!",
            "Test 2: Second notification test!",
            "Test 3: Acesta este al treilea mesaj!",
            "Test 4: Functioneaza perfect NTFY!",
            "Test 5: Ultimul test de confirmare!"
        ]
        
        for i, message in enumerate(messages, 1):
            print("=" * 70)
            print(f"TRIMITERE MESAJ {i}/5")
            print("=" * 70)
            print()
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"[INFO] Mesaj {i}: {message}")
            print(f"[INFO] Timestamp: {timestamp}")
            print()
            
            cmd = f'curl -s -X POST -d "{message} [{timestamp}]" "http://ntfy.sh/{TOPIC}"'
            
            print("[INFO] Trimitere...")
            out, err = ssh_exec(ssh, cmd, show=False, timeout=5)
            
            if out and '"message"' in out:
                print(f"[OK] Mesaj {i} trimis cu succes!")
            else:
                print(f"[WARN] Mesaj {i} - verificare necesara")
                if out:
                    print(f"Output: {out[:100]}")
            
            print()
            
            # Asteapta 1 secunda intre mesaje
            if i < len(messages):
                time.sleep(1)
        
        ssh.close()
        
        print("=" * 70)
        print("TRIMITERE COMPLETA!")
        print("=" * 70)
        print()
        print("[OK] Au fost trimise 5 mesaje de test!")
        print()
        print(">> VERIFICA TELEFONUL:")
        print("   - Ar trebui sa vezi 5 notificari NTFY")
        print("   - Deschide aplicatia NTFY")
        print("   - Tema: {TOPIC}")
        print()
        print("Spune-mi cat de repede ai primit notificarile!")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

