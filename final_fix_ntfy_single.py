#!/usr/bin/env python
"""
Elimina TOATE notificarile NTFY vechi si adauga O SINGURA dupa mailx
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
    print("   FINAL FIX - O SINGURA NOTIFICARE NTFY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Citeste scriptul
        print("=" * 70)
        print("1. CITESTE SCRIPTUL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        print("[OK] Script citit!")
        print()
        
        # 2. Backup
        print("=" * 70)
        print("2. BACKUP SCRIPT")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/exlibris/backup/scripts/backup_mailer.backup.{timestamp}"
        ssh_exec(ssh, f"cp /exlibris/backup/scripts/backup_mailer {backup_file}", show=False)
        print(f"[OK] Backup: {backup_file}")
        print()
        
        # 3. MODIFICARE: Elimina TOATE NTFY-urile vechi si adauga O SINGURA
        print("=" * 70)
        print("3. MODIFICARE: ELIMIN TOATE NTFY VECHI, ADAUG O SINGURA")
        print("=" * 70)
        print()
        
        lines = out.split('\n')
        new_lines = []
        
        i = 0
        mailx_added_ntfy = False  # Flag pentru a adauga doar O DATA dupa mailx
        
        while i < len(lines):
            line = lines[i]
            
            # ELIMINA orice linie cu NTFY vechi
            if any(x in line for x in [
                'ntfy_notify.sh',
                'NTFY_MSG=',
                'Notificare NTFY',
                'whatsapp_send.sh'
            ]):
                i += 1
                continue
            
            # Dupa mailx normal (nu special_mail), adauga O SINGURA NTFY
            if '/bin/cat /tmp/tmpmail${BKP_SLOT} | mailx -s "$SUBJECT  $BACKUP_TYPE " "$BKP_MAIL"' in line:
                new_lines.append(line)
                new_lines.append('')
                
                # Verifica daca urmeaza special_mail sau exit_backup
                next_context = '\n'.join(lines[i+1:i+10])
                
                if 'special_mail:' not in next_context and not mailx_added_ntfy:
                    # Adauga O SINGURA notificare dupa primul mailx
                    new_lines.append('# Trimitere notificare NTFY cu informatii unice despre backup')
                    new_lines.append('echo "BACKUP: ${BACKUP_TYPE} | DB: ${ORACLE_SID} | CODE: ${ERROR_NUMBER} | TIME: `/bin/date \'+%Y-%m-%d %H:%M:%S\'` | STATUS: ${ERROR_MESSAGE}" | /usr/local/bin/ntfy_notify.sh')
                    new_lines.append('')
                    mailx_added_ntfy = True
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
        
        # 5. Verifica CATE linii cu NTFY
        print("=" * 70)
        print("5. VERIFICARE FINALA")
        print("=" * 70)
        print()
        
        out_count, _ = ssh_exec(ssh, "grep -c 'ntfy_notify.sh' /exlibris/backup/scripts/backup_mailer", show=False)
        print(f"Numar linii cu NTFY: {out_count.strip()}")
        print()
        
        if int(out_count.strip()) == 1:
            print("[OK] EXACT O NOTIFICARE NTFY!")
        else:
            print(f"[WARN] AM GASIT {out_count.strip()} NOTIFICARI - TREBUIE SA FIE 1!")
        
        # Afiseaza linia cu NTFY
        out_ntfy, _ = ssh_exec(ssh, "grep -B 2 -A 1 'echo \"BACKUP:' /exlibris/backup/scripts/backup_mailer", show=False)
        print()
        print("Linia cu NTFY:")
        print(out_ntfy)
        print()
        
        # 6. Test final
        print("=" * 70)
        print("6. TEST FINAL")
        print("=" * 70)
        print()
        
        now = ssh_exec(ssh, "/bin/date '+%Y-%m-%d %H:%M:%S'", show=False)[0].strip()
        test_msg = f"BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: {now} | STATUS: End FULL backup"
        
        print(f"Mesaj de test: {test_msg}")
        print()
        ssh_exec(ssh, f'echo "{test_msg}" | /usr/local/bin/ntfy_notify.sh', show=False)
        
        print("[OK] Notificare trimisa!")
        print()
        print("=" * 70)
        print("SETUP FINAL COMPLET!")
        print("=" * 70)
        print()
        print(">> REZULTAT:")
        print("   - O SINGURA notificare NTFY")
        print("   - Dupa fiecare backup (intre 23:00-02:00)")
        print("   - Cu informatii unice:")
        print("     * BACKUP TYPE (FULL, INCREMENTAL)")
        print("     * Oracle SID")
        print("     * COD EROARE (00 = success)")
        print("     * TIMESTAMP (momentul exact)")
        print("     * STATUS (mesaj complet)")
        print()
        print("Acum poti astepta backup-ul real pentru a verifica!")
        print()
        
        ssh.close()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
