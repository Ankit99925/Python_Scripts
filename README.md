# python

Ops scripts in Python. Some are ports of the bash versions in `~/scripts`,
written to see what changes between the two languages.

| Script         | Does                                                    |
|----------------|---------------------------------------------------------|
| `netcheck.py`  | host:port reachability from a file                      |
| `health.py`    | uptime, disk, memory, containers on this machine        |
| `gcpstatus.py` | list GCE instances as a table                           |
| `ipwatch.py`   | report this machine's local IP, warn when it changes    |
| `opnwatch/`    | fetch the OPNsense config daily and report what changed |

`opnwatch` is a project rather than a script — its own venv, a dependency,
credentials and a systemd timer. It has its own README.

## Running them

Everything except `opnwatch` uses only the standard library, so:

    python3 netcheck.py -h

`opnwatch` needs its venv:

    cd opnwatch
    source venv/bin/activate

## What Python changed

**`argparse` replaced getopts**, plus the hand-written usage block. The help
text is generated from the same lines that define the flags, so it cannot go
stale.

**Exceptions replaced checking exit codes.** Instead of testing `$?` after each
command, failure raises and you catch what you expect. A malformed line in a
config file raises `ValueError` from `line.split()` rather than silently
putting two fields into one variable.

**The standard library replaced shelling out.** `shutil.disk_usage()` instead
of parsing `df` through `tail` and `tr`. `json.loads()` instead of `jq`.
`socket` instead of `nc`. Each swap removes a dependency and makes the script
more portable — `ipwatch.py` would run on Windows unchanged, while `health.py`
would not, because the commands it calls do not exist there.

**Nothing needed quoting.** No word splitting, no `"$var"` everywhere.

## Where bash still wins

`health.py` is mostly `subprocess.run(["uptime"], capture_output=True,
text=True)` where bash just says `uptime`. When a script is only orchestrating
commands, bash says it with less ceremony.

The rule that fell out of writing both: **bash to call commands, Python once
there is logic or data between them.**

## Things worth knowing

**`if __name__ == "__main__":`** means "only run this when the file is executed
directly, not when it is imported". Without it, importing a function from a
script also runs everything else in it.

**A local IP is not just the address on an interface.** A machine with Docker
and libvirt has several. The routing table decides which one is used for a
given destination, and `ipwatch.py` asks the kernel that question by opening a
UDP socket toward an external address and reading back which local address it
would use. No packet is sent.
