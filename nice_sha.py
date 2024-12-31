import time, os, subprocess



def get_sha():
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True).stdout.decode().strip()


def get_msg():
    return subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True).stdout.decode().split("\n")[0]

def set_time(timestamp="2025-01-01T00:00:00"):
    return subprocess.run(['git', 'commit', '--amend', '--no-edit', f'--date="{timestamp}"'])


def gen_timestamp(d, h, m, s):
    return f"2025-01-{d:02}T{h:02}:{m:02}:{s:02}"





sha = get_sha()
print(f"Working on {sha[:8]} {get_msg}")
if not input("continue? (y/N)") == "y": exit(0)

results = []
i = 0
while True:
    d = i // (3600*24)
    h = i // 3600 - d*24
    m = i // 60 - d*24*60 - h*60
    s = i - d*24*3600 - h*3600 - m*60
    timestamp = gen_timestamp(d+1, h, m, s)
    set_time(timestamp)
    sha = get_sha()
    results.append((sha, timestamp))
    print(sha[:8], timestamp)
    
    i+=1
    if i == 100000: break

sorted_sha = sorted(results, key=lambda x: int("0x" + x[0], 16))
print(sorted[:5])