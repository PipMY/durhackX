import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Example dataset
data = {
    "City": ["London", "Paris", "Hong Kong", "Singapore", "Mumbai", "Dubai",
             "Shanghai", "Zurich", "Geneva", "Aarhus", "Sydney", "Wroclaw", "Budapest"],
    "Cost (£)": [320, 280, 450, 400, 150, 300, 420, 350, 340, 310, 500, 230, 240],
    "Median Time (hrs)": [7.5, 6.0, 11.0, 10.5, 9.0, 8.5, 10.0, 6.5, 6.2, 5.8, 12.0, 7.0, 6.8],
    "Total CO2 (kg)": [180, 160, 300, 280, 120, 200, 290, 170, 165, 150, 320, 140, 145]
}

df = pd.DataFrame(data)

fig, ax1 = plt.subplots(figsize=(14, 7))
x = np.arange(len(df["City"]))
width = 0.25

# Bar 1: Cost (£)
bars1 = ax1.bar(x - width, df["Cost (£)"], width, label="Cost (£)", color="#03045e")
ax1.set_ylabel("Cost (£)", color="black", fontsize=12)
ax1.tick_params(axis='y', labelcolor="black")

# Create secondary y-axis for Median Time
ax2 = ax1.twinx()
bars2 = ax2.bar(x + width, df["Median Time (hrs)"], width, label="Median Time (hrs)", color="#8ecae6")
ax2.set_ylabel("Median Time (hrs)", color="black", fontsize=12)
ax2.tick_params(axis='y', labelcolor="black")

# Create *third* y-axis for CO₂
ax3 = ax1.twinx()
ax3.spines["right"].set_position(("outward", 60))  # Shift right
bars3 = ax3.bar(x, df["Total CO2 (kg)"], width, label="Total CO₂ (kg)", color="#0096c7")
ax3.set_ylabel("Total CO₂ (kg)", color="black", fontsize=12)
ax3.tick_params(axis='y', labelcolor="black")

# Common x-axis labels
ax1.set_xticks(x)
ax1.set_xticklabels(df["City"], rotation=45, ha="right")
ax1.set_xlabel("City", fontsize=12)

# Merge legends
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
lines3, labels3 = ax3.get_legend_handles_labels()
ax3.legend(lines + lines2 + lines3, labels + labels2 + labels3, loc="upper right")

# Title and layout
plt.title("Comparison of Cost, Travel Time, and CO₂ Emissions by City", fontsize=14, pad=20)
fig.tight_layout()

# Render in Streamlit
st.pyplot(fig)
