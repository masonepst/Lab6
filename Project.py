import json
import requests

# url = URL for JSON file of turret and globe coordinates

response = requests.get(url)

data = response.json()

if "turrets" in data:
	turrets = data["turrets"]
else:
	turrets = []

if "globes" in data:
	globes = data["globes"]
else:
	globes = []

for turret_id, coords in turrets.items():
    r = coords["r"]
    theta = coords["theta"]
    print(f"Turret {turret_id}: r = {r} cm, theta = {theta} rad")

