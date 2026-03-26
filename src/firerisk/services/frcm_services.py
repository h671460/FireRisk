import datetime as dt
from zoneinfo import ZoneInfo
from typing import List, Dict

from fastapi import HTTPException
from frcm.frcapi import METFireRiskAPI
from frcm.datamodel.model import Location, WeatherData, FireRiskPrediction
from pydantic import ValidationError
from src.firerisk.databases.timescale.models import FireRisk

UTC = dt.timezone.utc

frc = METFireRiskAPI()


def to_utc(ts: dt.datetime) -> dt.datetime:
    if ts.tzinfo is None:
        ts = ts.astimezone(UTC)
    return ts


def risk_level_from_score(score: float) -> str:
    # 🔧 adjust thresholds as needed
    if score < 4:
        return "low"
    elif score < 8:
        return "medium"
    elif score < 12:
        return "high"
    return "extreme"


def _prediction_map(pred: FireRiskPrediction):
    return {to_utc(r.timestamp): r for r in pred.firerisks}


def get_fire_risk_with_time_range(
    location: Location,
    start_time: dt.datetime,
    end_time: dt.datetime,
) -> List[FireRisk]:

    start_utc = to_utc(start_time)
    end_utc = to_utc(end_time)

    if end_utc < start_utc:
        raise ValueError("end_time must be >= start_time")

    now_utc = dt.datetime.now(tz=UTC)
    obs_delta = now_utc - start_utc

    wd: WeatherData = frc.get_weatherdata_now(location, obs_delta)

    # Filter weather points
    weather_points: Dict[dt.datetime, Dict] = {}

    for p in wd.observations.data:
        ts = to_utc(p.timestamp)
        if start_utc <= ts <= end_utc:
            weather_points[ts] = p

    for p in wd.forecast.data:
        ts = to_utc(p.timestamp)
        if start_utc <= ts <= end_utc and ts not in weather_points:
            weather_points[ts] = p

    # Compute predictions
    wd_in_range = wd.model_copy(update={
        "observations": wd.observations.model_copy(
            update={"data": [p for p in wd.observations.data if start_utc <= to_utc(p.timestamp) <= end_utc]}
        ),
        "forecast": wd.forecast.model_copy(
            update={"data": [p for p in wd.forecast.data if start_utc <= to_utc(p.timestamp) <= end_utc]}
        ),
    })

    pred: FireRiskPrediction = frc.compute(wd_in_range)
    pred_map = _prediction_map(pred)

    results: List[FireRisk] = []

    loc_str = f"{location.latitude},{location.longitude}"

    for ts in sorted(weather_points.keys()):
        w = weather_points[ts]
        pred_obj = pred_map.get(ts)

        # Skip rows without prediction (optional — remove if you want them)
        if not pred_obj:
            continue

        score = float(pred_obj.ttf)

        results.append(
            FireRisk(
                time=ts,
                location=loc_str,
                lat=location.latitude,
                lon=location.longitude,
                temperature=w.temperature,
                humidity=w.humidity,
                wind_speed=w.wind_speed,
                risk_score=score,
                risk_level=risk_level_from_score(score),
            )
        )

    return results

if __name__ == "__main__":
    from datetime import timedelta
    location = Location(latitude=60.383, longitude=5.3327)
    obs_delta = timedelta(days=2)
    start = dt.datetime(2024, 6, 1, tzinfo=UTC)
    end = dt.datetime(2024, 6, 7, tzinfo=UTC)
    
    #  data data types debuf
    dtyypes = {"start": str(type(start)), "end": str(type(end))}
    from pprint import pprint
    pprint(dtyypes)
    print()
    print()
    

    risks = get_fire_risk_with_time_range(location, start, end)
    
    
    from rich.table import Table
    from rich.console import Console
    def print_fire_risks(risks : List[FireRisk]):
        table = Table(title="Fire Risk")

        table.add_column("Time", justify="left")
        table.add_column("Location")
        table.add_column("Lat")
        table.add_column("Lon")
        table.add_column("Temp °C", justify="right")
        table.add_column("Humidity %", justify="right")
        table.add_column("Wind m/s", justify="right")
        table.add_column("Score", justify="right")
        table.add_column("Level")

        for r in risks:
            table.add_row(
                r.time.strftime("%Y-%m-%d %H:%M"),
                r.location,
                f"{r.lat:.4f}",
                f"{r.lon:.4f}",
                f"{r.temperature:.1f}",
                f"{r.humidity:.1f}",
                f"{r.wind_speed:.1f}",
                f"{r.risk_score:.2f}",
                r.risk_level,
            )

        Console().print(table)
        
    print_fire_risks(risks)
            
            