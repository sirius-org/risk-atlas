import os, faicons
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
    ui.nav_panel(
        "Atlas",
        ui.page_fillable(
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
                    full_screen=True
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
        ui.page_fillable(
            ui.layout_columns(
                ui.card(
                    'todo'
                ),
                '''*[
                    ui.card(
                        csv_file,
                        ui.output_data_frame(f"{csv_file.split('.')[0]}_df")
                    ) for csv_file in csv_files
                ],'''
            )
        )
    ),
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
        
        for file in selected_files():
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


    '''# Create a dynamic render function for each CSV file
    for csv_file in csv_files:
        def make_render_function(file_name):
            @render.data_frame
            def dynamic_df():
                file_path = os.path.join(data_folder, file_name)
                df = pd.read_csv(file_path)
                return render.DataTable(df)
            return dynamic_df

        render_func = make_render_function(csv_file)
        setattr(output, f"{csv_file.split('.')[0]}_df", render_func)'''


# Create app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()