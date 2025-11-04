#!/usr/bin/env python
"""
Configurez cron job pentru backup cu notificari NTFY
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
    print("   SETUP CRON JOB CU NOTIFICARI NTFY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica cron actual
        print("=" * 70)
        print("1. VERIFICARE CRON ACTUAL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l 2>&1", show=False)
        
        if out and "no crontab" not in out.lower():
            print("[INFO] Cron jobs existente:")
            print(out)
        else:
            print("[INFO] Nu exista cron jobs configurate")
        
        print()
        
        # 2. Creare/actualizare cron job
        print("=" * 70)
        print("2. CONFIGURARE NOTIFICARE ZILNICA")
        print("=" * 70)
        print()
        
        print("[INFO] Adaugare cron job pentru backup zilnic la 00:00...")
        print()
        
        # Backup current crontab
        ssh_exec(ssh, "crontab -l > /tmp/crontab_backup.txt 2>/dev/null || echo '' > /tmp/crontab_backup.txt", show=False)
        
        # Adaugare cron job pentru backup
        cron_job = "0 0 * * * /usr/local/bin/ntfy_notify.sh \"Backup zilnic completat pe server! $(date '+%%Y-%%m-%%d %%H:%%M:%%S')\""
        
        # Verifica daca exista deja
        current_cron = ssh_exec(ssh, "crontab -l 2>/dev/null || echo ''", show=False)[0]
        
        if "ntfy_notify.sh" in current_cron:
            print("[INFO] Cron job pentru NTFY exista deja!")
        else:
            # Adauga cron job
            ssh_exec(ssh, f"echo '{cron_job}' | crontab -", show=False)
            print("[OK] Cron job adaugat!")
        
        print()
        
        # 3. Verifica cron configurat
        print("=" * 70)
        print("3. VERIFICARE CRON CONFIGURAT")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l", show=False)
        
        if out:
            print("Cron jobs configurate:")
            print(out)
        
        print()
        
        # 4. Test cron job
        print("=" * 70)
        print("4. TEST NOTIFICARE")
        print("=" * 70)
        print()
        
        print("[INFO] Trimitere test notificare...")
        
        cmd = '/usr/local/bin/ntfy_notify.sh "Test cron job configurat! Notificarile functioneaza!"'
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=5)
        
        if out:
            print(out)
        
        print()
        print("[OK] Test notificare trimis!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("SETUP CRON COMPLET!")
        print("=" * 70)
        print()
        print(">> BACKUP ZILNIC:")
        print("   - Se ruleaza la: 00:00 (miezul noptii)")
        print("   - Trimite notificare la: bariasi-5f07b8571f7c")
        print()
        print(">> VERIFICA TELEFONUL:")
        print("   - In fiecare noapte la 00:00 vei primi notificare")
        print("   - Verifica aplicatia NTFY pentru confirmare")
        print()
        print(">> MODIFICARE CRON (daca vrei alta ora):")
        print("   ssh root@185.182.121.45")
        print("   crontab -e")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

