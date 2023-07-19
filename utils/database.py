from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE = {
    'drivername': 'postgresql+psycopg2',
    'host': 'spbtennisfree.ru',
    'port': '5433',
    'username': 'backup_user',
    'password': 'qs2ReJDVky',
    'database': 'postgres',
    'query': {}
}

engine = create_engine(URL(**DATABASE), echo=False)
# expire_on_commit=False will prevent attributes from being expired after commit.
engine.connect()

Session = sessionmaker(bind=engine, expire_on_commit=False)
session = Session()

Base = declarative_base()

