import json
import statistics

# Constants
FLIGHT_SPEED_KMH = 800  # average flight speed
CO2_PER_KM_PER_PERSON = 0.1  # fallback kg CO2 per km per person if missing

# Load office distances JSON
with open("durhackX/data/clean/office_dist.json", "r") as f:
    offices_data = json.load(f)

# Load attendees and event info JSON
with open("durhackX/sample_inputs/input_3.json", "r") as f:
    meeting_input = json.load(f)

attendees = meeting_input.get("attendees", {})

# Function to compute metrics per meeting location
def compute_metrics(meeting_location):
    attendee_travel_hours = {}
    total_co2 = 0

    # Find the office object for the meeting location
    location_office = next((o for o in offices_data.get("offices", []) if o.get("office_name") == meeting_location), None)
    if not location_office:
        return None

    for office_name, num_people in attendees.items():
        # Skip if the office is the same as the meeting location (no travel)
        if office_name == meeting_location:
            attendee_travel_hours[office_name] = 0.0
            continue

        # Find distance info from this office to the meeting location
        office = next((o for o in offices_data.get("offices", []) if o.get("office_name") == office_name), None)
        if not office:
            # mark as missing so user can see it's not available
            continue

        # Find the distance entry
        distance_entry = next(
            (d for d in office.get("distances_to_other_offices", []) if d.get("office_name") == meeting_location),
            None
        )
        if not distance_entry:
            continue

        flight_time_hours = distance_entry.get(
            "estimated_travel_time_hours",
            distance_entry.get("distance_km", 0) / FLIGHT_SPEED_KMH if distance_entry.get("distance_km", 0) else 0.0
        )
        co2_per_person = distance_entry.get(
            "co2_kg",
            distance_entry.get("distance_km", 0) * CO2_PER_KM_PER_PERSON if distance_entry.get("distance_km", 0) else 0.0
        )

        # Multiply CO2 by number of attendees from this office
        total_co2 += co2_per_person * num_people
        attendee_travel_hours[office_name] = flight_time_hours

    travel_times = list(attendee_travel_hours.values())
    metrics = {
        "total_co2": round(total_co2, 2),
        "average_travel_hours": round(statistics.mean(travel_times), 2) if travel_times else 0.0,
        "median_travel_hours": round(statistics.median(travel_times), 2) if travel_times else 0.0,
        "max_travel_hours": round(max(travel_times), 2) if travel_times else 0.0,
        "min_travel_hours": round(min(travel_times), 2) if travel_times else 0.0,
        "attendee_travel_hours": {k: round(v, 2) for k, v in attendee_travel_hours.items()}
    }

    return metrics

# Compute metrics for all meeting locations
meeting_locations = [o.get("office_name") for o in offices_data.get("offices", []) if o.get("office_name")]
results = {}

for location in meeting_locations:
    metrics = compute_metrics(location)
    if metrics:
        results[location] = metrics

# Print results
print(json.dumps(results, indent=4))


