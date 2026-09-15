import requests
from pathlib import Path
import argparse
import subprocess

parser = argparse.ArgumentParser(description="Report public IP, warn on change")
parser.add_argument("-q", "--quiet", action="store_true",help="only output when the IP has changed")
args = parser.parse_args()

CACHE = Path.home() / ".cache" / "pubip"

resp = requests.get("https://api.ipify.org?format=json", timeout=5)
resp.raise_for_status()
current = resp.json()["ip"]

CACHE.parent.mkdir(parents=True, exist_ok=True)

if CACHE.exists():
    previous = CACHE.read_text().strip()
    if previous != current:
        print(f"CHANGED: {previous} -> {current}")
    elif not args.quiet:
        print(current)
elif not args.quiet:
    print(current)

CACHE.write_text(current)
