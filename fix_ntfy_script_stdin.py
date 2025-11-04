#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix scriptul NTFY pentru a citi corect stdin
"""

import paramiko
import sys

HOST = "185.182.121.45"
USER = "root"
PASS = "YOUR-PASSWORD"
PORT = 22

def ssh_exec(ssh, cmd, show=True, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    if show:
        if out:
            print(out)
        if err:
            print(f"[ERR] {err}")
    return out, err


def main():
    print("=" * 70)
    print("   FIX SCRIPT NTFY - CITIRE STDIN")
    print("=" * 70)
    print()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Fix scriptul NTFY
        new_script = """#!/bin/bash
# Script NTFY optimizat pentru notificari server
# Compatibil cu OpenSSL vechi si curl 7.12.1

TOPIC="bariasi-5f07b8571f7c"
URL="http://ntfy.sh/${TOPIC}"

# Mesaj de la stdin sau argument
if [ -t 0 ]; then
    # Nu are stdin (terminal interactive)
    if [ -n "$1" ]; then
        MSG="$1"
    else
        MSG="Server notification"
    fi
else
    # Are stdin (redirect input), citeste de acolo
    MSG=$(cat)
    if [ -z "$MSG" ]; then
        MSG="Server notification"
    fi
fi

# Trimite notificare prin HTTP (fara HTTPS pentru compatibilitate)
curl -s -X POST -d "$MSG" "$URL" > /dev/null 2>&1

# Verifica succes
if [ $? -eq 0 ]; then
    echo "NTFY notification sent: $MSG"
else
    echo "Failed to send NTFY notification"
fi
"""
        
        print("[1] Creez script NTFY fixat...")
        ssh_exec(ssh, "cat > /usr/local/bin/ntfy_notify.sh << 'EOF'\n" + new_script + "\nEOF", show=False)
        print("[OK] Script creat!")
        print()
        
        print("[2] Setez permisiuni...")
        ssh_exec(ssh, "chmod +x /usr/local/bin/ntfy_notify.sh", show=False)
        print("[OK] Permisiuni setate!")
        print()
        
        print("[3] TEST: Test cu argument...")
        print()
        ssh_exec(ssh, "/usr/local/bin/ntfy_notify.sh 'Test fix - argument'")
        print()
        
        print("[4] TEST: Test cu stdin (pipe)...")
        print()
        ssh_exec(ssh, "echo 'Test fix - stdin pipe' | /usr/local/bin/ntfy_notify.sh")
        print()
        
        print("[5] TEST: Test cu comanda exacta din backup_mailer...")
        print()
        ssh_exec(ssh, """bash -c 'echo "BACKUP: FULL | DB: ALEPH | CODE: 00 | TIME: $(date "+%Y-%m-%d %H:%M:%S") | STATUS: End FULL backup test FINAL" | /usr/local/bin/ntfy_notify.sh'""")
        print()
        
        ssh.close()
        
        print()
        print("=" * 70)
        print("FIX FINALIZAT")
        print("=" * 70)
        print()
        print("Verifica telefonul pentru TOATE cele 3 notificari!")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

