import tomli, requests, zipfile, io, tempfile
import geopandas as gpd
from concurrent.futures import ThreadPoolExecutor, as_completed
import diskcache as dc
import pyogrio
import os
import cProfile, pstats, io
from pstats import SortKey
import json

with open("config.toml", mode="rb") as fp:
    config = tomli.load(fp)


class GeoDataManager():

    def __init__(self):
        self.data = self.load_data()

    def get_data(self):
        return self.data

    def load_data(self):
        geo_data = []
        for key in config["geo"]:
            geo_entry = config["geo"][key]
            shapefile_path = geo_entry["path"]
            name = geo_entry["name"]
            color = geo_entry["color"]
            gdf = gpd.read_file(shapefile_path)
            gdf_crs = gdf.to_crs(epsg=4326)
            geojson_data = json.loads(gdf_crs.to_json())
            geo_data.append({
                "name": name,
                "color": color,
                "geo_data": geojson_data
            })
        return geo_data
