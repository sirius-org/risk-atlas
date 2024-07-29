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

        @render_widget
        def map():
            map = self.map_manager.create_map()
            self.map_manager.add_markers(self.data_manager.get_data())
            return map

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
