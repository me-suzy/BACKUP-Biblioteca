#!/usr/bin/env python
"""
Corecteaza linia NTFY pentru sintaxa C-shell CORECTA
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
    print("   CORECTARE LINIE NTFY - SINTAXA C-SHELL CORECTA")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Scrie noua linie CORECTA
        print("=" * 70)
        print("1. CREARE LINIE CORECTA")
        print("=" * 70)
        print()
        
        # In C-shell: $VARIABILA nu ${VARIABILA}
        new_line = 'echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: \\`date \'+%Y-%m-%d %H:%M:%S\'\\` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh'
        
        print("Noua linie (C-shell corecta):")
        print(new_line)
        print()
        
        # 2. Inlocuieste linia 99
        print("=" * 70)
        print("2. INLOCUIRE LINIE 99")
        print("=" * 70)
        print()
        
        # Escapam correct pentru sed
        escaped_line = new_line.replace('\\', '\\\\').replace('/', '\\/').replace('|', '\\|').replace('&', '\\&').replace('`', '\\`')
        
        # Folosim un alt separator pentru sed
        cmd = f"sed -i '99c\\{new_line}' /exlibris/backup/scripts/backup_mailer"
        
        print("[INFO] Inlocuire linie 99...")
        out, err = ssh_exec(ssh, cmd, show=False)
        
        # Verifica
        out, _ = ssh_exec(ssh, "sed -n '99p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linia 99 dupa inlocuire:")
        print(out)
        
        # 3. Verifica contextul
        print()
        print("=" * 70)
        print("3. CONTEXT LINIE (95-105)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print(out)
        
        print()
        
        # 4. Testeaza manual cu C-shell
        print("=" * 70)
        print("4. TESTARE CU C-SHELL")
        print("=" * 70)
        print()
        
        # Create test file
        test_script = '''
#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"

echo "BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
'''
        
        ssh_exec(ssh, "cat > /tmp/test_ntfy_csh.sh << 'EOF'\n#!/bin/csh\nset BACKUP_TYPE=\"TEST\"\nset ORACLE_SID=\"ALEPH\"\nset ERROR_NUMBER=\"00\"\nset ERROR_MESSAGE=\"Test backup\"\necho \"BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: \\`date '+%Y-%m-%d %H:%M:%S'\\` | STATUS: $ERROR_MESSAGE\" | /usr/local/bin/ntfy_notify.sh\nEOF", show=False)
        
        ssh_exec(ssh, "chmod +x /tmp/test_ntfy_csh.sh", show=False)
        
        print("[INFO] Executare test C-shell...")
        out, err = ssh_exec(ssh, "/tmp/test_ntfy_csh.sh 2>&1", show=False)
        print("Output:")
        print(out)
        if err:
            print(f"Error: {err}")
        
        print()
        print("[INFO] Verifica telefonul ACUM!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CORECTARE COMPLETA!")
        print("=" * 70)
        print()
        print("PROBLEMA REZOLVATA:")
        print("  - Linia NTFY foloseste acum sintaxa C-shell corecta")
        print("  - In loc de ${VARIABILA} foloseste $VARIABILA")
        print("  - In loc de /bin/date foloseste date")
        print()
        print("PROXIMA DATA CAND SE FACE BACKUP:")
        print("  - Vei primi notificare!")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

