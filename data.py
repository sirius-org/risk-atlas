import os, sys
import pandas as pd
from typing import List, Dict
from SPARQLWrapper import SPARQLWrapper, JSON
from wikidata.client import Client
from datetime import datetime


def get_data():
    data_folder = 'data'
    data_csv_path = os.path.join(data_folder, 'data.csv')
    data_df = pd.read_csv(data_csv_path)
    return data_df


def get_polygons():
    base_folder ='data/polygons'
    shape_files = []
    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        for file in os.listdir(folder_path):
            if file.endswith('.shp'):
                shape_files.append(file)
    return shape_files


def get_wikidata_entities(entity_id):
    """
    This function takes a name and returns the Wikidata entities for that name.
    
    Args:
    row_name (str): The name to search for in Wikidata.
    
    Returns:
    list: A list of Wikidata entities related to the name.
    """
    query = f"""
        SELECT ?label ?description ?latitude ?longitude ?date_created ?official_site ?viaf WHERE {{
            wd:{entity_id} rdfs:label ?label .
            FILTER (LANG(?label) = "en")
            OPTIONAL {{ wd:{entity_id} schema:description ?description . FILTER (LANG(?description) = "en") }}
            OPTIONAL {{
                wd:{entity_id} p:P625 ?coordinate .
                ?coordinate psv:P625 ?coordinateValue .
                ?coordinateValue wikibase:geoLatitude ?latitude .
                ?coordinateValue wikibase:geoLongitude ?longitude .
            }}
            OPTIONAL {{
                wd:{entity_id} p:P571 ?inception .
                ?inception psv:P571 ?inceptionValue .
                ?inceptionValue wikibase:timeValue ?date_created .
            }}
            OPTIONAL {{ wd:{entity_id} wdt:P856 ?official_site }}
            OPTIONAL {{ wd:{entity_id} wdt:P214 ?viaf }}
    }}
    """
    data_extracter = WikiDataQueryResults(query)
    df = data_extracter.load_as_dict()
    df['id'] = entity_id
    return df


class WikiDataQueryResults:
    """
    A class that can be used to query data from Wikidata using SPARQL and return the results as a Pandas DataFrame or a list
    of values for a specific key.
    """
    def __init__(self, query: str):
        """
        Initializes the WikiDataQueryResults object with a SPARQL query string.
        :param query: A SPARQL query string.
        """
        self.user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        self.endpoint_url = "https://query.wikidata.org/sparql"
        self.sparql = SPARQLWrapper(self.endpoint_url, agent=self.user_agent)
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)

    def __transform2dict(self, result: List[Dict]) -> Dict:
        """
        Helper function to transform SPARQL query results into a list of dictionaries.
        :param results: A list of query results returned by SPARQLWrapper.
        :return: A list of dictionaries, where each dictionary represents a result row and has keys corresponding to the
        variables in the SPARQL SELECT clause.
        """
        new_result = {
            'date_created': '-'
        }
        for d in result:
            for key, value in d.items():
                if key == 'date_created':
                    year = datetime.strptime(value['value'], '%Y-%m-%dT%H:%M:%SZ').year
                    if year < 0:
                        value['value'] = f"{year} BCE"
                    else:
                        value['value'] = f"{year} CE"
                new_result[key] = value['value']
        return new_result

    def load_as_dict(self) -> Dict:
        """
        Helper function that loads the data from Wikidata using the SPARQLWrapper library, and transforms the results into
        a list of dictionaries.
        :return: A list of dictionaries, where each dictionary represents a result row and has keys corresponding to the
        variables in the SPARQL SELECT clause.
        """
        results = self.sparql.queryAndConvert()['results']['bindings']
        results = self.__transform2dict(results)
        return results