#!/usr/bin/env python
"""
Verifica programul de backup si log-urile
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
    print("   VERIFICARE PROGRAM BACKUP")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica cron jobs din /etc/cron.d
        print("=" * 70)
        print("1. CRON JOBS DIN /etc/cron.d")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /etc/cron.d/* 2>/dev/null", show=False)
        if out:
            print("Continut /etc/cron.d:")
            print(out)
        else:
            print("[INFO] Niciun fisier")
        
        print()
        
        # 2. Verifica la user oracle
        print("=" * 70)
        print("2. CRON JOBS - ORACLE USER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "su - oracle -c 'crontab -l' 2>&1", show=False)
        if "no crontab" not in out:
            print("Cron jobs oracle:")
            print(out)
        else:
            print("[INFO] Oracle nu are cron jobs")
        
        print()
        
        # 3. Cauta scripturi backup care ruleaza
        print("=" * 70)
        print("3. SCRIPTURI BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "find /exlibris/backup -name '*.sh' -executable 2>/dev/null", show=False)
        if out:
            print("Scripturi backup:")
            print(out)
        
        print()
        
        # 4. Verifica log-uri backup recente
        print("=" * 70)
        print("4. LOG-URI BACKUP RECENTE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "find /exlibris/backup -name '*.log' -mtime -5 -ls 2>/dev/null", show=False)
        if out:
            print("Log-uri din ultimele 5 zile:")
            print(out)
        else:
            print("[INFO] Nu sunt log-uri recente")
        
        print()
        
        # 5. Verifica cand s-a rulat ultimul backup
        print("=" * 70)
        print("5. DATA ULTIMUL BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -lt /exlibris/backup/logs/*.log 2>/dev/null | head -5", show=False)
        print("Ultimele log-uri:")
        print(out)
        
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

