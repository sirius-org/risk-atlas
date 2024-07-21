from shapely.geometry import Point, Polygon, shape
import ipyleaflet as L
from ipywidgets.widgets.widget_string import HTML
import data, os, json
import geopandas as gpd
from ipyleaflet import GeoJSON
import random


def add_polygon_layers(selected_files):
    geojson_layers = []
    for file in selected_files:
        file_path = os.path.join('data/polygons', file)
        try:
            gdf = gpd.read_file(file_path)
            gdf = gdf.to_crs(epsg=4326)
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


def add_data_points():
    markers = []
    data_points = data.get_data()
    risk_polygons = {
        'earthquake': [],
        'flood': []
    }
    for _, row in data_points.iterrows():
        point = (row['latitude'], row['longitude'])
        earthquake_risk = row.get('earthquake_risk', 0)
        flood_risk = row.get('flood_risk', 0)
        highest_risk = 0
        for risk_type, polygons in risk_polygons.items():
            for polygon_points in polygons:
                if is_point_in_polygon(point, polygon_points):
                    if risk_type == 'earthquake':
                        highest_risk = max(highest_risk, earthquake_risk)                    
                    elif risk_type == 'flood':
                        highest_risk = max(highest_risk, flood_risk)
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
    for marker in add_data_points():
        m.add(marker)
    if len(polygons) > 0:
        for geojson_obj in polygons:
            m.add(geojson_obj)
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


def is_point_in_polygon(point, polygon_points):
    polygon = Polygon(polygon_points)
    return polygon.contains(Point(point))
