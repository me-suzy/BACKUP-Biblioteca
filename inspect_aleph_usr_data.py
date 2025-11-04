import paramiko

CONFIG = "CONFIG_FINAL_29OCT.txt"

def read_cfg():
    cfg = {}
    with open(CONFIG, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip().upper()] = v.strip().strip("\"')")
    return cfg


def main():
    cfg = read_cfg()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(cfg["HOST"], username=cfg["USER"], password=cfg["PASSWORD"], port=int(cfg.get("PORT", "22") or 22), timeout=30)

    for c in [
        "ls -l /exlibris/backup/scripts/aleph_usr_data 2>/dev/null || true",
        "head -n 200 /exlibris/backup/scripts/aleph_usr_data",
        "grep -n 'tar ' /exlibris/backup/scripts/aleph_usr_data || true",
    ]:
        stdin, stdout, stderr = ssh.exec_command(c)
        print(stdout.read().decode("utf-8", errors="ignore"))

    ssh.close()


if __name__ == "__main__":
    main()
