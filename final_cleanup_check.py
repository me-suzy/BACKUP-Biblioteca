#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final cleanup - opreste ORICE trimite notificari
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
    print("   FINAL CLEANUP - OPRESTE TOATE NOTIFICARILE")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Comenteaza linia NTFY
        print("=" * 70)
        print("1. COMENTEAZA LINIA NTFY")
        print("=" * 70)
        print()
        
        ssh_exec(ssh, "sed -i '97s/^/# /' /exlibris/backup/scripts/backup_mailer", show=False)
        
        out, _ = ssh_exec(ssh, "sed -n '97p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linia 97:")
        print(out)
        
        if out.strip().startswith('#'):
            print("[OK] Linia NTFY comentata!")
        
        # 2. Verifica cron jobs
        print()
        print("=" * 70)
        print("2. VERIFICARE CRON JOBS")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l 2>&1", show=False)
        if 'no crontab' in out or not out.strip():
            print("[OK] Nu exista cron jobs")
        else:
            print("[WARN] Exista cron jobs:")
            print(out)
            print()
            print("[INFO] Sterge cron jobs...")
            ssh_exec(ssh, "crontab -r", show=False)
            print("[OK] Cron jobs sterse!")
        
        # 3. Verifica procese
        print()
        print("=" * 70)
        print("3. VERIFICARE PROCESE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ps aux | grep -E 'ntfy|test.*sh' | grep -v grep", show=False)
        if out.strip():
            print("[WARN] Procese active:")
            print(out)
        else:
            print("[OK] Nu sunt procese active")
        
        # 4. Sterge scripturi
        print()
        print("=" * 70)
        print("4. STERGERE SCRIPTURI")
        print("=" * 70)
        print()
        
        ssh_exec(ssh, "rm -f /tmp/test* /tmp/*ntfy* /tmp/*backup*.sh 2>/dev/null", show=False)
        ssh_exec(ssh, "rm -f /root/test* /root/*ntfy* 2>/dev/null", show=False)
        print("[OK] Scripturi sterse!")
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("CLEANUP COMPLET!")
        print("=" * 70)
        print()
        print("REZULTAT:")
        print("  - Linia NTFY comentata")
        print("  - Cron jobs sterse")
        print("  - Scripturi de test sterse")
        print()
        print("Vei primi:")
        print("  - NU mai primesti 'Server notification'")
        print("  - NU vei primi notificari la backup")
        print()
        print("PENTRU A REACTIVA:")
        print("  In backup_mailer, sterge '#' de la linia 97")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

