import json
import requests

url = "http://masone.local:8000/turret_test.json"

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

for stud_id, coords in turrets.items():
    r = coords["r"]
    theta = coords["theta"]
    print(f"Turret {stud_id}: r = {r} cm, theta = {theta} rad")

