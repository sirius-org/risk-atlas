from shiny import ui
from shinywidgets import output_widget 

class UIManager:
    def create_ui(self):
        app_ui = ui.page_fluid(
            ui.layout_sidebar(
                ui.panel_sidebar(
                    ui.h3("Simple Shiny App"),
                    ui.input_action_button("update_button", "Update")
                ),
                ui.panel_main(
                    ui.output_text("text_output"),
                    output_widget("map")
                )
            )
        )
        return app_ui
