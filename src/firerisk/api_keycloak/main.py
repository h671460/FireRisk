from fastapi import FastAPI, Depends, HTTPException

from src.firerisk.api_keycloak.routers.auth import get_user_info, has_roles, settings
from src.firerisk.api_keycloak.schemas.userPayload import userPayload

from firerisk.api_keycloak.routers import frcm_route
app = FastAPI(
    swagger_ui_init_oauth={
        "clientId": settings.client_id,                 # <-- your Keycloak client id (NOT "account")
        "clientSecret": settings.client_secret,         # <-- your Keycloak client secret
        "usePkceWithAuthorizationCodeGrant": True,
    }
)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


@app.get("/secure")
async def root(user: userPayload = Depends(get_user_info)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message": f"Hello {user.username}!"}

@app.get("/admin")
async def admin(user: userPayload = Depends(has_roles(["admin"]))):
    return user.to_dict()

@app.get("/developer")
async def developer(user: userPayload = Depends(has_roles(["developer"]))):
    return user.to_dict()

@app.get("/default")
async def default(user: userPayload = Depends(has_roles(["default-roles-frcm-realm"]))):
    return user.to_dict()

app.include_router(frcm_route.router)