import json

# Constants
FLIGHT_SPEED_KMH = 800  # average flight speed
CO2_PER_KM_PER_PERSON = 0.1  # fallback kg CO2 per km per person if missing

# Load office distances JSON
with open("durhackX/data/clean/office_dist.json", "r") as f:
    offices_data = json.load(f)

# Load attendees and event info JSON
with open("durhackX/sample_inputs/input_3.json", "r") as f:
    meeting_input = json.load(f)

attendees = meeting_input["attendees"]

# Function to compute total travel time, CO2, and price for a meeting location
def compute_metrics(meeting_location):
    total_time = 0
    total_co2 = 0
    total_price = 0

    # Find the office object for the meeting location
    location_office = next((o for o in offices_data["offices"] if o.get("office_name") == meeting_location), None)
    if not location_office:
        return None

    for office_name, num_people in attendees.items():
        # Skip if the office is the same as the meeting location (no travel)
        if office_name == meeting_location:
            continue

        # Find distance info from this office to the meeting location
        office = next((o for o in offices_data["offices"] if o.get("office_name") == office_name), None)
        if not office:
            continue

        # Find the distance entry
        distance_entry = next(
            (d for d in office.get("distances_to_other_offices", []) if d.get("office_name") == meeting_location),
            None
        )
        if not distance_entry:
            continue

        # Travel metrics (use fallbacks when fields are missing)
        distance_km = distance_entry.get("distance_km", 0)
        flight_time_hours = distance_entry.get("estimated_travel_time_hours", distance_km / FLIGHT_SPEED_KMH if distance_km else 0)
        co2_per_person = distance_entry.get("co2_kg", distance_km * CO2_PER_KM_PER_PERSON if distance_km else 0)
        price_per_person = distance_entry.get("estimated_price_gbp", 0)

        # Multiply by number of attendees
        total_time += flight_time_hours * num_people
        total_co2 += co2_per_person * num_people
        total_price += price_per_person * num_people

    return {
        "total_travel_time_hours": total_time,
        "total_co2_kg": total_co2,
        "total_price_gbp": total_price
    }

# Compute metrics for all meeting locations
meeting_locations = [o.get("office_name") for o in offices_data.get("offices", []) if o.get("office_name")]
results = {}

for location in meeting_locations:
    metrics = compute_metrics(location)
    if metrics is not None:
        results[location] = metrics

if not results:
    print("No meeting location metrics computed.")
else:
    # Find the best location by travel time, CO2, and price
    best_time_location = min(results, key=lambda x: results[x]["total_travel_time_hours"])
    best_co2_location = min(results, key=lambda x: results[x]["total_co2_kg"])
    best_price_location = min(results, key=lambda x: results[x]["total_price_gbp"])

    print("All metrics per location:")
    for loc, data in results.items():
        print(f"{loc}: {data}")

    print(f"\nBest location by travel time: {best_time_location} ({results[best_time_location]})")
    print(f"Best location by CO2: {best_co2_location} ({results[best_co2_location]})")
    print(f"Best location by price: {best_price_location} ({results[best_price_location]})")
