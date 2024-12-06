import duckdb
import bcrypt
import geopandas as gpd
import os
from shapely import wkt


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