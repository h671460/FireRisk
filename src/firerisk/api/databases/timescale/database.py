import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

try:
    TIMESCALE_USER = os.getenv("TIMESCALE_USER")
    TIMESCALE_PASSWORD = os.getenv("TIMESCALE_PASSWORD")
    TIMESCALE_DB = os.getenv("TIMESCALE_DATABASE")
    TIMESCALE_HOST = os.getenv("TIMESCALE_HOST") 
    TIMESCALE_PORT = os.getenv("TIMESCALE_PORT")
    TIMESCALE_SCHEMA = os.getenv("TIMESCALE_SCHEMA")
except KeyError as e:
    raise KeyError(f"Environment variable {str(e)} is not set. Please set it before running the application.")

SQLALCHEMY_DATABASE_URL = f"postgresql://{TIMESCALE_USER}:{TIMESCALE_PASSWORD}@{TIMESCALE_HOST}:{TIMESCALE_PORT}/{TIMESCALE_DB}"

metadata = MetaData(schema=TIMESCALE_SCHEMA)

TIMESCALE_Base = declarative_base(metadata=metadata)

TIMESCALE_engine = create_engine(SQLALCHEMY_DATABASE_URL)

TIMESCALE_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TIMESCALE_engine)