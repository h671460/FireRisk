
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
    
    def __str__(self) -> str:
        return (
            f"FireRisk("
            f"time={self.time.isoformat()}, "
            f"location='{self.location}', "
            f"lat={self.lat:.4f}, lon={self.lon:.4f}, "
            f"temperature={self.temperature:.1f}°C, "
            f"humidity={self.humidity:.1f}%, "
            f"wind_speed={self.wind_speed:.1f} m/s, "
            f"risk_score={self.risk_score:.2f}, "
            f"risk_level='{self.risk_level}'"
            f")"
        )
Index("fire_risk_location_time_idx", FireRisk.location, FireRisk.time.desc())
Index("fire_risk_time_idx", FireRisk.time.desc())
