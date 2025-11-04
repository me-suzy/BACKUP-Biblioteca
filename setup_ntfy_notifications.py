#!/usr/bin/env python
"""
Configurez NTFY pentru notificari gratis fara instalari pe server
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
    print("   SETUP NTFY PENTRU NOTIFICARI GRATIS")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Generare tema unica pentru NTFY
        print("=" * 70)
        print("1. GENERARE TEMA UNICA PENTRU NTFY")
        print("=" * 70)
        print()
        
        import hashlib
        unique_topic = hashlib.md5("bariasi_academy_linux_{}".format(HOST).encode()).hexdigest()[:12]
        ntfy_topic = "bariasi-{}".format(unique_topic)
        
        print(f"[OK] Tema unica generata: {ntfy_topic}")
        print()
        
        # 2. Creez script bash simplu pentru NTFY
        print("=" * 70)
        print("2. CREARE SCRIPT NTFY PE SERVER")
        print("=" * 70)
        print()
        
        ntfy_script = f'''#!/bin/bash
# Script simplu pentru trimitere notificari prin NTFY
# Nu necesita instalare, foloseste doar curl

TOPIC="{ntfy_topic}"
NTFY_URL="https://ntfy.sh/${{TOPIC}}"

send_notification() {{
    local message="$1"
    local title="${HOST}"
    local priority="default"
    
    # Trimite notificare prin NTFY
    curl -H "Title: ${{title}}" -H "Priority: ${{priority}}" -H "Tags: computer,server,linux" -d "${{message}}" "${{NTFY_URL}}" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "NTFY notification sent successfully"
    else
        echo "Failed to send NTFY notification"
    fi
}}

# Test mesaj
if [ "$1" == "test" ]; then
    send_notification "Test notificare de pe serverul Linux! Timestamp: $(date)"
else
    # Mesaj custom
    send_notification "$1"
fi
'''
        
        print("[INFO] Creez scriptul NTFY pe server...")
        ssh_exec(ssh, f'cat > /usr/local/bin/ntfy_send.sh <<\'EOFNTFY\'\n{ntfy_script}\nEOFNTFY', show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/ntfy_send.sh", show=False)
        print("[OK] Script NTFY creat in /usr/local/bin/ntfy_send.sh")
        print()
        
        # 3. Test NTFY
        print("=" * 70)
        print("3. TEST NOTIFICARE NTFY")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[INFO] Trimitere test notificare NTFY...")
        print(f"[INFO] Tema: {ntfy_topic}")
        print(f"[INFO] Message: Test notificare de pe serverul Linux!")
        print()
        
        cmd = f'/usr/local/bin/ntfy_send.sh "Test notificare NTFY de pe serverul Linux!\n\nTimestamp: {timestamp}\nServer: {HOST}\nStatus: SUCCESS"'
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=5)
        
        if out:
            print("Output:")
            print(out)
        
        print()
        print("[OK] Notificare NTFY trimisa!")
        print()
        
        # 4. Instructiuni pentru instalare pe telefon
        print("=" * 70)
        print("4. INSTALARE APLICATIE NTFY PE TELEFON")
        print("=" * 70)
        print()
        
        print(">> PASI PENTRU INSTALARE:")
        print()
        print("   1. DESCARCA aplicatia NTFY:")
        print("      - Android: https://play.google.com/store/apps/details?id=io.heckel.ntfy")
        print("      - iOS: https://apps.apple.com/app/ntfy/id1625396347")
        print()
        print("   2. DESCHIDE aplicatia NTFY")
        print()
        print("   3. ADAUGA SUBSCRIBE la tema:")
        print(f"      {ntfy_topic}")
        print()
        print("   4. ACUM VEI PRIMI NOTIFICARI de pe server!")
        print()
        
        # 5. Exemplu de utilizare
        print("=" * 70)
        print("5. EXEMPLE DE UTILIZARE")
        print("=" * 70)
        print()
        
        print(">> CUM SA FOLOSESTI:")
        print("   /usr/local/bin/ntfy_send.sh \"Mesajul tau\"")
        print()
        print(">> EXEMPLE:")
        print("   /usr/local/bin/ntfy_send.sh \"Backup completat!\"")
        print("   /usr/local/bin/ntfy_send.sh \"Eroare in sistem!\"")
        print("   /usr/local/bin/ntfy_send.sh \"Server restartat!\"")
        print()
        print(">> PENTRU CRON JOB:")
        print("   Adauga in crontab:")
        print("   0 0 * * * /usr/local/bin/ntfy_send.sh \"Backup completat!\"")
        print()
        print(">> PENTRU BACKUP:")
        print("   Echivalenteaza comanda 'mail' cu NTFY:")
        print("   echo 'Mesaj' | /usr/local/bin/ntfy_send.sh")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("SETUP NTFY COMPLET!")
        print("=" * 70)
        print()
        print("Notificari NTFY sunt configurate pe serverul Linux!")
        print("Instaleaza aplicatia NTFY pe telefon pentru a primi notificari!")
        print()
        print(f"Tema pentru subscribe: {ntfy_topic}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Eroare: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[WARN] Script intrerupt.")
        sys.exit(130)
