import os
import pandas as pd
import folium
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import ipyleaflet as L

# Get list of CSV files in the "data" folder
data_folder = 'data'
csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]


app_ui = ui.page_sidebar(  
    ui.sidebar(
        "Select CSV Files",
        *[ui.input_checkbox(f"file_{i}", csv_file) for i, csv_file in enumerate(csv_files)],
        bg="#f8f8f8"
    ),  
    ui.card(
        ui.card_header("Map"),
        output_widget("map"),
    ) 
)


# Define server logic
def server(input, output, session):

    @reactive.Calc
    def selected_files():
        # Get selected files
        selected = [csv_files[i] for i in range(len(csv_files)) if input[f"file_{i}"]()]
        return selected
    
    @render_widget
    def map():
        m = L.Map(
            zoom=14, 
            center=(44.4183598, 12.2035294)
        )

        # Add data points or polygons based on selected files
        for file in selected_files():
            file_path = os.path.join(data_folder, file)
            df = pd.read_csv(file_path)

            if file == 'data.csv':
                for _, row in df.iterrows():
                    m.add(
                        L.Marker(
                            location=(row['latitude'], row['longitude']),
                            draggable=False
                        )
                    )
            else:
                points = df[['latitude', 'longitude']].values.tolist()
                polygon = L.Polygon(
                    locations=points,
                    color="green",
                    fill_color="green"
                )
                m.add(polygon)
        
        control = L.LayersControl(position='topright')
        m.add(control)
        m.add(L.FullScreenControl())
        legend = L.LegendControl({"low":"#FAA", "medium":"#A55", "High":"#500"}, title="Legend", position="bottomright")
        m.add(legend)

        return m

# Create app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()