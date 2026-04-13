from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pytest
from datetime import datetime, timezone
import os
from dotenv import load_dotenv


from src.firerisk.databases.timescale.database import TIMESCALE_Base
from tests.test_src.test_firerisk.api.user_utils import app
from src.firerisk.api.routers.frcm_route import get_db
from src.firerisk.databases.timescale.models import FireRisk
from pathlib import Path

env_path = Path(".env")
if env_path.exists():
    load_dotenv(env_path)

TIMESCALE_USER = os.getenv("TIMESCALE_USER", "testuser")
TIMESCALE_PASSWORD = os.getenv("TIMESCALE_PASSWORD", "testpassword")
TIMESCALE_DB = os.getenv("TIMESCALE_DATABASE", "testdb")
TIMESCALE_HOST = os.getenv("TIMESCALE_HOST", "localhost")
TIMESCALE_PORT = os.getenv("TIMESCALE_PORT", "5432")

SQLALCHEMY_DATABASE_URL = f"postgresql://{TIMESCALE_USER}:{TIMESCALE_PASSWORD}@{TIMESCALE_HOST}:{TIMESCALE_PORT}/{TIMESCALE_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TIMESCALE_Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
app.dependency_overrides[get_db] = override_get_db
@pytest.fixture
def test_fire_risk():
    fire_risk = FireRisk(
        time=datetime(2026, 3, 27, 12, 0, 0, tzinfo=timezone.utc),
        location="60.383,5.3327",
        lat=60.383,
        lon=5.3327,
        temperature=15.0,
        humidity=60.0,
        wind_speed=5.0,
        risk_score=0.45,
        risk_level="low",
    )

    db = TestingSessionLocal()
    db.add(fire_risk)
    db.commit()
    yield fire_risk
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM fire_risk;"))
        connection.commit()