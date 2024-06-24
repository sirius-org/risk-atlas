import os
import pandas as pd
import plotly.express as px
from shapely.geometry import Point, Polygon
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget, render_plotly
from ipywidgets.widgets.widget_string import HTML
import ipyleaflet as L

# Get list of CSV files in the "data" folder
data_folder = 'data'
csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]


app_ui = ui.page_sidebar(
    ui.sidebar(
            "Data",
            *[ui.input_checkbox(f"file_{i}", csv_file) for i, csv_file in enumerate(csv_files)],
            bg="#f8f8f8"
        ),
    ui.page_fillable(
        ui.layout_columns(
            ui.value_box(
                "KPI Title",
                "$1 Billion Dollars",
                "Up 30% VS PREVIOUS 30 DAYS",
                theme="bg-gradient-indigo-purple",
            ),
            ui.value_box(
                "KPI Title",
                "$1 Billion Dollars",
                "Up 30% VS PREVIOUS 30 DAYS",
                theme="bg-gradient-indigo-purple",
            ),
            ui.value_box(
                "KPI Title",
                "$1 Billion Dollars",
                "Up 30% VS PREVIOUS 30 DAYS",
                theme="bg-gradient-indigo-purple",
            ),
            col_widths=(4, 4, 4)
        ),
        ui.layout_columns(
            ui.card(
                output_widget("map"),
                full_screen=True
            ),
        ),
        ui.layout_columns(
            ui.card(
                output_widget("plot"),
            ),
        )
    ),
)


# Define server logic
def server(input, output, session):

    @reactive.Calc
    def selected_files():
        selected = [csv_files[i] for i in range(len(csv_files)) if input[f"file_{i}"]()]
        return selected

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
    
    
    @render_widget
    def map():
        m = L.Map(
            zoom=14, 
            center=(44.4183598, 12.2035294),
            zoom_control=False
        )

        # Store polygons for each risk type
        risk_polygons = {
            'earthquake': [],
            'flood': []
        }
        
        # Add data points or polygons based on selected files
        for file in selected_files():
            if file == 'data.csv':
                continue
            file_path = os.path.join(data_folder, file)
            df = pd.read_csv(file_path)
            points = df[['latitude', 'longitude']].values.tolist()
            if 'earthquake' in file:
                risk_polygons['earthquake'].append(points)
            elif 'flood' in file:
                risk_polygons['flood'].append(points)
            polygon = L.Polygon(
                locations=points,
                color="green",
                fill_color="green"
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
                
                highest_risk = 0
                    
                for risk_type, polygons in risk_polygons.items():
                    for polygon_points in polygons:
                        if is_point_in_polygon(point, polygon_points):
                            if risk_type == 'earthquake':
                                highest_risk = max(highest_risk, earthquake_risk)                    
                            elif risk_type == 'flood':
                                highest_risk = max(highest_risk, flood_risk)
                
                popup_content = HTML(
                    value=f'''
                        <h2>{row['name']}</h2>
                        <p>Earthquake risk: {earthquake_risk}</p>
                        <p>Flood risk: {flood_risk}</p>
                    ''',
                )
                popup = L.Popup(
                    location=point,
                    child=popup_content
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
        
        zoom_control = L.ZoomControl(position='topright')
        m.add(zoom_control)
        fullscreen_control = L.FullScreenControl(position='topright')
        m.add(fullscreen_control)
        legend_control = L.LegendControl(
            {
                "low":"green", 
                "medium":"orange", 
                "High":"red"
            }, 
            title="Legend", 
            position="bottomright"
        )
        m.add(legend_control)

        return m


    @render_plotly
    def plot():
        
        for file in csv_files:
            if file == 'data.csv':
                data = []
                file_path = os.path.join(data_folder, file)
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    earthquake_risk = row['earthquake_risk']
                    flood_risk = row['flood_risk']
                    data.append({
                        'name': row['name'],
                        'earthquake_risk': earthquake_risk,
                        'flood_risk': flood_risk,
                        'total_risk': earthquake_risk + flood_risk
                    })
                sorted_data = sorted(data, key=lambda x: x['total_risk'], reverse=True)[:3]
                plot_df = pd.DataFrame(sorted_data)
                fig = px.bar(
                    plot_df,
                    x=['earthquake_risk', 'flood_risk'],
                    y='name',
                    title="Top 3 Points with Highest Total Risk",
                    labels={'value': 'Risk Value', 'name': 'Location'},
                    color_discrete_map={
                        'earthquake_risk': 'brown',
                        'flood_risk': 'blue'
                    },
                    orientation='h'
                )
                fig.update_layout(barmode='stack')

                return fig



# Create app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()