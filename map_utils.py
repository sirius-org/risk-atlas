from shapely.geometry import Point, Polygon, shape
import ipyleaflet as L
from ipywidgets.widgets.widget_string import HTML
import data, os, json
import geopandas as gpd
from ipyleaflet import GeoJSON
import random


def add_polygon_layers(selected_files):
    base_folder = 'data/polygons'
    geojson_layers = []
    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        if os.path.isdir(folder_path):
            for file in selected_files:
                file_path = os.path.join(folder_path, file)
                try:
                    gdf = gpd.read_file(file_path)
                    gdf = gdf.to_crs(epsg=4326)
                    gdf['type'] = folder_name
                    geojson_data = json.loads(gdf.to_json())
                    geo_json_layer = GeoJSON(
                        data=geojson_data,
                        name=file_path,
                        style={
                            'color': 'black', 'fillColor': 'blue', 'opacity': 1, 'dashArray': '9', 'fillOpacity': 0.1, 'weight': 1
                        },
                        hover_style={
                            'color': 'white', 'dashArray': '0', 'fillOpacity': 0.5
                        },
                    )
                    geojson_layers.append(geo_json_layer)
                except Exception as e:
                    print(f"Error reading file {file}: {e}")
    return geojson_layers


def get_highest_risk(point, row, active_polygons):
    highest_risk = 0
    risk_type = None
    point_shapely = Point(point)
    inverted_point = Point(point_shapely.y, point_shapely.x)
    for polygon_layer in active_polygons:
        polygon_data = polygon_layer.data
        for feature in polygon_data['features']:
            polygon_type = feature['properties']['type']
            polygon_shape = shape(feature['geometry'])
            if polygon_shape.contains(inverted_point):
                risk_key = f'{polygon_type}_risk'
                risk_value = row.get(risk_key, 0)
                if risk_value > highest_risk:
                    highest_risk = risk_value
                    risk_type = polygon_type
    return highest_risk, risk_type


def add_data_points(active_polygons):
    markers = []
    data_points = data.get_data()
    for _, row in data_points.iterrows():
        point = (row['latitude'], row['longitude'])
        highest_risk, rist_type = get_highest_risk(point, row, active_polygons)
        popup = create_popup(row, point)
        point_color = get_color(highest_risk)
        marker = L.Marker(
            name=row['name'],
            location=point,
            icon=L.Icon(icon_url=f'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-{point_color}.png'),
            draggable=False,
            popup=popup
        )
        markers.append(marker)
    return markers

        
def create_popup(row, point):
    popup_content = HTML(
        value=f'''
            <div class="card" style="width: 500px;">
                <div class="card-body">
                    <h5 class="card-title">{row['name']}</h5>
                    <h6 class="card-subtitle mb-2 text-muted">{row['alt_name']}</h6>
                    <div class="card-text">
                        <dl class="row">
                            <dt class="col-sm-3">Description</dt>
                            <dd class="col-sm-9">{row['description']}</dd>
                            <dt class="col-sm-3">Earthquake risk</dt>
                            <dd class="col-sm-9">{row['earthquake_risk']}</dd>
                            <dt class="col-sm-3">Flood risk</dt>
                            <dd class="col-sm-9">{row['flood_risk']}</dd>
                        </dl>
                    </div>
                    <a href="#" class="card-link">Card link</a>
                    <a href="#" class="card-link">Another link</a>
                </div>
            </div>
        ''',
    )
    popup = L.Popup(
        location=point,
        child=popup_content,
        min_width=1000,
    )
    return popup


def create_map(polygons):
    m = L.Map(
        zoom=14,
        center=(44.4183598, 12.2035294),
        zoom_control=False
    )
    zoom_control = L.ZoomControl(position='topright')
    m.add(zoom_control)
    fullscreen_control = L.FullScreenControl(position='topright')
    m.add(fullscreen_control)
    legend_control = L.LegendControl(
        {
            "low": "green",
            "medium": "orange",
            "high": "red"
        },
        title="Legend",
        position="bottomright"
    )
    m.add(legend_control)

    active_polygons = []
    if len(polygons) > 0:
        for geojson_obj in polygons:
            m.add(geojson_obj)
            active_polygons.append(geojson_obj)

    for marker in add_data_points(active_polygons):
        m.add(marker)
    
    return m


def get_color(risk_value):
    if risk_value > 5:
        return 'red'
    elif 3 <= risk_value <= 5:
        return 'orange'
    elif 1 <= risk_value <= 2:
        return 'green'
    else:
        return 'blue'

