from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List


# auth
from src.firerisk.api.routers.auth import has_roles
from src.firerisk.api.schemas.userPayload import userPayload


# database
from src.firerisk.databases.timescale.database import TIMESCALE_SessionLocal

# frcm services
from src.firerisk.services.frcm_services import get_fire_risk_with_time_range

# database services
from src.firerisk.services.database_services import frcm_db_read_last_100, frcm_db_check_range, frcm_db_get_range, frcm_db_save

# dynamic-frcm
from frcm.datamodel.model import Location

from src.firerisk.databases.timescale.models import FireRisk



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





example_start_str = "2026-03-27T12:00:00Z"
example_end_str = "2026-03-28T22:00:00Z"

@router.get("/range", status_code=status.HTTP_200_OK)
async def read_frcm_with_time_range(
    db: DB,
    # lon: float = Query(..., description="Longitude of the location", example=5.3327),
    # lat: float = Query(..., description="Latitude of the location", example=60.383),
    # start_time: datetime = Query(..., description="Start time (ISO 8601)", example=example_start_str),
    # end_time: datetime = Query(..., description="End time (ISO 8601)", example=example_end_str),
    lon, lat, start_time: datetime,end_time: datetime ,
    user: userPayload = Depends(has_roles(["default-roles-frcm-realm"])),
):  
    
    if lon is None or lat is None or start_time is None or end_time is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Missing required query parameters: lat, lon, start_time, end_time"
        )
    
    location = Location(latitude=lat, longitude=lon)
        
    exists = frcm_db_check_range(db, lat, lon, start_time, end_time)

    if exists:
        return frcm_db_get_range(db, lat, lon, start_time, end_time)

    try:
        records = get_fire_risk_with_time_range(location, start_time, end_time)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch fire risk data from frcm service"
        )

    frcm_db_save(db, records)
    return frcm_db_get_range(db, lat, lon, start_time, end_time)
