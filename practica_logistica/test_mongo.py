import pymongo
import subprocess

# get host IP
result = subprocess.run(["ip", "route", "show"], capture_output=True, text=True)
ip = ""
for line in result.stdout.split('\n'):
    if "default" in line:
        ip = line.split()[2]
        break

print(f"Host IP is {ip}")

try:
    client = pymongo.MongoClient(f"mongodb://{ip}:27017/", serverSelectionTimeoutMS=2000)
    print("Connection info:", client.server_info())
except Exception as e:
    print("Failed to connect:", e)
