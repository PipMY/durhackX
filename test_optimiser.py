# test_optimiser.py
import json
from src.optimiser import run_optimization

# The input JSON provided by the user
scenario_json = {
    "attendees": {
        "London": 4,
        "Paris": 10,
        "Zurich": 7,
        "Geneva": 1
    },
    "availability_window": {
        "start": "2024-01-04T12:30:00Z",
        "end": "2024-01-08T12:00:00Z"
    },
    "event_duration": {
        "days": 1,
        "hours": 2
    }
}

# Define the weights for the optimization
weights = {
    "co2": 0.33, 
    "mean_time": 0.33, 
    "cost": 0.34
}

if __name__ == "__main__":
    try:
        result = run_optimization(scenario_json, weights)
        print(json.dumps(result, indent=4))
    except Exception as e:
        print(f"An error occurred: {e}")
