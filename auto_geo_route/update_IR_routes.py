import requests
import json
import ipaddress
from pathlib import Path
import os
import subprocess
import sys

home = str(Path.home())
interface = sys.argv[1]
ir_resources = requests.get("https://stat.ripe.net/data/country-resource-list/data.json?resource=ir", verify=True)

old_ip_list = []
new_ip_list = []

if os.path.isfile(f"{home}/IR_IPs.txt") or os.path.isfile(f"{home}/IR_IPs.txt.old"):
    try:
        os.replace(f"{home}/IR_IPs.txt", f"{home}/IR_IPs.txt.old")
    except:
        print(f"W: IR_IPs.txt.old file exists but IR_IPs.txt doesn't")
    with open(f"{home}/IR_IPs.txt.old", "r") as f:
        old_ipv4 = f.readlines()
    for v4 in old_ipv4:
        v4 = v4.strip()
        try:
            ip = ipaddress.ip_network(v4)  # Validate the data
            old_ip_list.append(v4)
        except:
            print(f"E: del_old: {v4} is not a valid IP network")

ir_resources = json.loads(ir_resources.text)
ipv4 = ir_resources['data']['resources']['ipv4']
for v4 in ipv4:
    try:
        ip = ipaddress.ip_network(v4)  # Validate the data
        new_ip_list.append(v4)
    except:
        print(f"E: add_new: {v4} is not a valid IP network")

# This way, we avoid any traffic being routed into the wrong interface while we're changing the route table
new_added = 0
for v4 in new_ip_list:
    try:
        with open(f"{home}/IR_IPs.txt", "a") as f:
            f.write(f"{v4}\n")
        subprocess.run(["ip", "r", "add", v4, "dev", interface], shell=False, check=True)
        new_added += 1
    except:
        print(f"E: add_new: failed to add {v4}")

old_deleted = 0
for v4 in list(set(old_ip_list) - set(new_ip_list)):
    try:
        subprocess.run(["ip", "r", "del", v4], shell=False, check=True)
        old_deleted += 1
    except:
        print(f"E: del_old: failed to delete {v4}")

print(f"Added {new_added} new routes and deleted {old_deleted} old routes")
