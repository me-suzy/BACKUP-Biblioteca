#!/usr/bin/env python
"""
Verifica cron jobs pentru backup REAL
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
    print("   VERIFICARE CRON JOBS REALE PENTRU BACKUP")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Crontab pentru root
        print("=" * 70)
        print("1. CRONTAB - ROOT")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l 2>&1", show=False)
        if "no crontab" in out.lower() or not out.strip():
            print("[WARN] Nu exista crontab pentru root")
        else:
            print("Crontab root:")
            print(out)
        
        print()
        
        # 2. Crontab pentru oracle
        print("=" * 70)
        print("2. CRONTAB - ORACLE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l -u oracle 2>&1", show=False)
        if "no crontab" in out.lower():
            print("[WARN] Nu exista crontab pentru oracle")
        else:
            print("Crontab oracle:")
            print(out)
        
        print()
        
        # 3. Cron files din /etc
        print("=" * 70)
        print("3. CRON FILES DIN /ETC")
        print("=" * 70)
        print()
        
        for dir in ["/etc/cron.d/", "/etc/cron.daily/", "/etc/cron.hourly/", "/var/spool/cron/"]:
            out, _ = ssh_exec(ssh, f"ls -la {dir} 2>/dev/null", show=False)
            if "total" in out or "root" in out:
                print(f"Directory: {dir}")
                print(out)
                print()
        
        print()
        
        # 4. Cauta scripturi backup
        print("=" * 70)
        print("4. CAUTARE SCRIPTURI BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "find /exlibris/backup -name '*backup*' -name '*.sh' 2>/dev/null | head -10", show=False)
        if out:
            print("Scripturi backup gasite:")
            print(out)
        
        print()
        
        # 5. Verifica procese backup care ruleaza
        print("=" * 70)
        print("5. PROCESE BACKUP CARE RULEAZA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ps aux | grep -i backup | grep -v grep", show=False)
        if out:
            print("Procese backup active:")
            print(out)
        else:
            print("[INFO] Nu sunt procese backup active")
        
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

