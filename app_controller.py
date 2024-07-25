# app_controller.py
from shiny import ui, App, render
from shinywidgets import render_widget
from app_map import MapManager
from app_data import DataManager
from app_ui import UIManager
from ipyleaflet import Map

class AppController:
    def __init__(self):
        self.data_manager = DataManager()
        self.map_manager = MapManager()
        self.ui_manager = UIManager()

    def ui(self, request=None):
        return self.ui_manager.create_ui()

    def server(self, input, output, session):

        @render.text
        def text_output():
            data = self.data_manager.get_data()
            return f"{data}"

        @render_widget
        def map():
            map = self.map_manager.create_map()
            return map

    def start_app(self):
        app = App(ui=self.ui, server=self.server)
        app.run()
