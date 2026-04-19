import pytest
from fastapi import HTTPException
from firerisk.api.routers.auth import has_roles
from src.firerisk.api.schemas.userPayload import userPayload

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