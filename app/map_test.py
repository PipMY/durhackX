import streamlit as st
import pydeck as pdk
import pandas as pd
import json
from pathlib import Path


def render_map():
    """Loads computed centroid results and renders pydeck map visualization."""
    try:
        data_path = Path("outputs/computed_results_with_centroid.json")
        if not data_path.exists():
            st.warning("No computed results found. Run the optimizer first.")
            return

        with open(data_path, "r") as f:
            data = json.load(f)

        centroid_info = data.get("centroid_info", {})
        host_lat = centroid_info.get("latitude", 0)
        host_lon = centroid_info.get("longitude", 0)
        nearest_airport = centroid_info.get("nearest_airport", {}).get("airport", {})
        host_city_name = nearest_airport.get("name", "Unknown Location")
        host_country = nearest_airport.get("country", "")

        # --- Cities to connect ---
        cities = pd.DataFrame({
            'city': ['London', 'Paris', 'Hong Kong', 'Singapore', 'Mumbai', 'Dubai',
                     'Shanghai', 'Zurich', 'Geneva', 'Aarhus', 'Sydney', 'Wroclaw', 'Budapest'],
            'lat': [51.5074, 48.8566, 22.3193, 1.3521, 19.0760, 25.2048,
                    31.2304, 47.3769, 46.2044, 56.1629, -33.8688, 51.1079, 47.4979],
            'lon': [-0.1278, 2.3522, 114.1694, 103.8198, 72.8777, 55.2708,
                    121.4737, 8.5417, 6.1432, 10.2039, 151.2093, 17.0385, 19.0402]
        })

        host = pd.DataFrame([{
            "city": f"{host_city_name}, {host_country}",
            "lat": host_lat,
            "lon": host_lon
        }])

        arcs = []
        for _, row in cities.iterrows():
            arcs.append({
                "from_city": row['city'],
                "from_lon": row['lon'],
                "from_lat": row['lat'],
                "to_city": host_city_name,
                "to_lon": host_lon,
                "to_lat": host_lat
            })
        arcs_df = pd.DataFrame(arcs)

        # --- Pydeck Layers ---
        city_layer = pdk.Layer(
            "ScatterplotLayer",
            data=cities,
            get_position='[lon, lat]',
            get_radius=60000,
            get_color=[0, 128, 255, 180],
            pickable=True
        )

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

        text_layer = pdk.Layer(
            "TextLayer",
            data=cities,
            get_position='[lon, lat]',
            get_text="city",
            get_color=[255, 255, 255, 255],
            get_size=16,
            get_alignment_baseline="'bottom'"
        )

        host_layer = pdk.Layer(
            "ScatterplotLayer",
            data=host,
            get_position='[lon, lat]',
            get_radius=120000,
            get_color=[255, 215, 0, 255],
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=host_lat,
            longitude=host_lon,
            zoom=2,
            pitch=0
        )

        deck = pdk.Deck(
            layers=[city_layer, arc_layer, text_layer, host_layer],
            initial_view_state=view_state,
            tooltip={"text": "{from_city} → {to_city}"}
        )

        st.pydeck_chart(deck)
        st.success(f"Host Location: **{host_city_name} ({host_country})** — Nearest Airport: {nearest_airport.get('icao', 'N/A')}")

    except Exception as e:
        st.error(f"Error loading map: {e}")
