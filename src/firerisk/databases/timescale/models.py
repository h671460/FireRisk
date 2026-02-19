from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, String, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.firerisk.api.databases.timescale.database import TIMESCALE_Base

class FireRisk(TIMESCALE_Base):
    __tablename__ = "fire_risk"

    time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), primary_key=True)
    location: Mapped[str] = mapped_column(String, primary_key=True)

    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)

    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    wind_speed: Mapped[float] = mapped_column(Float, nullable=False)

    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String, nullable=False)

Index("fire_risk_location_time_idx", FireRisk.location, FireRisk.time.desc())
Index("fire_risk_time_idx", FireRisk.time.desc())
