from fastapi import FastAPI, Depends, HTTPException

from src.firerisk.api_keycloak.routers.auth import get_user_info, has_roles, settings
from src.firerisk.api_keycloak.schemas.userPayload import userPayload

from firerisk.api_keycloak.routers import frcm_route, user
app = FastAPI(
    swagger_ui_init_oauth={
        "clientId": settings.client_id,               
        "clientSecret": settings.client_secret,
        "usePkceWithAuthorizationCodeGrant": True,
    }
)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(user.router)
app.include_router(frcm_route.router)

