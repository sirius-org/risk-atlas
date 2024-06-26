import os, faicons
import pandas as pd
import plotly.express as px
from shapely.geometry import Point, Polygon
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget, render_plotly
from ipywidgets.widgets.widget_string import HTML
import ipyleaflet as L
from htmltools import a, div

# Get list of CSV files in the "data" folder
data_folder = 'data'
csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]

for file in csv_files:
    if file == 'data.csv':
        data_csv = file
        data_csv_path = os.path.join(data_folder, data_csv)

data_df = pd.read_csv(data_csv_path)


def find_highest_risk(df):
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
    return dominant_risk_data


highest_risk_data = find_highest_risk(data_df)
dominant_risk_data = find_dominant_risk_type(
    data_df, 
    [
        'earthquake_risk',
        'flood_risk'
    ]
)


app_ui = ui.page_navbar(
    ui.nav_spacer(),
    ui.nav_panel(
        "Atlas",
        ui.page_fluid(
            ui.layout_columns(
                ui.value_box(
                    "Object at highest risk",
                    f"{highest_risk_data['name']}",
                    f"Total risk: {highest_risk_data['total_risk']}",
                    showcase=faicons.icon_svg("triangle-exclamation")
                ),
                ui.value_box(
                    "Dominant risk on average",
                    f"{dominant_risk_data['dominant_risk']}",
                    f"Average value: {dominant_risk_data['avg_risk_value']}",
                    showcase=faicons.icon_svg("radiation")
                ),
                col_widths=(6, 6)
            ),
            ui.layout_columns(
                ui.card(
                    output_widget("map"),
                    height="1000px"
                ),
            ),
            ui.layout_columns(
                ui.card(
                    output_widget("plot"),
                ),
            )
        ),
    ),
    ui.nav_panel(
        "Data",
        ui.page_fluid(
            ui.layout_columns(
                ui.card(
                    ui.card_header(
                        'Object data',
                        ui.download_button("download_object_data", "Download"),
                    ),
                    ui.output_data_frame("object_data_df"),
                ),
                ui.card(
                    ui.card_header('Earthquake data'),
                    ui.output_data_frame("earthquake_data_df"),
                    ui.card_footer(
                        ui.download_button("download_earthquake_data", "Download"),
                    ),
                ),
                ui.card(
                    ui.card_header('Flood data'),
                    ui.output_data_frame("flood_data_df"),
                    ui.card_footer(
                        ui.download_button("download_flood_data", "Download"),
                    ),
                ),
                col_widths=(12)
            )
        )
    ),
    title=a(
        "SIRIUS", 
        href="https://site.unibo.it/patrimonioculturalearischio/en/risk-atlas/explore-the-atlas-1",
        target="_blank"
        ),
    fillable=True,
    sidebar=ui.sidebar(
            "Data",
            *[ui.input_checkbox(f"file_{i}", csv_file) for i, csv_file in enumerate(csv_files)],
            bg="#f8f8f8"
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



# Create app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()