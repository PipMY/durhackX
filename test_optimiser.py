# test_optimiser.py
import json
from src.optimiser import run_optimization

# The input JSON provided by the user
with open('sample_inputs/input_2.json', 'r') as f:
    scenario_json = json.load(f)

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
