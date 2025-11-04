import os
import sys
import time
from typing import Dict, Tuple

import paramiko

CONFIG_FILE = "CONFIG_FINAL_29OCT.txt"


def read_simple_kv_config(path: str) -> Dict[str, str]:
    cfg: Dict[str, str] = {}
    if not os.path.isfile(path):
        return cfg
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip().upper()] = v.strip().strip("\"')")
    return cfg


essential_paths = {
    "logs": "/exlibris/backup/logs",
    "scripts": "/exlibris/backup/scripts",
    "backup_mailer": "/exlibris/backup/scripts/backup_mailer",
    "ntfy_notify": "/usr/local/bin/ntfy_notify.sh",
}


def load_conn() -> Tuple[str, str, str, int]:
    cfg = read_simple_kv_config(CONFIG_FILE)
    host = cfg.get("HOST", "")
    user = cfg.get("USER", "")
    password = cfg.get("PASSWORD", "")
    port = int(cfg.get("PORT", "22") or 22)
    if not (host and user and password):
        print("[E] Missing HOST/USER/PASSWORD in", CONFIG_FILE)
        sys.exit(2)
    return host, user, password, port


def ssh_connect(host: str, user: str, password: str, port: int = 22) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=password, port=port, timeout=30)
    return client


def run(ssh: paramiko.SSHClient, cmd: str) -> Tuple[str, str, int]:
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    code = stdout.channel.recv_exit_status()
    return out, err, code


def main() -> None:
    host, user, password, port = load_conn()
    ssh = ssh_connect(host, user, password, port)

    print("=== Server time ===")
    out, _, _ = run(ssh, "date")
    print(out.strip())

    print("\n=== Check NTFY script presence and perms ===")
    out, _, _ = run(ssh, f"ls -l {essential_paths['ntfy_notify']} || echo MISSING")
    print(out.strip())

    print("\n=== Grep NTFY in backup_mailer (csh) ===")
    out, _, _ = run(ssh, f"grep -n 'ntfy' {essential_paths['backup_mailer']} || true")
    print(out.strip() or "(no ntfy lines found)")

    print("\n=== Logs directory listing (ls -ltr) ===")
    out, _, _ = run(ssh, f"cd {essential_paths['logs']} && ls -ltr | tail -n 20")
    print(out)

    print("\n=== Latest backup logs (names) ===")
    out, _, _ = run(ssh, f"cd {essential_paths['logs']} && ls -1t | head -n 8")
    files = [l.strip() for l in out.splitlines() if l.strip()]
    print("\n".join(files))

    for name in files[:4]:
        log_path = f"{essential_paths['logs']}/{name}"
        print(f"\n----- wc -l: {name} -----")
        wcout, wcerr, _ = run(ssh, f"(wc -l {log_path} 2>/dev/null) || echo 'wc not found'")
        print(wcout or wcerr)
        print(f"----- Head: {name} -----")
        head_out, head_err, _ = run(ssh, f"head -n 20 {log_path}")
        print(head_out or head_err)
        print(f"----- Tail: {name} -----")
        tail_out, tail_err, _ = run(ssh, f"tail -n 50 {log_path}")
        print(tail_out or tail_err)

    ssh.close()


if __name__ == "__main__":
    main()
