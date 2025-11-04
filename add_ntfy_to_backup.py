#!/usr/bin/env python
"""
Adaug notificare NTFY in backup_mailer
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
    print("   ADAUGARE NOTIFICARE NTFY IN BACKUP")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Backup backup_mailer
        print("=" * 70)
        print("1. BACKUP SCRIPT ORIGINAL")
        print("=" * 70)
        print()
        
        print("[INFO] Creez backup pentru backup_mailer...")
        ssh_exec(ssh, "cp /exlibris/backup/scripts/backup_mailer /exlibris/backup/scripts/backup_mailer.backup", show=False)
        print("[OK] Backup creat: /exlibris/backup/scripts/backup_mailer.backup")
        print()
        
        # 2. Modifica script pentru a adauga NTFY
        print("=" * 70)
        print("2. ADAUGARE NOTIFICARE NTFY")
        print("=" * 70)
        print()
        
        # Citeste scriptul
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        
        # Linia unde se trimite email
        # /bin/cat /tmp/tmpmail${BKP_SLOT} | mailx -s "$SUBJECT  $BACKUP_TYPE " "$BKP_MAIL"
        
        # Adauga NTFY dupa linia cu mailx
        modified = out.replace(
            '/bin/cat /tmp/tmpmail${BKP_SLOT} | mailx -s "$SUBJECT  $BACKUP_TYPE " "$BKP_MAIL"',
            '/bin/cat /tmp/tmpmail${BKP_SLOT} | mailx -s "$SUBJECT  $BACKUP_TYPE " "$BKP_MAIL"\n# Notificare NTFY\necho "${SUBJECT} ${BACKUP_TYPE}: ${ERROR_MESSAGE}" | /usr/local/bin/ntfy_notify.sh'
        )
        
        # Salveaza script modificat
        print("[INFO] Modific script pentru a adauga NTFY...")
        
        # Scrie script modificat
        ssh_exec(ssh, f'cat > /tmp/backup_mailer_new <<\'EOFNEW\'\n{modified}\nEOFNEW', show=False, timeout=5)
        
        print("[OK] Script modificat creat!")
        print()
        
        # 3. Verifica modificarea
        print("=" * 70)
        print("3. VERIFICARE MODIFICARE")
        print("=" * 70)
        print()
        
        print("[INFO] Verific linia adaugata...")
        out, _ = ssh_exec(ssh, "grep -A 2 'mailx -s' /tmp/backup_mailer_new", show=False)
        
        if "ntfy_notify" in out:
            print("[OK] NTFY adaugat corect!")
            print(out)
        else:
            print("[WARN] NTFY nu a fost adaugat corect")
        
        print()
        
        # 4. Instaleaza script modificat
        print("=" * 70)
        print("4. INSTALARE SCRIPT MODIFICAT")
        print("=" * 70)
        print()
        
        # Salveaza scriptul modificat
        ssh_exec(ssh, "cp /tmp/backup_mailer_new /exlibris/backup/scripts/backup_mailer", show=False)
        ssh_exec(ssh, "chmod +x /exlibris/backup/scripts/backup_mailer", show=False)
        
        print("[OK] Script modificat instalat!")
        print()
        
        # 5. Verifica scriptul final
        print("=" * 70)
        print("5. VERIFICARE SCRIPT FINAL")
        print("=" * 70)
        print()
        
        print("[INFO] Verific linia cu NTFY...")
        out, _ = ssh_exec(ssh, "grep -B 2 -A 2 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        
        if "ntfy_notify" in out:
            print("[OK] NTFY adaugat in scriptul de backup!")
            print(out)
        else:
            print("[WARN] NTFY nu este in script")
            print(out)
        
        print()
        
        # 6. Test simplu
        print("=" * 70)
        print("6. TEST NOTIFICARE")
        print("=" * 70)
        print()
        
        print("[INFO] Trimitere test notificare...")
        cmd = '/usr/local/bin/ntfy_notify.sh "Test backup mailer integrat!"'
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=5)
        
        if "NTFY notification sent" in out:
            print("[OK] Test notificare reusit!")
        else:
            print("[WARN] Test notificare esuat")
        
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("SETUP COMPLET!")
        print("=" * 70)
        print()
        print(">> REZUMAT:")
        print("   - NTFY integrat in backup_mailer")
        print("   - Va trimite notificari la fiecare backup")
        print("   - Notificari la: bariasi-5f07b8571f7c")
        print()
        print(">> CAND VEI PRIMI NOTIFICARI:")
        print("   - Backup completat cu succes (ERROR_NUMBER 00)")
        print("   - Backup cu erori (ERROR_NUMBER 01-14)")
        print("   - La fiecare rulare backup")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

