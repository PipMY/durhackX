# src/optimiser.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path
import json

# ------------------------------------------------------------------- #
# 1. Load city → IATA mapping from airports.csv (your data/clean/airports.csv)
# ------------------------------------------------------------------- #
AIRPORTS_CSV = Path(__file__).parent.parent / "data" / "clean" / "airports.csv"

_city_to_iata = {}

if AIRPORTS_CSV.exists():
    try:
        df = pd.read_csv(AIRPORTS_CSV)
        # Adjust column names if different in your CSV
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

# Fallback map (covers your example cities)
if not _city_to_iata:
    _city_to_iata = {
        "London": "LHR",
        "Paris": "CDG",
        "Zurich": "ZRH",
        "Geneva": "GVA",
        "Amsterdam": "AMS",
        "Dubai": "DXB",
        "New York": "JFK",
        "Singapore": "SIN"
    }

def city_to_iata(city_name: str) -> str:
    """Convert city name to IATA code."""
    return _city_to_iata.get(city_name.strip().title(), "XXX")


# ------------------------------------------------------------------- #
# 2. Mock travel leg generator (replace with real API later)
# ------------------------------------------------------------------- #
def find_best_travel_leg_MOCK(origin_iata: str, dest_iata: str, traveller_info=None):
    if origin_iata == dest_iata:
        return {"status": "success", "travel_hours": 0, "co2": 0, "cost": 0}
    return {
        "status": "success",
        "travel_hours": float(np.random.uniform(5, 30)),
        "co2": float(np.random.uniform(100, 800)),
        "cost": float(np.random.uniform(150, 1200))
    }


# ------------------------------------------------------------------- #
# 3. Helper functions
# ------------------------------------------------------------------- #
def calculate_fairness(hours_list):
    return float(np.std(hours_list)) if hours_list else 0.0


def normalize_weights(w):
    total = sum(w.values())
    if total == 0:
        n = len(w)
        return {k: 1/n for k in w}
    return {k: v/total for k, v in w.items()}


# ------------------------------------------------------------------- #
# 4. MAIN OPTIMIZER – Accepts your JSON format exactly
# ------------------------------------------------------------------- #
def run_optimization(scenario_json, weights):
    """
    Input:
        scenario_json = {
            "attendees": {"London": 4, "Paris": 10, ...},
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
            continue  # skip unknown
        try:
            count = int(count)
        except (ValueError, TypeError):
            continue
        attendees.extend([{"origin": iata}] * count)

    if not attendees:
        raise ValueError("No valid attendees after city → IATA mapping.")

    # --- 2. Parse candidates ---
    candidate_cities = scenario_json.get("candidates", list(attendees_raw.keys()))
    candidates = [city_to_iata(c) for c in candidate_cities]
    candidates = [c for c in candidates if c != "XXX"]
    if not candidates:
        raise ValueError("No valid candidate cities.")

    # --- 3. Weights ---
    w_co2 = weights.get("co2", 0.33)
    w_fairness = weights.get("mean_time", 0.33)
    w_cost = weights.get("cost", 0.34)

    # --- 4. Evaluate each candidate ---
    records = []
    for dest_iata in candidates:
        total_co2 = total_cost = 0.0
        travel_hours = []

        for person in attendees:
            leg = find_best_travel_leg_MOCK(person["origin"], dest_iata)
            if leg["status"] != "success":
                continue
            total_co2 += leg["co2"]
            total_cost += leg["cost"]
            travel_hours.append(leg["travel_hours"])

        fairness = calculate_fairness(travel_hours)
        records.append({
            "candidate_city": dest_iata,
            "total_co2": total_co2,
            "fairness_score": fairness,
            "total_cost": total_cost
        })

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError("No travel data generated.")

    # --- 5. Normalize & score ---
    scaler = MinMaxScaler()
    df[["norm_co2", "norm_fairness", "norm_cost"]] = scaler.fit_transform(
        df[["total_co2", "fairness_score", "total_cost"]]
    )

    norm_w = normalize_weights({"co2": w_co2, "fairness": w_fairness, "cost": w_cost})
    df["final_score"] = (
        norm_w["co2"] * df["norm_co2"] +
        norm_w["fairness"] * df["norm_fairness"] +
        norm_w["cost"] * df["norm_cost"]
    )

    best = df.sort_values("final_score").iloc[0]

    # --- 6. Return UI-friendly result ---
    return {
        "best_office": best["candidate_city"],
        "metrics": {
            "total_co2": round(best["total_co2"], 2),
            "stddev_travel_hours": round(best["fairness_score"], 2),
            "total_cost": round(best["total_cost"], 2)
        },
        "all_results": df.to_dict("records"),
        "final_score": round(best["final_score"], 3)
    }