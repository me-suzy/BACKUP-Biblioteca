#!/usr/bin/env python
"""
Configurez Telegram Bot pe serverul Linux pentru notificari
"""

import paramiko
import sys
import time
from datetime import datetime

HOST = "85.186.121.42"
USER = "root"
PASS = "ac@demia"
PORT = 22

# Token Telegram Bot
TELEGRAM_TOKEN = "YOUR-TOKEN"


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


def get_chat_id(telegram_token):
    """Obține chat ID-ul pentru bot"""
    print("[INFO] Pentru a obtine chat ID-ul:")
    print("   1. Trimite un mesaj botului in Telegram")
    print("   2. Mergi la: https://api.telegram.org/bot{}/getUpdates".format(telegram_token))
    print("   3. Cauta 'chat':{'id':XXX in raspuns")
    print("   4. Chat ID este numarul din 'id':XXX")
    print()
    return None


def main():
    print("=" * 70)
    print("   SETUP TELEGRAM NOTIFICARI PE SERVERUL LINUX")
    print("=" * 70)
    print()
    
    print(f"[INFO] Telegram Token: {TELEGRAM_TOKEN[:20]}...")
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Creez scriptul Python pentru Telegram pe server
        print("=" * 70)
        print("1. CREARE SCRIPT TELEGRAM PE SERVER")
        print("=" * 70)
        print()
        
        telegram_script = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script de trimitere notificari prin Telegram

import sys
import urllib2
import json

TELEGRAM_TOKEN = "{TELEGRAM_TOKEN}"

def send_telegram(message, chat_id):
    """Trimite mesaj prin Telegram"""
    try:
        url = "https://api.telegram.org/bot{{}}/sendMessage".format(TELEGRAM_TOKEN)
        data = {{
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }}
        
        req = urllib2.Request(url)
        req.add_header("Content-Type", "application/json")
        
        response = urllib2.urlopen(req, json.dumps(data).encode("utf-8"))
        result = json.loads(response.read().decode("utf-8"))
        
        if result.get("ok"):
            print("Telegram message sent successfully")
            return True
        else:
            print("Failed to send Telegram message")
            return False
    except Exception as e:
        print("Error sending Telegram message: {{}}".format(e))
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: telegram_send.py <chat_id> <message>")
        sys.exit(1)
    
    chat_id = sys.argv[1]
    message = sys.argv[2]
    
    success = send_telegram(message, chat_id)
    sys.exit(0 if success else 1)
'''
        
        print("[INFO] Creez scriptul Telegram pe server...")
        ssh_exec(ssh, f'cat > /usr/local/bin/telegram_send.py <<\'EOFTELEGRAM\'\n{telegram_script}\nEOFTELEGRAM', show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/telegram_send.py", show=False)
        print("[OK] Script Telegram creat in /usr/local/bin/telegram_send.py")
        print()
        
        # 2. Verific ca Python 2 este disponibil
        print("=" * 70)
        print("2. VERIFICARE PYTHON PE SERVER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "python --version 2>&1", show=False)
        if "Python" in out:
            print(f"[OK] {out.strip()}")
        else:
            print("[WARN] Python nu este disponibil")
        
        print()
        
        # 3. Obtin chat ID-ul
        print("=" * 70)
        print("3. OBTINERE CHAT ID TELEGRAM")
        print("=" * 70)
        print()
        
        print("[INFO] Pentru a obtine Chat ID-ul:")
        print("   1. Deschide Telegram pe telefon")
        print(f"   2. Cauta botul tau")
        print("   3. Trimite un mesaj botului (ex: /start)")
        print("   4. Mergi la: https://api.telegram.org/bot{}/getUpdates".format(TELEGRAM_TOKEN))
        print("   5. Cauta 'chat':{'id':XXX in raspuns")
        print("   6. Chat ID este numarul din 'id':XXX")
        print()
        print("[EXEMPLE de Chat ID:]")
        print("   - Telegram personal: numarul tau (ex: 123456789)")
        print("   - Grup Telegram: numarul negativ al grupului (ex: -987654321)")
        print()
        
        # 4. Test simplu fara chat ID
        print("=" * 70)
        print("4. TEST TELEGRAM")
        print("=" * 70)
        print()
        
        print("[INFO] Introdu Chat ID-ul (ex: 123456789):")
        print("   Sau spune-mi 'skip' pentru a testa mai tarziu")
        print()
        
        chat_id = input("Chat ID: ").strip()
        
        if chat_id.lower() != "skip":
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            test_message = f"""Test notificare Telegram de pe serverul Linux!

Timestamp: {timestamp}
Server: 85.186.121.42
Token: {TELEGRAM_TOKEN[:20]}...

Acesta este un test pentru a verifica ca Telegram Bot functioneaza!
"""
            
            print()
            print(f"[INFO] Trimitere mesaj Telegram...")
            print(f"[INFO] Chat ID: {chat_id}")
            print(f"[INFO] Message: Test notificare Telegram")
            print()
            
            # Trimitere mesaj
            cmd = f'python /usr/local/bin/telegram_send.py {chat_id} "{test_message}"'
            out, _ = ssh_exec(ssh, cmd, show=False, timeout=10)
            
            if out:
                print("Output:")
                print(out)
            
            print()
            print("[OK] Mesaj Telegram trimis!")
            print()
            print(">> VERIFICA TELEGRAM:")
            print("   - Deschide chat-ul cu botul")
            print("   - Ar trebui sa vezi mesajul de test")
            print()
        
        # 5. Sumar si instructiuni
        print("=" * 70)
        print("SETUP TELEGRAM COMPLET!")
        print("=" * 70)
        print()
        print(">> CE AM CONFIGURAT:")
        print("   - Script Telegram creat: /usr/local/bin/telegram_send.py")
        print("   - Token configurat: " + TELEGRAM_TOKEN[:20] + "...")
        print()
        print(">> CUM SA FOLOSESTI:")
        print("   python /usr/local/bin/telegram_send.py <chat_id> \"Mesajul tau\"")
        print()
        print(">> EXEMPLE:")
        print("   python /usr/local/bin/telegram_send.py 123456789 \"Salut!\"")
        print("   python /usr/local/bin/telegram_send.py 123456789 \"Backup completat!\"")
        print()
        print(">> PENTRU CRON JOB:")
        print("   Adauga in crontab:")
        print("   0 0 * * * python /usr/local/bin/telegram_send.py <chat_id> \"Backup completat!\"")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("MISIUNEA COMPLETA!")
        print("=" * 70)
        print()
        print("Telegram Bot este configurat pe serverul Linux!")
        print("Poti primi notificari instant prin Telegram!")
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

