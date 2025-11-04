#!/usr/bin/env python
"""
Corecteaza backup_mailer sa trimita O SINGURA notificare NTFY cu detalii complete
"""

import paramiko
import sys
from datetime import datetime

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
    print("   CORECTARE NOTIFICARE NTFY - UN SINGUR MESAJ DETALIAT")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Citeste scriptul actual
        print("=" * 70)
        print("1. CITESTE SCRIPTUL ACTUAL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        print("[OK] Script citit!")
        print()
        
        # 2. Creez backup
        print("=" * 70)
        print("2. CREARE BACKUP")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/exlibris/backup/scripts/backup_mailer.backup.{timestamp}"
        ssh_exec(ssh, f"cp /exlibris/backup/scripts/backup_mailer {backup_file}", show=False)
        print(f"[OK] Backup creat: {backup_file}")
        print()
        
        # 3. Modific scriptul
        print("=" * 70)
        print("3. MODIFICARE SCRIPT")
        print("=" * 70)
        print()
        
        lines = out.split('\n')
        new_lines = []
        
        skip_next_ntfy = False
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Elimina toate notificarile NTFY existente (simplificate)
            if 'echo "${SUBJECT} ${BACKUP_TYPE}: ${ERROR_MESSAGE}" | /usr/local/bin/ntfy_notify.sh' in line:
                # Salt peste notificarile simple
                skip_next_ntfy = True
                i += 1
                continue
            
            # Pastreaza doar notificarea detaliata dar o mutam dupa mailx
            if 'NTFY_MSG=' in line:
                # Remove linia NTFY_MSG pentru ca o vom face diferit
                i += 1
                continue
            
            if 'echo "${NTFY_MSG}" | /usr/local/bin/ntfy_notify.sh' in line:
                # Remove notificarea detaliata veche
                i += 1
                continue
            
            # Dupa mailx, adauga O SINGURA notificare NTFY detaliata
            if 'mailx -s' in line and 'special_mail:' not in lines[max(0, i-3):i]:
                new_lines.append(line)
                
                # Adauga doar daca nu urmeaza deja special_mail sau alt bloc special
                next_lines = '\n'.join(lines[i+1:i+5])
                if 'special_mail' not in next_lines and 'exit_backup' not in next_lines:
                    # Adauga O SINGURA notificare NTFY detaliata
                    new_lines.append('')
                    new_lines.append('# Notificare NTFY - O SINGURA LINIE detaliata')
                    new_lines.append('DETAILS="Backup: ${SUBJECT}${BACKUP_TYPE} | DB: ${ORACLE_SID} | Type: ${BACKUP_TYPE} | Status: ${ERROR_MESSAGE} | Code: ${ERROR_NUMBER} | Time: `date \'+%Y-%m-%d %H:%M:%S\'` | Check: /tmp/tmpmail${BKP_SLOT}"')
                    new_lines.append('echo "${DETAILS}" | /usr/local/bin/ntfy_notify.sh')
                    new_lines.append('')
            else:
                new_lines.append(line)
            
            i += 1
        
        modified_content = '\n'.join(new_lines)
        
        # 4. Salveaza scriptul modificat
        print("=" * 70)
        print("4. SALVARE SCRIPT MODIFICAT")
        print("=" * 70)
        print()
        
        # Scrie script modificat
        ssh_exec(ssh, f"cat > /tmp/backup_mailer_fixed <<'EOFSCRIPT'\n{modified_content}\nEOFSCRIPT", show=False)
        
        # Copiaza
        ssh_exec(ssh, "cp /tmp/backup_mailer_fixed /exlibris/backup/scripts/backup_mailer", show=False)
        ssh_exec(ssh, "chmod +x /exlibris/backup/scripts/backup_mailer", show=False)
        
        print("[OK] Script modificat!")
        print()
        
        # 5. Verifica
        print("=" * 70)
        print("5. VERIFICARE NOTIFICARE NTFY")
        print("=" * 70)
        print()
        
        out_verify, _ = ssh_exec(ssh, "grep -A 2 'Notificare NTFY - O SINGURA' /exlibris/backup/scripts/backup_mailer", show=False)
        
        if "O SINGURA LINIE" in out_verify:
            print("[OK] Notificare unica adaugata!")
            print(out_verify)
        else:
            print("[WARN] Notificare nu a fost adaugata corect!")
            print(out_verify)
        
        print()
        
        # 6. Test
        print("=" * 70)
        print("6. TEST NOTIFICARE")
        print("=" * 70)
        print()
        
        test_msg = "Backup: Test | DB: ALEPH | Type: FULL | Status: Success | Code: 00 | Time: $(date '+%Y-%m-%d %H:%M:%S') | Check: /tmp/test"
        ssh_exec(ssh, f'echo "{test_msg}" | /usr/local/bin/ntfy_notify.sh', show=False)
        print("[OK] Notificare de test trimisa!")
        print()
        
        print("Mesaj va contine:")
        print("  - Backup: SUBJECT + BACKUP_TYPE")
        print("  - DB: Oracle SID")
        print("  - Type: Tip backup")
        print("  - Status: Mesaj eroare")
        print("  - Code: Cod eroare (00 = success)")
        print("  - Time: Timestamp exact")
        print("  - Check: Locația fișierului temporar")
        print()
        print("TOATE INTRO O SINGURA LINIE COMPACTA!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CORECTARE COMPLETA!")
        print("=" * 70)
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
