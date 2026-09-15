from pathlib import Path
import argparse
import socket

parser = argparse.ArgumentParser(description="Report local IP, warn on change")
parser.add_argument("-q", "--quiet", action="store_true",help="only output when the IP has changed")
args = parser.parse_args()

CACHE = Path.home() / ".cache" / "ipwatch"

def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()
current = local_ip()

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


