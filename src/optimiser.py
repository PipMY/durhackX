import json
import statistics
import csv
from pathlib import Path

# -----------------------------------
# 🌍 Constants
# -----------------------------------
FLIGHT_SPEED_KMH = 800            # Average flight speed
CO2_PER_KM_PER_PERSON = 0.1       # Default fallback (kg CO₂ / km / person)

# -----------------------------------
# 📂 Load data safely using pathlib
# -----------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # DURHACKX root
OFFICE_FILE = BASE_DIR / "data" / "clean" / "office_dist.json"
INPUT_FILE = BASE_DIR / "sample_inputs" / "input_3.json"
AIRPORTS_CSV = BASE_DIR / "data" / "clean" / "airports.csv"

# Load office distance data
try:
    with open(OFFICE_FILE, "r") as f:
        offices_data = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"❌ Could not find office distance file at {OFFICE_FILE}")

# Load meeting input (attendees per office)
try:
    with open(INPUT_FILE, "r") as f:
        meeting_input = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"❌ Could not find meeting input file at {INPUT_FILE}")

attendees = meeting_input.get("attendees", {})

# -----------------------------------
# ⚙️ Compute travel & emissions metrics
# -----------------------------------
def compute_metrics(meeting_location):
    """Compute CO₂ and fairness metrics for a given meeting location."""
    attendee_travel_hours = {}
    total_co2 = 0.0

    # Find office entry for this meeting location
    location_office = next(
        (o for o in offices_data.get("offices", []) if o.get("office_name") == meeting_location),
        None
    )
    if not location_office:
        return None

    # Loop through all attendee offices
    for office_name, num_people in attendees.items():
        # If this office is the meeting location, no travel required
        if office_name == meeting_location:
            attendee_travel_hours[office_name] = 0.0
            continue

        # Find the office in the dataset
        office = next(
            (o for o in offices_data.get("offices", []) if o.get("office_name") == office_name),
            None
        )
        if not office:
            continue  # Skip unknown office

        # Find the distance entry from this office to the meeting location
        distance_entry = next(
            (d for d in office.get("distances_to_other_offices", [])
             if d.get("office_name") == meeting_location),
            None
        )
        if not distance_entry:
            continue  # No recorded distance

        # Travel time (hours)
        distance_km = distance_entry.get("distance_km", 0)
        flight_time_hours = distance_entry.get(
            "estimated_travel_time_hours",
            distance_km / FLIGHT_SPEED_KMH if distance_km else 0.0
        )

        # CO₂ emissions
        co2_per_person = distance_entry.get(
            "co2_kg",
            distance_km * CO2_PER_KM_PER_PERSON if distance_km else 0.0
        )

        total_co2 += co2_per_person * num_people
        attendee_travel_hours[office_name] = flight_time_hours

    # Compute summary metrics
    travel_times = list(attendee_travel_hours.values())
    if not travel_times:
        return None

    metrics = {
        "total_co2": round(total_co2, 2),
        "average_travel_hours": round(statistics.mean(travel_times), 2),
        "median_travel_hours": round(statistics.median(travel_times), 2),
        "stddev_travel_hours": round(statistics.pstdev(travel_times), 2),
        "max_travel_hours": round(max(travel_times), 2),
        "min_travel_hours": round(min(travel_times), 2),
        "attendee_travel_hours": {k: round(v, 2) for k, v in attendee_travel_hours.items()}
    }

    return metrics


# -----------------------------------
# 🧮 Evaluate all possible meeting locations
# -----------------------------------
meeting_locations = [
    o.get("office_name") for o in offices_data.get("offices", []) if o.get("office_name")
]

results = {}
for location in meeting_locations:
    metrics = compute_metrics(location)
    if metrics:
        results[location] = metrics

# -----------------------------------
# 🏆 Find best office and best global location
# -----------------------------------
# Best = lowest total CO₂ + fairness (stddev of travel time)
def compute_score(data):
    return data["total_co2"] + (data["stddev_travel_hours"] * 100)

best_office = min(results.items(), key=lambda x: compute_score(x[1]))[0]
best_metrics = results[best_office]

# -----------------------------------
# 🎯 Find Weighted Centroid
# -----------------------------------
total_weight = 0.0
sum_lat = sum_lon = 0.0

for office in offices_data.get("offices", []):
    name = office.get("office_name")
    weight = attendees.get(name, 0)
    if weight <= 0:
        continue
        
    coords = office.get("coordinates", {})
    lat = coords.get("latitude")
    lon = coords.get("longitude")
    if lat is None or lon is None:
        continue
        
    total_weight += weight
    sum_lat += weight * lat
    sum_lon += weight * lon

# -----------------------------------
# 🛩️ Find Nearest Non-Office Airport
# -----------------------------------
centroid_airport_candidate = None
if total_weight:
    centroid_lat = sum_lat / total_weight
    centroid_lon = sum_lon / total_weight
    
    # Load airports CSV
    airports = []
    try:
        with open(AIRPORTS_CSV, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                icao = row.get("icao") or row.get("IATA") or row.get("iata_code")
                lat = row.get("lat") or row.get("latitude")
                lon = row.get("lon") or row.get("longitude")
                if not all([icao, lat, lon]):
                    continue
                try:
                    airports.append({
                        "icao": icao.strip(),
                        "lat": float(lat),
                        "lon": float(lon),
                        "name": row.get("name", ""),
                        "country": row.get("country", "")
                    })
                except ValueError:
                    continue
    except FileNotFoundError:
        print(f"⚠️ Warning: Could not find airports CSV at {AIRPORTS_CSV}")
        airports = []

    # Find nearest non-office airport
    office_iatas = {o.get("airport_code") for o in offices_data.get("offices", []) if o.get("airport_code")}
    nearest = None
    nearest_dist = float("inf")
    
    for airport in airports:
        if airport.get("icao") in office_iatas:
            continue
        dist = haversine(centroid_lat, centroid_lon, airport["lat"], airport["lon"])
        if dist < nearest_dist:
            nearest = airport
            nearest_dist = dist
            
    if nearest:
        centroid_airport_candidate = {
            "airport": nearest,
            "distance_km": round(nearest_dist, 2)
        }

# -----------------------------------
# 📊 Compute Final Results
# -----------------------------------
output = {
    "best_office_location": best_office,
    "metrics": best_metrics,
    "all_results": results
}

print(json.dumps(output, indent=4))

# Optional: Save to outputs folder
OUTPUT_FILE = BASE_DIR / "outputs" / "computed_results.json"
with open(OUTPUT_FILE, "w") as f:
    json.dump(output, f, indent=4)
print(f"\n✅ Results saved to {OUTPUT_FILE}")


# at the bottom of optimiser.py
def run_optimization(attendees: dict, weights: dict):
    """
    Run optimization and return the best result.
    weights must contain {'co2': float, 'mean_time': float, 'cost': float}
    and sum to 1.0
    """
    if abs(sum(weights.values()) - 1.0) > 1e-6:
        raise ValueError("Weights must sum to 1.0")

    meeting_locations = [
        o.get("office_name") for o in offices_data.get("offices", []) if o.get("office_name")
    ]

    results = {}
    for location in meeting_locations:
        metrics = compute_metrics(location)
        if metrics:
            results[location] = metrics

    # Weighted score example
    def compute_score(data):
        return (
            weights["co2"] * data["total_co2"] +
            weights["mean_time"] * data["average_travel_hours"] +
            weights["cost"] * data["stddev_travel_hours"]
        )

    best_office, best_metrics = min(results.items(), key=lambda x: compute_score(x[1]))
    return {"best_office": best_office, "metrics": best_metrics, "all_results": results}

