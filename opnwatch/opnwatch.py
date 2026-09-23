import os
import requests
import urllib3
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BACKUP_DIR = Path.home() / "lab-backup" / "opnsense-configs"


def normalise(xml_text):
    """Return the config XML with volatile attributes removed."""
    root = ET.fromstring(xml_text)
    for element in root.iter():
        element.attrib.pop("persisted_at", None)
    return ET.tostring(root, encoding="unicode")


def changed_sections(old_text, new_text):
    """Return the names of top-level sections that differ."""
    old = ET.fromstring(normalise(old_text))
    new = ET.fromstring(normalise(new_text))

    old_s = {c.tag: ET.tostring(c, encoding="unicode") for c in old}
    new_s = {c.tag: ET.tostring(c, encoding="unicode") for c in new}

    names = set(old_s) | set(new_s)
    return sorted(n for n in names if old_s.get(n) != new_s.get(n))


def fetch_config():
    """Download the running config from the OPNsense API."""
    key = os.environ["OPN_KEY"]
    secret = os.environ["OPN_SECRET"]
    host = os.environ["OPN_HOST"]

    url = f"https://{host}/api/core/backup/download/this"
    resp = requests.get(url, auth=(key, secret), verify=False, timeout=15)
    resp.raise_for_status()
    return resp.text


def main():
    config = fetch_config()
    clean = normalise(config)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    latest = BACKUP_DIR / "latest.xml"

    changed = []
    if latest.exists():
        old_text = latest.read_text()
        if normalise(old_text) == clean:
            return 0
        changed = changed_sections(old_text, config)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = BACKUP_DIR / f"config-{stamp}.xml"

    for path in (archive, latest):
        path.write_text(config)
        path.chmod(0o600)

    if changed:
        print(f"CHANGED: {', '.join(changed)} — saved {archive.name}")
    else:
        print(f"First run: saved {archive.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
