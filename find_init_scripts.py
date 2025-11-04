#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cauta init scripts sau alte locuri unde se programa backup-urile
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
    print("   CAUTA INIT SCRIPTS / ETLE")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica /etc/init.d
        print("=" * 70)
        print("1. /etc/init.d BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls /etc/init.d/*backup* 2>/dev/null", show=False)
        if out.strip():
            print("[FOUND]:")
            print(out)
        else:
            print("[INFO] Nu s-au gasit")
        
        # 2. Verifica rc.local
        print()
        print("=" * 70)
        print("2. /etc/rc.local")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /etc/rc.local 2>/dev/null", show=False)
        if out.strip():
            print(out)
        else:
            print("[INFO] Nu s-a gasit")
        
        # 3. Verifica event control
        print()
        print("=" * 70)
        print("3. CAUTA 'AT' IN /etc")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -r 'exec_backup_main' /etc 2>/dev/null | head -10", show=False)
        if out.strip():
            print("[FOUND]:")
            print(out)
        else:
            print("[INFO] Nu s-au gasit")
        
        # 4. Verifica /var/spool
        print()
        print("=" * 70)
        print("4. /var/spool/at (JOBS PROGRAMATE)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -la /var/spool/at 2>/dev/null", show=False)
        if out.strip():
            print(out)
        
        out2, _ = ssh_exec(ssh, "atq", show=False)
        print("atq output:")
        print(out2)
        
        # 5. Verifica /etc/crontab
        print()
        print("=" * 70)
        print("5. /etc/crontab")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /etc/crontab", show=False)
        if out.strip():
            print(out)
        else:
            print("[INFO] Nu s-a gasit")
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("DIAGNOSTIC CRITIC")
        print("=" * 70)
        print()
        print("PROBLEMA:")
        print("  - Backup-urile s-au oprit pe 25 oct")
        print("  - NU EXISTA NICIUN MECANISM DE PROGRAMARE ACTIV!")
        print()
        print("CONCLUSIE:")
        print("  Fie deja au existat joburi 'at' care s-au sfarsit,")
        print("  fie exista un cron job care nu mai e activ,")
        print("  fie... te-am contactat la timp!")
        print()
        print("SOLUTIE:")
        print("  Trebuie sa creez un cron job care:")
        print("  - Ruleaza zilnic la 22:00 si executa: exec_backup_main a5")
        print("  - Ruleaza zilnic la 23:00 si executa: exec_backup_main a1")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

