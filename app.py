import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="QRT Meeting Optimizer",
    layout="wide"
)

# ---------- CUSTOM STYLE ----------
st.markdown("""
    <style>
        /* Import clean, geometric font */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            background-color: #0d072c !important;
            color: white;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #ffffff;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Sidebar background */
        section[data-testid="stSidebar"] {
            background-color: #12133f !important;
        }

        /* Buttons */
        .stButton>button {
            background-color: #ffffff;
            color: #0d072c;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #00aaff;
            color: white;
            transform: scale(1.03);
        }

        /* Metrics */
        div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] {
            color: white !important;
        }

        /* Divider lines */
        hr {
            border-color: rgba(255,255,255,0.2);
        }

        /* Dataframe styling */
        .stDataFrame {
            background-color: white !important;
            color: #0d072c !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
    <div style='background-color:#0d072c; padding:1.5rem; border-radius:10px; text-align:center;'>
        <h1 style='color:#ffffff; font-weight:600; margin-bottom:0;'>QRT Meeting Optimizer</h1>
        <p style='color:#b0b0b0; font-size:1.1rem;'>Let's find your next meetup location...</p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# ---------- SIDEBAR ----------
st.sidebar.header("Settings")
st.sidebar.markdown("Upload your data and adjust preferences:")

w_co2 = st.sidebar.slider("Weight for CO₂ (vs Fairness)", 0.0, 1.0, 0.5, 0.1)
uploaded_file = st.sidebar.file_uploader("Upload attendee data (JSON)", type=["json"])
run_button = st.sidebar.button("Run Optimization")

st.sidebar.divider()
st.sidebar.caption("Created at DurHack — Team BridgeBuilders")

# ---------- MAIN LAYOUT ----------
col1, col2 = st.columns([3, 1])

with col1:
    st.header("Map Visualization")
    st.info("Map will display the best city and travel paths here.")
    st.empty()  # placeholder for folium map later

    st.divider()
    st.header("Candidate Comparison")
    st.info("Comparison table and Pareto plot will appear here.")
    st.empty()  # placeholder for table/chart later

with col2:
    st.header("Summary")
    st.metric("Best City", "—")
    st.metric("Total CO₂", "—")
    st.metric("Fairness Score", "—")

    st.divider()
    st.header("Rationale")
    st.write("Once results are ready, an explanation of the chosen city will appear here.")

st.divider()
st.caption("© 2025 Qube Research & Technologies — Meeting in the Middle.")

