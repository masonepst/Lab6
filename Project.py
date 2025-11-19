import json
import requests

url = "http://192.168.1.254:8000/positions.json "

response = requests.get(url)

print("STATUS:", response.status_code)
print("RAW RESPONSE:", response.text)

data = response.json()

if "turrets" in data:
	turrets = data["turrets"]
else:
	turrets = []

if "globes" in data:
	globes = data["globes"]
else:
	globes = []

for stud_id, coords in turrets.items(): #items needed if turrets is a dict {}
    r = coords["r"]
    theta = coords["theta"]
    print(f"{stud_id}: r = {r} cm, theta = {theta} rad")

for coords in globes:
	r = coords["r"]
	theta = coords["theta"]
	z = coords["z"]
	print(f"Globe: r = {r} cm, theta = {theta} rad, z = {z} cm")

