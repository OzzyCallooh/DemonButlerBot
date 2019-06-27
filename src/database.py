import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative

from config import config

engine = sqlalchemy.create_engine(config['database']['uri'])
dbsession = sqlalchemy.orm.sessionmaker(bind=engine)
Base = sqlalchemy.ext.declarative.declarative_base()

def init():
	Base.metadata.create_all(engine)