from fastapi import HTTPException
from sqlalchemy.orm import Session
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
        
        