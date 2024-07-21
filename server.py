import os
import pandas as pd
from shiny import render, reactive
from shinywidgets import render_widget, render_plotly
from ipywidgets.widgets.widget_string import HTML
import plotly.express as px
from data_utils import find_highest_risk, find_dominant_risk_type
from map_utils import get_color, is_point_in_polygon, create_map, add_polygon_layers
import data


data_folder = "data"
data_df = data.get_data()
csv_files = data.get_files()
shape_files = data.get_polygons()


def server(input, output, session):

    @reactive.Calc
    def get_selected_files():
        return [shape_files[i] for i in range(len(shape_files)) if input[f"file_{i}"]()]

    @render_widget
    def map():
        
        if len(get_selected_files()) > 0:
            polygons = add_polygon_layers(get_selected_files())
        else:
            polygons = []

        return create_map(polygons)
        

        """
        for file in get_selected_files():
            file_path = os.path.join(data_folder, file)
            df = pd.read_csv(file_path)
            points = df[['latitude', 'longitude']].values.tolist()
            if 'earthquake' in file:
                risk_polygons['earthquake'].append(points)
                color_polygons = 'brown'
            elif 'flood' in file:
                risk_polygons['flood'].append(points)
                color_polygons = 'blue'
            polygon = L.Polygon(
                locations=points,
                color=color_polygons,
                fill_color=color_polygons
            )
            m.add(polygon)

        for file in selected_files():
            if file != 'data.csv':
                continue
            file_path = os.path.join(data_folder, file)
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                point = (row['latitude'], row['longitude'])
                earthquake_risk = row.get('earthquake_risk', 0)
                flood_risk = row.get('flood_risk', 0)
                
                
                
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
                
                point_color = get_color(highest_risk)

                marker = L.Marker(
                        name=row['name'],
                        location=point,
                        icon=L.Icon(icon_url=f'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-{point_color}.png'),
                        draggable=False,
                        popup=popup
                )

                m.add(marker)
        """
        
    """
    @render_plotly
    def plot():
        return False
        
        data = []
        for file in selected_files():
            if file != 'data.csv':
                file_path = os.path.join(data_folder, 'data.csv')
                df = pd.read_csv(file_path)
                type_label = file[:-4]
                for _, row in df.iterrows():
                    type_risk = row.get(f'{type_label}_risk', 0)
                    data.append({
                        'name': row['name'],
                        'risk_type': f'{type_label}_risk',
                        'risk_value': type_risk
                    })
    
        plot_df = pd.DataFrame(data)

        if plot_df.empty:
            return HTML(value="<div>Select a layer to visualize its related risk.</div>")

        fig = px.bar(
            plot_df,
            x='risk_value',
            y='name',
            color='risk_type',
            title="Combined Risk Values",
            labels={'risk_value': 'Risk Value', 'name': 'Object'},
            color_discrete_map={
                'earthquake_risk': 'brown',
                'flood_risk': 'blue'
            },
            orientation='h'
        )
        
        fig.update_layout(barmode='stack')

        return fig
    """

    @render.data_frame  
    def object_data_df():
        return render.DataTable(data_df)

    @render.data_frame  
    def earthquake_data_df():
        data_csv_path = os.path.join(data_folder, 'earthquake.csv')
        data_df = pd.read_csv(data_csv_path)
        return render.DataTable(data_df)

    @render.data_frame  
    def flood_data_df():
        data_csv_path = os.path.join(data_folder, 'flood.csv')
        data_df = pd.read_csv(data_csv_path)
        return render.DataTable(data_df)

    @render.download()
    def download_object_data():
        return data_csv_path

    @render.download()
    def download_earthquake_data():
        return os.path.join(data_folder, 'earthquake.csv')

    @render.download()
    def download_flood_data():
        return os.path.join(data_folder, 'flood.csv')

