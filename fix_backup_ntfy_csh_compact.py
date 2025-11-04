#!/usr/bin/env python
"""
Corecteaza backup_mailer sa trimita O SINGURA notificare NTFY compacta
Scriptul este C-shell (csh), nu Bash!
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
    print("   CORECTARE NTFY - MESAJ COMPACT PE O LINIE")
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
        print("1. CITESTE SCRIPTUL")
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
        
        # 3. Modific scriptul - ELIMINA duplicatele, pastreaza O singura notificare
        print("=" * 70)
        print("3. ELIMINARE DUPLICATE, PASTREZ O SINGURA NOTIFICARE")
        print("=" * 70)
        print()
        
        lines = out.split('\n')
        new_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # ELIMINA toate notificarile NTFY vechi (simple)
            if 'echo "${SUBJECT} ${BACKUP_TYPE}: ${ERROR_MESSAGE}" | /usr/local/bin/ntfy_notify.sh' in line:
                i += 1
                continue
            
            # ELIMINA linia cu NTFY_MSG si echo "${NTFY_MSG}"
            if 'NTFY_MSG=' in line:
                # Sar peste linia NTFY_MSG si urmatoarea cu echo
                i += 2
                continue
            
            if 'echo "${NTFY_MSG}" | /usr/local/bin/ntfy_notify.sh' in line:
                i += 1
                continue
            
            # Dupa mailx, adauga O SINGURA notificare compacta
            if '/bin/cat /tmp/tmpmail${BKP_SLOT} | mailx -s "$SUBJECT  $BACKUP_TYPE " "$BKP_MAIL"' in line:
                new_lines.append(line)
                new_lines.append('')
                # Adauga O SINGURA notificare compacta
                new_lines.append('# Notificare NTFY - informatii unice: timestamp si cod eroare')
                new_lines.append('echo "BACKUP: ${BACKUP_TYPE} | DB: ${ORACLE_SID} | CODE: ${ERROR_NUMBER} | TIME: `/bin/date \'+%Y-%m-%d %H:%M:%S\'` | STATUS: ${ERROR_MESSAGE}" | /usr/local/bin/ntfy_notify.sh')
                new_lines.append('')
            else:
                new_lines.append(line)
            
            i += 1
        
        modified_content = '\n'.join(new_lines)
        
        # 4. Salveaza
        print("=" * 70)
        print("4. SALVARE SCRIPT")
        print("=" * 70)
        print()
        
        ssh_exec(ssh, f"cat > /tmp/backup_mailer_final <<'EOFSCRIPT'\n{modified_content}\nEOFSCRIPT", show=False)
        
        ssh_exec(ssh, "cp /tmp/backup_mailer_final /exlibris/backup/scripts/backup_mailer", show=False)
        ssh_exec(ssh, "chmod +x /exlibris/backup/scripts/backup_mailer", show=False)
        
        print("[OK] Script salvat!")
        print()
        
        # 5. Verifica
        print("=" * 70)
        print("5. VERIFICARE")
        print("=" * 70)
        print()
        
        out_verify, _ = ssh_exec(ssh, "grep -B 1 -A 1 'Notificare NTFY - informatii unice' /exlibris/backup/scripts/backup_mailer", show=False)
        print(out_verify)
        print()
        
        # 6. Verifica cate notificari NTFY sunt
        out_count, _ = ssh_exec(ssh, "grep -c 'ntfy_notify.sh' /exlibris/backup/scripts/backup_mailer", show=False)
        print(f"Numar linii cu NTFY: {out_count.strip()}")
        print()
        
        # 7. Test
        print("=" * 70)
        print("6. TEST NOTIFICARE COMPACTA")
        print("=" * 70)
        print()
        
        now = ssh_exec(ssh, "/bin/date '+%Y-%m-%d %H:%M:%S'", show=False)[0].strip()
        
        test_msg = f"BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: {now} | STATUS: End FULL backup"
        print(f"Mesaj: {test_msg}")
        print()
        
        ssh_exec(ssh, f'echo "{test_msg}" | /usr/local/bin/ntfy_notify.sh', show=False)
        
        print("[OK] Notificare trimisa!")
        print()
        print("VEI PRIMI:")
        print("  - O SINGURA notificare dupa fiecare backup")
        print("  - Mesaj compact pe o linie")
        print("  - Informatii unice:")
        print("    * BACKUP TYPE (FULL, INCREMENTAL, etc.)")
        print("    * Oracle SID")
        print("    * COD EROARE (00 = success, 01-14 = error)")
        print("    * TIMESTAMP (momentul exact)")
        print("    * STATUS (mesaj detaliat)")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("SETUP COMPLET!")
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
