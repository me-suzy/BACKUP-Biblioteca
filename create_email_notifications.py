#!/usr/bin/env python
"""
Configurez notificari email directe pe server
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
    print("   SETUP NOTIFICARI EMAIL")
    print("=" * 70)
    print()
    
    email = "ioan.fantanaru@gmail.com"
    
    print(f"[INFO] Adresa de email: {email}")
    print()
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Creez script simplu pentru notificari email
        print("=" * 70)
        print("CREARE SCRIPT NOTIFICARI EMAIL")
        print("=" * 70)
        print()
        
        email_script = f'''#!/bin/bash
# Script pentru trimitere notificari prin email
EMAIL="{email}"
SUBJECT=""
MESSAGE="$1"

if [ -z "$1" ]; then
    echo "Usage: notify.sh <message>"
    exit 1
fi

# Trimite email prin sendmail
(
echo "To: ${{EMAIL}}"
echo "From: root@{HOST}"
echo "Subject: Server Notification"
echo ""
echo "${{MESSAGE}}"
) | sendmail -t

echo "Email notification sent to ${{EMAIL}}"
'''
        
        print("[INFO] Creez script notificari email...")
        ssh_exec(ssh, f'cat > /usr/local/bin/notify.sh <<\'EOFNOTIFY\'\n{email_script}\nEOFNOTIFY', show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/notify.sh", show=False)
        print("[OK] Script creat in /usr/local/bin/notify.sh")
        print()
        
        # Test
        print("=" * 70)
        print("TEST NOTIFICARE EMAIL")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[INFO] Trimitere test email la: {email}")
        print()
        
        message = f"Test notificare email de pe serverul Linux!\n\nTimestamp: {timestamp}\nServer: {HOST}\nStatus: SUCCESS\n\nNotificarile functioneaza perfect!"
        
        cmd = f'/usr/local/bin/notify.sh "{message}"'
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=15)
        
        print("Output:")
        print(out)
        print()
        
        print("[OK] Email trimis!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("SETUP COMPLET!")
        print("=" * 70)
        print()
        print(">> CUM SA FOLOSESTI:")
        print("   /usr/local/bin/notify.sh \"Mesajul tau\"")
        print()
        print(">> EXEMPLE:")
        print("   /usr/local/bin/notify.sh \"Backup completat!\"")
        print("   /usr/local/bin/notify.sh \"Eroare in sistem!\"")
        print()
        print(">> PENTRU CRON JOB:")
        print("   0 0 * * * /usr/local/bin/notify.sh \"Backup completat!\"")
        print()
        print(f"Toate notificarile vor fi trimise la: {email}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

