import os
from dotenv import load_dotenv

load_dotenv()

PGDB_HOST = os.getenv("PGDB_HOST")
PGDB_PORT = os.getenv("PGDB_PORT")
PGDB_USERNAME = os.getenv("PGDB_USERNAME")
PGDB_PASSWORD = os.getenv("PGDB_PASSWORD")
PGDB_DB = os.getenv("PGDB_DB")

DATABASE = {
    'drivername': 'postgresql+psycopg2',
    'host': PGDB_HOST,
    'port': PGDB_PORT,
    'username': PGDB_USERNAME,
    'password': PGDB_PASSWORD,
    'database': PGDB_DB,
    'query': {}
}

