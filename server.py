import os, io
import pandas as pd
from shiny import render, reactive
from shinywidgets import render_widget, render_plotly
from ipywidgets.widgets.widget_string import HTML
import plotly.express as px
from data_utils import find_highest_risk, find_dominant_risk_type
from map_utils import get_color, create_map, add_polygon_layers
import data
import seaborn as sns
import matplotlib.pyplot as plt



data_folder = "data"
data_df = data.get_data()
shape_files = data.get_polygons()


def server(input, output, session):

    @reactive.Calc
    def get_selected_files():
        return [shape_files[i] for i in range(len(shape_files)) if input[f"file_{i}"]()]

    @render_widget
    def map():
        
        if len(get_selected_files()) > 0:
            polygons = add_polygon_layers(get_selected_files())
        else:
            polygons = []

        return create_map(polygons)
        
    
    @render.plot
    def plot():
        plot_data = []        
        base_folder = 'data/polygons'
        for file in get_selected_files():
            for folder_name in os.listdir(base_folder):
                folder_path = os.path.join(base_folder, folder_name)
                if os.path.isdir(folder_path):
                    if file in os.listdir(folder_path):
                        for _, row in data.get_data().iterrows():
                            type_risk = row.get(f'{folder_name}_risk', 0)
                            plot_data.append({
                                'name': row['name'],
                                'risk_type': f'{folder_name}_risk',
                                'risk_value': type_risk
                            })
        plot_df = pd.DataFrame(plot_data)
        if not plot_df.empty:
            plt.figure(figsize=(10, 6))
            ax = sns.barplot(
                x='risk_value',
                y='name',
                hue='risk_type',
                data=plot_df,
                palette={'earthquake_risk': 'brown', 'flood_risk': 'blue'})
                
            ax.set_title("Combined Risk Values")
            ax.set_xlabel("Risk Value")
            ax.set_ylabel("Object")
            return ax
