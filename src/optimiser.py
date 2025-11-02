# src/optimiser.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.flight_search import find_best_flight
from src.co2_calculator import calculate_co2
from datetime import datetime

# ------------------------------------------------------------------- #
# 1. CITY → IATA MAPPING – ONLY THE 13 CITIES FROM input_3.json
# ------------------------------------------------------------------- #
from pathlib import Path
import pandas as pd

# --- Global map: city → IATA ---
_city_to_iata = {}

# --- Step 1: Load from airports.csv (if exists) ---
AIRPORTS_CSV = Path(__file__).parent.parent / "data" / "clean" / "airports.csv"

if AIRPORTS_CSV.exists():
    try:
        df = pd.read_csv(AIRPORTS_CSV)
        city_col = next((c for c in df.columns if "city" in c.lower()), None)
        iata_col = next((c for c in df.columns if "iata" in c.lower()), None)
        if city_col and iata_col:
            for _, row in df.iterrows():
                city = str(row[city_col]).strip().title()
                iata = str(row[iata_col]).strip().upper()
                if city and iata and len(iata) == 3:
                    _city_to_iata[city] = iata
    except Exception as e:
        print(f"Warning: Could not load airports.csv: {e}")

# --- Step 2: HARD-CODED MAP FOR THE 13 CITIES IN input_3.json ---
INPUT_3_CITIES = {
    "London": "LHR",
    "Paris": "CDG",
    "Hong Kong": "HKG",
    "Singapore": "SIN",
    "Mumbai": "BOM",
    "Dubai": "DXB",
    "Shanghai": "PVG",
    "Zurich": "ZRH",
    "Geneva": "GVA",
    "Aarhus": "AAR",
    "Sydney": "SYD",
    "Wroclaw": "WRO",
    "Budapest": "BUD"
}
_city_to_iata.update(INPUT_3_CITIES)  # Override or add

# --- Step 3: GLOBAL city_to_iata function (safe fallback) ---
def city_to_iata(city_name: str) -> str:
    """
    Returns IATA code for any city.
    - From airports.csv
    - From INPUT_3_CITIES
    - Dynamic 3-letter code if unknown (e.g. "Timbuktu" → "TIM")
    """
    city = city_name.strip().title()
    if city in _city_to_iata:
        return _city_to_iata[city]

    # Dynamic fallback: first 3 letters
    code = "".join(word[0].upper() for word in city.split() if word)[:3]
    if len(code) < 3:
        code = (code + "X" * 3)[:3]
    
    _city_to_iata[city] = code
    return code

# ------------------------------------------------------------------- #
# 2. Travel leg generator (using flight_search)
# ------------------------------------------------------------------- #
def find_best_travel_leg(origin_iata: str, dest_iata: str, arrival_datetime: str):
    """
    Finds the best travel leg using the flight search module.
    Returns a dictionary with status, travel_hours, co2, and cost.
    """
    if origin_iata == dest_iata:
        return {"status": "success", "travel_hours": 0, "co2": 0, "cost": 0}

    # Use leeway_hours=2 to allow for some flexibility in arrival time
    flight = find_best_flight(origin_iata, dest_iata, arrival_datetime, leeway_hours=2)

    if not flight:
        # Fallback for no flights found - maybe return a high-cost dummy
        # to penalise this option, or simply mark as failed.
        return {"status": "failed", "travel_hours": None, "co2": None, "cost": None}

    travel_minutes = flight.get("duration", 0)
    travel_hours = travel_minutes / 60.0 if travel_minutes else 0.0
    cost = flight.get("price", 0)
    
    # Use the new CO2 calculator
    co2 = calculate_co2(travel_hours)

    return {
        "status": "success",
        "travel_hours": travel_hours,
        "co2": co2,
        "cost": cost
    }


# ------------------------------------------------------------------- #
# 3. Helper functions
# ------------------------------------------------------------------- #
def calculate_fairness(hours_list):
    return float(np.std(hours_list)) if hours_list else 0.0


def normalise_weights(w):
    total = sum(w.values())
    if total == 0:
        n = len(w)
        return {k: 1/n for k in w}
    return {k: v/total for k, v in w.items()}


def evaluate_candidate(dest_iata, attendees, arrival_datetime):
    """Evaluates a single candidate city."""
    total_co2 = total_cost = 0.0
    travel_hours = []
    leg_cache = {}

    for person in attendees:
        cache_key = (person["origin"], dest_iata)
        if cache_key in leg_cache:
            leg = leg_cache[cache_key]
        else:
            leg = find_best_travel_leg(person["origin"], dest_iata, arrival_datetime)
            leg_cache[cache_key] = leg

        if leg["status"] != "success":
            continue
        total_co2 += leg["co2"]
        total_cost += leg["cost"]
        travel_hours.append(leg["travel_hours"])

    if not travel_hours:
        return None

    fairness = calculate_fairness(travel_hours)
    mean_time = float(np.mean(travel_hours)) if travel_hours else 0.0
    median_time = float(np.median(travel_hours)) if travel_hours else 0.0
    return {
        "candidate_city": dest_iata,
        "total_co2": total_co2,
        "fairness_score": fairness,
        "total_cost": total_cost,
        # Include both for compatibility; UI prefers mean_time
        "mean_time": mean_time,
        "median_time": median_time
    }


# ------------------------------------------------------------------- #
# 4. MAIN OPTIMIZER – Accepts your JSON format exactly
# ------------------------------------------------------------------- #
def run_optimization(scenario_json, weights):
    """
    Input:
        scenario_json = {
            "attendees": {"London": 4, "Paris": 10, ...},
            "availability_window": {
                "start": "2025-08-04T12:30:00Z",
                "end": "2025-08-08T12:00:00Z"
            },
            "candidates": ["London", "Paris", ...]  # optional
        }
        weights = {"co2": 0.33, "mean_time": 0.33, "cost": 0.34}
    Output: Same dict your Streamlit app expects
    """
    # --- 1. Parse attendees ---
    attendees_raw = scenario_json.get("attendees", {})
    if not isinstance(attendees_raw, dict):
        raise ValueError("'attendees' must be a dictionary of city → count")

    attendees = []
    for city, count in attendees_raw.items():
        iata = city_to_iata(city)
        if iata == "XXX":
            continue
        try:
            count = int(count)
        except (ValueError, TypeError):
            continue
        attendees.extend([{"origin": iata}] * count)

    if not attendees:
        raise ValueError("No valid attendees.")

    # --- 2. Parse candidates & availability ---
    candidate_cities = scenario_json.get("candidates", list(attendees_raw.keys()))
    candidates = [city_to_iata(c) for c in candidate_cities if city_to_iata(c) != "XXX"]
    if not candidates:
        raise ValueError("No valid candidate cities.")

    availability = scenario_json.get("availability_window", {})
    arrival_datetime = availability.get("start")
    if not arrival_datetime:
        raise ValueError("Missing 'availability_window.start' in input JSON.")

    # --- 3. Weights ---
    w_co2 = weights.get("co2", 0.33)
    w_fairness = weights.get("mean_time", 0.33)
    w_cost = weights.get("cost", 0.34)

    # --- 4. Evaluate each candidate in parallel ---
    records = []
    with ThreadPoolExecutor() as executor:
        future_to_candidate = {
            executor.submit(evaluate_candidate, dest, attendees, arrival_datetime): dest
            for dest in candidates
        }
        for future in as_completed(future_to_candidate):
            result = future.result()
            if result:
                records.append(result)

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError("No travel data could be generated for any candidate city.")

    # --- 5. Normalise & score ---
    scaler = MinMaxScaler()
    df[["normalised_co2", "normalised_fairness", "normalised_cost"]] = scaler.fit_transform(
        df[["total_co2", "fairness_score", "total_cost"]]
    )

    norm_w = normalise_weights({"co2": w_co2, "fairness": w_fairness, "cost": w_cost})
    df["final_score"] = (
        norm_w["co2"] * df["normalised_co2"] +
        norm_w["fairness"] * df["normalised_fairness"] +
        norm_w["cost"] * df["normalised_cost"]
    )

    best = df.sort_values("final_score").iloc[0]

    # --- 6. SAVE for graph (city name → metrics) ---
    output_for_graph = {}
    for _, row in df.iterrows():
        city_iata = row["candidate_city"]
        city_name = next((k for k, v in _city_to_iata.items() if v == city_iata), city_iata)
        output_for_graph[city_name] = {
            "cost": round(row["total_cost"], 2),
            "median_travel_hours": round(row["median_travel_hours"], 2),
            "total_co2": round(row["total_co2"], 2)
        }

    output_dir = Path(__file__).parent.parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "computed_results_with_centroid.json"
    with open(output_path, "w") as f:
        json.dump(output_for_graph, f, indent=2)

    # --- 7. Return UI result ---
    return {
        "best_office": best["candidate_city"],
        "metrics": {
            "total_co2": round(best["total_co2"], 2),
            "stddev_travel_hours": round(best["fairness_score"], 2),
            "total_cost": round(best["total_cost"], 2),
            # Prefer mean for UI, keep median for backwards compatibility
            "mean_travel_hours": round(best.get("mean_time", 0.0), 2),
            "median_travel_hours": round(best.get("median_time", 0.0), 2)
        },
        "all_results": df.to_dict("records"),
        "final_score": round(best["final_score"], 3)
    }