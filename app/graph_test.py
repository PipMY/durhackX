# --- Convert dictionary to DataFrame ---
df = pd.DataFrame([
    {
        "City": city,
        "Cost (£)": values.get("cost", np.nan),
        "Median Time (hrs)": values.get("median_travel_hours", np.nan),
        "Total CO2 (kg)": values.get("total_co2", np.nan),
    }
    for city, values in city_data.items()
])

# --- Plot setup ---
fig, ax1 = plt.subplots(figsize=(12, 6))
x = np.arange(len(df["City"]))
width = 0.25

# Bar 1: Cost (£)
bars1 = ax1.bar(x - width, df["Cost (£)"], width, label="Cost (£)", color="#03045e")
ax1.set_ylabel("Cost (£)", color="black", fontsize=12)
ax1.tick_params(axis='y', labelcolor="black")

# Secondary y-axis: Median Time
ax2 = ax1.twinx()
bars2 = ax2.bar(x + width, df["Median Time (hrs)"], width, label="Median Time (hrs)", color="#8ecae6")
ax2.set_ylabel("Median Time (hrs)", color="black", fontsize=12)
ax2.tick_params(axis='y', labelcolor="black")

# Third y-axis: CO₂
ax3 = ax1.twinx()
ax3.spines["right"].set_position(("outward", 60))  # Shift outward
bars3 = ax3.bar(x, df["Total CO2 (kg)"], width, label="Total CO₂ (kg)", color="#0096c7")
ax3.set_ylabel("Total CO₂ (kg)", color="black", fontsize=12)
ax3.tick_params(axis='y', labelcolor="black")

# X-axis labels
ax1.set_xticks(x)
ax1.set_xticklabels(df["City"], rotation=45, ha="right")
ax1.set_xlabel("City", fontsize=12)

# Merge legends
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
lines3, labels3 = ax3.get_legend_handles_labels()
ax3.legend(lines + lines2 + lines3, labels + labels2 + labels3, loc="upper right")

# Title & layout
plt.title("Comparison of Cost, Travel Time, and CO₂ Emissions by City", fontsize=14, pad=20)
fig.tight_layout()

# Render in Streamlit
st.pyplot(fig)