from htmltools import a
from shiny import ui
from shinywidgets import output_widget
import tomli


with open("config.toml", mode="rb") as fp:
    config = tomli.load(fp)


class UIManager:
    

    def create_ui(self):
        app_ui = ui.page_navbar(
            ui.nav_spacer(),
            ui.nav_panel(
                config["app"]["nav_panel_01"]["title"],
                ui.page_fluid(
                    ui.layout_columns(
                        output_widget("map"),
                        ui.layout_columns(
                            ui.row(
                                ui.column(12, 
                                    ui.output_ui("value_boxes")
                                ),
                            ),
                        ),
                    col_widths=(8, 4)
                    ),
                    ui.output_plot("plot"),
                )
            ),
            ui.nav_panel(
                config["app"]["nav_panel_02"]["title"],
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
                config["app"]["title"], 
                href=config["app"]["href"],
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
