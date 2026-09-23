#!/usr/bin/env python3
import subprocess
import json
import argparse

result = subprocess.run(
        ["gcloud", "compute", "instances", "list", "--format=json"],
    capture_output=True, text=True
    )

parser = argparse.ArgumentParser(description="List GCE instances")
parser.add_argument("-r", "--running", action="store_true",help="show only running instances")
args = parser.parse_args()

instances = json.loads(result.stdout)

print(f"{'NAME':<20} {'STATUS':<12} {'ZONE':<14} {'MACHINE'}")

if args.running:
    instances = [i for i in instances if i["status"] == "RUNNING"]

for inst in instances:
    zone = inst["zone"].split("/")[-1]
    machine = inst["machineType"].split("/")[-1]
    print(f"{inst['name']:<20} {inst['status']:<12} {zone:<14} {machine}")
