from datetime import datetime
import subprocess, os, sys, time, hashlib, threading


RESET = "\033[0m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
DIM = "\033[2m"


def get_sha():
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True).stdout.decode().strip()


def get_msg():
    return subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True).stdout.decode().split("\n")[0]


def get_commit(sha):
    result = subprocess.run(
        ["git", "cat-file", "-p", sha],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Git error: {result.stderr}")

    lines = result.stdout.splitlines()
    parsed = {
        "tree": None,
        "parent": None,
        "author": None,
        "committer": None,
        "message": ""
    }

    in_message = False
    message_lines = []

    for line in lines:
        if in_message:
            message_lines.append(line)
            continue

        if line.startswith("tree "):
            parsed["tree"] = line.split(" ", 1)[1]
        elif line.startswith("parent "):
            parsed["parent"] = line.split(" ", 1)[1]
        elif line.startswith("author "):
            parsed["author"] = line[len("author "):]
        elif line.startswith("committer "):
            parsed["committer"] = line[len("committer "):]
        elif line.strip() == "":
            in_message = True
        else:
            continue
    parsed["message"] = "\n".join(message_lines).strip()
    return parsed


def set_date(date):
    env = os.environ.copy()
    env["GIT_COMMITTER_DATE"] = date
    return subprocess.run(["git", "commit", "--amend", "--no-edit", f'--date="{date}"'], env=env, capture_output=True)


def set_commit_timestamp(commit, timestamp):
    def replace_timestamp(field):
        parts = field.rsplit(" ", 2)
        parts[-2] = str(timestamp)
        return " ".join(parts)

    commit["author"] = replace_timestamp(commit["author"])
    commit["committer"] = replace_timestamp(commit["committer"])
    return commit


def unix_to_iso(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def build_commit(commit):
    lines = []
    lines.append(f"tree {commit['tree']}")
    if commit.get('parent'):
        lines.append(f"parent {commit['parent']}")
    lines.append(f"author {commit['author']}")
    lines.append(f"committer {commit['committer']}")
    lines.append("")
    lines.append(commit['message'].rstrip("\n"))

    content = "\n".join(lines) + "\n"
    header = f"commit {len(content)}\0"
    full_data = (header + content).encode("utf-8")
    return hashlib.sha1(full_data).hexdigest()


def is_closer_to_key(new_sha, old_sha, key):
    new = 0
    old = 0
    for i in range(min(len(key), 40)):
        if new_sha[i] == key[i]:
            new += 1
        else:
            break
    
    for i in range(min(len(key), 40)):
        if old_sha[i] == key[i]:
            old += 1
        else:
            break
    return new > old


def wait_for_enter():
    input("Press [Enter] to stop...\n")
    global stop_requested
    stop_requested = True



stop_requested = False
threading.Thread(target=wait_for_enter, daemon=True).start()


key = sys.argv[1] + "0"*(40-len(sys.argv[1] )) if len(sys.argv) >= 2 else "0"*40
sha = get_sha()
result = (sha, None)
commit = get_commit(sha)

timestamp = int(time.time())
t_start = time.monotonic()
i = 0
try:
    while not stop_requested:
        new_timestamp = timestamp - i
        commit = set_commit_timestamp(commit, new_timestamp)
        sha = build_commit(commit)

        if is_closer_to_key(sha, result[0], key):
            result = (sha, new_timestamp)

        rate = "--" if time.monotonic() - t_start == 0 else f"{i/(time.monotonic() - t_start) / 1000:.2f}"
        if i % 100_000 == 0:
            print(f"\033[2K\r{CYAN}🔹{result[0][:8]}{RESET}{DIM} - {RESET}{YELLOW}{result[1]} {RESET}{DIM}|{RESET} {BLUE}⚡{rate} kH/s{RESET}", end="")
        
        i += 1

    if result[1] is not None:
        print(f"\033[2K\r  {BLUE}Applying lowest SHA found...{RESET}", end=" ")

        set_date(unix_to_iso(result[1]))

        print(f"{GREEN}Done!{RESET}")
    else:
        print(f"\033[2K\r  {YELLOW}No lower SHA was found during execution.{RESET}")

    print(f"  {DIM}Exiting cleanly{RESET}")
    sys.exit(0)

except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
