from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware


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

import os
FRONTEND_HOST = os.getenv('KC_PUBLIC_IP_ADDRESS', 'localhost')

# ✅ CORS
origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:3333",
    "http://localhost:3333",
    f"http://{FRONTEND_HOST}:3333",
    f"http://{FRONTEND_HOST}:3000",
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}



app.include_router(frcm_route.router)
app.include_router(user.router)

