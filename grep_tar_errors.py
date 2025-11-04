import os
from typing import Dict
import paramiko

CONFIG_FILE = "CONFIG_FINAL_29OCT.txt"


def read_cfg() -> Dict[str, str]:
    cfg: Dict[str, str] = {}
    with open(CONFIG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip().upper()] = v.strip().strip("\"')")
    return cfg


def main() -> None:
    cfg = read_cfg()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(cfg["HOST"], username=cfg["USER"], password=cfg["PASSWORD"], port=int(cfg.get("PORT", "22") or 22), timeout=30)

    cmd = (
        "cd /exlibris/backup/logs && ls -1t | grep '^user_data_a5_Detail_' | head -n 1"
    )
    _, stdout, _ = ssh.exec_command(cmd)
    latest = stdout.read().decode("utf-8", errors="ignore").strip()
    print("Latest:", latest)
    if not latest:
        ssh.close()
        return

    # show tar error lines
    _, stdout, _ = ssh.exec_command(f"cd /exlibris/backup/logs && grep -n 'tar:' {latest} | head -n 80")
    print("\n-- tar lines --\n" + stdout.read().decode("utf-8", errors="ignore"))

    for pat in ["Permission denied", "file changed as we read it", "No such file or directory", "Input/output error"]:
        _, stdout, _ = ssh.exec_command(f"cd /exlibris/backup/logs && grep -n 'tar: .*{pat}' {latest} | head -n 40")
        out = stdout.read().decode("utf-8", errors="ignore")
        if out:
            print(f"\n-- {pat} --\n{out}")

    ssh.close()


if __name__ == "__main__":
    main()
