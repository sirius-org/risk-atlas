import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from shapely.geometry import Point, Polygon

# Load data
points_df = pd.read_csv('data.csv')
earthquake_df = pd.read_csv('earthquake.csv')
flood_df = pd.read_csv('flood.csv')

# Initialize map centered on Ravenna
m = folium.Map(location=[44.4184, 12.2035], zoom_start=13)

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

# Toggle visualization
risk_type = st.radio("Select risk type to visualize", ('None', 'Earthquake Risk', 'Flood Risk'))

if risk_type == 'Earthquake Risk':
    earthquake_polygon_coords = add_polygon(earthquake_df, 'brown')
    for _, row in points_df.iterrows():
        if is_point_in_polygon((row['latitude'], row['longitude']), earthquake_polygon_coords):
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"Name: {row['name']}<br>Earthquake Risk: {row['earthquake_risk']}",
                icon=folium.Icon(color=get_color(row['earthquake_risk']))
            ).add_to(m)
elif risk_type == 'Flood Risk':
    flood_polygon_coords = add_polygon(flood_df, 'blue')
    for _, row in points_df.iterrows():
        if is_point_in_polygon((row['latitude'], row['longitude']), flood_polygon_coords):
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"Name: {row['name']}<br>Flood Risk: {row['flood_risk']}",
                icon=folium.Icon(color=get_color(row['flood_risk']))
            ).add_to(m)
else:
    for _, row in points_df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Name: {row['name']}",
        ).add_to(m)

# Display the map
folium_static(m)
