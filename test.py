import requests
import json
from datetime import datetime

API_KEY = "07cf11657cmsh21c663563e149dap170cb6jsnadfef35c2ab0"
BASE_URL = "https://kiwi-com-cheap-flights.p.rapidapi.com/one-way"

# 🗺️ Only 13 known airports/cities
LOCATION_MAP = {
    "london": "City:london_gb",
    "paris": "City:paris_fr",
    "hong kong": "City:hong-kong_hk",
    "singapore": "City:singapore_sg",
    "mumbai": "City:mumbai_in",
    "dubai": "City:dubai_ae",
    "shanghai": "City:shanghai_cn",
    "zurich": "City:zurich_ch",
    "geneva": "City:geneva_ch",
    "aarhus": "City:aarhus_dk",
    "sydney": "City:sydney_au",
    "wroclaw": "City:wroclaw_pl",
    "budapest": "City:budapest_hu",
}

def get_location_code_local(name):
    key = name.strip().lower()
    if key in LOCATION_MAP:
        result = LOCATION_MAP[key]
        print(f"📍 Found local match for '{name}' → {result}")
        return result
    print(f"⚠️ Unknown city '{name}', please use one of: {', '.join(LOCATION_MAP.keys())}")
    return None


def get_flights(source, destination, latest_arrival):
    params = {
        "source": source,
        "destination": destination,
        "currency": "gbp",
        "locale": "en",
        "adults": "1",
        "children": "0",
        "infants": "0",
        "handbags": "1",
        "holdbags": "0",
        "cabinClass": "ECONOMY",
        "sortBy": "PRICE",
        "limit": "20",
        "transportTypes": "FLIGHT",
        "contentProviders": "KIWI",
    }

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "kiwi-com-cheap-flights.p.rapidapi.com"
    }

    print(f"\n🔍 Searching flights from {source} → {destination} ...")
    response = requests.get(BASE_URL, headers=headers, params=params)

    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("❌ API returned invalid JSON.")
        print(response.text[:500])
        return None

    if "itineraries" not in data:
        print("⚠️ No flights found.")
        return None

    flights = data["itineraries"]
    latest_dt = datetime.fromisoformat(latest_arrival)

    valid_flights = [
        f for f in flights
        if datetime.fromisoformat(f["sector"]["sectorSegments"][0]["segment"]["destination"]["localTime"]) <= latest_dt
    ]

    if not valid_flights:
        print("⚠️ No flights arrive before your target time.")
        return None

    cheapest = min(valid_flights, key=lambda f: float(f["price"]["amount"]))
    seg = cheapest["sector"]["sectorSegments"][0]["segment"]

    src = seg["source"]["station"]["code"]
    dst = seg["destination"]["station"]["code"]
    dep = seg["source"]["localTime"]
    arr = seg["destination"]["localTime"]
    airline = seg["carrier"]["name"]
    price = cheapest["price"]["amount"]
    booking_url = "https://www.kiwi.com" + cheapest["bookingOptions"]["edges"][0]["node"]["bookingUrl"]

    print("\n✅ Cheapest valid flight found:\n")
    print(f"🛫 {airline} | {src} → {dst}")
    print(f"   Depart: {dep}")
    print(f"   Arrive: {arr}")
    print(f"   💰 Price: £{price}")
    print(f"   🔗 {booking_url}\n")

    return cheapest


# --- Run interactively ---
if __name__ == "__main__":
    print("✈️ Kiwi.com Cheapest Flight Finder (13-City Edition)")

    start_name = input("Enter start city (one of London, Paris, Hong Kong, etc.): ").strip()
    dest_name = input("Enter destination city: ").strip()
    latest_arrival = input("Enter latest acceptable arrival time (YYYY-MM-DDTHH:MM:SS): ").strip()

    start_code = get_location_code_local(start_name)
    dest_code = get_location_code_local(dest_name)

    if start_code and dest_code:
        get_flights(start_code, dest_code, latest_arrival)
