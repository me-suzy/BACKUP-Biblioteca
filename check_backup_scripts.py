#!/usr/bin/env python
"""
Verific scripturile de backup existente pentru a integra notificarile
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
    print("   VERIFICARE BACKUP EXISTENTE")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica cron jobs pentru backup
        print("=" * 70)
        print("1. CRON JOBS PENTRU BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l", show=False)
        
        if out:
            print("Cron jobs existente:")
            print(out)
        
        print()
        
        # 2. Verifica scripturile de backup
        print("=" * 70)
        print("2. SCRIPTURI BACKUP")
        print("=" * 70)
        print()
        
        backup_scripts = [
            "/exlibris/backup/scripts/exec_backup_main",
            "/exlibris/backup/scripts/exec_tarol"
        ]
        
        for script in backup_scripts:
            print(f"[INFO] Verificare: {script}")
            
            # Verifica daca exista
            out, _ = ssh_exec(ssh, f"ls -la {script} 2>&1", show=False)
            
            if "No such file" not in out and "cannot access" not in out:
                print(f"[OK] Script exista: {script}")
                
                # Verifica content
                print(f"[INFO] Continut script:")
                out, _ = ssh_exec(ssh, f"head -50 {script}", show=False)
                print(out[:500])
                print()
                
                # Verifica daca trimite email
                out, _ = ssh_exec(ssh, f"grep -n 'mail\\|sendmail\\|MAIL' {script} 2>&1", show=False)
                if "mail" in out.lower() or "sendmail" in out.lower():
                    print("[INFO] Script trimite deja email!")
                    print(out)
                else:
                    print("[INFO] Script NU trimite email")
                
                print()
            else:
                print(f"[WARN] Script nu exista: {script}")
        
        print()
        
        # 3. Test trimitere notificare
        print("=" * 70)
        print("3. TEST NOTIFICARE")
        print("=" * 70)
        print()
        
        print("[INFO] Trimitere notificare de test...")
        
        test_message = "Test notificare dupa backup!"
        cmd = f'/usr/local/bin/ntfy_notify.sh "{test_message}"'
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=5)
        
        if out:
            print(out)
        
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("VERIFICARE COMPLETA!")
        print("=" * 70)
        print()
        print(">> REZUMAT:")
        print("   - Cron jobs pentru backup exista")
        print("   - Trebuie sa integrez notificarile in scripturile existente")
        print()
        print(">> URMAREA PASI:")
        print("   1. Verific scripturile de backup")
        print("   2. Adaug notificare la sfarsitul backup-ului")
        print("   3. Test notificare")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

