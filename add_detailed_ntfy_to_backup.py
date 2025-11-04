#!/usr/bin/env python
"""
Adaug NTFY detaliate in backup_mailer cu informatii despre backup
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
    print("   ADAUGARE NTFY DETALIATE IN BACKUP_MAILER")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Citeste scriptul original
        print("=" * 70)
        print("1. CITESTE SCRIPTUL BACKUP_MAILER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "cat /exlibris/backup/scripts/backup_mailer", show=False)
        
        print("[OK] Script citit!")
        print()
        
        # 2. Verifica daca NTFY exista deja
        print("=" * 70)
        print("2. VERIFICARE NTFY EXISTENT")
        print("=" * 70)
        print()
        
        if "ntfy" in out.lower():
            print("[INFO] NTFY exista deja in script!")
            print()
            
            # Verifica ce fel de NTFY
            out_grep, _ = ssh_exec(ssh, "grep -n 'ntfy' /exlibris/backup/scripts/backup_mailer", show=False)
            print("Linii cu NTFY:")
            print(out_grep)
            print()
        else:
            print("[INFO] NTFY NU exista - voi adauga!")
            print()
        
        # 3. Creez backup
        print("=" * 70)
        print("3. CREARE BACKUP ORIGINAL")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/exlibris/backup/scripts/backup_mailer.backup.{timestamp}"
        
        ssh_exec(ssh, f"cp /exlibris/backup/scripts/backup_mailer {backup_file}", show=False)
        print(f"[OK] Backup creat: {backup_file}")
        print()
        
        # 4. Adaug NTFY dupa linia cu mailx
        print("=" * 70)
        print("4. ADAUGARE NTFY DETALIAT")
        print("=" * 70)
        print()
        
        # Mesajul NTFY cu detalii complete despre backup
        ntfy_code = '''
# Notificare NTFY cu detalii complete despre backup
NTFY_MSG="${SUBJECT}${BACKUP_TYPE}\\n\\nOracle DB: ${ORACLE_SID}\\nType: ${BACKUP_TYPE}\\nStatus: ${ERROR_MESSAGE}\\nCode: ${ERROR_NUMBER}\\nTime: `date '+%Y-%m-%d %H:%M:%S'`\\n\\nVerifica: /tmp/tmpmail${BKP_SLOT}"
echo "${NTFY_MSG}" | /usr/local/bin/ntfy_notify.sh'''
        
        print("Cod NTFY de adaugat:")
        print(ntfy_code)
        print()
        
        # Cautam linia unde se trimite email
        # /bin/cat /tmp/tmpmail${BKP_SLOT} | mailx -s "$SUBJECT  $BACKUP_TYPE " "$BKP_MAIL"
        
        # Modific scriptul
        lines = out.split('\n')
        new_lines = []
        added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Daca gasim linia cu mailx si nu am adaugat inca NTFY
            if 'mailx -s' in line and not added:
                # Adauga NTFY dupa linia cu mailx
                new_lines.append(ntfy_code)
                added = True
        
        modified_content = '\n'.join(new_lines)
        
        # 5. Salveaza scriptul modificat
        print("=" * 70)
        print("5. SALVARE SCRIPT MODIFICAT")
        print("=" * 70)
        print()
        
        # Scrie script modificat pe server
        ssh_exec(ssh, f"cat > /tmp/backup_mailer_modified <<'EOFSCRIPT'\n{modified_content}\nEOFSCRIPT", show=False)
        
        # Copiaza scriptul modificat
        ssh_exec(ssh, "cp /tmp/backup_mailer_modified /exlibris/backup/scripts/backup_mailer", show=False)
        ssh_exec(ssh, "chmod +x /exlibris/backup/scripts/backup_mailer", show=False)
        
        print("[OK] Script modificat salvat!")
        print()
        
        # 6. Verifica modificarea
        print("=" * 70)
        print("6. VERIFICARE MODIFICARE")
        print("=" * 70)
        print()
        
        out_verify, _ = ssh_exec(ssh, "grep -B 2 -A 5 'ntfy_notify' /exlibris/backup/scripts/backup_mailer", show=False)
        
        if "ntfy_notify" in out_verify:
            print("[OK] NTFY adaugat cu succes!")
            print()
            print("Linia adaugata:")
            print(out_verify[:500])
        else:
            print("[WARN] NTFY nu a fost adaugat!")
            print(out_verify)
        
        print()
        
        # 7. Test notificare
        print("=" * 70)
        print("7. TEST NOTIFICARE DETALIATA")
        print("=" * 70)
        print()
        
        test_msg = "Test backup detaliat\\n\\nOracle DB: ALEPH\\nType: FULL\\nStatus: SUCCESS\\nCode: 00\\nTime: $(date)\\n\\nBackup complet!"
        ssh_exec(ssh, f'echo "{test_msg}" | /usr/local/bin/ntfy_notify.sh', show=False)
        
        print("[OK] Notificare de test trimisa!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("SETUP COMPLET!")
        print("=" * 70)
        print()
        print(">> REZUMAT:")
        print("   - NTFY adaugat in backup_mailer cu detalii complete")
        print("   - Va trimite la fiecare backup:")
        print("     - Tipul backup-ului")
        print("     - Status (SUCCESS/ERROR)")
        print("     - Cod eroare (00, 01, 02, etc.)")
        print("     - Timestamp complet")
        print("     - Oracle SID")
        print("     - Mesaj detaliat")
        print()
        print(">> INFORMATII UNICE:")
        print("   - Timestamp: momentul exact al backup-ului")
        print("   - Cod eroare: 00 = succes, 01-14 = erori")
        print("   - Tip backup: FULL, INCREMENTAL, etc.")
        print("   - Oracle SID: baza de date care a fost backup-uita")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
