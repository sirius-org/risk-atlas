from ipyleaflet import Map, GeoJSON, ZoomControl, FullScreenControl, LegendControl, Marker, Icon, Popup
import ipywidgets as widgets
from ipywidgets.widgets.widget_string import HTML
import os

class MapManager:
    def __init__(self):
        self.map = None

    def create_map(self):
        self.map = Map(
            zoom=14,
            center=(44.4183598, 12.2035294), 
            zoom_control=False
            )
        self.__set_map_controls()
        return self.map

    def __set_map_controls(self):
        zoom_control = ZoomControl(position='topright')
        fullscreen_control = FullScreenControl(position='topright')
        legend_control = LegendControl(
            {
                "low": "green",
                "medium": "orange",
                "high": "red"
            },
            title="Legend",
            position="bottomright"
        )
        self.map.add(zoom_control)
        self.map.add(fullscreen_control)
        self.map.add(legend_control)

    def add_markers(self, data):
        for row in data:
            point = (row['latitude'], row['longitude'])
            # highest_risk, rist_type = get_highest_risk(point, row, active_polygons)
            popup = self.__add_popup(row, point)
            # point_color = get_color(highest_risk)
            point_color = 'blue'
            marker = Marker(
                name=row['id'],
                location=point,
                icon=Icon(
                    icon_url=f'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-{point_color}.png'
                ),
                draggable=False,
                popup=popup
            )
            self.map.add(marker)

    def __add_popup(self, row, point):
        popup_content = HTML(
        value=f'''
            <div class="card" style="width: 500px;">
                <div class="card-body">
                    <h5 class="card-title">{row['label']}</h5>
                    <h6 class="card-subtitle mb-2 text-muted">{row['alt_label']}</h6>
                    <div class="card-text">
                        <dl class="row">
                            <dt class="col-sm-3">Description</dt>
                            <dd class="col-sm-9">{row['description']}</dd>
                            <dt class="col-sm-3">Inception</dt>
                            <dd class="col-sm-9">{row['date_created']}</dd>
                            <dt class="col-sm-3">Risk 1</dt>
                            <dd class="col-sm-9">{row['risk1']}</dd>
                            <dt class="col-sm-3">Risk 2</dt>
                            <dd class="col-sm-9">{row['risk2']}</dd>
                            <dt class="col-sm-3">Risk 3</dt>
                            <dd class="col-sm-9">{row['risk3']}</dd>
                            <dt class="col-sm-3">Risk 4</dt>
                            <dd class="col-sm-9">{row['risk4']}</dd>
                        </dl>
                    </div>
                    <a href="https://www.wikidata.org/wiki/{row['id']}" target="_blank" class="card-link">Wikidata</a>
                    <a href="{row['official_site']}" target="_blank" class="card-link">Official site</a>
                    <a href="https://viaf.org/viaf/{row['viaf']}/" target="_blank" class="card-link">VIAF</a>
                </div>
            </div>
        ''',
        )
        popup = Popup(
            location=point,
            child=popup_content,
            min_width=1000,
        )
        return popup

    def add_layer(self, layer):
        self.map.add(layer)
