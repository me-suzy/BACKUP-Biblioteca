#!/usr/bin/env python
"""
Creez scriptul final NTFY pentru notificari pe server
"""

import paramiko
import sys

HOST = "185.182.121.45"
USER = "root"
PASS = "YOUR-PASSWORD"
PORT = 22
TOPIC = "bariasi-5f07b8571f7c"


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
    print("   CREARE SCRIPT FINAL NTFY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Creez script optimizat pentru cron
        print("=" * 70)
        print("CREARE SCRIPT NTFY OPTIMIZAT")
        print("=" * 70)
        print()
        
        ntfy_script = f'''#!/bin/bash
# Script NTFY optimizat pentru notificari server
# Compatibil cu OpenSSL vechi si curl 7.12.1

TOPIC="{TOPIC}"
URL="http://ntfy.sh/${{TOPIC}}"

# Mesaj de la stdin sau argument
if [ -t 0 ]; then
    # Are stdin (redirect input), citeste de acolo
    MSG=$(cat)
else
    # Are argument, foloseste arg
    MSG="$1"
fi

if [ -z "$MSG" ]; then
    MSG="Server notification"
fi

# Trimite notificare prin HTTP (fara HTTPS pentru compatibilitate)
curl -s -X POST -d "$MSG" "$URL" > /dev/null 2>&1

# Verifica succes
if [ $? -eq 0 ]; then
    echo "NTFY notification sent: $MSG"
else
    echo "Failed to send NTFY notification"
fi
'''
        
        print("[INFO] Creez scriptul NTFY...")
        ssh_exec(ssh, f'cat > /usr/local/bin/ntfy_notify.sh <<\'EOFNTFY\'\n{ntfy_script}\nEOFNTFY', show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/ntfy_notify.sh", show=False)
        print("[OK] Script creat in /usr/local/bin/ntfy_notify.sh")
        print()
        
        # Test
        print("=" * 70)
        print("TEST SCRIPT FINAL")
        print("=" * 70)
        print()
        
        print("[INFO] Trimitere test...")
        
        out, _ = ssh_exec(ssh, '/usr/local/bin/ntfy_notify.sh "Script final configurat! Functioneaza perfect!"', show=False, timeout=5)
        
        if out:
            print(out)
        
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("SETUP FINALIZAT!")
        print("=" * 70)
        print()
        print(">> UTILIZARE:")
        print("   /usr/local/bin/ntfy_notify.sh \"Mesajul tau\"")
        print()
        print(">> EXEMPLE:")
        print("   /usr/local/bin/ntfy_notify.sh \"Backup completat!\"")
        print("   echo \"Eroare!\" | /usr/local/bin/ntfy_notify.sh")
        print()
        print(">> PENTRU CRON (backup zilnic):")
        print("   0 0 * * * /usr/local/bin/ntfy_notify.sh \"Backup completat!\"")
        print()
        print(">> PENTRU MONITORING:")
        print("   tail -f /var/log/syslog | /usr/local/bin/ntfy_notify.sh")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

