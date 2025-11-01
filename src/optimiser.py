import json

# Constants
FLIGHT_SPEED_KMH = 800  # average flight speed
CO2_PER_KM_PER_PERSON = 0.1  # kg CO2 per km per person

# Load office distances JSON
with open("durhackX/data/clean/office_dist.json", "r") as f:
    offices_data = json.load(f)

# Load attendees and event info JSON
with open("durhackX/sample_inputs/input_3.json", "r") as f:
    meeting_input = json.load(f)

attendees = meeting_input["attendees"]

# Function to compute total travel time and CO2 for a meeting location
def compute_metrics(meeting_location):
    total_time = 0
    total_co2 = 0

    # Find the office object for the meeting location
    location_office = next((o for o in offices_data["offices"] if o["office_name"] == meeting_location), None)
    if not location_office:
        return None

    for office_name, num_people in attendees.items():
        # Skip if the office is the same as the meeting location (no travel)
        if office_name == meeting_location:
            continue

        # Find distance info from this office to the meeting location
        office = next((o for o in offices_data["offices"] if o["office_name"] == office_name), None)
        if not office:
            continue

        # Find the distance entry
        distance_entry = next(
            (d for d in office["distances_to_other_offices"] if d["office_name"] == meeting_location),
            None
        )
        if not distance_entry:
            continue

        distance_km = distance_entry["distance_km"]
        flight_time_hours = distance_km / FLIGHT_SPEED_KMH
        co2_per_person = distance_km * CO2_PER_KM_PER_PERSON

        total_time += flight_time_hours * num_people
        total_co2 += co2_per_person * num_people

    return {"total_travel_time_hours": total_time, "total_co2_kg": total_co2}

# Compute metrics for all meeting locations
meeting_locations = [o["office_name"] for o in offices_data["offices"]]
results = {}

for location in meeting_locations:
    metrics = compute_metrics(location)
    if metrics:
        results[location] = metrics

# Find the best location (min travel time or CO2)
best_time_location = min(results, key=lambda x: results[x]["total_travel_time_hours"])
best_co2_location = min(results, key=lambda x: results[x]["total_co2_kg"])

print("All metrics per location:")
for loc, data in results.items():
    print(f"{loc}: {data}")

print(f"\nBest location by travel time: {best_time_location} ({results[best_time_location]})")
print(f"Best location by CO2: {best_co2_location} ({results[best_co2_location]})")
