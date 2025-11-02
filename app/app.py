# app.py
import streamlit as st
import json
import sys
from pathlib import Path

# ---------- PATH SETUP ----------
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

from src.optimiser import run_optimization

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="QRT Meeting Optimizer", layout="wide")

# ---------- CUSTOM STYLE ----------
st.markdown(
    """
<style>
    .stApp {background-color:#0d072c !important;color:white;font-family:"Source Sans Pro",sans-serif;}
    .block-container {padding-top:3rem;padding-bottom:1rem;max-width:1200px;}
    h1,h2,h3 {color:#fff;font-weight:600;letter-spacing:0.3px;}
    [data-testid="stSidebar"] {background-color:#121639;color:white;}
    .stSlider > div > div > div {background:linear-gradient(90deg,#4b5fff,#00c6ff);}
    hr {border-color:#3a3f73 !important;}
    [data-testid="stMetricValue"] {color:#fff !important;}
</style>
""",
    unsafe_allow_html=True,
)

# ---------- SIDEBAR ----------
st.sidebar.header("Settings")
st.sidebar.markdown("Upload your data and adjust preferences:")

w_co2 = st.sidebar.slider("Weight for CO₂", 0.0, 1.0, 0.33, 0.01)
w_cost = st.sidebar.slider("Weight for Cost", 0.0, 1.0, 0.33, 0.01)
w_fairness = st.sidebar.slider("Weight for Fairness", 0.0, 1.0, 0.34, 0.01)

# Normalise weights
total = w_co2 + w_cost + w_fairness
if total > 0:
    w_co2 /= total
    w_cost /= total
    w_fairness /= total

st.sidebar.write("**Normalized Weights:**")
st.sidebar.write(f"CO₂: {w_co2:.2f} | Cost: {w_cost:.2f} | Fairness: {w_fairness:.2f}")

# FILE UPLOADER
uploaded_file = st.sidebar.file_uploader(
    "Upload attendee data (JSON)",
    type=["json"],
    help="Must contain `attendees` list with `origin` fields"
)

# ---------- RUN OPTIMIZATION ----------
if st.sidebar.button("Run Optimization", type="primary"):
    if not uploaded_file:
        st.sidebar.error("Please upload a JSON file.")
    else:
        with st.spinner("Optimizing..."):
            try:
                raw_text = uploaded_file.read().decode("utf-8").strip()
                scenario = json.loads(raw_text)

                # Optional debug
                st.sidebar.code(raw_text, language="json")

                weights = {
                    "co2": w_co2,
                    "mean_time": w_fairness,
                    "cost": w_cost
                }

                # CORRECT CALL – only 2 args
                results = run_optimization(scenario, weights)

                st.session_state.results = results
                st.success("Optimization complete!")
                st.rerun()

            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")
            except Exception as e:
                st.error(f"Error: {e}")

# ---------- MAIN LAYOUT ----------
col_logo, col_title = st.columns([0.15, 0.85])
with col_logo:
    if Path("qrt-logo.svg").exists():
        st.image("qrt-logo.svg", width=100)
with col_title:
    st.title("EcoMeet Optimizer")
    st.subheader("Find the most sustainable and fair event location.")

st.divider()

col1, col2 = st.columns([3, 1])

# LEFT: Map & Graph
with col1:
    st.header("Map Visualization")
    try:
        import importlib
        map_mod = importlib.import_module("map_test")
        map_mod.render_map()
    except Exception as e:
        st.warning(f"Map module error: {e}")

    st.divider()
    st.header("Candidate Comparison")
    try:
        graph_mod = importlib.import_module("graph_test")
        graph_mod.render_graph()
    except Exception as e:
        st.warning(f"Graph module error: {e}")

# RIGHT: Summary
with col2:
    st.header("Summary")

    if "results" in st.session_state:
        r = st.session_state.results
        m = r["metrics"]
        st.metric("Best City", r["best_office"])
        st.metric("Total CO₂", f'{m["total_co2"]} kg')
        st.metric("Fairness (std-dev hrs)", f'{m["stddev_travel_hours"]} hrs')
        st.metric("Total Cost", f'${m["total_cost"]}')
    else:
        st.metric("Best City", "—")
        st.metric("Total CO₂", "—")
        st.metric("Fairness (std-dev hrs)", "—")
        st.metric("Total Cost", "—")

    st.divider()
    st.header("Rationale")
    if "results" in st.session_state:
        st.write(
            "The selected city minimizes the **weighted score** of CO₂, "
            "travel fairness, and cost. Adjust sliders and re-run to explore."
        )
    else:
        st.write("Upload a JSON file and click **Run Optimization**.")

st.divider()
st.caption("QRT — Meeting in the middle.")