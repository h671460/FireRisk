from fastapi import APIRouter, Query
from typing import Annotated
from pydantic import Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime


from src.firerisk.api.databases.timescale.database import TIMESCALE_SessionLocal
from src.firerisk.api.routers.auth import get_current_user
from src.firerisk.api.databases.timescale.models import FireRisk


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
user_dependency = Annotated[dict, Depends(get_current_user)]
one_week = 7 * 24


@router.get("/", status_code=status.HTTP_200_OK)
async def read_last_100(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(FireRisk).limit(100).all()


@router.get("/location/{location}", status_code=status.HTTP_200_OK)
async def read_by_location(location: str, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(FireRisk).filter(FireRisk.location == location).order_by(FireRisk.time.desc()).limit(one_week).all()


@router.get("/time-range/", status_code=status.HTTP_200_OK)
async def read_by_time_range(user: user_dependency, 
                             db: db_dependency,
                             start_time: datetime = Query(..., description="Example: 2025-01-01T00:00:00Z"),
                             end_time: datetime = Query(..., description="Example: 2025-01-10T00:00:00Z")):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(FireRisk).filter(FireRisk.time >= start_time, FireRisk.time <= end_time).order_by(FireRisk.time.desc()).limit(one_week).all()


@router.get("/location-time-range/", status_code=status.HTTP_200_OK)
async def read_by_location_time_range(location: str, 
                                      user: user_dependency, 
                                      db: db_dependency, 
                                      start_time: datetime = Query(..., description="Example: 2025-01-01T00:00:00Z"),
                                      end_time: datetime = Query(..., description="Example: 2025-01-10T00:00:00Z")):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(FireRisk).filter(
        FireRisk.location == location,
        FireRisk.time >= start_time,
        FireRisk.time <= end_time
    ).order_by(FireRisk.time.desc()).limit(one_week).all()