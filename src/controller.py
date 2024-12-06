from shiny import ui, App, render, reactive
from shinywidgets import render_widget
from src.mapmanager import MapManager
from src.datamanager import DataManager
from src.uimanager import UIManager
from src.plotmanager import PlotManager
from src.entitydatamanager import EntityDataManager
from ipyleaflet import Map
import tomli
from src.dbfunctions import check_login, add_geodataframe, get_table_names, get_geospatial_data
import tempfile
import zipfile
import shutil
import os


with open("config.toml", mode="rb") as fp:
    config = tomli.load(fp)


class AppController:

    def __init__(self):
        #
        self.data_manager = DataManager()
        self.entity_data_manager = EntityDataManager()
        self.map_manager = MapManager()
        self.ui_manager = UIManager()
        self.plot_manager = PlotManager()

    def ui(self, request=None):
        return self.ui_manager.create_ui()


    def server(self, input, output, session):
        status_message = reactive.Value("")
        logged_in = reactive.Value(False)
        username = reactive.Value("")

        @reactive.Effect
        @reactive.event(input.login_button)
        def check_credentials():
            username_input = input.username()
            password_input = input.password()

            if not username_input or not password_input:
                status_message.set("Please enter both username and password.")
            else:
                if check_login(username_input, password_input):
                    username.set(username_input)
                    logged_in.set(True)
                    status_message.set("Login successful.")
                else:
                    status_message.set("Invalid username or password.")

        @reactive.Effect
        @reactive.event(input.logout_button)
        def logout():
            logged_in.set(False)
            username.set("")
            status_message.set("Logged out successfully.")

        @output
        @render.ui
        def login_content():
            if logged_in():
                return ui.layout_columns(
                    ui.card(
                        ui.card_header("Geographical data"),
                        ui.input_file(
                            "geodata_upload",
                            "Upload data",
                            accept=[".zip"],
                            multiple=False
                        ),
                        ui.input_action_button(
                            "geodata_upload_button", 
                            "Process data"),
                    ),
                    ui.card(
                        ui.input_select("object_select", "Object", config["entity"]["entities"]),
                        ui.input_text("author", "Author"),
                    ),
                    ui.card(
                        ui.card_header("Context"),
                        ui.layout_column_wrap(
                            ui.input_action_button("add_activity", "Add activity"),
                        )
                    ),
                    
                    ui.input_action_button("logout_button", "Logout"),
                    
                    col_widths=12
                )
            else:
                return ui.layout_columns(
                    ui.input_text("username", "Username", ""),
                    ui.input_password("password", "Password", ""),
                    ui.input_action_button("login_button", "Login")
                )

        
        activity_block_counter = reactive.Value(0)
        #activity_observations = reactive.Value({})
        @reactive.Effect
        @reactive.event(input.add_activity)
        def add_activity_block():
            current_block = activity_block_counter()
            ui.insert_ui(
                ui.card(
                    ui.card_header(f"activity-{current_block}"),
                    ui.input_selectize(f"activity_type_{current_block}", "Activity type", ["Blalla", "Blolososososo"]),
                    ui.input_text_area(f"activity_description_{current_block}", "Activity description"),
                    ui.input_selectize(f"previous_activity_{current_block}", "Previous activity", ["Act1", "Act2"]),
                    ui.row(
                        ui.input_action_button(f"add_observation_{current_block}", "Add observation", class_="btn-success"),
                        ui.input_action_button(f"remove_activity_{current_block}", "Remove activity", class_="btn-danger")
                    ),
                    id=f"activity_{current_block}",
                ),
                selector="#add_activity",
                where="beforeBegin",
            )

            #activity_observations.set({**activity_observations(), current_block: []})
            activity_block_counter.set(current_block + 1)
            
            observation_block_counter = reactive.Value(0)
            @reactive.Effect
            @reactive.event(input[f"add_observation_{current_block}"])
            def add_observation():
                observation_id = observation_block_counter()
                ui.insert_ui(
                    ui.card(
                        ui.card_header(f"observation-{observation_id}"),
                        ui.input_text_area(f"observation_text_{current_block}_{observation_id}", "Observation details"),
                        ui.input_action_button(f"remove_observation_{current_block}_{observation_id}", "Remove observation", class_="btn-danger"),
                        id=f"observation_{current_block}_{observation_id}"
                    ),
                    selector=f"#add_observation_{current_block}",
                    where="beforeBegin",
                )
                observation_block_counter.set(observation_id + 1)

                @reactive.Effect
                @reactive.event(input[f"remove_observation_{current_block}_{observation_id}"])
                def remove_observation():
                    ui.remove_ui(selector=f"#observation_{current_block}_{observation_id}")

            @reactive.Effect
            @reactive.event(input[f"remove_activity_{current_block}"])
            def remove_activity_block():
                ui.remove_ui(selector=f"#activity_{current_block}")
        

        uploaded_file = reactive.Value(None)
        @reactive.Effect
        @reactive.event(input.geodata_upload_button)
        def process_file():
            file = input.geodata_upload()
            if file:
                zip_file_path = file[0]["datapath"]
                with tempfile.TemporaryDirectory() as temp_dir:
                    try:
                        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                            zip_ref.extractall(temp_dir)
                        file_path = None
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                if file.endswith(".shp"):
                                    file_path = os.path.join(root, file)
                                    break
                            if file_path:
                                break
                        if file_path:
                            add_geodataframe(file_path)
                            print("File processed and added to the database successfully!")
                    except Exception as e:
                        print(f"Error processing file.")
            else:
                print("No file uploaded.")


        selected_layers = reactive.Value([])
        @reactive.Effect
        @reactive.event(input.update_map_button)
        async def update_map():
            with ui.Progress(min=0, max=100) as p:
                p.set(message="Initializing", detail="Loading layers...")
                
                layers = []
                num_tables = len(get_table_names())

                for i, table_name in enumerate(get_table_names()):
                    p.set(i * 100 // num_tables, message=f"Processing {table_name}")
                    if input[f"file_{i}"]():
                        geo_data = get_geospatial_data(table_name)
                        layers.append(geo_data)
                selected_layers.set(layers)
                if layers:
                    p.set(100, message="Rendering map...", detail="Finished loading layers.")
                    self.map_manager.update_map(layers)
                else:
                    p.set(100, message="No layers to render.", detail="Clearing map.")
                    self.map_manager.clear_map()       


        @render_widget
        def map():
            map = self.map_manager.create_map()
            entities = self.data_manager.get_entities()
            #entities = self.entity_data_manager.data
            markers = self.map_manager.generate_markers(entities)
            self.map_manager.add_markers(markers)
            #layers = get_selected_layers()
            #if layers:
                #self.map_manager.add_active_layers(layers)
                
                #self.map_manager.update_markers(markers)
                
                #self.map_manager.update_value_boxes(input.box_1)
            
            return map

        @render.ui
        def layers():
            tables = get_table_names()
            checkboxes = [ui.input_checkbox(f"file_{i}", table) for i, table in enumerate(tables)]
            return *checkboxes, ui.input_action_button("update_map_button", "Update Map")
        
        
        @render.ui
        def value_boxes():
            boxes = [ui.column(4, ui.value_box(title, 0, id=f"box_{i}")) for i, title in enumerate(config["app"]["nav_panel_01"]["value_boxes"])]
            return ui.row(*boxes)

        @render.plot
        def plot():
            plot = self.plot_manager.create_plot()
            return plot

        @render.data_frame
        def table():
            data = self.data_manager.get_data()
            return render.DataGrid(data, selection_mode="rows")


        '''@reactive.Calc
        def get_selected_layers():
            layer_group = self.map_manager.generate_layers()
            layers = layer_group.layers
            selected_layers = [layers[i] for i in range(len(layers)) if input[f"file_{i}"]()]
            self.map_manager.active_layers = selected_layers
            return selected_layers'''