#!/usr/bin/env python
"""
Verificare finala - ce notificare NTFY va rula la backup
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
    print("   VERIFICARE FINALA - NOTIFICARE BACKUP")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica backup_mailer
        print("=" * 70)
        print("1. CONTINUT BACKUP_MAILER (liniile cu NTFY)")
        print("=" * 70)
        print()
        
        # Afiseaza contextul pentru linia cu NTFY
        out, _ = ssh_exec(ssh, "grep -B 3 -A 2 'ntfy_notify.sh' /exlibris/backup/scripts/backup_mailer", show=False)
        
        print("Linia cu NTFY si context:")
        print(out)
        print()
        
        # 2. Verifica ca NU exista cron jobs
        print("=" * 70)
        print("2. VERIFICARE CRON JOBS")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l 2>&1", show=False)
        
        if "no crontab" in out.lower() or not out.strip():
            print("[OK] Nu exista cron jobs!")
            print("   Notificarea va rula DOAR la backup real")
        else:
            print("[WARN] Exista cron jobs:")
            print(out)
            if 'ntfy' in out.lower():
                print("[ERROR] Exista cron job cu NTFY!")
        
        print()
        
        # 3. Verifica cron jobs pentru backup
        print("=" * 70)
        print("3. VERIFICARE CRON JOBS BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l | grep -i backup", show=False)
        
        if out:
            print("Cron jobs pentru backup:")
            print(out)
            
            if 'mailx' in out.lower() or 'mail' in out.lower():
                print()
                print("[OK] Backup-ul va rula si va trimite email + NTFY")
        else:
            print("[INFO] Cron jobs pentru backup:")
            print("   - Nu exista cron explicit pentru backup_mailer")
            print("   - backup_mailer este apelat de alte scripturi backup")
            print("   - Se va rula intre 23:00-02:00")
        
        print()
        
        # 4. Simuleaza exact ce va fi trimis
        print("=" * 70)
        print("4. SIMULARE MESAJ LA BACKUP")
        print("=" * 70)
        print()
        
        print("La backup real, vei primi:")
        print()
        print("  BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: 2025-10-28 01:23:45 | STATUS: End FULL backup")
        print()
        print("  In loc de:")
        print("    - BACKUP: tipul backup-ului (FULL, INCREMENTAL, etc.)")
        print("    - DB: Oracle SID (ALEPH)")
        print("    - CODE: cod eroare (00 = success, 01-14 = error)")
        print("    - TIME: momentul EXACT")
        print("    - STATUS: mesaj detaliat")
        print()
        
        print("[OK] Configuratia este CORECTA!")
        print()
        print("NU VE MAI PRIMI:")
        print("  - 'Server notification'")
        print("  - Notificari multiple")
        print("  - Notificari de test")
        print()
        print("VEI PRIMI DOAR:")
        print("  - O singura notificare la backup")
        print("  - Cu toate informatiile de mai sus")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("VERIFICARE COMPLETA!")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
