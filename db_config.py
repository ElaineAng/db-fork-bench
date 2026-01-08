# db_config.py
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def get_dolt_connection():
    connection = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="password",
        database="dolt_data"
    )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return connection