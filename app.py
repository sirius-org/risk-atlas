import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Load data
data = pd.read_csv('data.csv')

# Initialize map centered on Ravenna
m = folium.Map(location=[44.4184, 12.2035], zoom_start=13)

# Function to determine color based on value
def get_color(value):
    if value > 5:
        return 'red'
    elif value >= 2:
        return 'orange'
    else:
        return 'green'

# Add points to the map
for _, row in data.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"Name: {row['name']}<br>Value: {row['value']}",
        icon=folium.Icon(color=get_color(row['value']))
    ).add_to(m)

# Display the map
folium_static(m)

