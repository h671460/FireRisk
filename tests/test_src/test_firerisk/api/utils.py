import os
from datetime import datetime, timezone
from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import pytest

from src.firerisk.api.main import app
from src.firerisk.api.routers.auth import get_user_info
from src.firerisk.api.routers.frcm_route import get_db
from src.firerisk.api.schemas.userPayload import userPayload
from src.firerisk.databases.timescale.database import TIMESCALE_Base
from src.firerisk.databases.timescale.models import FireRisk


from pathlib import Path

env_path = Path(".env")
if env_path.exists():
    load_dotenv(env_path)

TIMESCALE_USER = os.getenv("TEST_TIMESCALE_USER")
TIMESCALE_PASSWORD = os.getenv("TEST_TIMESCALE_PASSWORD")
TIMESCALE_DB = os.getenv("TEST_TIMESCALE_DATABASE")
TIMESCALE_HOST = os.getenv("TEST_TIMESCALE_HOST")
TIMESCALE_PORT = os.getenv("TEST_TIMESCALE_PORT")

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


def override_get_user_info_admin():
    return userPayload(
        id="test-user-id",
        username="testuser",
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        realm_roles=["admin", "default-roles-frcm-realm"],
    )


def override_get_user_info_developer():
    return userPayload(
        id="test-user-id",
        username="testuser",
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        realm_roles=["developer", "default-roles-frcm-realm"],
    )


def override_get_user_info_default():
    return userPayload(
        id="test-user-id",
        username="testuser",
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        realm_roles=["default-roles-frcm-realm"],
    )


def override_get_user_info_no_roles():
    return userPayload(
        id="test-user-id",
        username="testuser",
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        realm_roles=[],
    )


app.dependency_overrides[get_user_info] = override_get_user_info_admin
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


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