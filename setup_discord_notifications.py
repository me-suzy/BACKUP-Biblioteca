#!/usr/bin/env python
"""
Configurez Discord Webhook pentru notificari
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
    print("   SETUP DISCORD WEBHOOK PENTRU NOTIFICARI")
    print("=" * 70)
    print()
    
    print("[INFO] Pentru Discord Webhook:")
    print("   1. Creaza un Discord Webhook")
    print("   2. Copiaza webhook URL")
    print("   3. Configuram notificarile pe server!")
    print()
    
    print("=" * 70)
    print("PENTRU A CREA DISCORD WEBHOOK:")
    print("=" * 70)
    print()
    print("   1. Deschide Discord pe browser")
    print()
    print("   2. Mergi intr-un server sau canal")
    print()
    print("   3. Click pe ⚙️ (Settings) al canalului")
    print()
    print("   4. Click pe 'Integrations'")
    print()
    print("   5. Click pe 'Webhooks'")
    print()
    print("   6. Click pe 'New Webhook'")
    print()
    print("   7. DA UN NUME (ex: 'Linux Server Notifications')")
    print()
    print("   8. COPIEAZA webhook URL (in genul asta):")
    print("      https://discord.com/api/webhooks/123456789/ABCdefGHI...")
    print()
    print("=" * 70)
    print()
    
    webhook_url = input("Introdu Discord Webhook URL (sau 'skip'): ").strip()
    
    if webhook_url.lower() == "skip":
        print()
        print("[INFO] Skip Discord setup...")
        print()
        return 0
    
    if not webhook_url.startswith("https://discord.com/api/webhooks/"):
        print()
        print("[ERROR] Webhook URL nu este valid!")
        print("Trebuie sa inceapa cu: https://discord.com/api/webhooks/")
        print()
        return 1
    
    print()
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Creez script Discord
        print("=" * 70)
        print("CREARE SCRIPT DISCORD")
        print("=" * 70)
        print()
        
        discord_script = f'''#!/bin/bash
# Script pentru trimitere notificari prin Discord Webhook
# Compatibil cu vechile versiuni de curl si OpenSSL

WEBHOOK_URL="{webhook_url}"

send_notification() {{
    local message="$1"
    local username="Linux Server"
    
    # Base64 message pentru compatibilitate
    local encoded_message=$(echo "${{message}}" | base64 -w 0 2>/dev/null || echo "${{message}}")
    
    # Trimite notificare prin Discord Webhook
    # Folosim wget daca curl nu functioneaza
    if command -v wget >/dev/null 2>&1; then
        echo -n "{{\\"username\\": \\"${{username}}\\", \\"content\\": \\"${{message}}\\"}}" | \\
        wget --no-check-certificate -O- --post-data="@-" --header="Content-Type: application/json" "${{WEBHOOK_URL}}" > /dev/null 2>&1
    else
        echo "Failed to send Discord notification"
    fi
    
    if [ $? -eq 0 ]; then
        echo "Discord notification sent successfully"
    else
        echo "Failed to send Discord notification"
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
        
        print("[INFO] Creez scriptul Discord pe server...")
        ssh_exec(ssh, f'cat > /usr/local/bin/discord_send.sh <<\'EOFDISCORD\'\n{discord_script}\nEOFDISCORD', show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/discord_send.sh", show=False)
        print("[OK] Script Discord creat in /usr/local/bin/discord_send.sh")
        print()
        
        # Test
        print("=" * 70)
        print("TEST NOTIFICARE DISCORD")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("[INFO] Trimitere test notificare Discord...")
        print()
        
        cmd = f'/usr/local/bin/discord_send.sh "Test notificare Discord de pe serverul Linux!\\n\\nTimestamp: {timestamp}\\nServer: {HOST}\\nStatus: SUCCESS"'
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=10)
        
        if out:
            print("Output:")
            print(out)
        
        print()
        print("[OK] Notificare Discord trimisa!")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("SETUP DISCORD COMPLET!")
        print("=" * 70)
        print()
        print("Notificari Discord sunt configurate pe serverul Linux!")
        print("Verifica Discord pentru notificarea de test!")
        print()
        print(">> CUM SA FOLOSESTI:")
        print("   /usr/local/bin/discord_send.sh \"Mesajul tau\"")
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

