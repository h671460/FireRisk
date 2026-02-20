from fastapi import APIRouter, Depends, HTTPException, status
# from datetime import datetime
# from pydantic import Field
from typing import Annotated
from sqlalchemy.orm import Session



from src.firerisk.api_keycloak.routers.auth import has_roles, get_user_info
from src.firerisk.api_keycloak.schemas.userPayload import userPayload


from src.firerisk.databases.timescale.database import TIMESCALE_SessionLocal
from src.firerisk.databases.timescale.models import FireRisk

from src.firerisk.services.frcm_services import get_fire_risk_with_time_range
from src.firerisk.services.database_services import frcm_db_read_last_100
from src.firerisk.services.database_services import frcm_db_read_last_100



router = APIRouter(
    prefix='/frcm',
    tags=['frcm']
)


def get_db():
    db = TIMESCALE_SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
one_week = 7 * 24






@router.get("/", status_code=status.HTTP_200_OK)
async def read_last_100(
    db:db_dependency=db_dependency,
    user: userPayload = Depends(has_roles(["admin"]))):
    
    
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return frcm_db_read_last_100(db)

