import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from shapely.geometry import Point, Polygon
import streamlit.components.v1 as components

# Load data
points_df = pd.read_csv('data.csv')
earthquake_df = pd.read_csv('earthquake.csv')
flood_df = pd.read_csv('flood.csv')

# Function to determine color based on risk value
def get_color(value):
    if value > 5:
        return 'red'
    elif value >= 2:
        return 'orange'
    else:
        return 'green'

# Function to check if a point is inside a polygon
def is_point_in_polygon(point, polygon_coords):
    polygon = Polygon(polygon_coords)
    return polygon.contains(Point(point))

# Add earthquake and flood polygons to the map
def add_polygon(df, color):
    coordinates = df[['latitude', 'longitude']].values.tolist()
    folium.Polygon(
        locations=coordinates,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.4
    ).add_to(m)
    return coordinates

# Load or initialize map state
if 'map_state' not in st.session_state:
    st.session_state.map_state = {'location': [44.4184, 12.2035], 'zoom': 13}

# Create map with saved state
m = folium.Map(location=st.session_state.map_state['location'], zoom_start=st.session_state.map_state['zoom'])

# Toggle visualization
earthquake_risk = st.checkbox("Show Earthquake Risk")
flood_risk = st.checkbox("Show Flood Risk")

earthquake_polygon_coords = None
flood_polygon_coords = None

if earthquake_risk:
    earthquake_polygon_coords = add_polygon(earthquake_df, 'brown')

if flood_risk:
    flood_polygon_coords = add_polygon(flood_df, 'blue')

for _, row in points_df.iterrows():
    max_risk = 0
    risk_color = None
    popup_text = f"Name: {row['name']}<br>"

    if earthquake_polygon_coords and is_point_in_polygon((row['latitude'], row['longitude']), earthquake_polygon_coords):
        earthquake_risk_value = row['earthquake_risk']
        if earthquake_risk_value > max_risk:
            max_risk = earthquake_risk_value
            risk_color = get_color(earthquake_risk_value)
        popup_text += f"Earthquake Risk: {earthquake_risk_value}<br>"

    if flood_polygon_coords and is_point_in_polygon((row['latitude'], row['longitude']), flood_polygon_coords):
        flood_risk_value = row['flood_risk']
        if flood_risk_value > max_risk:
            max_risk = flood_risk_value
            risk_color = get_color(flood_risk_value)
        popup_text += f"Flood Risk: {flood_risk_value}<br>"

    if risk_color:
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_text,
            icon=folium.Icon(color=risk_color)
        ).add_to(m)
    else:
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_text
        ).add_to(m)

# Save current map state using JavaScript
map_state_js = """
<script>
    const map = window._leaflet_maps[Object.keys(window._leaflet_maps)[0]];
    map.on('moveend', function() {
        const center = map.getCenter();
        const zoom = map.getZoom();
        const mapState = {location: [center.lat, center.lng], zoom: zoom};
        window.parent.postMessage(JSON.stringify(mapState), '*');
    });
</script>
"""

# Display the map and JavaScript
folium_static(m)
components.html(map_state_js)

# Update map state from JavaScript
if 'mapState' in st.query_params():
    map_state = st.query_params()['mapState'][0]
    st.session_state.map_state = eval(map_state)
