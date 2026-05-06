import pytest
from fastapi import HTTPException
from firerisk.api.routers.auth import has_roles
from firerisk.api.routers.auth import get_user_info
from firerisk.api.routers.auth import get_payload
from src.firerisk.api.schemas.userPayload import userPayload
from unittest.mock import patch

@pytest.mark.asyncio
async def test_has_roles():

    user = userPayload(
        id ="1",
        username = "test",
        email ="test@test.com",
        first_name = "Test",
        last_name = "User",
        realm_roles = ["admin"]    
    )

    checker = has_roles(["admin"])
    
    result = await checker(user)

    assert result == user

@pytest.mark.asyncio
async def test_has_roles_forbidden():

    user = userPayload(
        id ="1",
        username = "test",
        email ="test@test.com",
        first_name = "Test",
        last_name = "User",
        realm_roles = ["developer"]    
    )

    checker = has_roles(["admin"])
    
    with pytest.raises(HTTPException) as exc:
        await checker(user)

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_user_info_success():
    payload = {
        "sub": "1",
        "preferred_username": "test",
        "email": "test@test.com",
        "given_name": "Test",
        "family_name": "User",
        "realm_access": {"roles": ["admin"]},
    }

    result = await get_user_info(payload)

    assert result.username == "test"
    assert "admin" in result.realm_roles


@pytest.mark.asyncio
async def test_get_user_info_failure():
    payload = None  # invalid

    with pytest.raises(HTTPException):
        await get_user_info(payload)




@pytest.mark.asyncio
async def test_get_payload_success():
    fake_payload = {"sub": "1"}

    with patch("firerisk.api.routers.auth.keycloak_openid.decode_token") as mock_decode:
        mock_decode.return_value = fake_payload

        result = await get_payload("fake_token")

        assert result == fake_payload

@pytest.mark.asyncio
async def test_get_payload_failure():
    with patch("firerisk.api.routers.auth.keycloak_openid.decode_token") as mock_decode:
        mock_decode.side_effect = Exception("invalid token")

        with pytest.raises(HTTPException) as exc:
            await get_payload("bad_token")

        assert exc.value.status_code == 401