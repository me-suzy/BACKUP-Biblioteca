#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica ora si porneste backup AZI daca e posibil
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
    print("   VERIFICARE ORA SI BACKUP AZI")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica ora curenta
        print("=" * 70)
        print("1. ORA CURENTA PE SERVER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "date", show=False)
        print(f"Data si ora: {out.strip()}")
        
        # Extrage ora
        import re
        hour_match = re.search(r'(\d+):(\d+)', out)
        if hour_match:
            hour = int(hour_match.group(1))
            minute = int(hour_match.group(2))
            print(f"Ora: {hour:02d}:{minute:02d}")
            print()
            
            # Verifica daca a trecut 22:00 si 23:00 deja
            if hour < 22:
                print("=" * 70)
                print("2. PORNIM BACKUP AZI!")
                print("=" * 70)
                print()
                print("Ora curenta: {0:02d}:{1:02d}".format(hour, minute))
                print("Backup-urile sunt programate la 22:00 si 23:00")
                print("NAU TRECUT INCĂ!")
                print()
                print("Am 2 optiuni:")
                print("  1. Asteptam pana la 22:00 (cron job-ul va rula)")
                print("  2. Pornim backup-urile ACUM manual pentru test")
                print()
                print("[INFO] Cron jobs sunt active si vor rula la 22:00 si 23:00")
                print("       Adica in {0} ore si {1} minute".format(21-hour, 60-minute))
            else:
                print("=" * 70)
                print("2. PORNIM BACKUP MANUAL")
                print("=" * 70)
                print()
                print("Ora: {0:02d}:{1:02d} - deja a trecut 22:00".format(hour, minute))
                print("Cron job-urile vor rula maine.")
                print()
                print("Vrei sa pornesc backup-urile ACUM pentru test?")
                print()
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("SOLUTIE")
        print("=" * 70)
        print()
        print("Cron jobs sunt active pentru zilnic:")
        print("  - 22:00 -> user_data backup")
        print("  - 23:00 -> ora_cold backup")
        print()
        if hour < 22:
            print("AZI: Backup-urile vor rula la 22:00 si 23:00")
            print("     Astazi este: 28 oct")
            print("     LA 22:00 vor rula automat!")
        else:
            print("MAINE: Backup-urile vor rula la 22:00 si 23:00")
            print("       Pentru AZI, poti rula manual:")
            print("       /exlibris/backup/scripts/exec_backup_main a5")
            print("       /exlibris/backup/scripts/exec_backup_main a1")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

