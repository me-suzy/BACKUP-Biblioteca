#!/usr/bin/env python
"""
Setup WhatsApp notifications pentru server Linux
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
    
    print("[INFO] Pentru WhatsApp folosim Twilio API")
    print()
    
    print("=" * 70)
    print("PENTRU A CREA TWILIO ACCOUNT:")
    print("=" * 70)
    print()
    print("   1. Mergi la: https://www.twilio.com/try-twilio")
    print()
    print("   2. Creeaza un cont FREE (nu costa nimic pentru test)")
    print()
    print("   3. Verifica telefonul pentru activare")
    print()
    print("   4. In Twilio Console, ia:")
    print("      - Account SID")
    print("      - Auth Token")
    print()
    print("   5. Numara telefon:")
    print("      - Foloseste Twilio number pentru trimitere")
    print("      - Sau configureaza WhatsApp Business API")
    print()
    
    print("=" * 70)
    print()
    
    print("[INFO] Alternative mai simple pentru WhatsApp:")
    print()
    print("   OPȚIUNEA 1: Twilio WhatsApp API")
    print("   - Necesita account Twilio")
    print("   - Destul de complex pentru setup")
    print()
    print("   OPȚIUNEA 2: WhatsApp Business API")
    print("   - Free pentru test")
    print("   - Destul de complex pentru setup")
    print()
    print("   OPȚIUNEA 3: reusita.me (RECOMANDAT)")
    print("   - Cel mai simplu pentru test")
    print("   - Setup in 5 minute")
    print()
    print("   OPȚIUNEA 4: NTFY + WhatsApp Forward")
    print("   - Foloseste NTFY existent")
    print("   - Forward automat din NTFY catre WhatsApp")
    print()
    
    print("=" * 70)
    print()
    
    print("[INFO] Recomandare:")
    print()
    print("   - Deja ai NTFY functionand perfect!")
    print("   - NTFY trimite notificari instant pe telefon")
    print("   - Poti adauga mai multi oameni pe NTFY")
    print("   - WhatsApp ar fi doar o alternativa, dar mai complexa")
    print()
    print("   ESTI SIGUR ca vrei WhatsApp sau esti multumit cu NTFY?")
    print()
    
    choice = input("Continui cu WhatsApp? (y/n): ").strip().lower()
    
    if choice != "y":
        print()
        print("[INFO] Setup anulat. NTFY functioneaza perfect deja!")
        return 0
    
    print()
    print("=" * 70)
    print("SETUP WHATSAPP")
    print("=" * 70)
    print()
    
    # Asteapta credentialele
    print("[INFO] Introdu credentialele Twilio:")
    print()
    
    account_sid = input("Twilio Account SID (sau 'skip'): ").strip()
    
    if account_sid.lower() == "skip":
        print()
        print("[INFO] Setup anulat. NTFY ramane functional!")
        return 0
    
    auth_token = input("Twilio Auth Token: ").strip()
    twilio_number = input("Twilio Number (sau WhatsApp number): ").strip()
    recipient_number = input("Numarul tau de telefon (WhatsApp): ").strip()
    
    print()
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
TWILIO_NUMBER="{twilio_number}"
RECIPIENT="{recipient_number}"

send_whatsapp() {{
    local message="$1"
    
    # Trimite mesaj prin Twilio WhatsApp API
    curl -s -X POST "https://api.twilio.com/2010-04-01/Accounts/${{ACCOUNT_SID}}/Messages.json" \\
        --data-urlencode "From=whatsapp:${{TWILIO_NUMBER}}" \\
        --data-urlencode "To=whatsapp:${{RECIPIENT}}" \\
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
        ssh_exec(ssh, f'cat > /usr/local/bin/whatsapp_send.sh <<\'EOFWHA\'\n{whatsapp_script}\nEOFWHA', show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/whatsapp_send.sh", show=False)
        print("[OK] Script WhatsApp creat!")
        print()
        
        # Test
        print("=" * 70)
        print("TEST NOTIFICARE WHATSAPP")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_message = f"Test notificare WhatsApp de pe serverul Linux! {timestamp}"
        
        print(f"[INFO] Trimitere test la: {recipient_number}")
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
        print("SETUP WHATSAPP COMPLET!")
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

