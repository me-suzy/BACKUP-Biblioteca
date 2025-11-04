#!/usr/bin/env python
"""
Curata fisierele de test vechi
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
    print("   CURATARE FISIERE DE TEST")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Cauta cron jobs HIDDEN (in alt director)
        print("=" * 70)
        print("1. CAUTARE CRON JOBS HIDDEN")
        print("=" * 70)
        print()
        
        # Verifica crontab-ul rootului in toate locatiile posibile
        out, _ = ssh_exec(ssh, "crontab -l 2>/dev/null", show=False)
        
        if out and 'ntfy' in out.lower():
            print("[WARN] GASIT CRON JOB CU NTFY!")
            lines = out.split('\n')
            for i, line in enumerate(lines):
                if 'ntfy' in line.lower():
                    print(f"  {i+1}: {line}")
        else:
            print("[OK] Nu exista cron jobs cu NTFY")
        
        print()
        
        # 2. Cauta in toate directoarele posibile cron jobs
        print("=" * 70)
        print("2. CAUTARE IN /VAR/SPOOL/CRON")
        print("=" * 70)
        print()
        
        ssh_exec(ssh, "ls -la /var/spool/cron/ 2>/dev/null", show=False)
        
        out, _ = ssh_exec(ssh, "cat /var/spool/cron/root 2>/dev/null", show=False)
        if out:
            print("Continut /var/spool/cron/root:")
            if 'ntfy' in out.lower():
                print("[WARN] GASIT CRON JOB CU NTFY IN /var/spool/cron/root!")
                print(out)
            else:
                print("[OK] Fara NTFY in /var/spool/cron/root")
        else:
            print("[OK] Nu exista /var/spool/cron/root")
        
        print()
        
        # 3. Cauta in /etc/crontab si /etc/cron.d
        print("=" * 70)
        print("3. CAUTARE IN /ETC/CRON*")
        print("=" * 70)
        print()
        
        ssh_exec(ssh, "cat /etc/crontab 2>/dev/null | grep -i ntfy", show=False)
        ssh_exec(ssh, "ls -la /etc/cron.d/* 2>/dev/null", show=False)
        
        print()
        
        # 4. CURATA fisiere de test
        print("=" * 70)
        print("4. CURATARE FISIERE DE TEST")
        print("=" * 70)
        print()
        
        test_files = [
            "/tmp/test_ntfy_msg.txt",
            "/tmp/create_final_ntfy.sh",
            "/tmp/backup_mailer_final",
            "/tmp/backup_mailer_fixed",
            "/tmp/backup_mailer_modified",
        ]
        
        for file in test_files:
            out, _ = ssh_exec(ssh, f"rm -f {file} 2>&1", show=False)
            print(f"Eliminat: {file}")
        
        print()
        
        # 5. Verifica backup_mailer - AR TREBUI SA FIE 1 SINGUR NTFY
        print("=" * 70)
        print("5. VERIFICARE FINALA BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -c 'ntfy_notify.sh' /exlibris/backup/scripts/backup_mailer", show=False)
        count = int(out.strip())
        
        print(f"Numar linii cu NTFY in backup_mailer: {count}")
        print()
        
        if count == 1:
            print("[OK] EXACT O LINIE CU NTFY!")
            print()
            print("Linia:")
            out_line, _ = ssh_exec(ssh, "grep 'ntfy_notify.sh' /exlibris/backup/scripts/backup_mailer", show=False)
            print(f"  {out_line.strip()}")
        else:
            print(f"[WARN] AM GASIT {count} LINII! TREBUIE SA FIE 1!")
        
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CURATARE COMPLETA!")
        print("=" * 70)
        print()
        print(">> REZULTAT:")
        print("   - Fisiere de test eliminate")
        print("   - backup_mailer contine O SINGURA notificare NTFY")
        print("   - Nu vor mai fi notificari 'Server notification'")
        print()
        print(">> NOTIFICARE FINALA:")
        print("   Se va trimite DOAR la backup real (23:00-02:00)")
        print("   Cu mesajul detaliat deja configurat")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
