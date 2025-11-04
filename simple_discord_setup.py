#!/usr/bin/env python
"""
Setup Discord Webhook simplu
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
    print("   SETUP DISCORD WEBHOOK")
    print("=" * 70)
    print()
    
    print("[INFO] Pentru Discord Webhook:")
    print("   1. Creaza un Discord Webhook")
    print("   2. Copiaza webhook URL")
    print()
    
    webhook_url = input("Discord Webhook URL (sau 'skip'): ").strip()
    
    if webhook_url.lower() == "skip":
        return 0
    
    print()
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Script simplu cu wget
        discord_script = f'''#!/bin/bash
WEBHOOK="{webhook_url}"
MSG="$1"
JSON="{{\\"content\\": \\"${{MSG}}\\"}}"
echo "${{JSON}}" | wget --post-data="@-" -O- --no-check-certificate "${{WEBHOOK}}" >/dev/null 2>&1
echo "Notification sent to Discord"
'''
        
        print("[INFO] Creez script Discord...")
        ssh_exec(ssh, f'cat > /usr/local/bin/discord_send.sh <<\'EOF\'\n{discord_script}\nEOF', show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/discord_send.sh", show=False)
        
        # Test
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ssh_exec(ssh, f'/usr/local/bin/discord_send.sh "Test: {timestamp}"', timeout=10)
        
        print("[OK] Script creat si testat!")
        print()
        print(">> UTILIZARE:")
        print("   /usr/local/bin/discord_send.sh \"Mesajul tau\"")
        print()
        
        ssh.close()
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

