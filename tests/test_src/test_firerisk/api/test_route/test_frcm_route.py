from tests.test_src.test_firerisk.api.utils import (
    client,
    app,
    override_get_user_info_admin,
    override_get_user_info_no_roles,
    test_fire_risk,
)
from src.firerisk.api.routers.auth import get_user_info
from fastapi import status


# ---------------------------------------------------------------------------
# GET /frcm/
# ---------------------------------------------------------------------------
def test_read_last_100_authenticated(test_fire_risk):
    response = client.get("/frcm/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_read_last_100_forbidden():
    app.dependency_overrides[get_user_info] = override_get_user_info_no_roles
    response = client.get("/frcm/")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    app.dependency_overrides[get_user_info] = override_get_user_info_admin


# ---------------------------------------------------------------------------
# GET /frcm/range
# ---------------------------------------------------------------------------
def test_read_frcm_range_authenticated(test_fire_risk):
    response = client.get(
        "/frcm/range",
        params={
            "lat": 60.383,
            "lon": 5.3327,
            "start_time": "2026-03-27T12:00:00Z",
            "end_time": "2026-03-28T22:00:00Z",
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_read_frcm_range_forbidden():
    app.dependency_overrides[get_user_info] = override_get_user_info_no_roles
    response = client.get(
        "/frcm/range",
        params={
            "lat": 60.383,
            "lon": 5.3327,
            "start_time": "2026-03-27T12:00:00Z",
            "end_time": "2026-03-28T22:00:00Z",
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    app.dependency_overrides[get_user_info] = override_get_user_info_admin


def test_read_frcm_range_missing_params():
    response = client.get("/frcm/range")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT