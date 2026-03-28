from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import datetime as dt


from src.firerisk.databases.timescale.models import FireRisk

# test query, db'slast 100 records in descending order
def frcm_db_read_last_100(db: Session):
    try:
        res = db.query(FireRisk).order_by(FireRisk.time.desc()).limit(100).all()
        return res
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading last 100 FireRisk records: {str(e)}"
        )


def frcm_db_check_range(
    db: Session,
    lat: float,
    lon: float,
    start_time: dt.datetime,
    end_time: dt.datetime,
) -> bool:
    try:
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=dt.timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=dt.timezone.utc)
            
        # SELECT MIN(time), MAX(time)
        # FROM fire_risk
        # WHERE lat = 60.383
        # AND lon = 5.3327;
        result = (
            db.query(
                func.min(FireRisk.time),
                func.max(FireRisk.time),
            )
            .filter(
                and_(
                    FireRisk.lat == lat,
                    FireRisk.lon == lon,
                )
            )
            .one()
        )
        db_min, db_max = result

        if db_min is None or db_max is None:
            return False

        return db_min <= start_time and db_max >= end_time

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking range: {str(e)}"
        )


def frcm_db_get_range(
    db: Session,
    lat: float,
    lon: float,
    start_time: dt.datetime,
    end_time: dt.datetime,
) -> list[FireRisk]:
    try:
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=dt.timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=dt.timezone.utc)
            
        # SELECT *
        # FROM fire_risk
        # WHERE lat = 60.383
        # AND lon = 5.3327
        # AND time >= start_time
        # AND time <= end_time
        # ORDER BY time ASC;
        return (
            db.query(FireRisk)
            .filter(
                and_(
                    FireRisk.lat == lat,
                    FireRisk.lon == lon,
                    FireRisk.time >= start_time,
                    FireRisk.time <= end_time,
                )
            )
            .order_by(FireRisk.time.asc())
            .all()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching range from database: {str(e)}"
        )


def frcm_db_save(db: Session, records: list[FireRisk]) -> None:
    try:
        for record in records:
            db.add(record)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error saving records to database: {str(e)}"
        )