import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

TIMESCALE_USER = os.getenv("TIMESCALE_USER", "defaultuser")
TIMESCALE_PASSWORD = os.getenv("TIMESCALE_PASSWORD", "defaultpassword")
TIMESCALE_DB = os.getenv("TIMESCALE_DATABASE", "defaultdb")
TIMESCALE_HOST = os.getenv("TIMESCALE_HOST", "localhost")
TIMESCALE_PORT = os.getenv("TIMESCALE_PORT", "5432")
TIMESCALE_SCHEMA = os.getenv("TIMESCALE_SCHEMA", "public")

print(f"TimescaleDB config: user={TIMESCALE_USER}, db={TIMESCALE_DB}, host={TIMESCALE_HOST}, port={TIMESCALE_PORT}, schema={TIMESCALE_SCHEMA}")


SQLALCHEMY_DATABASE_URL = f"postgresql://{TIMESCALE_USER}:{TIMESCALE_PASSWORD}@{TIMESCALE_HOST}:{TIMESCALE_PORT}/{TIMESCALE_DB}"

metadata = MetaData(schema=TIMESCALE_SCHEMA)

TIMESCALE_Base = declarative_base(metadata=metadata)

TIMESCALE_engine = create_engine(SQLALCHEMY_DATABASE_URL)

TIMESCALE_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TIMESCALE_engine)