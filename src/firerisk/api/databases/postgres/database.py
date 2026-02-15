import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

try:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgrespass123")
    POSTGRES_DB = os.getenv("POSTGRES_DATABASE", "postgres_db")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres-db") 
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", "public")
except KeyError as e:
    raise KeyError(f"Environment variable {str(e)} is not set. Please set it before running the application.")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

metadata = MetaData(schema=POSTGRES_SCHEMA)

POSTGRES_Base = declarative_base(metadata=metadata)

POSTGRES_engine = create_engine(SQLALCHEMY_DATABASE_URL)

POSTGRES_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=POSTGRES_engine)