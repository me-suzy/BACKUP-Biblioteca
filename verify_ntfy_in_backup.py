#!/usr/bin/env python
"""
Verifica exact ce a fost adaugat in backup_mailer pentru NTFY
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
    print("   VERIFICARE NTFY IN BACKUP_MAILER")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Citeste tot scriptul
        print("=" * 70)
        print("1. CONTINUT COMPLET BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        
        # 2. Cauta toate liniile cu NTFY
        print("=" * 70)
        print("2. LINII CU NTFY")
        print("=" * 70)
        print()
        
        out_grep, _ = ssh_exec(ssh, "grep -n 'ntfy' /exlibris/backup/scripts/backup_mailer", show=False)
        print(out_grep)
        print()
        
        # 3. Afiseaza contextul pentru fiecare NTFY
        print("=" * 70)
        print("3. CONTEXT PENTRU NTFY")
        print("=" * 70)
        print()
        
        lines = out.split('\n')
        for i, line in enumerate(lines):
            if 'ntfy' in line.lower():
                # Afiseaza 5 linii inainte si dupa
                start = max(0, i - 5)
                end = min(len(lines), i + 6)
                print(f"--- Linia {i+1} ---")
                for j in range(start, end):
                    marker = ">>>" if j == i else "   "
                    print(f"{marker} {j+1}: {lines[j]}")
                print()
        
        # 4. Cauta mailx
        print("=" * 70)
        print("4. LINII CU MAILX")
        print("=" * 70)
        print()
        
        out_mailx, _ = ssh_exec(ssh, "grep -n 'mailx' /exlibris/backup/scripts/backup_mailer", show=False)
        print(out_mailx)
        print()
        
        # 5. Afiseaza structura completa unde se trimite email si NTFY
        print("=" * 70)
        print("5. STRUCTURA TRIMITERII EMAIL SI NTFY")
        print("=" * 70)
        print()
        
        for i, line in enumerate(lines):
            if 'mailx -s' in line:
                print(f"LINIA {i+1}: Email trimis")
                print(f"  {line}")
                print()
                
                # Verifica ce urmeaza dupa email
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip():
                        print(f"  {j+1}: {lines[j]}")
                        if 'ntfy' in lines[j].lower():
                            print("     ^^^^ ACEASTA ESTE NOTIFICAREA NTFY ^^^^")
                            print()
                            # Afiseaza urmatoarele 5 linii
                            for k in range(j+1, min(j+6, len(lines))):
                                if lines[k].strip():
                                    print(f"  {k+1}: {lines[k]}")
                            break
                print()
        
        ssh.close()
        
        print("=" * 70)
        print("VERIFICARE COMPLETA!")
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
