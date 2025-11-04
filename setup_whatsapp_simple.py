#!/usr/bin/env python
"""
Setup WhatsApp notifications simple
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
    print("   SETUP WHATSAPP NOTIFICARI")
    print("=" * 70)
    print()
    
    print("[INFO] Alternative pentru WhatsApp:")
    print()
    print("   OPTIUNEA 1: Twilio WhatsApp API")
    print("   - Necesita Twilio account (FREE for test)")
    print("   - Destul de complex")
    print()
    print("   OPTIUNEA 2: WhatsApp Business API")
    print("   - Free pentru business")
    print("   - Destul de complex pentru setup")
    print()
    print("   OPTIUNEA 3: Callmebot (CEL MAI SIMPLU)")
    print("   - GRATUIT")
    print("   - Setup in 2 minute")
    print("   - Recomandat pentru test")
    print()
    
    print("=" * 70)
    print()
    print("[INFO] Recomand: Callmebot pentru simplitate!")
    print()
    print("   - Necesita doar: API_KEY de pe https://www.callmebot.com/")
    print("   - Setup instant")
    print("   - GRATUIT")
    print()
    
    choice = input("Vrei sa continui cu Callmebot? (y/n): ").strip().lower()
    
    if choice != "y":
        print()
        print("[INFO] Setup anulat. NTFY functioneaza perfect deja!")
        return 0
    
    print()
    print("[INFO] Pentru Callmebot:")
    print("   1. Mergi la: https://www.callmebot.com/")
    print("   2. Login cu Facebook")
    print("   3. Ia API_KEY")
    print()
    
    api_key = input("Callmebot API_KEY (sau 'skip'): ").strip()
    
    if api_key.lower() == "skip":
        print()
        print("[INFO] Setup anulat.")
        return 0
    
    print()
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Creez script Callmebot
        print("=" * 70)
        print("CREARE SCRIPT CALLMEBOT")
        print("=" * 70)
        print()
        
        callmebot_script = f'''#!/bin/bash
# Script pentru trimitere notificari prin WhatsApp (Callmebot)

API_KEY="{api_key}"

send_whatsapp() {{
    local message="$1"
    
    # Trimite mesaj prin Callmebot
    curl -s -X POST "https://api.callmebot.com/whatsapp.php?apikey=${{API_KEY}}&text=${{message}}" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "WhatsApp notification sent successfully"
    else
        echo "Failed to send WhatsApp notification"
    fi
}}

if [ -z "$1" ]; then
    echo "Usage: whatsapp_send.sh <message>"
    exit 1
fi

send_whatsapp "$1"
'''
        
        print("[INFO] Creez script Callmebot...")
        ssh_exec(ssh, f'cat > /usr/local/bin/whatsapp_send.sh <<\'EOFCALL\'\n{callmebot_script}\nEOFCALL', show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/whatsapp_send.sh", show=False)
        print("[OK] Script Callmebot creat!")
        print()
        
        # Test
        print("=" * 70)
        print("TEST NOTIFICARE WHATSAPP")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_message = f"Test WhatsApp de pe server Linux {timestamp}"
        
        print(f"[INFO] Trimitere test...")
        print()
        
        cmd = f'/usr/local/bin/whatsapp_send.sh "{test_message}"'
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=10)
        
        print("Output:")
        print(out)
        print()
        
        print("[OK] Test trimis! Verifica WhatsApp!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("SETUP CALLMEBOT COMPLET!")
        print("=" * 70)
        print()
        print(">> UTILIZARE:")
        print("   /usr/local/bin/whatsapp_send.sh \"Mesajul tau\"")
        print()
        print(">> PENTRU CRON:")
        print("   0 0 * * * /usr/local/bin/whatsapp_send.sh \"Backup completat!\"")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

