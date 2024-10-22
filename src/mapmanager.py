from ipyleaflet import Map, GeoJSON, ZoomControl, FullScreenControl, LegendControl, MarkerCluster, Marker, Icon, Popup, LayerGroup
import ipywidgets as widgets
from ipywidgets.widgets.widget_string import HTML
from shapely.geometry import Point, Polygon, shape
from bs4 import BeautifulSoup
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
        self.points_in_geometry = set()


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
                f'{config["map"]["legend"]["text"]["medium"]} {config["map"]["legend"]["value"]["medium"] + 1} and {config["map"]["legend"]["value"]["high"]}': config["map"]["legend"]["color"]["medium"],
                f'{config["map"]["legend"]["text"]["high"]} {config["map"]["legend"]["value"]["high"]}': config["map"]["legend"]["color"]["high"]
            },
            title = config["map"]["legend"]["title"],
            position = "bottomright"
        )
        self.map.add(zoom_control)
        self.map.add(fullscreen_control)
        self.map.add(legend_control)


    def generate_layers(self):
        layers = []
        for i in range(1, len(config["risk"]["risks"]) + 1):
            path = config["risk"][f"{i}"]["path"]
            fill_color = config["risk"][f"{i}"]["fill_color"]
            heading = config["risk"][f"{i}"]["heading"]
            layer = self.__transform_to_geojson(heading, path, fill_color)
            layers.append(layer)
        layer_group = LayerGroup(layers = layers)
        return layer_group


    def add_active_layers(self, layers):
        for layer in layers:
            self.map.add(layer)


    def __transform_to_geojson(self, heading, file_path, fill_color):
        gdf = gpd.read_file(file_path)
        gdf = gdf.to_crs(epsg=4326)
        #gdf['type'] = folder_name
        geojson_data = json.loads(gdf.to_json())
        geo_json_layer = GeoJSON(
            data = geojson_data,
            name = heading,
            style = {
                'title': heading,
                'color': 'black', 
                'fillColor': f'{fill_color}', 
                'opacity': 1, 
                'dashArray': '9', 
                'fillOpacity': 0.1, 
                'weight': 1
            },
            hover_style = {
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
                name = row['id'],
                location = point,
                icon = Icon(
                    icon_url = f'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-{point_color}.png'
                ),
                draggable = False,
                popup = popup
            )
            markers.append(marker)
        marker_cluster = MarkerCluster(markers=markers)
        return marker_cluster


    def add_markers(self, marker_cluster):
        self.map.add(marker_cluster)


    def update_markers(self, marker_cluster):
        for marker in marker_cluster.markers:
            highest_risk_value = self.__get_highest_risk_value(marker)
            point_color = self.__get_color(highest_risk_value)
            marker.icon = Icon(
                icon_url=f'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-{point_color}.png'
            )


    def is_in_geometry(self, point):
        for layer in self.active_layers:
            layer_data = layer.data
            for feature in layer_data["features"]:
                geometry = shape(feature['geometry'])
                if geometry.contains(point):
                    self.points_in_geometry.add(point)
                    return True


    def count_points_in_geometry(self):
        count = len(self.points_in_geometry)
        return count

    
    def update_value_boxes(self, box):
        # prendi i valori che servono da map_manager
        # - funzione per 1: 
            # check punti nei layer attivi;
            # prendi i marker;
            # prendi i popup;
                # per ogni popup, prendi i rischi associati ai layer attivi
                # somma i rischi
                # trova la somma più alta tra tutti i popup
                # ritorna il titolo dell'oggetto con la somma più alta
        # - funzione per 2
            # check punti nei layer attivi;
            # prendi i marker;
            # prendi i popup;
                # per ogni popup, prendi i rischi associati ai layer attivi
                # somma gli stessi tipi di rischio tra diversi popup e fai la media
                # ritorna il tipo di rischio con la media più alta
        count_points = self.count_points_in_geometry()
        #box.value = count_points
        return count_points


    def __get_highest_risk_value(self, marker):
        highest_risk = 0
        html_value = marker.popup.child.value
        soup = BeautifulSoup(html_value, 'html.parser')
        point = Point(marker.location[1], marker.location[0])
        if self.is_in_geometry(point):
            for layer in self.active_layers:
                layer_data = layer.data
                for feature in layer_data["features"]:
                    risk_header = feature['properties']['style']['title']
                    risk_value = soup.find(attrs={"data-id": risk_header}).get('data-value')
                    if risk_value:
                        if int(risk_value) > highest_risk:
                            highest_risk = int(risk_value)
        return highest_risk


    def __get_color(self, risk_value):
        if risk_value > config["map"]["legend"]["value"]["high"]:
            return config["map"]["legend"]["color"]["high"]
        elif config["map"]["legend"]["value"]["medium"] < risk_value <= config["map"]["legend"]["value"]["high"]:
            return config["map"]["legend"]["color"]["medium"]
        elif config["map"]["legend"]["value"]["low"] <= risk_value <= config["map"]["legend"]["value"]["medium"]:
            return config["map"]["legend"]["color"]["low"]
        else:
            return config["map"]["legend"]["color"]["neutral"]


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



'''def find_highest_risk(df):
    df['total_risk'] = df['earthquake_risk'] + df['flood_risk']
    highest_risk_row = df.loc[df['total_risk'].idxmax()]
    highest_risk_data = {
        'total_risk': highest_risk_row['total_risk'],
        'earthquake_risk': highest_risk_row['earthquake_risk'],
        'flood_risk': highest_risk_row['flood_risk'],
        'name': highest_risk_row['name']
    }
    return highest_risk_data


def find_dominant_risk_type(df, risk_columns):
    avg_risks = {}
    for risk in risk_columns:
        avg_risks[risk] = df[risk].mean()
    dominant_risk = max(avg_risks, key=avg_risks.get)
    avg_risk_value = avg_risks[dominant_risk]
    dominant_risk_data = {
        'dominant_risk': dominant_risk,
        'avg_risk_value': avg_risk_value
    }
    return dominant_risk_data'''