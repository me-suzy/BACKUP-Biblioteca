import paramiko

CONFIG = "CONFIG_FINAL_29OCT.txt"
EXC_FILE = "/exlibris/backup/scripts/tar_excludes_user_data.txt"
TARGET = "/exlibris/backup/scripts/aleph_usr_data"


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


def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=180)
    return stdout.read().decode("utf-8", errors="ignore"), stderr.read().decode("utf-8", errors="ignore")


def main():
    cfg = read_cfg()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(cfg["HOST"], username=cfg["USER"], password=cfg["PASSWORD"], port=int(cfg.get("PORT", "22") or 22), timeout=30)

    # Ensure we replace tar lines to include $TAR_EXC_OPT
    cmd = (
        "sed -n '1,120p' {t}; echo '---'; grep -n 'tar ' {t}; echo '---REPL---'; "
        "sed -i 's/DOING :tar  -cvhf/DOING :tar $TAR_EXC_OPT -cvhf/' {t}; "
        "sed -i 's/DOING :tar -cvhf/DOING :tar $TAR_EXC_OPT -cvhf/' {t}; "
        "sed -i 's/tar -cvhf -/tar $TAR_EXC_OPT -cvhf -/' {t}; "
        "grep -n 'tar ' {t}"
    ).format(t=TARGET)
    out, err = run(ssh, cmd)
    print(out or err)

    ssh.close()


if __name__ == "__main__":
    main()
