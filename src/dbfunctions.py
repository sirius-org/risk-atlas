import duckdb
import bcrypt
import geopandas as gpd
import os
import sys
from shapely import wkt
from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime


def check_login(username, password, db_path="users.duckdb"):
    conn = duckdb.connect(db_path)

    result = conn.execute("""
    SELECT password_hash 
    FROM users
    WHERE username = ?
    """, (username,)).fetchone()

    if result and bcrypt.checkpw(password.encode(), result[0].encode()):
        return True
    return False


def add_geodataframe(file_path, db_path="users.duckdb"):
    conn = duckdb.connect(db_path)
    table_name = os.path.basename(file_path).replace('.shp', '')
    table_name_quoted = f'"{table_name}"'
    gdf = gpd.read_file(file_path)
    if "geometry" in gdf.columns:
        gdf["geometry"] = gdf["geometry"].apply(lambda geom: geom.wkt if isinstance(geom, object) else geom)
    else:
        print("No geometry column found")
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name_quoted} AS
        SELECT * FROM gdf
    """)
    conn.commit()


def get_table_names(db_path="users.duckdb"):
    conn = duckdb.connect(db_path)
    result = conn.execute("""
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'geometry'
        AND table_schema = 'main'    
    """).fetchall()
    table_names = [row[0] for row in result]
    conn.close()
    return table_names


def get_geospatial_data(table_name, db_path="users.duckdb"):
    conn = duckdb.connect(db_path)
    query = f"""
        SELECT * FROM '{table_name}'
    """
    result = conn.execute(query).fetchall()
    columns = [col[0] for col in conn.description]
    gdf = gpd.GeoDataFrame(result, columns=columns)
    if "geometry" in gdf.columns:
        gdf["geometry"] = gdf["geometry"].apply(wkt.loads)
        gdf.set_geometry("geometry", inplace=True)
        if gdf.crs != 4326:
            gdf.set_crs(32632, allow_override=True, inplace=True)
            gdf = gdf.to_crs(4326)
    conn.close()
    return gdf.to_json()


def build_query(entity_id):
    return f"""
        SELECT ?label ?alt_label ?description ?latitude ?longitude ?date ?official_site ?viaf ?property WHERE {{
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
                ?inceptionValue wikibase:timeValue ?date .
            }}
            OPTIONAL {{ wd:{entity_id} wdt:P856 ?official_site }}
            OPTIONAL {{ wd:{entity_id} wdt:P214 ?viaf }}
            OPTIONAL {{ wd:{entity_id} wdt:P708 ?property }}
        }}
    """


def transform_to_dict(results):
    def process_item(d):
        new_result = {"date": "-"}
        for key, value in d.items():
            if key == "date":
                year = datetime.strptime(value["value"], "%Y-%m-%dT%H:%M:%SZ").year
                value["value"] = f"{year} BCE" if year < 0 else f"{year} CE"
            new_result[key] = value["value"]
        return new_result
    return [process_item(d) for d in results]


def get_entity_data(entity_id):
    query = build_query(entity_id)
    user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
    endpoint_url = "https://query.wikidata.org/sparql"
    
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.queryAndConvert()["results"]["bindings"]
    return transform_to_dict(results)


def add_object(entity_id, db_path="users.duckdb"):
    entity_data = get_entity_data(entity_id)
    if entity_data:
        conn = duckdb.connect(db_path)
        
        entity = entity_data[0]
        label_value = entity.get("label")
        alt_label_value = entity.get("alt_label")
        description_value = entity.get("description")
        date_value = entity.get("date")
        latitude_value = entity.get("latitude")
        longitude_value = entity.get("longitude")
        property_value = entity.get("property")
        official_site_value = entity.get("official_site")
        viaf_value = entity.get("viaf")
        
        if entity_id and label_value:
            
            conn.execute('''
            INSERT OR IGNORE INTO objects (
                id, wikidata_id, label, alt_label, description, date, latitude, longitude, property, official_site, viaf
            ) VALUES (nextval('seq_id'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entity_id,
                label_value,
                alt_label_value or None,
                description_value or None,
                date_value or None,
                latitude_value or None, 
                longitude_value or None, 
                property_value or None, 
                official_site_value or None, 
                viaf_value or None
            ))
            print(f"Added object: {entity_id} with label: {label_value}")
            conn.commit()
            conn.close()
        else:
            print(f"Missing data for entity {entity_id}.")


def get_objects(db_path="users.duckdb"):
    conn = duckdb.connect(db_path)
    result = conn.execute("SELECT * FROM objects").fetchdf()
    conn.close()
    return result
