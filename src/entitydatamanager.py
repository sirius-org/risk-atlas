import os, sys, json, tomli
from datetime import datetime
from SPARQLWrapper import SPARQLWrapper, JSON


with open("config.toml", mode="rb") as fp:
    config = tomli.load(fp)


class EntityDataManager():

    def __init__(self):
        self.data = self.load_data()

    def get_data(self):
        return self.data

    def load_data(self):
        identifiers = config["entity"]["entities"]
        values_clause = "VALUES ?entity { " + " ".join([f'wd:{identifier}' for identifier in identifiers]) + " }"
        query_template = config["entity"]["query"]
        query = query_template.replace("VALUES_CLAUSE", values_clause)
        results = self.request_data(query)
        return results

    def request_data(self, query):
        endpoint_url = config["entity"]["endpoint_url"]
        user_agent_template = config["entity"]["user_agent"]
        user_agent = eval(f"f'''{user_agent_template}'''")
        data_extractor = SPARQLWrapper(endpoint_url, agent=user_agent)
        data_extractor.setQuery(query)
        data_extractor.setReturnFormat(JSON)
        results = data_extractor.queryAndConvert()['results']['bindings']
        return results

