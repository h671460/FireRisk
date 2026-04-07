from tests.test_src.test_firerisk.api.utils import (
    client,
    app,
    override_get_user_info_admin,
    override_get_user_info_developer,
    override_get_user_info_default,
    override_get_user_info_no_roles,
)
from src.firerisk.api.routers.auth import get_user_info
from fastapi import status


def test_secure_authenticated():
    response = client.get("/user/secure")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello testuser!"}


def test_admin_authenticated():
    response = client.get("/user/admin")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"
    assert response.json()["id"] == "test-user-id"
    assert "admin" in response.json()["realm_roles"]


def test_admin_forbidden():
    app.dependency_overrides[get_user_info] = override_get_user_info_no_roles
    response = client.get("/user/admin")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    app.dependency_overrides[get_user_info] = override_get_user_info_admin


def test_developer_authenticated():
    app.dependency_overrides[get_user_info] = override_get_user_info_developer
    response = client.get("/user/developer")
    assert response.status_code == status.HTTP_200_OK
    assert "developer" in response.json()["realm_roles"]
    app.dependency_overrides[get_user_info] = override_get_user_info_admin


def test_developer_forbidden():
    app.dependency_overrides[get_user_info] = override_get_user_info_no_roles
    response = client.get("/user/developer")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    app.dependency_overrides[get_user_info] = override_get_user_info_admin


def test_default_authenticated():
    app.dependency_overrides[get_user_info] = override_get_user_info_default
    response = client.get("/user/default")
    assert response.status_code == status.HTTP_200_OK
    assert "default-roles-frcm-realm" in response.json()["realm_roles"]
    app.dependency_overrides[get_user_info] = override_get_user_info_admin


def test_default_forbidden():
    app.dependency_overrides[get_user_info] = override_get_user_info_no_roles
    response = client.get("/user/default")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    app.dependency_overrides[get_user_info] = override_get_user_info_admin