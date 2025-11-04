#!/usr/bin/env python
"""
Test final - simuleaza exact ce vei primi la backup real
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
    print("   TEST FINAL - SIMULARE BACKUP REAL")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        print("=" * 70)
        print("TRIMITERE NOTIFICARE SIMILAR CU BACKUP REAL")
        print("=" * 70)
        print()
        
        # Simuleaza ce variabile ar avea la backup real
        backup_type = "FULL"
        oracle_sid = "ALEPH"
        error_number = "00"  # 00 = success
        timestamp = ssh_exec(ssh, "/bin/date '+%Y-%m-%d %H:%M:%S'", show=False)[0].strip()
        error_message = "End FULL backup"
        
        message = f"BACKUP: {backup_type} | DB: {oracle_sid} | CODE: {error_number} | TIME: {timestamp} | STATUS: {error_message}"
        
        print("MESAJ EXACT CA LA BACKUP REAL:")
        print(message)
        print()
        print("VA CONTININE:")
        print("  - Tip backup: FULL, INCREMENTAL, etc.")
        print("  - Oracle SID: ALEPH")
        print("  - Cod eroare: 00 = success, 01-14 = error")
        print("  - Timestamp: momentul EXACT al backup-ului")
        print("  - Status: mesaj detaliat")
        print()
        
        ssh_exec(ssh, f'echo "{message}" | /usr/local/bin/ntfy_notify.sh', show=False)
        
        print("[OK] Notificare trimisa!")
        print()
        print("Trebuie sa primesti ACUM pe telefon notificarea de mai sus.")
        print()
        print("CAND VA RULA BACKUP-UL REAL (intre 23:00-02:00):")
        print("  - O singura notificare")
        print("  - Cu toate informatiile de mai sus")
        print("  - Timestamp-ul va fi momentul EXACT al backup-ului")
        print("  - Cod eroare 00 = success, orice alt cod = eroare")
        print()
        print("VERIFICARE INFORMATIE UNICA:")
        print("  - Timestamp-ul e ALWAYS diferit (momentul exact)")
        print("  - Nu poate fi o notificare 'fara sens'")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("TEST COMPLET!")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
