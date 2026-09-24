# opnwatch

Fetches the OPNsense configuration over its API on a timer, archives a copy,
and reports which sections changed since last time. Silent when nothing has.

Firewall rules, VLANs, aliases and DHCP settings live inside OPNsense, not in
any repository. This is what keeps a history of them.

## Requires

- Python 3.9+
- An OPNsense API key: System → Access → Users → `root` → **API keys** → **+**
- Network access to OPNsense's web interface on port 443

## Setup

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

    cp creds.env.example creds.env
    chmod 600 creds.env
    # fill in the key, secret and host

## Usage

    set -a; source creds.env; set +a
    python3 opnwatch.py

`set -a` makes everything defined afterwards an environment variable, which is
what the script reads. Without it they are shell variables only.

Output is one line when something changed, and nothing at all otherwise:

    CHANGED: filter, revision — saved config-20260923T112606Z.xml

`revision` is OPNsense's own change counter and appears on every real change,
so expect it alongside whatever actually differs.

## On a timer

    cp systemd/opnwatch.{service,timer} ~/.config/systemd/user/
    systemctl --user daemon-reload
    systemctl --user enable --now opnwatch.timer
    loginctl enable-linger $USER

The last line is needed or the timer stops when you log out.

    systemctl --user list-timers opnwatch.timer
    journalctl --user -u opnwatch.service -n 20

The unit reads `creds.env` with `EnvironmentFile`, so the credentials are never
in the unit file itself.

## How it works

1. Fetch `/api/core/backup/download/this` with the key and secret as basic auth
2. Strip every `persisted_at` attribute from the XML
3. Compare against the last saved copy, normalised the same way
4. If identical, exit silently
5. Otherwise archive a timestamped copy, update `latest.xml`, and name the
   top-level sections that differ

### Why the stripping matters

OPNsense writes a timestamp into a section whenever it saves that section. Two
configs that are identical in substance therefore differ in text. Without
removing those first, every single run would report a change, and a check that
always cries wolf is worse than no check.

### Why it names sections rather than showing a diff

The configuration contains the web certificate's private key, the root password
hash, and any WireGuard keys. Printing a diff would put those in your terminal
and in the journal. Naming the sections tells you what to look at without
exposing anything.

For the same reason the archives go to `~/lab-backup/`, which is deliberately
not a git repository, and every file is written mode `0600`.

## Notes

`verify=False` skips certificate checking, because OPNsense uses a self-signed
certificate. The warning it would otherwise print on every run is suppressed.

Possible additions: filter `revision` out of the reported sections, since it is
always present, and send a desktop notification rather than only writing to the
journal.
