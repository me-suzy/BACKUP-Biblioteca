#!/usr/bin/env python
"""
Test notificare NTFY de pe serverul Linux
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
        
        # Generare mesaj de test
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("=" * 70)
        print("TRIMITERE MESAJE DE TEST")
        print("=" * 70)
        print()
        
        test_messages = [
            {
                "title": "Test Notificare 1",
                "message": "Primul test de notificare NTFY de pe serverul Linux!\n\nTimestamp: {}\nServer: {}\nStatus: SUCCESS\n\nDaca primesti acest mesaj, NTFY functioneaza perfect!".format(timestamp, HOST)
            },
            {
                "title": "Test Notificare 2",
                "message": "Al doilea test de notificare!\n\nAcest mesaj confirma ca notificarile functioneaza!".format(timestamp)
            },
            {
                "title": "Test Final",
                "message": "Ultimul test de notificare!\n\nTelefonul ar trebui sa afiseze 3 notificari!\n\nToate functioneaza perfect!"
            }
        ]
        
        for i, test in enumerate(test_messages, 1):
            print(f"[INFO] Trimitere mesaj de test {i}/3...")
            print(f"[INFO] Title: {test['title']}")
            print()
            
            # Trimite notificare prin script
            cmd = '/usr/local/bin/ntfy_send.sh "{}"'.format(test["message"].replace('"', '\\"'))
            out, _ = ssh_exec(ssh, cmd, show=False, timeout=5)
            
            if out:
                print("Output:")
                print(out)
            
            print("[OK] Mesaj trimis!")
            print()
            
            # Asteapta 2 secunde intre mesaje
            import time
            if i < len(test_messages):
                print("[INFO] Astept 2 secunde...")
                time.sleep(2)
                print()
        
        ssh.close()
        
        print("=" * 70)
        print("TEST COMPLET!")
        print("=" * 70)
        print()
        print("[OK] Au fost trimise 3 mesaje de test!")
        print()
        print(">> VERIFICA TELEFONUL:")
        print("   - Ar trebui sa ai 3 notificari NTFY")
        print("   - Deschide aplicatia NTFY pe telefon")
        print("   - Ar trebui sa vezi 3 mesaje de test")
        print()
        print("Spune-mi daca ai primit notificarile!")
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

