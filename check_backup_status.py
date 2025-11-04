#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica de ce backup-ul s-a oprit
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
    print("   VERIFICARE PROBLEMA BACKUP - DE CE S-A OPRIT")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica jurnalul
        print("=" * 70)
        print("1. JURNAL BACKUP (ultimele linii)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "tail -50 /exlibris/backup/logs/*.summary 2>/dev/null | grep -i 'start\\|end\\|error'", show=False)
        if out.strip():
            print(out)
        else:
            print("[INFO] Nu s-au gasit linii")
        
        out2, _ = ssh_exec(ssh, "cat /exlibris/backup/logs/*.summary 2>/dev/null | tail -50", show=False)
        print("Ultimele linii din .summary:")
        print(out2)
        
        print()
        
        # 2. Verifica cron jobs
        print("=" * 70)
        print("2. VERIFICARE CRON JOBS")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l", show=False)
        if out.strip():
            print("Cron jobs curente:")
            print(out)
        else:
            print("[INFO] Nu sunt cron jobs pentru root")
        
        print()
        
        # 3. Verifica at jobs (atd)
        print("=" * 70)
        print("3. VERIFICARE AT JOBS (programari viitoare)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "atq", show=False)
        if out.strip():
            print("Jobs programate cu 'at':")
            print(out)
        else:
            print("[INFO] Nu sunt jobs programate cu 'at'")
        
        print()
        
        # 4. Verifica daca atd ruleaza
        print("=" * 70)
        print("4. VERIFICARE ATD (daemon)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ps aux | grep atd | grep -v grep", show=False)
        if out.strip():
            print("[OK] atd ruleaza:")
            print(out)
        else:
            print("[ERROR] atd NU ruleaza!")
        
        print()
        
        # 5. Cauta unde se programeaza backup-urile
        print("=" * 70)
        print("5. CAUTA SCRIPT-URI CARE PROGRAMEAZA BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "find /exlibris/backup/scripts -name '*.sh' -o -name '*backup*' -type f 2>/dev/null", show=False)
        if out.strip():
            print("Script-uri backup:")
            for line in out.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
                    # Verifica daca contine 'at' sau programare
                    content, _ = ssh_exec(ssh, f"grep -n 'at\\|cron' {line} 2>/dev/null | head -5", show=False)
                    if content.strip():
                        print(f"    -> {content.strip()}")
        
        print()
        
        # 6. Verifica log-uri erori
        print("=" * 70)
        print("6. LOG-URI ERORI RECENTE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "tail -100 /var/log/messages | grep -i 'backup\\|error\\|cron\\|atd'", show=False)
        if out.strip():
            print(out)
        else:
            print("[INFO] Nu sunt erori evidente")
        
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("DIAGNOSTIC")
        print("=" * 70)
        print()
        print("PROBLEMA:")
        print("  Backup-urile s-au oprit de pe 25 octombrie")
        print("  Ultimul backup: 25 oct 22:00")
        print()
        print("POSIBILE CAUZE:")
        print("  1. Script-ul principal de programare s-a oprit")
        print("  2. ATD nu mai ruleaza")
        print("  3. Cron job s-a modificat")
        print("  4. Script-ul exec_backup_main are probleme")
        print()
        print("PAȘI URMĂTORI:")
        print("  1. Verifica unde se programeaza backup-urile")
        print("  2. Verifica daca exec_backup_main exista si e executabil")
        print("  3. Ruleaza manual un backup pentru test")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

