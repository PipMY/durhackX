import streamlit as st
import pandas as pd
import pydeck as pdk

# Define your DataFrame
cities = pd.DataFrame({
    'city': ['London', 'Paris', 'Hong Kong', 'Singapore', 'Mumbai', 'Dubai',
             'Shanghai', 'Zurich', 'Geneva', 'Aarhus', 'Sydney', 'Wroclaw', 'Budapest'],
    'lat': [51.5074, 48.8566, 22.3193, 1.3521, 19.0760, 25.2048,
            31.2304, 47.3769, 46.2044, 56.1629, -33.8688, 51.1079, 47.4979],
    'lon': [-0.1278, 2.3522, 114.1694, 103.8198, 72.8777, 55.2708,
            121.4737, 8.5417, 6.1432, 10.2039, 151.2093, 17.0385, 19.0402]
})

# ADD HOST CITY VARIABLE
host_city = 'Singapore'

# Get host city row
host = cities[cities['city'] == host_city].iloc[0]

# Build arcs from each city to host
arcs = []
for _, row in cities.iterrows():
    if row['city'] != host_city:
        arcs.append({
            "from_city": row['city'],
            "from_lon": row['lon'],
            "from_lat": row['lat'],
            "to_city": host_city,
            "to_lon": host['lon'],
            "to_lat": host['lat']
        })
arcs_df = pd.DataFrame(arcs)

# Scatterplot layer for cities
city_layer = pdk.Layer(
    "ScatterplotLayer",
    data=cities,
    get_position='[lon, lat]',
    get_radius=60000,
    get_color=[0, 128, 255, 180],
    pickable=True
)

# Arc layer for connections
arc_layer = pdk.Layer(
    "ArcLayer",
    data=arcs_df,
    get_source_position='[from_lon, from_lat]',
    get_target_position='[to_lon, to_lat]',
    get_source_color=[255, 0, 0],
    get_target_color=[0, 255, 0],
    auto_highlight=True,
    width_scale=0.0005,
    width_min_pixels=2
)

# Text layer for city names (white labels)
text_layer = pdk.Layer(
    "TextLayer",
    data=cities,
    get_position='[lon, lat]',
    get_text="city",
    get_color=[255, 255, 255, 255],
    get_size=16,
    get_alignment_baseline="'bottom'"
)

# Highlight the host city with a larger dot
host_layer = pdk.Layer(
    "ScatterplotLayer",
    data=pd.DataFrame([host]),
    get_position='[lon, lat]',
    get_radius=100000,
    get_color=[255, 215, 0, 255],  # gold color
    pickable=True
)

# View state centered near host city
view_state = pdk.ViewState(
    latitude=host['lat'],
    longitude=host['lon'],
    zoom=2,
    pitch=0
)

# Combine layers
deck = pdk.Deck(
    layers=[city_layer, arc_layer, text_layer, host_layer],
    initial_view_state=view_state,
    tooltip={"text": "{from_city} → {to_city}"}
)

st.title(f"Meetup Map with Arcs to {host_city} 🌍")
st.pydeck_chart(deck)

