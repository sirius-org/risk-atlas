from shiny import ui, App, render
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
        
        @reactive.Calc
        def get_selected_files():
            return [shape_files[i] for i in range(len(shape_files)) if input[f"file_{i}"]()]

        @render_widget
        def map():
            map = self.map_manager.create_map()
            self.map_manager.add_markers(self.data_manager.get_entities())
            
            #if len(self.data_manager.get_shapes()) > 0:
            #    for shape in self.data_manager.get_shapes():
            #        self.map_manager.add_layer(shape)
            return map

        @render.ui
        def layers():
             return *[ui.input_checkbox(f"file_{i}", shape_file) for i, shape_file in enumerate(self.data_manager.get_shapes())]

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
