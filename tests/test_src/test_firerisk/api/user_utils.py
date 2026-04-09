from fastapi.testclient import TestClient
from src.firerisk.api.main import app
from src.firerisk.api.routers.auth import get_user_info
from src.firerisk.api.schemas.userPayload import userPayload

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

client = TestClient(app)
