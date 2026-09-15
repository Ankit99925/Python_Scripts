import subprocess
import json

result = subprocess.run(
        ["gcloud", "compute", "instances", "list", "--format=json"],
    capture_output=True, text=True
    )

instances = json.loads(result.stdout)
for inst in instances:
    zone = inst["zone"].split("/")[-1]
    machine = inst["machineType"].split("/")[-1]
    print(f"{'NAME':<20} {'STATUS':<12} {'ZONE':<14} {'MACHINE'}")
    print(f"{inst['name']:<20} {inst['status']:<12} {zone:<14} {machine}")
