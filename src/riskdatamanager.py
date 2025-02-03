import os, sys, json, tomli


with open("config.toml", mode="rb") as fp:
    config = tomli.load(fp)


class RiskDataManager():

    def __init__(self):
        self.data = self.load_data()

    def get_data(self):
        return self.data

    def load_data(self):
        pass