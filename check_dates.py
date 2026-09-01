import requests

API_BASE_URL = "https://railway.stepprojects.ge"

response = requests.get(f"{API_BASE_URL}/api/departures", timeout=10)
response.raise_for_status()
departures = response.json()

print("\n===== AVAILABLE TRAIN DATES & ROUTES =====")
for departure in departures:
    date = departure.get("date")
    source = departure.get("source")
    destination = departure.get("destination")
    print(f"\n📅 Date: {date}")
    print(f"   Route: {source}  --->  {destination}")

    for train in departure.get("trains", []):
        print(
            f"   🚆 Train #{train.get('number')} ({train.get('name')}) | "
            f"{train.get('departure')} - {train.get('arrive')}"
        )
print("\n==========================================")