import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from shapely.geometry import Point, Polygon
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go

# Set the page layout to wide
st.set_page_config(layout="wide")

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

# Track risk data for each point of interest
risk_data = []

for _, row in points_df.iterrows():
    max_risk = 0
    risk_color = None
    popup_text = f"Name: {row['name']}<br>"

    earthquake_risk_value = 0
    flood_risk_value = 0

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

    risk_data.append({
        'name': row['name'],
        'earthquake_risk': earthquake_risk_value,
        'flood_risk': flood_risk_value,
        'total_risk': earthquake_risk_value + flood_risk_value
    })

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

# Generate the Folium map as an HTML iframe
map_html = m._repr_html_()
map_html_with_js = f"""
    {map_html}
    {map_state_js}
"""
# Display the map and JavaScript in a column
map_col, data_col = st.columns([1, 1])
with map_col:
    components.html(map_html_with_js, height=600)

with data_col:
    # Create a horizontal bar graph
    risk_df = pd.DataFrame(risk_data)
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=risk_df['name'],
        x=risk_df['earthquake_risk'],
        name='Earthquake Risk',
        orientation='h',
        marker=dict(color='red')
    ))

    fig.add_trace(go.Bar(
        y=risk_df['name'],
        x=risk_df['flood_risk'],
        name='Flood Risk',
        orientation='h',
        marker=dict(color='blue')
    ))

    fig.update_layout(
        barmode='stack',
        title='Total Risk by Point of Interest',
        xaxis_title='Total Risk',
        yaxis_title='Point of Interest',
        height=600,  # Adjust the height if needed
        width=800    # Adjust the width if needed
    )

    st.plotly_chart(fig)

st.subheader("Points of Interest Data")
st.dataframe(points_df)

st.subheader("Earthquake Data")
st.dataframe(earthquake_df)

st.subheader("Flood Data")
st.dataframe(flood_df)