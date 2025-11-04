#!/usr/bin/env python
"""
Citeste scriptul NTFY de pe server si verifica limita de lungime
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
    print("   VERIFICARE SCRIPT NTFY SI LIMITA LUNGIME")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Citeste scriptul NTFY
        print("=" * 70)
        print("1. CONTINUT SCRIPT NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /usr/local/bin/ntfy_notify.sh", show=False)
        print(out)
        
        print()
        
        # Testeaza mesaj SCURT
        print("=" * 70)
        print("2. TEST MESAJ SCURT")
        print("=" * 70)
        print()
        
        msg_short = "TEST SCURT"
        out, err = ssh_exec(ssh, f"/usr/local/bin/ntfy_notify.sh '{msg_short}' 2>&1", show=False)
        print(f"Mesaj: {msg_short}")
        print(f"Rezultat: {out}")
        
        print()
        
        # Testeaza mesaj LUNG (simulare mesaj backup)
        print("=" * 70)
        print("3. TEST MESAJ LUNG (simulare backup)")
        print("=" * 70)
        print()
        
        msg_long = "BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-28 01:23:45 | STATUS: End FULL backup"
        out, err = ssh_exec(ssh, f"/usr/local/bin/ntfy_notify.sh '{msg_long}' 2>&1", show=False)
        print(f"Mesaj: {msg_long}")
        print(f"Rezultat: {out}")
        
        print()
        print("[INFO] Verifica telefonul - ar trebui sa primesti 2 notificari")
        print()
        
        # Verifica backup_mailer - daca exista o problema cu formatul
        print("=" * 70)
        print("4. LINIA NTFY DIN BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '98,101p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linia NTFY si context:")
        print(out)
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("VERIFICARE COMPLETA!")
        print("=" * 70)
        print()
        print("ANALIZA:")
        print("  - Mesajul backup este prea lung?")
        print("  - Formatul este corect?")
        print("  - Variabilele ${BACKUP_TYPE}, ${ORACLE_SID}, etc. sunt definite?")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

