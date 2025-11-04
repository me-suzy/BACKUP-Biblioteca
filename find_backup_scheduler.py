#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cauta scriptul care PROGRAMEAZA backup-urile
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
    print("   CAUTA SCRIPT-UL CARE PROGRAMEAZA BACKUP-URILE")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Cauta toate script-urile care contin 'at '
        print("=" * 70)
        print("1. CAUTA 'at ' IN SCRIPT-URI BACKUP")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -r 'at ' /exlibris/backup/scripts/*.sh /exlibris/backup/scripts/* 2>/dev/null | grep -v Binary", show=False)
        if out.strip():
            print("[FOUND] Script-uri cu 'at ':")
            print(out)
        else:
            print("[INFO] Nu s-au gasit script-uri cu 'at '")
        
        # 2. Cauta script-uri cu 'exec_backup_main'
        print()
        print("=" * 70)
        print("2. CAUTA SCRIPT-URI CARE APELEAZA 'exec_backup_main'")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -r 'exec_backup_main' /exlibris/backup/scripts/*.sh /exlibris/backup/scripts/* 2>/dev/null | grep -v Binary | grep -v exec_backup_main:", show=False)
        if out.strip():
            print("[FOUND] Script-uri care apeleaza exec_backup_main:")
            print(out)
        else:
            print("[INFO] Nu s-au gasit")
        
        # 3. Lista toate script-urile
        print()
        print("=" * 70)
        print("3. TOATE SCRIPT-URILE DIN /exlibris/backup/scripts")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -lt /exlibris/backup/scripts/", show=False)
        if out.strip():
            print(out)
        
        # 4. Cauta in cron.*
        print()
        print("=" * 70)
        print("4. CAUTA IN /etc/cron.*")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -r 'exec_backup_main\\|backup' /etc/cron.d /etc/cron.daily /etc/cron.hourly 2>/dev/null | grep -v Binary", show=False)
        if out.strip():
            print("[FOUND]:")
            print(out)
        else:
            print("[INFO] Nu s-au gasit")
        
        # 5. Cauta init script-uri
        print()
        print("=" * 70)
        print("5. CAUTA INIT SCRIPT-URI (exec_tarol, etc)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ls -lt /exlibris/backup/scripts/exec_*", show=False)
        if out.strip():
            print("[FOUND] Script-uri exec_*:")
            print(out)
            print()
            print("[INFO] Verific executie:")
            for f in out.strip().split('\n'):
                if f and 'exec_' in f:
                    filepath = f.split()[-1]
                    if filepath.startswith('/exlibris'):
                        content, _ = ssh_exec(ssh, f"head -20 {filepath}", show=False)
                        print(f"\n{filepath}:")
                        print(content[:500])
        
        # 6. Cauta dupa init_file
        print()
        print("=" * 70)
        print("6. CAUTA INIT_FILE (conf)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "find /exlibris/backup/conf -name '*.conf' -o -name '*init*' 2>/dev/null", show=False)
        if out.strip():
            print("[FOUND]:")
            print(out)
        else:
            print("[INFO] Nu s-au gasit")
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("DIAGNOSTIC")
        print("=" * 70)
        print()
        print("MOTIV: Trebuie sa gasim scriptul care PROGRAMEAZA")
        print("       backup-urile cu comanda 'at' la 22:00 si 23:00")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

