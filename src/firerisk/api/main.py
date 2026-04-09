from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware


from src.firerisk.api.routers.auth import get_user_info, has_roles, settings
from src.firerisk.api.schemas.userPayload import userPayload

from firerisk.api.routers import frcm_route, user
app = FastAPI(
    swagger_ui_init_oauth={
        "clientId": settings.client_id,               
        "clientSecret": settings.client_secret,
        "usePkceWithAuthorizationCodeGrant": True,
    },
    root_path="/api/v1",
)

import os
FRONTEND_HOST = os.getenv('KC_PUBLIC_IP_ADDRESS', 'localhost')

# ✅ CORS
origins = [
    "https://fireriskgroup02.com",
    "https://www.fireriskgroup02.com",
    "https://localhost:3000",
    "https://localhost:3333",
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

