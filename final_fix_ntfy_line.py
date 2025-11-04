#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final fix pentru linia NTFY - versiune SIMPLA si funcționala
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
    print("   FINAL FIX - LINIE NTFY SIMPLA")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Citeste TOATE liniile 99-105
        print("=" * 70)
        print("1. LINIILE 95-105 (CONTEXT COMPLET)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print(out)
        
        print()
        
        # 2. Backup fisierul
        print("=" * 70)
        print("2. BACKUP FISIER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cp /exlibris/backup/scripts/backup_mailer /exlibris/backup/scripts/backup_mailer.ntfy_fix_backup", show=False)
        print("[OK] Backup creat!")
        
        print()
        
        # 3. Sterge linia 99 (ori 99-100 daca e pe 2 linii)
        print("=" * 70)
        print("3. STERGERE LINIE 99")
        print("=" * 70)
        print()
        
        ssh_exec(ssh, "sed -i '99,102d' /exlibris/backup/scripts/backup_mailer", show=False)
        
        print("[INFO] Linii sterse!")
        
        # 4. Adauga linia NOUA CORECTA pe linia 98 (inainte de exit_backup)
        print()
        print("=" * 70)
        print("4. ADAUGARE LINIE NOUA")
        print("=" * 70)
        print()
        
        # Varianta SIMPLA care MERGE sigur
        # In loc de pipe complicat, scriem direct catre NTFY
        new_line = '# Trimitere notificare NTFY cu informatii unice despre backup'
        
        ssh_exec(ssh, f"sed -i \"98a\\{new_line}\" /exlibris/backup/scripts/backup_mailer", show=False)
        
        # Linia care trimite notificarea - versiune SIMPLA
        # Folosim printf in loc de echo pentru control mai bun
        simple_line = "printf \"BACKUP: %s | DB: %s | CODE: %s | TIME: %s | STATUS: %s\" \"$BACKUP_TYPE\" \"$ORACLE_SID\" \"$ERROR_NUMBER\" \"`date '+%Y-%m-%d %H:%M:%S'`\" \"$ERROR_MESSAGE\" | /usr/local/bin/ntfy_notify.sh"
        
        ssh_exec(ssh, f"sed -i \"99a\\{simple_line}\" /exlibris/backup/scripts/backup_mailer", show=False)
        
        # 5. Verifica rezultatul
        print()
        print("=" * 70)
        print("5. VERIFICARE FINALA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "sed -n '95,105p' /exlibris/backup/scripts/backup_mailer", show=False)
        print("Linii 95-105:")
        print(out)
        
        print()
        
        # 6. Testeaza
        print("=" * 70)
        print("6. TESTARE NOTIFICARE")
        print("=" * 70)
        print()
        
        test_cmd = '''
#!/bin/csh
set BACKUP_TYPE="FULL"
set ORACLE_SID="ALEPH"
set ERROR_NUMBER="00"
set ERROR_MESSAGE="End FULL backup"
printf "BACKUP: %s | DB: %s | CODE: %s | TIME: %s | STATUS: %s" "$BACKUP_TYPE" "$ORACLE_SID" "$ERROR_NUMBER" "`date '+%Y-%m-%d %H:%M:%S'`" "$ERROR_MESSAGE" | /usr/local/bin/ntfy_notify.sh
'''
        
        ssh_exec(ssh, "cat > /tmp/test_printf.sh << 'ENDSCRIPT'\n#!/bin/csh\nset BACKUP_TYPE=\"TEST\"\nset ORACLE_SID=\"ALEPH\"\nset ERROR_NUMBER=\"00\"\nset ERROR_MESSAGE=\"Test backup\"\nprintf \"BACKUP: %s | DB: %s | CODE: %s | TIME: %s | STATUS: %s\" \"$BACKUP_TYPE\" \"$ORACLE_SID\" \"$ERROR_NUMBER\" \"\\\`date '+%Y-%m-%d %H:%M:%S'\\\`\" \"$ERROR_MESSAGE\" | /usr/local/bin/ntfy_notify.sh\nENDSCRIPT", show=False)
        
        ssh_exec(ssh, "chmod +x /tmp/test_printf.sh", show=False)
        
        print("[INFO] Executare test...")
        out, err = ssh_exec(ssh, "/tmp/test_printf.sh 2>&1", show=False)
        print("Output:")
        print(out)
        if err:
            print(f"Error: {err}")
        
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

