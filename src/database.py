from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import config

engine = create_engine(config['database']['uri'])
dbsession = sessionmaker(bind=engine)
Base = declarative_base()

def init():
	Base.metadata.create_all(engine)
