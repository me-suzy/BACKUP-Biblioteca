#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Adauga linia NTFY automat in backup_mailer
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
    print("   ADAUGARE LINIE NTFY IN BACKUP_MAILER")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Citeste backup_mailer
        print("=" * 70)
        print("1. CITESTE BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'mailx' /exlibris/backup/scripts/backup_mailer", show=False)
        if out.strip():
            print("Linii cu mailx:")
            print(out)
        
        # 2. Verifica daca exista deja linia NTFY
        print()
        print("=" * 70)
        print("2. VERIFICA LINIA NTFY")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        if out.strip():
            print("[INFO] Exista deja linia NTFY:")
            print(out)
            print()
            print("NU E NEVOIE SA ADAUGAM DIN NOU!")
            ssh.close()
            return 0
        else:
            print("[INFO] NU exista linia NTFY - va fi adaugata")
        
        # 3. Adauga linia
        print()
        print("=" * 70)
        print("3. ADAUGA LINIA NTFY")
        print("=" * 70)
        print()
        
        # Creez fisier nou cu linia adaugata
        # Citesc backup_mailer
        full_content, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        
        lines = full_content.split('\n')
        new_lines = []
        added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            # Dupa linia cu mailx, adaug linia NTFY
            if 'mailx' in line and not added:
                # Linia NTFY
                ntf_line = "echo \"BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE\" | /usr/local/bin/ntfy_notify.sh"
                new_lines.append(ntf_line)
                added = True
        
        new_content = '\n'.join(new_lines)
        
        # Scrie fisier nou
        print("Creez backup...")
        ssh_exec(ssh, "cp /exlibris/backup/scripts/backup_mailer /exlibris/backup/scripts/backup_mailer.backup_$(date +%Y%m%d_%H%M%S)", show=False)
        
        print("Scriu fisier nou...")
        ssh_exec(ssh, "cat > /tmp/backup_mailer_new << 'EOFEOF'\n" + new_content + "\nEOFEOF", show=False)
        
        print("Inlocuiesc fisierul...")
        ssh_exec(ssh, "mv /tmp/backup_mailer_new /exlibris/backup/scripts/backup_mailer")
        
        # 4. Verifica
        print()
        print("=" * 70)
        print("4. VERIFICARE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -n 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        if out.strip():
            print("[OK] Linia NTFY adaugata:")
            print(out)
        else:
            print("[ERROR] Linia NTFY NU a fost adaugata!")
        
        # 5. Testeaza
        print()
        print("=" * 70)
        print("5. TEST")
        print("=" * 70)
        print()
        
        # Testam sintaxa
        out, _ = ssh_exec(ssh, "/bin/csh -n /exlibris/backup/scripts/backup_mailer", show=False)
        if not out.strip() and "error" not in out.lower():
            print("[OK] Sintaxa corecta!")
        else:
            print("[WARN] Posibile probleme de sintaxa")
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("GATA!")
        print("=" * 70)
        print()
        print("Linia NTFY a fost adaugata in backup_mailer.")
        print()
        print("La backup-urile din aceasta noapte (22:00 si 23:00)")
        print("vei primi notificari DETALIATE cu:")
        print("  - BACKUP: type")
        print("  - DB: ALEPH")
        print("  - CODE: error code")
        print("  - TIME: timestamp")
        print("  - STATUS: message")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

