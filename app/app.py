import streamlit as st
import time

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="QRT Meeting Optimizer",
    layout="wide"
)

# ---------- INITIAL STATE ----------
# Initialize session state for loading
if "loading" not in st.session_state:
    st.session_state.loading = False

# ---------- CUSTOM STYLE (Consolidated CSS) ----------
st.markdown("""
    <style>
        /* Base App Styles */
        .stApp {
            background-color: #0d072c !important;
            color: white !important;
            font-family: "Source Sans Pro", sans-serif !important;
        }
        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 1rem !important;
            max-width: 1200px;
        }
        h1, h2, h3 {
            color: #ffffff !important;
            font-weight: 600 !important;
            letter-spacing: 0.3px;
        }
        [data-testid="stSidebar"] {
            background-color: #121639 !important;
            color: white !important;
        }
        .stSlider > div > div > div {
            background: linear-gradient(90deg, #4b5fff, #00c6ff);
        }
        hr {
            border-color: #3a3f73 !important;
        }
        [data-testid="stMetricValue"] {
            color: #ffffff !important;
        }

        /* --- Full-Screen Planet Animation Styles (200px size) --- */
        /* Custom overlay to cover the whole screen and center content */
        #overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-color: #0d072c;
            z-index: 9998;
            display: flex;
            flex-direction: column;
            align-items: center; 
            justify-content: center; 
        }

        /* Styles for the smaller planet (200px) */
        .planet-container {
            border-radius: 50%;
            box-shadow: 5px -3px 10px 3px #5e90f1;
            height: 200px; 
            overflow: hidden;
            position: relative;
            width: 200px; 
            z-index: 1;
        }
        .night, .day, .clouds, .inner-shadow {
            height: 200px; 
            width: 200px;  
        }
        
        .night {
            animation: rotate-night 80s linear infinite;
            background-image: url(https://www.solarsystemscope.com/textures/download/2k_earth_nightmap.jpg);
            background-size: 200%;
            position: absolute;
            z-index: 2;
        }
        .day {
            animation: rotate-day 80s linear infinite;
            background-image: url(https://www.solarsystemscope.com/textures/download/2k_earth_daymap.jpg);
            background-size: 200%;
            border-left: solid 1px black;
            border-radius: 50%;
            box-shadow: 5px 0 20px 10px #040615 inset; 
            margin-left: 44px; /* Scaled margin */
            position: absolute;
            z-index: 3;
        }
        .clouds {
            animation: rotate-day 50s linear infinite, spin-clouds 100s ease infinite;
            background-image: url(https://www.solarsystemscope.com/textures/download/2k_earth_clouds.jpg);
            background-size: 200%;
            border-radius: 50%;     
            box-shadow: 5px 0 20px 10px #040615 inset, -9px 0px 20px 10px #5e90f1 inset;
            margin-left: 40px; /* Scaled margin */
            opacity: 0.45;
            position: absolute;
            z-index: 4;
        }
        .inner-shadow {
            background: transparent;
            border-radius: 50%;
            box-shadow: -5px 0 10px 1px #152b57 inset, 5px 0 10px 1px #040615 inset;
            margin-left: 0;
            position: absolute;
            z-index: 5;
        }

        /* Keyframe Animations */
        @keyframes rotate-day {
            0% { background-position: 120% 0; }
            100% { background-position: -80% 0; }
        }
        @keyframes rotate-night {
            0% { background-position: calc(120% + 120px) 0; }
            100% { background-position: calc(-80% + 120px) 0; }
        }
        @keyframes spin-clouds {
            0% { transform: rotate(0deg); }
            50% { transform: rotate(20deg); }
            100% { transform: rotate(0deg); }
        }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# ---------- LOADING SCREEN LOGIC (The Planet) -----
# ------------------------------------------------
if st.session_state.loading:
    # Render the full-screen loading overlay
    st.markdown(
        """
        <div id='overlay'>
            <div class='planet-container'>
                <div class='night'></div>
                <div class='day'></div>
                <div class='clouds'></div>
                <div class='inner-shadow'></div>
            </div>
            <h2 style='color: white; text-align: center; margin-top: 2rem; font-size: 1.5rem;'>
                Optimising your meeting planet-wide...
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Simulate the calculation time
    time.sleep(3)
    
    # After simulation, turn off loading and rerun to show main content
    st.session_state.loading = False
    st.rerun()

# ------------------------------------------------
# ---------- SIDEBAR -----------------------------
# ------------------------------------------------
st.sidebar.header("Settings")
st.sidebar.markdown("Upload your data and adjust preferences:")

import streamlit as st

# Sliders (independent)
w_co2 = st.sidebar.slider("Weight for CO₂", 0.0, 1.0, 0.33, 0.01)
w_cost = st.sidebar.slider("Weight for Cost", 0.0, 1.0, 0.33, 0.01)
w_mean_distance = st.sidebar.slider("Weight for Mean Distance", 0.0, 1.0, 0.34, 0.01)

# Normalization function
def normalize_weights(*weights):
    total = sum(weights)
    if total == 0:
        return [1/len(weights)] * len(weights)
    return [w / total for w in weights]

# Apply normalization
w_co2, w_cost, w_mean_distance = normalize_weights(w_co2, w_cost, w_mean_distance)

# Display normalized weights
st.sidebar.write(f"Normalized Weights:")
st.sidebar.write(f"CO₂: {w_co2:.2f}, Cost: {w_cost:.2f}, Distance: {w_mean_distance:.2f}")

uploaded_file = st.sidebar.file_uploader("Upload attendee data (JSON)", type=["json"], key="data_uploader")

# RUN BUTTON: Always triggers the loading screen for testing
if st.sidebar.button("**Run Optimization**"):
    st.session_state.loading = True
    st.rerun() 

st.sidebar.divider()
st.sidebar.caption("Created at DurHack — Team BridgeBuilders")

# ------------------------------------------------
# ---------- HEADER AND MAIN APP CONTENT ---------
# ------------------------------------------------
col_logo, col_title = st.columns([0.15, 0.85])
with col_logo:
    # REVERTED: Using the intended logo file
    st.image("qrt-logo.svg", width=100) 
with col_title:
    st.title("EcoMeet Optimizer")
    st.subheader("Find the most sustainable and fair event location.")

st.divider()

col1, col2 = st.columns([3, 1])

with col1:
    st.header("Map Visualization")
    st.info("Map will display the best city and travel paths here.")
    st.empty() 

    st.divider()
    st.header("Candidate Comparison")
    st.info("Comparison table and Pareto plot will appear here.")
    st.empty() 

with col2:
    st.header("Summary")
    st.metric("Best City", "—")
    st.metric("Total CO₂", "—")
    st.metric("Fairness Score", "—")

    st.divider()
    st.header("Rationale")
    st.write("Once results are ready, an explanation of the chosen city will appear here.")

st.divider()
st.caption("QRT — Meeting in the middle.")