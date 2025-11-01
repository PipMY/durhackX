# 🧭 QRT x DurHack 2025 — Team Plan

> **Challenge:** “Meet in the Middle” — design a tool that finds the optimal meeting location for a global team, balancing **CO₂ emissions** and **fairness** in travel time.

---

## 🧩 Team Overview

| Role | Name | Focus |
|------|------|--------|
| 👩‍💻 **Data Wrangler & Parser** | *Person 1* | Clean, load, and prepare the travel data for analysis |
| 🧠 **Optimisation Engineers** | *Person 2 + 3* | Develop algorithm to choose the fairest and most sustainable meeting point |
| 🌍 **Visualisation & Frontend Engineer** | *Person 4* | Create an interactive dashboard to explore and visualise results |

---

## 👩‍💻 Person 1 — Cleaner

### 🎯 Goal
Prepare the local datasets for downstream analysis and ensure clean, structured access for the optimisation module.

### 🧱 Tasks
- Inspect all local files (`flights`, `emissions`, `offices`, etc.) and document columns.  
- Implement a unified loader:
  ```python
  def load_data(base_path="./data"):
      flights = pl.read_parquet(f"{base_path}/flights.parquet")
      co2 = pl.read_csv(f"{base_path}/emissions.csv")
      offices = pl.read_json(f"{base_path}/offices.json")
      return flights, co2, offices
  ```
- Map offices → nearest airport(s)
- Build (origin, destination) → CO₂ + duration table
- Save processed data to `data/processed/`
- Create a quick data summary notebook for exploration

### 📦 Deliverables
- `src/data_loader.py`
- `data/processed/flight_summary.csv`
- `README_data.md` (data structure and assumptions)

---

## 🧠 Person 2 + 3 — Optimisation Engineers

### 🎯 Goal
Design the algorithm that finds the optimal meeting point balancing emissions and fairness.

### 🧱 Tasks
- Load preprocessed data from `data_loader`
- Define objective function:
  ```python
  def compute_score(location, weights):
      co2 = total_emissions(location)
      fairness = variance_of_travel_times(location)
      return weights["co2"]*normalize(co2) + weights["fairness"]*normalize(fairness)
  ```
- Allow dynamic weight tuning via `weights.json`
- Produce structured JSON outputs:
  ```json
  {
    "event_location": "Singapore",
    "total_co2": 134.2,
    "average_travel_hours": 7.8,
    "median_travel_hours": 6.5,
    "attendee_travel_hours": {"Mumbai": 20.5, ...}
  }
  ```
- Cache results to speed up re-runs

### 📦 Deliverables
- `src/optimizer.py`
- Unit tests (`tests/test_optimizer.py`)
- Example run:  
  ```bash
  python optimizer.py sample_inputs/scenario1.json
  ```

---

## 🌍 Person 4 — Visualisation & Frontend Engineer

### 🎯 Goal
Develop an interactive visualisation to help users and judges intuitively explore results.

### 🧱 Tasks
- Build **Streamlit** or **React + Flask** app  
- Core features:
  - Upload and parse JSON input  
  - Adjust CO₂ vs fairness weight sliders  
  - Map view (Plotly/Mapbox/Deck.gl) showing routes and destinations  
  - Summary metrics & comparison table  
- Style the app with QRT branding and responsive layout
- Optional: animate travel routes or show CO₂ intensity by colour

### 📦 Deliverables
- `app/` folder (Streamlit or React)
- `requirements.txt`
- Screenshots for `README.md`

---

## 🗂 Folder Structure

```
qrt-meet-middle/
├── data/
│   ├── raw/
│   └── clean/
├── src/
│   ├── data_loader.py
│   ├── optimizer.py
│   └── utils/
│       └── metrics.py
├── app/
│   └── app.py
├── sample_inputs/
│   └── scenario1.json
├── outputs/
│   └── example_result.json
├── tests/
│   └── test_optimizer.py
├── README.md
└── run_demo.py
```

---

## ⚙️ Coordination Plan

| Phase | Description | Owner(s) | Target Time |
|--------|--------------|----------|--------------|
| **1. Data Ready** | Data cleaned & available in `/data/processed` | Person 1 | +3 hrs |
| **2. Algorithm Prototype** | Generate first results for a sample scenario | Person 2 | +6 hrs |
| **3. UI Mockup** | Map visual + slider interactions | Person 3 | +8 hrs |
| **4. Integration & Polish** | Final pipeline, README, and slides | Person 4 | End of hackathon |

---

## 🌟 Stretch Goals

- Incorporate **train and short-haul alternatives** where possible  
- Add **CO₂ savings vs baseline (HQ)** metric  
- Track **fairness over multiple meetings**  
- Suggest **ranked alternative meeting cities**  
- Estimate **hotel/flight costs** for extra realism  

---

**Let’s help QRT meet in the middle — sustainably and fairly 🌍**
