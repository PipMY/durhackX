# app/normal_dist.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import matplotlib.ticker as mticker

def render_normal_dist_graph(results: dict | None = None):
    """Renders a normal distribution graph for the travel times of the best city."""
    if not results:
        # Don't show anything if there are no results yet
        return

    best_office_iata = results.get("best_office")
    all_results_data = results.get("all_results")

    if not best_office_iata or not all_results_data:
        st.warning("Could not generate distribution graph: missing data.")
        return

    best_result = next((r for r in all_results_data if r.get("candidate_city") == best_office_iata), None)

    if not best_result or "travel_hours" not in best_result:
        st.warning("Travel time data for the best office is not available.")
        return

    travel_hours = best_result["travel_hours"]
    if not travel_hours:
        st.warning("No travel hours recorded for the best city.")
        return

    mean_travel_time = np.mean(travel_hours)
    std_dev_travel_time = np.std(travel_hours)

    # Avoid plotting if std dev is zero (or very close to it)
    if std_dev_travel_time < 0.01:
        st.info("All travel times are nearly identical; distribution plot is not meaningful.")
        return

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5))

    # Generate data for the normal distribution curve
    x_min = max(0, mean_travel_time - 4 * std_dev_travel_time)
    x_max = mean_travel_time + 4 * std_dev_travel_time
    x = np.linspace(x_min, x_max, 1000)
    y = norm.pdf(x, mean_travel_time, std_dev_travel_time)

    ax.plot(x, y, color="#00c6ff", lw=2, label="Normal Distribution")
    ax.fill_between(x, y, color="#00c6ff", alpha=0.2)

    # Add a histogram of the actual data
    ax.hist(travel_hours, bins='auto', density=True, alpha=0.6, color="#8ecae6", label="Actual Travel Times")

    # Mark mean
    ax.axvline(mean_travel_time, color='#fca311', linestyle='--', lw=2, label=f"Mean: {mean_travel_time:.2f} hrs")

    # Formatting
    ax.set_title(f"Travel Time Distribution for {best_office_iata}", color="white", fontsize=16)
    ax.set_xlabel("Travel Time (hours)", color="white", fontsize=12)
    ax.set_ylabel("Probability Density", color="white", fontsize=12)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='#3a3f73')
    
    # Set x-axis limits to be reasonable
    ax.set_xlim(left=0)

    # Legend
    ax.legend(loc='upper right', frameon=False, labelcolor='white')

    fig.tight_layout()
    st.pyplot(fig)
