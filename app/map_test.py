import streamlit as st
import pydeck as pdk
import pandas as pd

# Hardcoded office locations and their coordinates
OFFICE_LOCATIONS = {
    "London": {"lat": 51.5074, "lon": -0.1278, "country": "GB"},
    "Paris": {"lat": 48.8566, "lon": 2.3522, "country": "FR"},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694, "country": "HK"},
    "Singapore": {"lat": 1.3521, "lon": 103.8198, "country": "SG"},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "country": "IN"},
    "Dubai": {"lat": 25.2048, "lon": 55.2708, "country": "AE"},
    "Shanghai": {"lat": 31.2304, "lon": 121.4737, "country": "CN"},
    "Zurich": {"lat": 47.3769, "lon": 8.5417, "country": "CH"},
    "Geneva": {"lat": 46.2044, "lon": 6.1432, "country": "CH"},
    "Aarhus": {"lat": 56.1629, "lon": 10.2039, "country": "DK"},
    "Sydney": {"lat": -33.8688, "lon": 151.2093, "country": "AU"},
    "Wroclaw": {"lat": 51.1079, "lon": 17.0385, "country": "PL"},
    "Budapest": {"lat": 47.4979, "lon": 19.0402, "country": "HU"},
}

# Helper to find city name from IATA code
_iata_to_city = {
    "LHR": "London", "CDG": "Paris", "HKG": "Hong Kong", "SIN": "Singapore",
    "BOM": "Mumbai", "DXB": "Dubai", "PVG": "Shanghai", "ZRH": "Zurich",
    "GVA": "Geneva", "AAR": "Aarhus", "SYD": "Sydney", "WRO": "Wroclaw",
    "BUD": "Budapest"
}


def render_map(scenario: dict | None = None, results: dict | None = None):
    """Renders a map using fixed coordinates for office locations."""
    try:
        if not results or not scenario:
            st.info("Run the optimizer to see the map visualization.")
            return

        # --- Get host city info from results ---
        best_office_iata = results.get("best_office")
        if not best_office_iata:
            st.warning("Best office not found in results.")
            return
        
        host_city_name = _iata_to_city.get(best_office_iata, "Unknown")
        host_location = OFFICE_LOCATIONS.get(host_city_name)
        if not host_location:
            st.warning(f"Host city '{host_city_name}' not found in predefined locations.")
            return
            
        host_lat = host_location["lat"]
        host_lon = host_location["lon"]
        host_country = host_location["country"]

        # --- Get attendee cities from scenario ---
        attendee_cities = list(scenario.get("attendees", {}).keys())
        
        cities_data = []
        for city_name in attendee_cities:
            location = OFFICE_LOCATIONS.get(city_name)
            if location:
                cities_data.append({"city": city_name, "lat": location["lat"], "lon": location["lon"]})
        
        if not cities_data:
            st.warning("No valid attendee cities found in predefined locations.")
            return

        cities = pd.DataFrame(cities_data)

        # --- Host dataframe ---
        host = pd.DataFrame([{"city": f"{host_city_name}, {host_country}", "lat": host_lat, "lon": host_lon}])

        # --- Arcs from attendees to host ---
        arcs = []
        for _, row in cities.iterrows():
            arcs.append({
                "from_city": row['city'], "from_lon": row['lon'], "from_lat": row['lat'],
                "to_city": host_city_name, "to_lon": host_lon, "to_lat": host_lat
            })
        arcs_df = pd.DataFrame(arcs)

        # --- Pydeck Layers ---
        city_layer = pdk.Layer(
            "ScatterplotLayer", data=cities, get_position='[lon, lat]', get_radius=60000,
            get_color=[0, 128, 255, 180], pickable=True
        )
        arc_layer = pdk.Layer(
            "ArcLayer", data=arcs_df, get_source_position='[from_lon, from_lat]',
            get_target_position='[to_lon, to_lat]', get_source_color=[255, 0, 0],
            get_target_color=[0, 255, 0], auto_highlight=True, width_scale=0.0005, width_min_pixels=2
        )
        text_layer = pdk.Layer(
            "TextLayer", data=cities, get_position='[lon, lat]', get_text="city",
            get_color=[255, 255, 255, 255], get_size=16, get_alignment_baseline="'bottom'"
        )
        host_layer = pdk.Layer(
            "ScatterplotLayer", data=host, get_position='[lon, lat]', get_radius=120000,
            get_color=[255, 215, 0, 255], pickable=True
        )

        # --- View and Deck ---
        view_state = pdk.ViewState(latitude=host_lat, longitude=host_lon, zoom=1.5, pitch=45)
        deck = pdk.Deck(
            layers=[city_layer, arc_layer, text_layer, host_layer],
            initial_view_state=view_state,
            tooltip={"text": "{from_city} → {to_city}"}
        )

        st.pydeck_chart(deck)
        st.success(f"Optimal Host Location: **{host_city_name} ({host_country})**")

    except Exception as e:
        st.error(f"Error loading map: {e}")
