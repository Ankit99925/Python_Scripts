import subprocess
import shutil
import argparse

CHECKS = [
    ("Uptime",  ["uptime"]),
    ("Disk",    ["df", "-h", "/"]),
    ("Memory",  ["free", "-h"]),
    ("Docker",["docker","ps","--format","table {{.Names}}\t{{.Status}}"])
]

def run_check(label, command):
    print(f"--- {label} ---")
    try:
        result = subprocess.run(command, capture_output=True, text=True)
    except FileNotFoundError:
        print(f"(skipped: {command[0]} not installed)")
        return
    if result.returncode != 0:
        print(f"(failed: {result.stderr.strip()})")
        return
    print(result.stdout)

for label, command in CHECKS:
    run_check(label, command)

usage = shutil.disk_usage("/")
percent = usage.used / usage.total * 100

if percent > 80:
    print(f"WARNING: disk at {percent:.1f}%")
    raise SystemExit(1)

