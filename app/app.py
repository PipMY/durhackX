import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="QRT Meeting Optimizer",
    layout="wide"
)

# ---------- CUSTOM STYLE ----------
st.markdown("""
    <style>
        /* Overall page background */
        .stApp {
            background-color: #0d072c !important;
            color: white !important;
            font-family: "Source Sans Pro", sans-serif !important;
        }

        /* Main container */
        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 1rem !important;
            max-width: 1200px;
        }

        /* Headings */
        h1, h2, h3 {
            color: #ffffff !important;
            font-weight: 600 !important;
            letter-spacing: 0.3px;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #121639 !important;
            color: white !important;
        }

        /* Slider accent */
        .stSlider > div > div > div {
            background: linear-gradient(90deg, #4b5fff, #00c6ff);
        }

        /* Divider colour */
        hr {
            border-color: #3a3f73 !important;
        }

        /* Dataframes */
        .dataframe {
            color: #ffffff !important;
        }

        /* Metrics section (col2) text alignment fix */
        [data-testid="stMetricValue"] {
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
col_logo, col_title = st.columns([0.15, 0.85])
with col_logo:
    st.image("qrt-logo.svg", width=100)
with col_title:
    st.title("Meeting in the middle.")
    st.subheader("Find the most sustainable and fair event location.")

st.divider()

# ---------- SIDEBAR ----------
st.sidebar.header("Settings")
st.sidebar.markdown("Upload your data and adjust preferences:")

w_co2 = st.sidebar.slider("Weight for CO₂ (vs Fairness)", 0.0, 1.0, 0.5, 0.1)
uploaded_file = st.sidebar.file_uploader("Upload attendee data (JSON)", type=["json"])
run_button = st.sidebar.button("Run Optimization")

st.sidebar.divider()
st.sidebar.caption("Created at DurHackX — Team 3319")

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
st.caption("QRT — Meeting in the middle.")
