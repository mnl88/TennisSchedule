from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE

engine = create_engine(URL(**DATABASE), echo=False)
# expire_on_commit=False will prevent attributes from being expired after commit.
engine.connect()

Session = sessionmaker(bind=engine, expire_on_commit=False)
# session = Session()

Base = declarative_base()

