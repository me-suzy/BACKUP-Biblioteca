#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix NTFY - metoda corecta pentru a evita problemele de encoding
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
    print("   FIX NTFY - METODA FINALA")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Restaureaza backup
        print("=" * 70)
        print("1. RESTAURARE BACKUP")
        print("=" * 70)
        print()
        
        ssh_exec(ssh, "cp /exlibris/backup/scripts/backup_mailer.before_ntfy_final /exlibris/backup/scripts/backup_mailer 2>/dev/null || cp /exlibris/backup/scripts/backup_mailer.backup /exlibris/backup/scripts/backup_mailer", show=False)
        print("[OK] Backup restaurat!")
        
        # 2. Adauga linia NTFY folosind comandile SSH direct
        print()
        print("=" * 70)
        print("2. ADAUGARE LINIE NTFY")
        print("=" * 70)
        print()
        
        # Folosim heredoc pentru a evita probleme de encoding
        add_line_cmd = '''bash -c "
# Backup linia 96 (mailx)
cp /exlibris/backup/scripts/backup_mailer /exlibris/backup/scripts/backup_mailer.tmp

# Adauga linia NTFY DUPA linia 96 (care contine mailx)
sed -i '96a\\
echo \"BACKUP: \\\\$BACKUP_TYPE | DB: \\\\$ORACLE_SID | CODE: \\\\$ERROR_NUMBER | TIME: \\\\\`/bin/date '\\''+%Y-%m-%d %H:%M:%S'\\'' \\\` | STATUS: \\\\$ERROR_MESSAGE\" | /usr/local/bin/ntfy_notify.sh
' /exlibris/backup/scripts/backup_mailer.tmp

# Verifica
mv /exlibris/backup/scripts/backup_mailer.tmp /exlibris/backup/scripts/backup_mailer
"
'''
        
        print("[INFO] Adaugare linie NTFY...")
        ssh_exec(ssh, add_line_cmd, show=False)
        print("[OK] Linie adaugata!")
        
        # 3. Verifica
        print()
        print("=" * 70)
        print("3. VERIFICARE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linii 95-105:")
        print(out)
        
        # 4. Test
        print()
        print("=" * 70)
        print("4. TEST NOTIFICARE")
        print("=" * 70)
        print()
        
        # Creaza test file
        test_cmd = '''cat > /tmp/test_backup.sh << 'EOF'
#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"

echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
EOF
chmod +x /tmp/test_backup.sh
/tmp/test_backup.sh
'''
        
        print("[INFO] Executare test...")
        ssh_exec(ssh, test_cmd, show=False)
        
        # Sterge test
        ssh_exec(ssh, "rm /tmp/test_backup.sh", show=False)
        
        print()
        print("[INFO] VERIFICA TELEFONUL!")
        print("   Ar trebui sa primesti notificare corecta!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CONFIGURARE COMPLETA!")
        print("=" * 70)
        print()
        print("Linia NTFY adaugata!")
        print("Proximul backup: luni 27 oct la 23:00")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

