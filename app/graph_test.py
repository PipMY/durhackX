# --- graph_test.py ---
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os

def render_graph():
    json_path = os.path.join("outputs", "computed_results_with_centroid.json")
    with open(json_path, "r") as f:
        office_metrics = json.load(f)

    df = pd.DataFrame([
        {
            "City": city,
            "Cost (£)": values.get("cost", np.nan),
            "Median Time (hrs)": values.get("median_travel_hours", np.nan),
            "Total CO2 (kg)": values.get("total_co2", np.nan),
        }
        for city, values in office_metrics.items()
    ])

    fig, ax1 = plt.subplots(figsize=(12, 6))
    x = np.arange(len(df["City"]))
    width = 0.25

    ax1.bar(x - width, df["Cost (£)"], width, label="Cost (£)", color="#03045e")
    ax1.set_ylabel("Cost (£)", color="black")
    ax2 = ax1.twinx()
    ax2.bar(x + width, df["Median Time (hrs)"], width, label="Median Time (hrs)", color="#8ecae6")
    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("outward", 60))
    ax3.bar(x, df["Total CO2 (kg)"], width, label="Total CO₂ (kg)", color="#0096c7")

    ax1.set_xticks(x)
    ax1.set_xticklabels(df["City"], rotation=45, ha="right")
    ax1.set_xlabel("City")
    plt.title("Comparison of Cost, Travel Time, and CO₂ Emissions by City")
    plt.tight_layout()

    st.pyplot(fig)