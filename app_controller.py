from shiny import ui, App, render, reactive
from shinywidgets import render_widget
from app_map import MapManager
from app_data import DataManager
from app_ui import UIManager
from app_plot import PlotManager
from ipyleaflet import Map


class AppController:

    def __init__(self):
        self.data_manager = DataManager()
        self.map_manager = MapManager()
        self.ui_manager = UIManager()
        self.plot_manager = PlotManager()

    def ui(self, request=None):
        return self.ui_manager.create_ui()

    def server(self, input, output, session):
        
        '''@reactive.Calc
        def get_selected_files():
            selected_files = [self.data_manager.get_shape_files()[i] for i in range(len(self.data_manager.get_shape_files())) if input[f"file_{i}"]()]
            print(selected_files)
            return selected_files'''

        @render_widget
        def map():
            map = self.map_manager.create_map()
            self.map_manager.add_markers(self.data_manager.get_entities())
            self.map_manager.add_layers(self.data_manager.get_layers())

            #shapes = self.data_manager.create_shapes(get_selected_files())
            #print(shapes)
            #if len(get_selected_files()) > 0:
            #    self.map_manager.
            #if len(self.data_manager.get_shapes()) > 0:
            #    for shape in self.data_manager.get_shapes():
            #        self.map_manager.add_layer(shape)
            return map

        @render.ui
        def layers():
            return ui.input_checkbox_group(
                "layer_checkboxes",
                label="Layers",
                choices={
                    f"{folder}": ui.span(f"{folder}") for folder in self.data_manager.get_folders()
                }
            )

        @render.plot
        def plot():
            plot = self.plot_manager.create_plot()
            return plot

        @render.data_frame
        def table():
            data = self.data_manager.get_data()
            return render.DataGrid(data, selection_mode="rows")

    def start_app(self):
        app = App(ui=self.ui, server=self.server)
        app.run()
