import faicons
from shiny import ui
from htmltools import a
from shinywidgets import output_widget
import data
import data_utils

data_df = data.get_data()
highest_risk_data = data_utils.find_highest_risk(data_df)
dominant_risk_data = data_utils.find_dominant_risk_type(data_df, ['earthquake_risk', 'flood_risk'])

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
        "Layers",
        *[ui.input_checkbox(f"file_{i}", shape_file) for i, shape_file in enumerate(data.get_polygons())],
        bg="#f8f8f8"
    ),
)
