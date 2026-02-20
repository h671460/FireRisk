from fastapi import APIRouter, Depends

from src.firerisk.api_keycloak.routers.auth import get_user_info, has_roles
from src.firerisk.api_keycloak.schemas.userPayload import userPayload


router = APIRouter(
    prefix="/user", 
    tags=["user"]
)


@router.get("/secure")
async def root(user: userPayload = Depends(get_user_info)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message": f"Hello {user.username}!"}


@router.get("/admin")
async def admin(user: userPayload = Depends(has_roles(["admin"]))):
    return user.to_dict()

@router.get("/developer")
async def developer(user: userPayload = Depends(has_roles(["developer"]))):
    return user.to_dict()

@router.get("/default")
async def default(user: userPayload = Depends(has_roles(["default-roles-frcm-realm"]))):
    return user.to_dict()