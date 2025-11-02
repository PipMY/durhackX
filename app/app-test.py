import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.flight_search import find_best_flight

result = find_best_flight("LHR", "CDG", "2024-06-15T12:00:00Z", leeway_hours=3)
if result:
    print("Departure:", result['departure_time'])
    print("Arrival:", result['arrival_time'])
    print("Duration:", result['duration'], "mins")
    print("Price: £", result['price'])
else:
    print("No flight found.")
