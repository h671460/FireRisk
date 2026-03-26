import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

def must_get(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v

TIMESCALE_USER = must_get("TIMESCALE_USER")
TIMESCALE_PASSWORD = must_get("TIMESCALE_PASSWORD")
TIMESCALE_DB = must_get("TIMESCALE_DATABASE")
TIMESCALE_HOST = must_get("TIMESCALE_HOST")
TIMESCALE_PORT = must_get("TIMESCALE_PORT")
TIMESCALE_SCHEMA = os.getenv("TIMESCALE_SCHEMA", "public")

print(f"TimescaleDB config: user={TIMESCALE_USER}, db={TIMESCALE_DB}, host={TIMESCALE_HOST}, port={TIMESCALE_PORT}, schema={TIMESCALE_SCHEMA}")


SQLALCHEMY_DATABASE_URL = f"postgresql://{TIMESCALE_USER}:{TIMESCALE_PASSWORD}@{TIMESCALE_HOST}:{TIMESCALE_PORT}/{TIMESCALE_DB}"

metadata = MetaData(schema=TIMESCALE_SCHEMA)

TIMESCALE_Base = declarative_base(metadata=metadata)

TIMESCALE_engine = create_engine(SQLALCHEMY_DATABASE_URL)

TIMESCALE_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TIMESCALE_engine)