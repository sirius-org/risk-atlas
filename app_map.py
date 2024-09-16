from ipyleaflet import Map, GeoJSON, ZoomControl, FullScreenControl, LegendControl, MarkerCluster, Marker, Icon, Popup, LayerGroup
import ipywidgets as widgets
from ipywidgets.widgets.widget_string import HTML
from shapely.geometry import Point, Polygon, shape
import os
import json
import geopandas as gpd
import tomli


with open("config.toml", mode="rb") as fp:
    config = tomli.load(fp)

class MapManager:
    def __init__(self):
        self.map = None
        self.active_layers = None

    def create_map(self):
        self.map = Map(
            zoom = config["map"]["zoom"],
            center = (
                config["map"]["latitude"], 
                config["map"]["longitude"]
            ), 
            zoom_control = False
            )
        self.__set_map_controls()
        return self.map

    def __set_map_controls(self):
        zoom_control = ZoomControl(position='topright')
        fullscreen_control = FullScreenControl(position='topright')
        legend_control = LegendControl(
            {
                f'{config["map"]["legend"]["text"]["low"]} {config["map"]["legend"]["value"]["low"]} and {config["map"]["legend"]["value"]["medium"]}': config["map"]["legend"]["color"]["low"],
                f'{config["map"]["legend"]["text"]["medium"]} {config["map"]["legend"]["value"]["medium"]} and {config["map"]["legend"]["value"]["high"]}': config["map"]["legend"]["color"]["medium"],
                f'{config["map"]["legend"]["text"]["high"]} {config["map"]["legend"]["value"]["high"]}': config["map"]["legend"]["color"]["high"]
            },
            title = config["map"]["legend"]["title"],
            position = "bottomright"
        )
        self.map.add(zoom_control)
        self.map.add(fullscreen_control)
        self.map.add(legend_control)


    def load_files(self):
        shape_files = []
        base_folder = config["geo"]["base_folder"]
        folders = [folder for folder in os.listdir(base_folder)]
        for folder in folders:
            folder_path = os.path.join(base_folder, folder)
            files = [file for file in os.listdir(folder_path)]
            for file in files:
                if file.endswith('.shp'):
                    file_path = os.path.join(folder_path, file)
                    shape_files.append(file_path)
        return shape_files

    def generate_layers(self):
        layers = []
        files = self.load_files()
        for file in files:
            layer = self.__transform_to_geojson(file)
            layers.append(layer)
        layer_group = LayerGroup(layers=layers)
        return layer_group

    def add_active_layers(self, layers):
        for layer in layers:
            self.map.add(layer)

    def __transform_to_geojson(self, file_path):
        gdf = gpd.read_file(file_path)
        gdf = gdf.to_crs(epsg=4326)
        #gdf['type'] = folder_name
        geojson_data = json.loads(gdf.to_json())
        geo_json_layer = GeoJSON(
            data=geojson_data,
            name=file_path,
            style={
                'color': 'black', 
                'fillColor': 'blue', 
                'opacity': 1, 
                'dashArray': '9', 
                'fillOpacity': 0.1, 
                'weight': 1
            },
            hover_style={
                'color': 'white', 
                'dashArray': '0', 
                'fillOpacity': 0.5
            },
        )
        return geo_json_layer


    def generate_markers(self, data):
        markers = []
        for row in data:
            point = (row['latitude'], row['longitude'])
            point_color = 'grey'
            popup = self.__add_popup(row, point)
            marker = Marker(
                name=row['id'],
                location=point,
                icon=Icon(
                    icon_url=f'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-{point_color}.png'
                ),
                draggable=False,
                popup=popup
            )
            markers.append(marker)
        marker_cluster = MarkerCluster(markers=markers)
        return marker_cluster

    def add_markers(self, marker_cluster):
        self.map.add(marker_cluster)

    def update_markers(self, marker_cluster):
        for marker in marker_cluster.markers:
            print(marker)
            highest_risk_value = self.__get_highest_risk_value(marker)
            point_color = self.__get_color(4)
            marker.icon = Icon(
                icon_url=f'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-{point_color}.png'
            )

    def __get_highest_risk_value(self, marker):
        highest_risk = 0
        point = Point(marker.location[1], marker.location[0])
        for layer in self.active_layers:
            layer_data = layer.data
            for feature in layer_data["features"]:
                # polygon_type = feature['properties']['type']
                geometry = shape(feature['geometry'])
                if geometry.contains(point):
                    # risk_key = f'{polygon_type}_risk'
                    # risk_value = row.get(risk_key, 0)
                    # if risk_value > highest_risk:
                    #    highest_risk = risk_value
                    #    risk_type = polygon_type
                    print(True)

    def __get_color(self, risk_value):
        if risk_value > config["map"]["legend"]["value"]["high"]:
            return config["map"]["legend"]["color"]["high"]
        elif config["map"]["legend"]["value"]["medium"] < risk_value <= config["map"]["legend"]["value"]["high"]:
            return config["map"]["legend"]["color"]["medium"]
        elif config["map"]["legend"]["value"]["low"] <= risk_value <= config["map"]["legend"]["value"]["medium"]:
            return config["map"]["legend"]["color"]["low"]
        else:
            return config["map"]["legend"]["color"]["neutral"]
    '''
    def get_highest_risk(point, row, active_polygons):
                polygon_type = feature['properties']['type']
                polygon_shape = shape(feature['geometry'])
                if polygon_shape.contains(inverted_point):
                    risk_key = f'{polygon_type}_risk'
                    risk_value = row.get(risk_key, 0)
                    if risk_value > highest_risk:
                        highest_risk = risk_value
                        risk_type = polygon_type
        return highest_risk

    '''

    def __add_popup(self, row, point):
        popup_template = config['map']['popup_content']
        popup_content = eval(f"f'''{popup_template}'''")
        popup_html = HTML(
            value = popup_content,
        )
        popup = Popup(
            location=point,
            child=popup_html,
            min_width=1000,
        )
        return popup