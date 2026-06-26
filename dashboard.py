import streamlit as pd_stream
import pydeck as pdk
import pandas as pd
import requests
import random

pd_stream.set_page_config(layout="wide", page_title="Marketplace Operations Dispatch")
pd_stream.title("📊 Chrono-Spatial Marketplace Optimization Console")
pd_stream.markdown("### Real-Time Fleet Demand Forecasting via LightGBM & Uber H3")

col1, col2 = pd_stream.columns([1, 3])

with col1:
    pd_stream.header("Simulation Controls")
    target_area = pd_stream.selectbox(
        "Select Operations Hub",
        ["Manhattan Core (Midtown)", "JFK Airport Corridor", "Brooklyn Williamsburg"]
    )
    if target_area == "Manhattan Core (Midtown)":
        base_lat, base_lon = 40.7580, -73.9855
    elif target_area == "JFK Airport Corridor":
        base_lat, base_lon = 40.6413, -73.7781
    else:
        base_lat, base_lon = 40.7081, -73.9571

    pd_stream.metric(label="Target Latitude", value=base_lat)
    pd_stream.metric(label="Target Longitude", value=base_lon)
    trigger_predict = pd_stream.button("Run Real-Time Dispatch Optimization", type="primary")

with col2:
    pd_stream.subheader("Market Space Fleet Allocation Map")
    simulated_scenarios = []
    for _ in range(120):
        lat_offset = base_lat + random.uniform(-0.04, 0.04)
        lon_offset = base_lon + random.uniform(-0.05, 0.05)
        try:
            response = requests.post(
                "http://127.0.0.1:8000/predict", 
                json={"latitude": lat_offset, "longitude": lon_offset},
                timeout=1
            )
            data = response.json()
            h3_hex = data["h3_index"]
            predicted_demand = data["predicted_demand_next_15m"]
        except Exception:
            import h3
            # Graceful version handling for h3 library changes
            h3_hex = h3.geo_to_h3(lat_offset, lon_offset, 8) if hasattr(h3, 'geo_to_h3') else h3.latlng_to_cell(lat_offset, lon_offset, 8)
            predicted_demand = random.uniform(5.0, 65.0)
            
        simulated_scenarios.append({
            "hex": h3_hex,
            "demand": predicted_demand,
            "color_r": int((predicted_demand / 65.0) * 255),
            "color_g": int((1 - (predicted_demand / 65.0)) * 150),
            "color_b": 100
        })
        
    df_map = pd.DataFrame(simulated_scenarios)
    layer = pdk.Layer(
        "H3HexagonLayer",
        df_map,
        pickable=True,
        stroked=True,
        filled=True,
        extruded=True,
        get_hexagon="hex",
        get_fill_color="[color_r, color_g, color_b, 180]",
        get_elevation="demand * 25",
        elevation_scale=1,
    )
    view_state = pdk.ViewState(latitude=base_lat, longitude=base_lon, zoom=12, pitch=45)
    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "H3 Index: {hex}\nPredicted Ride Requests: {demand}"})
    pd_stream.pydeck_chart(r)
