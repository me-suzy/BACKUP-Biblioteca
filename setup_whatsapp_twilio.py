#!/usr/bin/env python
"""
Setup WhatsApp prin Twilio - pas cu pas
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
    print("   SETUP WHATSAPP PRIN TWILIO")
    print("=" * 70)
    print()
    
    print("[INFO] PASUL 1: CONFIGUREAZA WHATSAPP SANDBOX IN TWILIO")
    print()
    print("   1. In Twilio Console, mergi la 'Messaging' din sidebar")
    print()
    print("   2. Click pe 'Try it out' sau 'Get Started with WhatsApp'")
    print()
    print("   3. Dupa ce ai configurat Sandbox, vei primi un COD")
    print()
    print("   4. Trimite acel COD pe WhatsApp la numarul precizat")
    print()
    print("   5. CONFIRM pe WhatsApp pentru activare!")
    print()
    
    print("=" * 70)
    print()
    
    print("[INFO] PASUL 2: OBTINE CREDENTIALELE")
    print()
    print("   In Twilio Console, ia:")
    print()
    
    account_sid = input("Account SID (din coltul de sus): ").strip()
    auth_token = input("Auth Token (click Show): ").strip()
    twilio_whatsapp = input("WhatsApp Number (din Sandbox, ex: whatsapp:+14155238886): ").strip()
    recipient = input("Numarul tau pentru WhatsApp (ex: +40723123456): ").strip()
    
    print()
    
    if not account_sid or not auth_token or not twilio_whatsapp or not recipient:
        print("[ERROR] Toate campurile sunt obligatorii!")
        return 1
    
    print("=" * 70)
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Creez script WhatsApp
        print("=" * 70)
        print("CREARE SCRIPT WHATSAPP")
        print("=" * 70)
        print()
        
        whatsapp_script = f'''#!/bin/bash
# Script pentru trimitere notificari prin WhatsApp (Twilio)

ACCOUNT_SID="{account_sid}"
AUTH_TOKEN="{auth_token}"
TWILIO_NUM="{twilio_whatsapp}"
RECIPIENT="{recipient}"

send_whatsapp() {{
    local message="$1"
    
    # URL encode message
    encoded_message=$(printf "%s" "${{message}}" | curl -Gso /dev/null -w %{{url_effective}} --data-urlencode @- "" | sed -E "s/GET \\//?/g")
    encoded_message=${{encoded_message#?}}
    
    # Trimite mesaj prin Twilio WhatsApp API
    curl -s -X POST "https://api.twilio.com/2010-04-01/Accounts/${{ACCOUNT_SID}}/Messages.json" \\
        --data-urlencode "From=${{TWILIO_NUM}}" \\
        --data-urlencode "To=${{RECIPIENT}}" \\
        --data-urlencode "Body=${{message}}" \\
        -u "${{ACCOUNT_SID}}:${{AUTH_TOKEN}}" \\
        > /dev/null 2>&1
    
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
        
        print("[INFO] Creez script WhatsApp...")
        ssh_exec(ssh, f'cat > /usr/local/bin/whatsapp_send.sh <<\'EOFTW\'\n{whatsapp_script}\nEOFTW', show=False, timeout=5)
        ssh_exec(ssh, "chmod +x /usr/local/bin/whatsapp_send.sh", show=False)
        print("[OK] Script creat in /usr/local/bin/whatsapp_send.sh")
        print()
        
        # Test
        print("=" * 70)
        print("TEST NOTIFICARE WHATSAPP")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_message = f"Test WhatsApp de pe serverul Linux! {timestamp}"
        
        print(f"[INFO] Trimitere test mesaj...")
        print(f"[INFO] To: {recipient}")
        print()
        
        cmd = f'/usr/local/bin/whatsapp_send.sh "{test_message}"'
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=15)
        
        print("Output:")
        print(out)
        print()
        
        print("[OK] Test trimis!")
        print()
        print(">> VERIFICA WHATSAPP!")
        print("   Ar trebui sa primesti mesaj de test!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("SETUP WHATSAPP COMPLET!")
        print("=" * 70)
        print()
        print(">> UTILIZARE:")
        print("   /usr/local/bin/whatsapp_send.sh \"Mesajul tau\"")
        print()
        print(">> PENTRU BACKUP:")
        print("   Modifica /exlibris/backup/scripts/backup_mailer")
        print("   Adauga linia dupa 'mailx':")
        print("   /usr/local/bin/whatsapp_send.sh \"${{SUBJECT}} ${{BACKUP_TYPE}}: ${{ERROR_MESSAGE}}\"")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

