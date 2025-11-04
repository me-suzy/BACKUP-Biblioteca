import paramiko

SCRIPTS_DIR = "/exlibris/backup/scripts"
EXCLUDE_FILE = f"{SCRIPTS_DIR}/tar_excludes_user_data.txt"
TARGET_SCRIPT = f"{SCRIPTS_DIR}/aleph_usr_data"  # correct script name

PATTERNS = [
    "/exlibris/aleph/u20_2/alephe/apache/logs/access_log",
    "/exlibris/aleph/u20_2/rai01/pc_tab/catalog/.#*",
]

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
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=180)
    return stdout.read().decode("utf-8", errors="ignore"), stderr.read().decode("utf-8", errors="ignore")


def main():
    cfg = read_cfg()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(cfg["HOST"], username=cfg["USER"], password=cfg["PASSWORD"], port=int(cfg.get("PORT", "22") or 22), timeout=30)

    # 1) Write excludes file (idempotent)
    content = "\n".join(PATTERNS) + "\n"
    run(ssh, f"cat > {EXCLUDE_FILE} <<'EOF'\n{content}EOF")
    out, err = run(ssh, f"ls -l {EXCLUDE_FILE} && echo '---' && cat {EXCLUDE_FILE}")
    print(out or err)

    # 2) Ensure target script exists
    out, err = run(ssh, f"ls -l {TARGET_SCRIPT} 2>/dev/null || echo MISSING")
    print(out or err)

    # 3) Patch aleph_usr_data: add TAR_EXC_OPT and inject into tar commands
    setenv_line = f"setenv TAR_EXC_OPT '-X {EXCLUDE_FILE} --ignore-failed-read'"
    patch = (
        f"cp {TARGET_SCRIPT} {TARGET_SCRIPT}.bak_$(date +%Y%m%d_%H%M%S); "
        f"head -n 1 {TARGET_SCRIPT} > /tmp/_new; echo {repr(setenv_line)} >> /tmp/_new; tail -n +2 {TARGET_SCRIPT} >> /tmp/_new; mv /tmp/_new {TARGET_SCRIPT}; "
        f"sed -i 's/DOING :tar  -cvhf/DOING :tar $TAR_EXC_OPT -cvhf/' {TARGET_SCRIPT} || true; "
        f"sed -i 's/DOING :tar -cvhf/DOING :tar $TAR_EXC_OPT -cvhf/' {TARGET_SCRIPT} || true; "
        f"sed -i 's/tar -cvhf -/tar $TAR_EXC_OPT -cvhf -/' {TARGET_SCRIPT} || true; "
        f"chmod +x {TARGET_SCRIPT}; grep -n 'TAR_EXC_OPT\|tar ' {TARGET_SCRIPT}"
    )
    out, err = run(ssh, patch)
    print(out or err)

    ssh.close()


if __name__ == "__main__":
    main()
