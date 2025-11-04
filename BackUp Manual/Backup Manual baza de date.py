#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pentru backup manual pe server Linux
Permite rularea unui backup instant (a5 sau a1) fara sa astepte cron-ul.

Utilizare:
    python "Backup Manual baza de date.py"          # Default: a5 (user_data)
    python "Backup Manual baza de date.py" a5       # user_data backup
    python "Backup Manual baza de date.py" a1       # ora_cold backup

Tipuri backup:
    - a5: user_data backup (aproximativ 1.8 GB)
    - a1: ora_cold backup (aproximativ 2.1 GB)

Notificari:
    - Trimite notificari NTFY la start si la trigger
    - Notificarea finala (succes/eroare) vine automat de la backup_mailer
"""

import os
import sys
import time
import socket
from typing import Dict, Tuple

import paramiko
import urllib.request
import urllib.error


# Cauta config-ul in acelasi folder cu scriptul
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "CONFIG_FINAL_29OCT.txt")


def read_simple_kv_config(path: str) -> Dict[str, str]:
    """Read KEY=VALUE lines, ignoring blanks and comments (#)."""
    cfg: Dict[str, str] = {}
    if not os.path.isfile(path):
        return cfg
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                cfg[key.strip().upper()] = value.strip().strip("\"')")
    return cfg


def load_connection_details() -> Dict[str, str]:
    cfg = read_simple_kv_config(CONFIG_FILE)
    host = os.getenv("BACKUP_HOST", cfg.get("HOST", ""))
    user = os.getenv("BACKUP_USER", cfg.get("USER", ""))
    password = os.getenv("BACKUP_PASSWORD", cfg.get("PASSWORD", ""))
    port = int(os.getenv("BACKUP_PORT", cfg.get("PORT", "22") or "22"))
    if not host or not user or not password:
        print("[E] Lipsesc credențiale (HOST/USER/PASSWORD). Setează în ENV sau in CONFIG_FINAL_29OCT.txt.")
        sys.exit(1)
    return {"host": host, "user": user, "password": password, "port": port}


def ensure_config_skeleton() -> None:
    """Creează fișier de config dacă nu există."""
    if os.path.isfile(CONFIG_FILE):
        return
    content = (
        "# Config pentru backup manual si NTFY\n"
        "# Completeaza valorile sau foloseste variabile de mediu BACKUP_* / NTFY_*\n"
        "HOST=\n"
        "USER=\n"
        "PASSWORD=\n"
        "PORT=22\n"
        "# IMPORTANT: Foloseste HTTP (nu HTTPS) pentru compatibilitate\n"
        "# Exemplu: http://ntfy.sh/NUME_TOPIC sau http://ntfy.server.tld/topic\n"
        "NTFY_URL=\n"
        "# Optional: token bearer\n"
        "NTFY_TOKEN=\n"
        "# Optional: titlu afisat in aplicatie\n"
        "NTFY_TITLE=Manual Backup\n"
        "# Optional: priority (min, low, default, high, max)\n"
        "NTFY_PRIORITY=default\n"
    )
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[INFO] Am creat schelet configuratie: {CONFIG_FILE}")
        print("[INFO] Completează valorile în fișierul de config!")
    except OSError:
        pass


def load_ntfy_details() -> Dict[str, str]:
    cfg = read_simple_kv_config(CONFIG_FILE)
    url = os.getenv("NTFY_URL", cfg.get("NTFY_URL", "")).strip()
    token = os.getenv("NTFY_TOKEN", cfg.get("NTFY_TOKEN", "")).strip()
    title = os.getenv("NTFY_TITLE", cfg.get("NTFY_TITLE", "Manual Backup")).strip() or "Manual Backup"
    priority = os.getenv("NTFY_PRIORITY", cfg.get("NTFY_PRIORITY", "default")).strip() or "default"
    return {"url": url, "token": token, "title": title, "priority": priority}


def send_ntfy(ntfy_cfg: Dict[str, str], message: str) -> None:
    """Trimite notificare NTFY. Suporta HTTP si HTTPS."""
    url = ntfy_cfg.get("url", "").strip()
    if not url:
        return
    
    # Asigura-te ca URL-ul este corect (HTTP sau HTTPS)
    # Daca e configurat cu https:// dar nu functioneaza, se poate schimba manual in config
    try:
        req = urllib.request.Request(url, data=message.encode("utf-8"), method="POST")
        # Headers: Title, Priority, Authorization (optional)
        req.add_header("Title", ntfy_cfg.get("title", "Manual Backup"))
        req.add_header("Priority", ntfy_cfg.get("priority", "default"))
        token = ntfy_cfg.get("token", "").strip()
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            _ = resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        # Nu afisa erori pentru NTFY - e optional
        pass


def ssh_connect(host: str, user: str, password: str, port: int = 22) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=password, port=port, timeout=30)
    return client


def run(ssh: paramiko.SSHClient, command: str, timeout: int = 60) -> Tuple[str, str, int]:
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    exit_code = stdout.channel.recv_exit_status()
    return out, err, exit_code


def trigger_manual_backup(ssh: paramiko.SSHClient, backup_type: str) -> str:
    # Generate timestamp on the remote host to build a deterministic log path
    ts_out, _, _ = run(ssh, "/bin/date +%Y%m%d_%H%M%S")
    ts = ts_out.strip() or str(int(time.time()))
    log_path = f"/exlibris/backup/logs/manual_backup_{ts}.log"

    # Start backup in background using csh entrypoint
    start_cmd = (
        "cd /exlibris/backup/scripts && "
        f"nohup /bin/csh exec_backup_main {backup_type} > {log_path} 2>&1 & echo $!"
    )
    out, err, _ = run(ssh, start_cmd)
    pid = out.strip().splitlines()[-1] if out.strip() else ""
    print(f"[OK] Backup pornit (pid={pid}). Log: {log_path}")
    return log_path


def tail_log(ssh: paramiko.SSHClient, log_path: str, seconds: int = 20) -> None:
    # Show a short rolling tail to give immediate feedback
    try:
        for i in range(seconds // 5):
            time.sleep(5)
            out, _, _ = run(ssh, f"/bin/tail -n 30 {log_path} || true", timeout=20)
            print("\n----- Ultimele linii din log -----\n" + out)
    except (socket.timeout, paramiko.SSHException):
        pass


def main() -> None:
    """Functie principala pentru backup manual."""
    # Accept optional arg: a5 (user_data) or a1 (ora_cold)
    backup_type = (sys.argv[1] if len(sys.argv) > 1 else "a5").strip().lower()
    
    # Mapare tipuri backup
    backup_names = {
        "a5": "user_data",
        "a1": "ora_cold"
    }
    
    if backup_type not in {"a5", "a1"}:
        print("[E] Tip invalid. Folosește: a5 (user_data) sau a1 (ora_cold)")
        print(f"    Exemplu: python \"{os.path.basename(__file__)}\" a5")
        sys.exit(2)

    backup_name = backup_names.get(backup_type, backup_type)
    
    print("=" * 60)
    print("  BACKUP MANUAL - Server Linux")
    print("=" * 60)
    print()
    
    ensure_config_skeleton()
    ntfy_cfg = load_ntfy_details()
    conn = load_connection_details()
    
    print(f"[INFO] Configurare:")
    print(f"  - Host: {conn['host']}")
    print(f"  - User: {conn['user']}")
    print(f"  - Tip backup: {backup_type} ({backup_name})")
    if ntfy_cfg.get("url"):
        print(f"  - NTFY: Configurat")
    else:
        print(f"  - NTFY: Neconfigurat (notificari dezactivate)")
    print()

    try:
        print("[INFO] Conectare la server...")
        ssh = ssh_connect(conn["host"], conn["user"], conn["password"], conn["port"])
        print("[OK] Conectat!")
        print()

        # Quick sanity: show server time
        server_time, _, _ = run(ssh, "/bin/date '+%Y-%m-%d %H:%M:%S'")
        server_time = server_time.strip()
        print(f"[INFO] Ora server: {server_time}")
        print()

        # Notify start
        start_msg = f"START manual backup | Type: {backup_type} ({backup_name}) | Server: {conn['host']} | Time: {server_time}"
        print(f"[INFO] Trimitere notificare start...")
        send_ntfy(ntfy_cfg, start_msg)
        print("[OK] Notificare start trimisă")
        print()

        print("[INFO] Pornire backup în background...")
        log_path = trigger_manual_backup(ssh, backup_type)
        print()
        
        print("[INFO] Așteptăm câteva secunde pentru a vedea progresul...")
        tail_log(ssh, log_path, seconds=20)
        print()

        # Notify triggered with log path
        trigger_msg = f"TRIGGERED manual backup | Type: {backup_type} ({backup_name}) | Log: {log_path}"
        send_ntfy(ntfy_cfg, trigger_msg)

        print("=" * 60)
        print("  BACKUP PORNIT CU SUCCES")
        print("=" * 60)
        print()
        print(f"[OK] Backup-ul rulează în background pe server")
        print(f"[OK] Log complet: {log_path}")
        print()
        print("[INFO] Vei primi notificare NTFY la finalizare (succes/eroare)")
        print("      Notificarea va fi trimisă automat de către backup_mailer")
        print()
        print("[TIP] Pentru a verifica progresul în timp real:")
        print(f"      ssh {conn['user']}@{conn['host']}")
        print(f"      tail -f {log_path}")
        print()

        ssh.close()
        
    except paramiko.AuthenticationException:
        print("[E] Eroare autentificare. Verifică USER și PASSWORD în config.")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"[E] Eroare SSH: {e}")
        sys.exit(1)
    except socket.timeout:
        print("[E] Timeout la conectare. Verifică HOST și PORT în config.")
        sys.exit(1)
    except Exception as e:
        print(f"[E] Eroare neașteptată: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()



