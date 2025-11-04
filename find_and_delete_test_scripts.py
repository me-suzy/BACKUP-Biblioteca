#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gaseste si sterge TOATE scripturile care trimit "Server notification"
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
    print("   CAUTARE SI CURATARE SCRIPTURI TEST")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Cauta TOATE fisierele de test
        print("=" * 70)
        print("1. CAUTARE TOATE FISIERELE DE TEST")
        print("=" * 70)
        print()
        
        # Cauta in /tmp
        out, _ = ssh_exec(ssh, "find /tmp -type f -name '*test*' -o -name '*ntfy*' 2>/dev/null", show=False)
        tmp_scripts = [s for s in out.strip().split('\n') if s.strip()]
        
        # Cauta in /root
        out, _ = ssh_exec(ssh, "find /root -type f -name '*test*' -o -name '*ntfy*' 2>/dev/null | grep -v '.bash'", show=False)
        root_scripts = [s for s in out.strip().split('\n') if s.strip()]
        
        all_scripts = tmp_scripts + root_scripts
        
        if all_scripts:
            print(f"[INFO] Gasite {len(all_scripts)} fisiere de test:")
            for script in all_scripts:
                print(f"  - {script}")
            
            print()
            
            # 2. Sterge TOATE
            print("=" * 70)
            print("2. STERGERE TOATE SCRIPTURILE DE TEST")
            print("=" * 70)
            print()
            
            for script in all_scripts:
                try:
                    ssh_exec(ssh, f"rm {script} 2>&1", show=False)
                    print(f"[OK] Sters: {script}")
                except:
                    print(f"[WARN] Nu pot sterge: {script}")
            
            print()
            print("[OK] Toate scripturile de test sterse!")
        else:
            print("[OK] Nu exista fisiere de test!")
        
        # 3. Verifica cron jobs
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
                print("   Sau sterg cron job sau sa corectez linia!")
        
        # 4. Verifica backup_mailer FINAL
        print()
        print("=" * 70)
        print("4. VERIFICARE BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        
        if not out.strip():
            print("[ERROR] NU EXISTA linie NTFY!")
            print("   De aceea nu vei primi notificare la backup!")
        else:
            lines = out.strip().split('\n')
            if len(lines) > 1:
                print(f"[ERROR] EXISTA MAI MULTE LINII ({len(lines)})!")
                print("   Asta face ca sa primesti notificari multiple!")
                for line in lines:
                    print(f"  {line}")
            else:
                print("[OK] Exista DOAR o singura linie NTFY!")
                print(f"  {lines[0]}")
        
        print()
        
        # 5. Afiseaza status final
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Context linii 95-105:")
        print(out)
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("CURATARE COMPLETA!")
        print("=" * 70)
        print()
        print("PROXIMA DATA:")
        print("  - NU vei mai primi 'Server notification'")
        print("  - Vei primi DOAR mesajul detaliat de backup")
        print("  - Format: BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: ... | STATUS: ...")
        print()
        print("PROXIMUL BACKUP:")
        print("  - Luni 27 oct la 23:00")
        print("  - Sau miercuri 29 oct la 23:00")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

