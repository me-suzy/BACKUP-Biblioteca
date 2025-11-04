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


def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode("utf-8", errors="ignore")


def main():
    cfg = read_cfg()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(cfg["HOST"], username=cfg["USER"], password=cfg["PASSWORD"], port=int(cfg.get("PORT", "22") or 22), timeout=30)

    print(run(ssh, "ls -l /exlibris/backup/scripts/exec_backup_main 2>/dev/null || true"))
    print(run(ssh, "cd /exlibris/backup/scripts && ls -1"))
    print("EXEC_BACKUP_MAIN part1:\n" + run(ssh, "sed -n '1,160p' /exlibris/backup/scripts/exec_backup_main"))
    print("EXEC_BACKUP_MAIN part2:\n" + run(ssh, "sed -n '160,320p' /exlibris/backup/scripts/exec_backup_main"))
    print("EXEC_BACKUP_MAIN part3:\n" + run(ssh, "sed -n '320,640p' /exlibris/backup/scripts/exec_backup_main"))

    ssh.close()


if __name__ == "__main__":
    main()
