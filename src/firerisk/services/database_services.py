from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import datetime as dt


from src.firerisk.databases.timescale.models import FireRisk


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
        loc_str = f"{lat},{lon}"
        result = (
            db.query(
                func.min(FireRisk.time),
                func.max(FireRisk.time),
            )
            .filter(FireRisk.location == loc_str)
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
        #     existing = (
        #         db.query(FireRisk)
        #         .filter(
        #             and_(
        #                 FireRisk.time == record.time,
        #                 FireRisk.location == record.location,
        #             )
        #         )
        #         .first()
        #     )
        #     if existing:
        #         existing.temperature = record.temperature
        #         existing.humidity = record.humidity
        #         existing.wind_speed = record.wind_speed
        #         existing.risk_score = record.risk_score
        #         existing.risk_level = record.risk_level
        #     else:
            db.add(record)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error saving records to database: {str(e)}"
        )