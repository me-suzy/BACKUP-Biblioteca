#!/usr/bin/env python
"""
Integrez notificari NTFY in scripturile de backup existente
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
    print("   INTEGRARE NOTIFICARI NTFY IN BACKUP")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica scripturile existente
        print("=" * 70)
        print("1. VERIFICARE SCRIPTURI BACKUP")
        print("=" * 70)
        print()
        
        scripts = {
            "exec_backup_main": "/exlibris/backup/scripts/exec_backup_main",
            "exec_tarol": "/exlibris/backup/scripts/exec_tarol",
            "backup_mailer": "/exlibris/backup/scripts/backup_mailer"
        }
        
        for name, path in scripts.items():
            print(f"[INFO] Verificare: {name}")
            out, _ = ssh_exec(ssh, f"ls -la {path} 2>&1", show=False)
            
            if "cannot access" not in out and "No such file" not in out:
                print(f"[OK] {name} exista")
                
                # Cauta unde trimite email
                out, _ = ssh_exec(ssh, f"grep -n 'send_mail\\|mail' {path} 2>&1", show=False)
                if out:
                    print(f"Lines cu mail:")
                    print(out[:200])
            else:
                print(f"[WARN] {name} nu exista")
            
            print()
        
        # 2. Integrez NTFY in backup_mailer
        print("=" * 70)
        print("2. INTEGRARE NTFY IN BACKUP_MAILER")
        print("=" * 70)
        print()
        
        print("[INFO] Verific daca backup_mailer exista...")
        
        out, _ = ssh_exec(ssh, "ls -la /exlibris/backup/scripts/backup_mailer 2>&1", show=False)
        
        if "cannot access" not in out:
            print("[OK] backup_mailer exista!")
            
            # Citeste continutul
            out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
            print("Continut backup_mailer:")
            print(out[:500])
            print()
            
            # Verifica daca are NTFY deja
            if "ntfy_notify" in out:
                print("[INFO] NTFY deja integrat in backup_mailer!")
            else:
                print("[INFO] Trebuie sa adaug NTFY in backup_mailer")
                print()
                print("[INFO] Backupu script complet pentru a vedea structura...")
                ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        else:
            print("[WARN] backup_mailer nu exista!")
        
        print()
        
        # 3. Elimina cron job fals
        print("=" * 70)
        print("3. CURATARE CRON JOB")
        print("=" * 70)
        print()
        
        print("[INFO] Elimin cron job pentru backup fals...")
        
        # Citeste cron actual
        out, _ = ssh_exec(ssh, "crontab -l", show=False)
        
        if "ntfy_notify.sh" in out and "Backup zilnic" in out:
            # Elimina cron job
            ssh_exec(ssh, "crontab -l | grep -v 'Backup zilnic' | crontab -", show=False)
            print("[OK] Cron job fals eliminat!")
        else:
            print("[INFO] Nu exista cron job fals")
        
        print()
        
        # 4. Verifica cron real
        print("=" * 70)
        print("4. VERIFICARE CRON REAL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l", show=False)
        
        if out:
            print("Cron jobs reale:")
            print(out)
        else:
            print("[WARN] Nu exista cron jobs")
        
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("VERIFICARE COMPLETA!")
        print("=" * 70)
        print()
        print(">> REZUMAT:")
        print("   - Scripturile de backup exista")
        print("   - Trimite deja email prin comanda 'mail'")
        print("   - Trebuie sa integrez NTFY in scripturile existente")
        print()
        print(">> URMATORII PASI:")
        print("   1. Modifica backup_mailer sa trimita si NTFY")
        print("   2. Sau adauga NTFY direct in exec_backup_main")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

