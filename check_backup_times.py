#!/usr/bin/env python
"""
Verifica EXACT cand s-a rulat ultimul backup si daca a trimis NTFY
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
    print("   VERIFICARE EXACTA - BACKUP SI NOTIFICARI")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica TOATE log-urile backup
        print("=" * 70)
        print("1. TOATE LOG-URILE BACKUP (ultimele 10)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -lt /exlibris/backup/logs/*.log 2>/dev/null | head -10", show=False)
        print("Log-uri backup:")
        print(out)
        
        print()
        
        # 2. Verifica data EXACTA a ultimului backup
        print("=" * 70)
        print("2. DATA EXACTA ULTIMUL BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "stat /exlibris/backup/logs/Summary.log 2>/dev/null | grep 'Modify'", show=False)
        if out:
            print("Ultima modificare Summary.log:")
            print(out)
        else:
            print("[WARN] Fisier Summary.log nu exista")
        
        # Verifica si cea mai recenta log
        out, _ = ssh_exec(ssh, "ls -t /exlibris/backup/logs/*.log 2>/dev/null | head -1", show=False)
        latest_log = out.strip()
        if latest_log:
            out, _ = ssh_exec(ssh, f"stat {latest_log} 2>/dev/null | grep 'Modify'", show=False)
            print()
            print(f"Ultima modificare {latest_log}:")
            print(out)
        
        print()
        
        # 3. Verifica LINIA EXACTA cu NTFY din backup_mailer
        print("=" * 70)
        print("3. LINIA NTFY EXACTA DIN BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linia cu NTFY:")
        print(out)
        
        # Afiseaza linia complet
        if out:
            line_num = out.split(':')[0]
            print()
            print(f"Linia {line_num} - Context complet:")
            out, _ = ssh_exec(ssh, f"sed -n '{int(line_num)-2},{int(line_num)+3}p' /exlibris/backup/scripts/backup_mailer", show=False)
            print(out)
        
        print()
        
        # 4. Verifica daca linia este COMENTATA
        print("=" * 70)
        print("4. VERIFICARE DACA LINIA ESTE ACTIVA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep 'ntfy_notify' /exlibris/backup/scripts/backup_mailer | head -1", show=False)
        if out:
            line = out.strip()
            print(f"Linia gasita: {line}")
            if line.strip().startswith('#'):
                print()
                print("[ERROR] LINIA ESTE COMENTATA!")
                print("   Din acest motiv NU ai primit notificare!")
            else:
                print()
                print("[OK] Linia este ACTIVA")
        
        print()
        
        # 5. Verifica programul de backup din /etc/cron.d
        print("=" * 70)
        print("5. PROGRAMUL BACKUP DIN CRON")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -r 'backup\|exlibris' /etc/cron.d/ 2>/dev/null", show=False)
        if out:
            print("Cron jobs backup:")
            print(out)
        else:
            print("[INFO] Nu exista cron jobs backup in /etc/cron.d")
        
        # Verifica si direct in /etc/crontab
        out, _ = ssh_exec(ssh, "cat /etc/crontab", show=False)
        if 'backup' in out.lower() or 'exlibris' in out.lower():
            print()
            print("Cron jobs backup in /etc/crontab:")
            for line in out.split('\n'):
                if 'backup' in line.lower() or 'exlibris' in line.lower():
                    print(f"  {line}")
        
        print()
        
        # 6. Verifica daca exista scripturi care apeleaza backup_mailer
        print("=" * 70)
        print("6. SCRIPTURI CARE APELEAZA BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -r 'backup_mailer' /exlibris/backup/ 2>/dev/null | grep -v '.log' | head -10", show=False)
        if out:
            print("Scripturi care apeleaza backup_mailer:")
            print(out)
        else:
            print("[INFO] Nu s-au gasit scripturi")
        
        print()
        
        # 7. Verifica care este ora curenta pe server
        print("=" * 70)
        print("7. ORA SI DATA CURENTA PE SERVER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "date", show=False)
        print(f"Ora curenta pe server: {out.strip()}")
        
        print()
        
        ssh.close()
        
        print()
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

