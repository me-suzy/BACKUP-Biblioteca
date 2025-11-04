#!/usr/bin/env python
"""
Citeste si corecteaza linia 99 completa
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
    print("   VERIFICARE SI CORECTARE LINIE 99")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Citeste linia 99 completa
        print("=" * 70)
        print("1. LINIA 99 ACTUALA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '99p' /exlibris/backup/scripts/backup_mailer | wc -c", show=False)
        print(f"Lungime linie 99: {out.strip()} caractere")
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '99p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linia completa (mod ascii cat):")
        print(out)
        
        # 2. Creeaza linia corecta
        print()
        print("=" * 70)
        print("2. CREARE LINIE CORECTA")
        print("=" * 70)
        print()
        
        # Sintaxa C-shell corecta
        correct_line = "echo \"BACKUP: \$BACKUP_TYPE | DB: \$ORACLE_SID | CODE: \$ERROR_NUMBER | TIME: \\`date '+%Y-%m-%d %H:%M:%S'\\` | STATUS: \$ERROR_MESSAGE\" | /usr/local/bin/ntfy_notify.sh"
        
        print("Linia corecta:")
        print(correct_line)
        print()
        
        # 3. Inlocuieste cu metoda mai sigura
        print("=" * 70)
        print("3. INLOCUIRE LINIE")
        print("=" * 70)
        print()
        
        # Folosim o metoda mai sigura - scriem in fisier temporar
        script = f'''#!/bin/bash
cat > /tmp/line99.txt << 'EOF'
{correct_line}
EOF

# Backup linia veche
cp /exlibris/backup/scripts/backup_mailer /exlibris/backup/scripts/backup_mailer.before_ntfy_fix_$(date +%s)

# Inlocuieste linia 99
sed -i '99r /tmp/line99.txt' /exlibris/backup/scripts/backup_mailer
sed -i '100d' /exlibris/backup/scripts/backup_mailer
'''
        
        print("[INFO] Executare corectare...")
        out, err = ssh_exec(ssh, script, show=False)
        
        # 4. Verifica rezultatul
        print()
        print("=" * 70)
        print("4. VERIFICARE REZULTAT")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '99p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linia 99 dupa corectare:")
        print(out)
        
        # 5. Testeaza manual
        print()
        print("=" * 70)
        print("5. TEST NOTIFICARE")
        print("=" * 70)
        print()
        
        test_cmd = '''
#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"

echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
'''
        
        ssh_exec(ssh, "cat > /tmp/test_ntfy_final.sh << 'ENDSCRIPT'\n#!/bin/csh\nset BACKUP_TYPE=\"TEST\"\nset ORACLE_SID=\"ALEPH\"\nset ERROR_NUMBER=\"00\"\nset ERROR_MESSAGE=\"Test backup\"\necho \"BACKUP: \$BACKUP_TYPE | DB: \$ORACLE_SID | CODE: \$ERROR_NUMBER | TIME: \\\`date '+%Y-%m-%d %H:%M:%S'\\\` | STATUS: \$ERROR_MESSAGE\" | /usr/local/bin/ntfy_notify.sh\nENDSCRIPT", show=False)
        
        ssh_exec(ssh, "chmod +x /tmp/test_ntfy_final.sh", show=False)
        ssh_exec(ssh, "/tmp/test_ntfy_final.sh 2>&1", show=False)
        
        print()
        print("[INFO] Verifica telefonul - ar trebui sa primesti notificare!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CORECTARE COMPLETA!")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

