#!/usr/bin/env python
"""
Verifica TOATE scripturile care trimit NTFY si elimina cele vechi
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
    print("   VERIFICARE TOATE SCRIPTURILE NTFY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Cauta toate scripturile care contin "ntfy_notify.sh"
        print("=" * 70)
        print("1. CAUTARE TOATE SCRIPTURILE CU NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "find /usr/local/bin -name '*ntfy*' -o -name '*NTFY*' 2>/dev/null", show=False)
        print("Scripturi gasite:")
        scripts = out.strip().split('\n')
        for script in scripts:
            if script.strip():
                print(f"  {script}")
        print()
        
        # 2. Verifica cron jobs
        print("=" * 70)
        print("2. VERIFICARE CRON JOBS")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l", show=False)
        
        if out:
            print("Cron jobs existente:")
            print(out)
            
            # Cauta cron jobs cu NTFY
            if 'ntfy' in out.lower():
                print()
                print("[WARN] Am gasit cron jobs cu NTFY!")
                
                # Cauta liniile cu NTFY
                lines = out.split('\n')
                for i, line in enumerate(lines):
                    if 'ntfy' in line.lower():
                        print(f"  Linia {i+1}: {line.strip()}")
        else:
            print("[OK] Nu exista cron jobs")
        
        print()
        
        # 3. Verifica backup_mailer
        print("=" * 70)
        print("3. VERIFICARE BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep 'ntfy_notify.sh' /exlibris/backup/scripts/backup_mailer 2>/dev/null | wc -l", show=False)
        print(f"Linii cu NTFY in backup_mailer: {out.strip()}")
        print()
        
        # 4. Verifica daca exista alte scripturi de test
        print("=" * 70)
        print("4. VERIFICARE ALTE SCRIPTURI DE TEST")
        print("=" * 70)
        print()
        
        test_scripts = [
            "/tmp/test_ntfy_msg.txt",
            "/tmp/create_final_ntfy.sh",
        ]
        
        for script in test_scripts:
            out, _ = ssh_exec(ssh, f"ls -la {script} 2>/dev/null", show=False)
            if "No such file" not in out and "cannot access" not in out:
                print(f"[WARN] GASIT: {script}")
                print("Continut:")
                out_content, _ = ssh_exec(ssh, f"cat {script} 2>/dev/null", show=False)
                print(out_content[:200])
                print()
        
        # 5. Verifica backup_mailer complet
        print("=" * 70)
        print("5. CONTINUT BACKUP_MAILER - LINII CU NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'ntfy_notify.sh' /exlibris/backup/scripts/backup_mailer 2>/dev/null", show=False)
        print("Linii cu NTFY in backup_mailer:")
        print(out)
        print()
        
        ssh.close()
        
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
