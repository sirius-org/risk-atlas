from htmltools import a
from shiny import ui
from shinywidgets import output_widget 

class UIManager:
    def create_ui(self):
        app_ui = ui.page_navbar(
            ui.nav_spacer(),
            ui.nav_panel(
                "Risk Atlas",
                ui.page_fluid(
                    ui.layout_columns(
                        output_widget("map"),
                        ui.layout_columns(
                            ui.row(
                                ui.column(12, 
                                    ui.value_box(
                                        "Object at highest risk",
                                        "VALUE",
                                        "blblblb"
                                        #f"{highest_risk_data['name']}",
                                        #f"Total risk: {highest_risk_data['total_risk']}",
                                    ),
                                    ui.value_box(
                                        "Dominant risk on average",
                                        "VALUE",
                                        "blblblb"
                                        #f"{dominant_risk_data['dominant_risk']}",
                                        #f"Average value: {dominant_risk_data['avg_risk_value']}",
                                    ),
                                    ui.value_box(
                                        "Number of objects affected",
                                        "VALUE",
                                        "blblblb"
                                        #f"{highest_risk_data['name']}",
                                        #f"Total risk: {highest_risk_data['total_risk']}",
                                    ),
                                ),
                            ),
                        ),
                    col_widths=(8, 4)
                    ),
                    ui.output_plot("plot"),
                )
            ),
            ui.nav_panel(
                "Data",
                ui.page_fluid(
                    ui.card(
                        ui.layout_columns(
                            ui.output_data_frame("table"),
                            ui.p("quale rischio maggiore con punteggio"),
                            ui.p("cosa implica il punteggio"),
                            col_widths=[6, 3, 3]
                        ),
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
                "title sidebar",
                ui.output_ui("layers"),
                bg="#f8f8f8",
                open="always",
            ),
        )
        return app_ui
