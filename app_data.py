import os, sys, json
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime

class DataManager:
    def __init__(self):
        self.data = self.load_data()
        #self.layers = self.load_layers()
        self.entities = self.load_entities()
        #self.folders = self.load_folders()

    def load_data(self):
        data_folder = 'data'
        data_csv_path = os.path.join(data_folder, 'data.csv')
        data = pd.read_csv(data_csv_path)
        return data

    def load_entities(self):
        entities = []
        for _, row in self.get_data().iterrows():
            entity = self.__get_entity(row["id"])
            row_dict = row.to_dict()
            entity.update(row_dict)
            entities.append(entity)
        return entities

    def __get_entity(self, entity_id):
        query = f"""
            SELECT ?label ?alt_label ?description ?latitude ?longitude ?date_created ?official_site ?viaf WHERE {{
                wd:{entity_id} rdfs:label ?label ;
                    skos:altLabel ?alt_label
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
        return df

    '''def load_folders(self):
        base_folder = 'data/polygons'
        
        return folders'''

    '''def load_layers(self):
        shape_files = []
        base_folder = 'data/polygons'
        shape_folder = self.load_folders()
        for folder_name in shape_folder:
            folder_path = os.path.join(base_folder, folder_name)
            files = [f for f in os.listdir(folder_path)]
            for file in files:
                if file.endswith('.shp'):
                    file_path = os.path.join(folder_path, file)
                    shape_files.append(file_path)
        return shape_files'''
    
    def get_entities(self):
        return self.entities

    def get_data(self):
        return self.data
    
    '''def get_layers(self):
        return self.layers'''

    '''def get_folders(self):
        return self.folders'''


class WikiDataQueryResults:
    def __init__(self, query: str):
        self.user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
        self.endpoint_url = "https://query.wikidata.org/sparql"
        self.sparql = SPARQLWrapper(self.endpoint_url, agent=self.user_agent)
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)

    def __transform2dict(self, result):
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

    def load_as_dict(self):
        results = self.sparql.queryAndConvert()['results']['bindings']
        results = self.__transform2dict(results)
        return results