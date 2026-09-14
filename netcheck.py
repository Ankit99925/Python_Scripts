import socket 
import argparse


parser = argparse.ArgumentParser(description="Check host:port reachability")
parser.add_argument("-f", "--file", default="hosts.txt", help="host list file")
parser.add_argument("-t", "--timeout", type=int, default=2, help="connection timeout")
parser.add_argument("-q", "--quiet", action="store_true", help="only show failures")
args = parser.parse_args()

hosts=[]
def check(host,port, timeout=2):
    try:
        with socket.create_connection((host,port),timeout):
            return True
    except OSError:
        return False

try:
    with open(args.file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                host, port = line.split()
                hosts.append((host, int(port)))
            except ValueError:
                print(f"SKIP  bad line: {line}")
except FileNotFoundError:
    print(f"No such file: {args.file}")
    raise SystemExit(1)

failed = False

for host, port in hosts:
    ok = check(host, port, args.timeout)
    if ok:
        if not args.quiet:
            print(f"UP   {host}:{port}")
    else:
        print(f"DOWN {host}:{port}")
        failed = True

if failed:
    raise SystemExit(1)

