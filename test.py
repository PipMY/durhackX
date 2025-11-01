import requests
import json

# 🔑 Your RapidAPI credentials
API_KEY = "07cf11657cmsh21c663563e149dap170cb6jsnadfef35c2ab0"
BASE_URL = "https://kiwi-com-cheap-flights.p.rapidapi.com/one-way"

# 🧭 Search parameters
params = {
    "source": "City:london_gb",
    "destination": "City:dubrovnik_hr",
    "outboundDepartureDateEnd": "2025-12-29",
    "currency": "gbp",
    "locale": "en",
    "adults": "1",
    "children": "0",
    "infants": "0",
    "handbags": "1",
    "holdbags": "0",
    "cabinClass": "ECONOMY",
    "sortBy": "QUALITY",
    "limit": "20",  # get up to 20 flights
    "transportTypes": "FLIGHT",
    "contentProviders": "KIWI",
}

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "kiwi-com-cheap-flights.p.rapidapi.com"
}

print("🔍 Fetching flight data...")
response = requests.get(BASE_URL, headers=headers, params=params)

if response.status_code != 200:
    print(f"❌ Error {response.status_code}: {response.text}")
    exit()

data = response.json()

# 🧩 Extract results
if "itineraries" not in data:
    print("⚠️ No itineraries found in response.")
    print(json.dumps(data, indent=2))
    exit()

flights = data["itineraries"]

# Filter flights by arrival time before the cutoff
cutoff_time = "2025-11-14T10:55:00"
filtered_flights = [
    f for f in flights
    if f["sector"]["sectorSegments"][0]["segment"]["destination"]["localTime"] < cutoff_time
]

# Sort flights by arrival time
filtered_flights.sort(key=lambda f: f["sector"]["sectorSegments"][0]["segment"]["destination"]["localTime"])

print(f"\nFound {len(filtered_flights)} flights arriving before {cutoff_time}:\n")

for fli in filtered_flights:
    seg = fli["sector"]["sectorSegments"][0]["segment"]
    src = seg["source"]["station"]["code"]
    dst = seg["destination"]["station"]["code"]
    dep = seg["source"]["localTime"]
    arr = seg["destination"]["localTime"]
    airline = seg["carrier"]["name"]
    price = fli["price"]["amount"]

    print(f"🛫 {airline} | {src} → {dst}")
    print(f"   Depart: {dep} | Arrive: {arr}")
    print(f"   💰 Price: £{price}\n")
