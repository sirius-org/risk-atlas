import os
import pandas as pd


class DataManager:
    def __init__(self):
        self.data = self.load_data()

    def load_data(self):
        data_folder = 'data'
        data_csv_path = os.path.join(data_folder, 'data.csv')
        data = pd.read_csv(data_csv_path)
        return data

    def get_data(self):
        return self.data
