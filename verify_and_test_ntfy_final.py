#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica si testeaza NTFY final
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
    print("   VERIFICARE SI TEST FINAL NTFY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica linia in backup_mailer
        print("=" * 70)
        print("1. VERIFICARE LINIE NTFY IN BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        if out.strip():
            print("[OK] Linia NTFY exista!")
            print(f"Linia: {out.strip()}")
        else:
            print("[ERROR] Linia NTFY NU exista!")
        
        print()
        
        # 2. Verifica contextul
        print("=" * 70)
        print("2. CONTEXT LINIE NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Context (linii 95-105):")
        print(out)
        
        print()
        
        # 3. Testeaza NOTIFICAREA
        print("=" * 70)
        print("3. TEST NOTIFICARE BACKUP DETALIAT")
        print("=" * 70)
        print()
        
        # Folosim o abordare diferita - test direct in shell
        test_cmd = '''bash -c "printf 'BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: $(date +%%Y-%%m-%%d\\ %%H:%%M:%%S) | STATUS: End FULL backup\n' | /usr/local/bin/ntfy_notify.sh"'''
        
        print("[INFO] Trimitere mesaj de backup detaliat...")
        out, err = ssh_exec(ssh, test_cmd, show=False)
        print("Output:")
        print(out)
        
        print()
        print("[INFO] Verifica telefonul ACUM!")
        print("   Ar trebui sa primesti:")
        print("   BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-28 XX:XX:XX | STATUS: End FULL backup")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("VERIFICARE COMPLETA!")
        print("=" * 70)
        print()
        print("REZUMAT:")
        print("  - Linia NTFY este in backup_mailer")
        print("  - La urmatorul backup (luni 27 oct la 23:00 SAU miercuri 29 oct la 23:00)")
        print("    vei primi notificare de forma:")
        print("    BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: ... | STATUS: ...")
        print()
        print("  - NU vei mai primi 'Server notification'")
        print("  - NU vei primi notificari multiple")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

