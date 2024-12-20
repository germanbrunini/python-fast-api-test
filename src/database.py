import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# --------- Configuration ---------
HOST = 'localhost'
PT = '5433'
DBN = 'postgres'
USER = 'postgres'
PASS = 'germanpostgres1'
# Define your connection parameters
DB_DSN = f'host={HOST} port={PT} dbname={DBN} user={USER} password={PASS}'

DATABASE_URL = f'postgresql+psycopg2://{USER}:{PASS}@{HOST}:{PT}/{DBN}'


# Create the database engine
engine = create_engine(DATABASE_URL, echo=False)


# Define the base class for your models
class Base(DeclarativeBase):
    pass


# Create a session factory bound to this engine
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
