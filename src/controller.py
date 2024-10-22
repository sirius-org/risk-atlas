from shiny import ui, App, render, reactive
from shinywidgets import render_widget
from src.mapmanager import MapManager
from src.datamanager import DataManager
from src.uimanager import UIManager
from src.plotmanager import PlotManager
from ipyleaflet import Map
import tomli


with open("config.toml", mode="rb") as fp:
    config = tomli.load(fp)


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
        def get_selected_layers():
            layer_group = self.map_manager.generate_layers()
            layers = layer_group.layers
            selected_layers = [layers[i] for i in range(len(layers)) if input[f"file_{i}"]()]
            self.map_manager.active_layers = selected_layers
            return selected_layers        


        @render_widget
        def map():
            map = self.map_manager.create_map()
            entities = self.data_manager.get_entities()
            layers = get_selected_layers()
            markers = self.map_manager.generate_markers(entities)
            self.map_manager.add_markers(markers)
            if layers:
                self.map_manager.add_active_layers(layers)
                self.map_manager.update_markers(markers)
                
                self.map_manager.update_value_boxes(input.box_1)
            
            return map

        @render.ui
        def layers():
            layers = [ui.input_checkbox(f"file_{i}", risk) for i, risk in enumerate(config["risk"]["risks"])]
            return layers
        
        @render.ui
        def value_boxes():
            return [ui.value_box(title, 0, id=f"box_{i}") for i, title in enumerate(config["app"]["nav_panel_01"]["value_boxes"])]

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
