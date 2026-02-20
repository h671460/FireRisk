from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session


# auth
from src.firerisk.api_keycloak.routers.auth import has_roles
from src.firerisk.api_keycloak.schemas.userPayload import userPayload


# database
from src.firerisk.databases.timescale.database import TIMESCALE_SessionLocal

# services
from src.firerisk.services.frcm_services import get_fire_risk_with_time_range
from src.firerisk.services.database_services import frcm_db_read_last_100

# dynamic-frcm
from frcm.datamodel.model import Location

router = APIRouter(
    prefix="/frcm", 
    tags=["frcm"]
)


def get_db():
    db = TIMESCALE_SessionLocal()
    try:
        yield db
    finally:
        db.close()


DB = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_last_100(
    db: DB,
    user: userPayload = Depends(has_roles(["admin"])),
):
    if user is None:
        return {"error": "Unauthorized"}
    if db is None:
        return {"error": "Database connection error"}
    return frcm_db_read_last_100(db)


today_str = datetime.now().date().isoformat()
yesterday_str = (datetime.now().date() + timedelta(days=-1)).isoformat()
@router.get("/range", status_code=status.HTTP_200_OK)
async def read_frcm_with_time_range(
    lon: float = Query(..., description="Longitude of the location", example=5.3327),
    lat: float = Query(..., description="Latitude of the location", example=60.383),
    start_time: datetime = Query(..., description="Start time (ISO 8601)", example=yesterday_str + "T12:00:00Z"),
    end_time: datetime = Query(..., description="End time (ISO 8601)", example=today_str + "T12:00:00Z"),
    user: userPayload = Depends(has_roles(["default-roles-frcm-realm"])),
):
    location = Location(latitude=lat, longitude=lon)  
    return get_fire_risk_with_time_range(location, start_time,end_time)
    # return each value data type for debugging
    # return {"lon": str(type(lon)), "lat": str(type(lat)), "start_time": str(type(start_time)), "end_time": str(type(end_time))}