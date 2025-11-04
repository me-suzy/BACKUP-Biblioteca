import os
import sys
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


def run(ssh: paramiko.SSHClient, cmd: str):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=180)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    code = stdout.channel.recv_exit_status()
    return out, err, code


BACKUP_MAILER = "/exlibris/backup/scripts/backup_mailer"
NTFY = "/usr/local/bin/ntfy_notify.sh"


def main() -> None:
    host, user, password, port = load_conn()
    ssh = ssh_connect(host, user, password, port)

    print("[1] chmod +x backup_mailer")
    out, err, _ = run(ssh, f"chmod +x {BACKUP_MAILER} || true; ls -l {BACKUP_MAILER}")
    print(out or err)

    print("[2] Add csh safe defaults if missing")
    marker = "SAFE_DEFAULTS_ADDED"
    check_out, _, _ = run(ssh, f"grep -q '{marker}' {BACKUP_MAILER} && echo PRESENT || echo ABSENT")
    if "ABSENT" in check_out:
        defaults = (
            "# SAFE_DEFAULTS_ADDED\n"
            "if ( ! $?BACKUP_TYPE ) set BACKUP_TYPE = unknown\n"
            "if ( ! $?ORACLE_SID ) set ORACLE_SID = ALEPH\n"
            "if ( ! $?ERROR_NUMBER ) set ERROR_NUMBER = 00\n"
            "if ( ! $?ERROR_MESSAGE ) set ERROR_MESSAGE = unknown\n"
        )
        run(ssh, "cat > /tmp/defaults.csh <<'EOF'\n" + defaults + "EOF")
        cmd = (
            f"cp {BACKUP_MAILER} {BACKUP_MAILER}.bak_$(date +%Y%m%d_%H%M%S); "
            f"head -n 1 {BACKUP_MAILER} > /tmp/_bm_new; "
            f"echo '' >> /tmp/_bm_new; "
            f"cat /tmp/defaults.csh >> /tmp/_bm_new; "
            f"(tail -n +2 {BACKUP_MAILER} 2>/dev/null || tail +2 {BACKUP_MAILER}) >> /tmp/_bm_new; "
            f"mv /tmp/_bm_new {BACKUP_MAILER}; chmod +x {BACKUP_MAILER}"
        )
        out, err, _ = run(ssh, cmd)
        print(out or err)
    else:
        print("Defaults already present.")

    print("[3] Send csh NTFY test")
    test_script = (
        "#!/bin/csh -f\n"
        "set BACKUP_TYPE = user_data\n"
        "set ORACLE_SID = ALEPH\n"
        "set ERROR_NUMBER = 00\n"
        "set ERROR_MESSAGE = 'Test NTFY via csh'\n"
        "echo \"BACKUP: $BACKUP_TYPE | DB: $ORACLE_SID | CODE: $ERROR_NUMBER | TIME: `/bin/date '+%Y-%m-%d %H:%M:%S'` | STATUS: $ERROR_MESSAGE\" | "
        f"{NTFY}\n"
    )
    run(ssh, "cat > /tmp/test_ntfy.csh <<'EOF'\n" + test_script + "EOF")
    out, err, _ = run(ssh, "chmod +x /tmp/test_ntfy.csh && /tmp/test_ntfy.csh || true")
    print(out or err)

    ssh.close()


if __name__ == "__main__":
    main()
