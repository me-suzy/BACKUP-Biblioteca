#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Citeste bkp_init.dat
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
    print("   CITIRE BKP_INIT.DAT")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Citeste bkp_init.dat
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/conf/bkp_init.dat", show=False)
        print("CONTINUT BKP_INIT.DAT:")
        print("=" * 70)
        print(out)
        print("=" * 70)
        
        # Citeste bkp_param.conf
        out2, _ = ssh_exec(ssh, "cat /exlibris/backup/conf/bkp_param.conf", show=False)
        print()
        print("CONTINUT BKP_PARAM.CONF:")
        print("=" * 70)
        print(out2)
        print("=" * 70)
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("ANALIZA")
        print("=" * 70)
        print()
        print("Din bkp_init.dat:")
        print("  Slot a5 -> user_data backup (22:00)")
        print("  Slot a1 -> ora_cold backup (23:00)")
        print()
        print("DAR: NU AM GASIT SCRIPT-UL CARE PROGRAMEAZA ACESTE SLOT-URI!")
        print()
        print("POSIBIL: Exista un cron job sau un init script")
        print("         care ruleaza zilnic si executa:")
        print("         exec_backup_main a5  # la 22:00")
        print("         exec_backup_main a1  # la 23:00")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

