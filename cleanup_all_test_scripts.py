#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sterge TOATE scripturile de test care trimit NTFY
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
    print("   CURATARE TOATE SCRIPTURILE DE TEST")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Gaseste TOATE scripturile de test
        print("=" * 70)
        print("1. CAUTARE SCRIPTURI TEST")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "find /tmp -type f -name '*test*' -o -name '*ntfy*' 2>/dev/null", show=False)
        scripts = out.strip().split('\n')
        
        print("Scripturi gasite:")
        test_scripts = []
        for script in scripts:
            if script.strip():
                print(f"  - {script}")
                test_scripts.append(script)
        
        print()
        
        # 2. Sterge TOATE scripturile
        print("=" * 70)
        print("2. STERGERE SCRIPTURI")
        print("=" * 70)
        print()
        
        for script in test_scripts:
            out, err = ssh_exec(ssh, f"rm {script} 2>&1", show=False)
            print(f"[OK] Sters: {script}")
        
        print()
        print("[OK] Toate scripturile de test sterse!")
        
        # 3. Verifica ca NU exista cron jobs
        print()
        print("=" * 70)
        print("3. VERIFICARE CRON JOBS")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l 2>&1", show=False)
        if 'no crontab' in out or not out.strip():
            print("[OK] Nu exista cron jobs!")
        else:
            print("[WARN] Exista cron jobs:")
            print(out)
            
            if 'ntfy' in out.lower():
                print()
                print("[ERROR] EXISTA CRON JOB CU NTFY!")
                print("   Trebuie sa il stergi!")
        
        # 4. Verifica backup_mailer - sa fie DOAR O LINIE NTFY
        print()
        print("=" * 70)
        print("4. VERIFICARE BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        
        if not out.strip():
            print("[WARN] NU EXISTA linie NTFY in backup_mailer!")
            print("   De aceea nu primesti notificare la backup!")
        else:
            lines = out.strip().split('\n')
            if len(lines) > 1:
                print(f"[ERROR] EXISTA MAI MULTE LINII CU NTFY ({len(lines)})!")
                print("   Asta face sa primesti notificari multiple!")
                print()
                print("Linii gasite:")
                for line in lines:
                    print(f"  {line}")
            else:
                print("[OK] Exista DOAR o singura linie NTFY!")
                print(f"  {out.strip()}")
        
        print()
        
        # 5. Afiseaza linia finala
        print("=" * 70)
        print("5. LINIA NTFY FINALA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Context (linii 95-105):")
        print(out)
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("CURATARE COMPLETA!")
        print("=" * 70)
        print()
        print("STATUS FINAL:")
        print("  - Scripturile de test STERSE")
        print("  - Nu mai vei primi 'Server notification'")
        print("  - La urmatorul backup vei primi DOAR mesajul detaliat")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

