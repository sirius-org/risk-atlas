# map_manager.py
from ipyleaflet import Map, GeoJSON
import ipywidgets as widgets

class MapManager:
    def __init__(self):
        self.map = None

    def create_map(self):
        self.map = Map(center=(50.6252978589571, 0.34580993652344), zoom=3)
        return self.map

    def add_layer(self, geojson_data):
        if self.map:
            geojson_layer = GeoJSON(data=geojson_data)
            self.map.add(geojson_layer)
