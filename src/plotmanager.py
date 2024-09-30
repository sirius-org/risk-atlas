import matplotlib.pyplot as plt
import io
import pandas as pd
import seaborn as sns
from shinywidgets import output_widget

class PlotManager:
    def __init__(self):
        self.plot = None
    
    def create_plot(self):
        fig, ax = plt.subplots()
        data = [
            {
                'name': 'Oggetto 1',
                'risk_type': 'earthquake_risk',
                'risk_value': 2
            },
            {
                'name': 'Oggetto 1',
                'risk_type': 'flood_risk',
                'risk_value': 6
            },
        ]
        df = pd.DataFrame(data)
        # IF NOT EMPTY
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(
            x='risk_value',
            y='name',
            hue='risk_type',
            data=df,
            palette={'earthquake_risk': 'brown', 'flood_risk': 'blue'})
            
        ax.set_title("Combined Risk Values")
        ax.set_xlabel("Risk Value")
        ax.set_ylabel("Object")
        self.plot = ax
        return self.plot
