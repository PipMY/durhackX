# --- graph_test.py ---
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Helper to map IATA codes back to city names for display
_iata_to_city = {
    "LHR": "London", "CDG": "Paris", "HKG": "Hong Kong", "SIN": "Singapore",
    "BOM": "Mumbai", "DXB": "Dubai", "PVG": "Shanghai", "ZRH": "Zurich",
    "GVA": "Geneva", "AAR": "Aarhus", "SYD": "Sydney", "WRO": "Wroclaw",
    "BUD": "Budapest"
}

def render_graph(results: dict | None = None):
    """Renders a bar chart comparing all candidate cities from the optimizer results."""
    if not results:
        st.info("Run the optimizer to see the comparison graph.")
        return

    all_results_data = results.get("all_results")
    if not all_results_data:
        st.warning("No detailed results available to generate the graph.")
        return

    # Create DataFrame from the results
    df = pd.DataFrame(all_results_data)
    
    # Map IATA codes to city names for the chart labels
    df["City"] = df["candidate_city"].map(_iata_to_city).fillna(df["candidate_city"])

    # --- Matplotlib Chart ---
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(12, 7))

    x = np.arange(len(df["City"]))
    width = 0.25

    # Bar 1: Cost
    bar1 = ax1.bar(x - width, df["total_cost"], width, label="Total Cost (£)", color="#0077b6")
    ax1.set_ylabel("Total Cost (£)", color="white", fontsize=12)
    ax1.tick_params(axis='y', labelcolor="white")
    ax1.yaxis.set_major_formatter(mticker.StrMethodFormatter('£{x:,.0f}'))

    # Bar 2: Mean Travel Time
    ax2 = ax1.twinx()
    bar2 = ax2.bar(x, df["mean_time"], width, label="Mean Time (hrs)", color="#8ecae6")
    ax2.set_ylabel("Mean Travel Time (hrs)", color="white", fontsize=12)
    ax2.tick_params(axis='y', labelcolor="white")

    # Bar 3: Total CO2
    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("outward", 80))
    bar3 = ax3.bar(x + width, df["total_co2"], width, label="Total CO₂ (kg)", color="#fca311")
    ax3.set_ylabel("Total CO₂ (kg)", color="white", fontsize=12)
    ax3.tick_params(axis='y', labelcolor="white")

    # --- Formatting ---
    ax1.set_xticks(x)
    ax1.set_xticklabels(df["City"], rotation=45, ha="right", fontsize=11)
    ax1.set_xlabel("Candidate City", color="white", fontsize=12, labelpad=15)
    
    fig.suptitle("Candidate City Comparison", fontsize=16, color="white")
    
    # Create a single legend for all axes
    bars = [bar1, bar2, bar3]
    labels = [b.get_label() for b in bars]
    ax1.legend(bars, labels, loc='upper left', frameon=False, labelcolor='white')

    # Remove grid and ensure layout is tight
    ax1.grid(False)
    ax2.grid(False)
    ax3.grid(False)
    fig.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout to make space for title

    st.pyplot(fig)