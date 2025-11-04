#!/usr/bin/env python
"""
Test notificare NTFY detaliata cu informatii complete
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
    print("   TEST NOTIFICARE NTFY DETALIATA")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Creaza mesaj detaliat ca cel din scriptul modificat
        timestamp = ssh_exec(ssh, "date '+%Y-%m-%d %H:%M:%S'", show=False)[0].strip()
        
        detailed_message = f"""Backup was successful on : FULL

Oracle DB: ALEPH
Type: FULL
Status: End FULL backup
Code: 00
Time: {timestamp}

Verifica: /tmp/tmpmail00"""

        print("=" * 70)
        print("MESAJ DETALIAT DE TRIMIS:")
        print("=" * 70)
        print(detailed_message)
        print()
        
        print("=" * 70)
        print("TRIMITERE NOTIFICARE...")
        print("=" * 70)
        print()
        
        # Scrie mesajul in fisier
        ssh_exec(ssh, f'echo "{detailed_message}" > /tmp/test_ntfy_msg.txt', show=False)
        
        # Trimite prin NTFY
        ssh_exec(ssh, 'cat /tmp/test_ntfy_msg.txt | /usr/local/bin/ntfy_notify.sh', show=False)
        
        print("[OK] Notificare trimisa!")
        print()
        print("Ar trebui sa primesti pe telefon un mesaj cu toate detaliile de mai sus.")
        print()
        print("INFORMATII UNICE DIN MESAJ:")
        print("  - Timestamp exact: " + timestamp)
        print("  - Cod eroare: 00 (succes)")
        print("  - Tip backup: FULL")
        print("  - Oracle SID: ALEPH")
        print("  - Loc verificare: /tmp/tmpmail00")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("TEST COMPLET!")
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
