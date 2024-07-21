import os
import pandas as pd

def get_data():
    data_folder = 'data'
    data_csv_path = os.path.join(data_folder, 'data.csv')
    data_df = pd.read_csv(data_csv_path)
    return data_df

def get_polygons():
    path ='data/polygons'
    shape_files = [f for f in os.listdir(path) if f.endswith('.shp')]
    return shape_files

def get_files():
    data_folder = 'data'
    csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    return csv_files