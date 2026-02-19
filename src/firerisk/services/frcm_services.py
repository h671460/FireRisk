# src/firerisk/services/frcm_services.py

import datetime as dt
from zoneinfo import ZoneInfo
from typing import Any, Dict, List

from frcm.frcapi import METFireRiskAPI
from frcm.datamodel.model import Location, WeatherData, FireRiskPrediction

OSLO_TZ = ZoneInfo("Europe/Oslo")
UTC = dt.timezone.utc

frc = METFireRiskAPI()


def to_utc(ts: dt.datetime, assume_tz: ZoneInfo = OSLO_TZ) -> dt.datetime:
    """
    Normalize datetime to timezone-aware UTC.

    - If naive: assume it's in `assume_tz` (Europe/Oslo by default)
    - If aware: convert to UTC
    """
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=assume_tz)
    return ts.astimezone(UTC)


def _prediction_map(pred: FireRiskPrediction) -> Dict[dt.datetime, float]:
    # Using FireRisk.ttf as the numeric prediction value
    out: Dict[dt.datetime, float] = {}
    for r in pred.firerisks:
        out[to_utc(r.timestamp)] = r.ttf
    return out


def get_fire_risk_with_time_range(
    location: Location,
    start_time: dt.datetime,
    end_time: dt.datetime,
) -> Dict[str, Any]:
    """
    Returns:
      {
        "location": {"latitude": ..., "longitude": ...},
        "start_time": "...UTC...",
        "end_time": "...UTC...",
        "created": "...UTC...",
        "data": [
          {
            "time": "...UTC...",
            "lon": float,
            "lat": float,
            "humidity": float | None,
            "temperature": float | None,
            "wind_speed": float | None,
            "firerisk_prediction": float | None,
            "type": "observation" | "forecast"
          },
          ...
        ]
      }
    """
    start_utc = to_utc(start_time)
    end_utc = to_utc(end_time)
    if end_utc < start_utc:
        raise ValueError("end_time must be >= start_time")

    now_utc = dt.datetime.now(tz=UTC)

    # Fetch enough history so observations cover [start_time, now]
    obs_delta = now_utc - start_utc
    if obs_delta.total_seconds() < 0:
        obs_delta = dt.timedelta(0)

    wd: WeatherData = frc.get_weatherdata_now(location, obs_delta)
    created_utc = to_utc(wd.created)

    lat = location.latitude
    lon = location.longitude

    # Build a unique time index: prefer observation if both exist at same timestamp
    by_ts: Dict[dt.datetime, Dict[str, Any]] = {}

    # Observations (always "observation")
    for p in wd.observations.data:
        ts = to_utc(p.timestamp)
        if start_utc <= ts <= end_utc:
            by_ts[ts] = {
                "time": ts.isoformat(),
                "lon": lon,
                "lat": lat,
                "humidity": p.humidity,
                "temperature": p.temperature,
                "wind_speed": p.wind_speed,
                "firerisk_prediction": None,  # fill later
                "type": "observation",
            }

    # Forecast (only if not already covered by observation at same timestamp)
    for p in wd.forecast.data:
        ts = to_utc(p.timestamp)
        if start_utc <= ts <= end_utc and ts not in by_ts:
            by_ts[ts] = {
                "time": ts.isoformat(),
                "lon": lon,
                "lat": lat,
                "humidity": p.humidity,
                "temperature": p.temperature,
                "wind_speed": p.wind_speed,
                "firerisk_prediction": None,  # fill later
                "type": "observation" if ts <= now_utc else "forecast",
            }

    # Compute predictions only for the filtered range
    wd_in_range = wd.model_copy(update={
        "observations": wd.observations.model_copy(update={
            "data": [p for p in wd.observations.data if start_utc <= to_utc(p.timestamp) <= end_utc]
        }),
        "forecast": wd.forecast.model_copy(update={
            "data": [p for p in wd.forecast.data if start_utc <= to_utc(p.timestamp) <= end_utc]
        }),
    })

    pred: FireRiskPrediction = frc.compute(wd_in_range)
    pred_by_ts = _prediction_map(pred)

    # Merge prediction into rows (match by timestamp)
    for ts, row in by_ts.items():
        row["firerisk_prediction"] = pred_by_ts.get(ts)

    data_rows = [by_ts[ts] for ts in sorted(by_ts.keys())]

    return {
        "location": {"latitude": lat, "longitude": lon},
        "start_time": start_utc.isoformat(),
        "end_time": end_utc.isoformat(),
        "created": created_utc.isoformat(),
        "data": data_rows,
    }


if __name__ == "__main__":
    import pandas as pd
    
    location = Location(latitude=60.383, longitude=5.3327)  # Bergen
    start_time = dt.datetime.now(tz=UTC) - dt.timedelta(days=3)
    end_time = dt.datetime.now(tz=UTC) + dt.timedelta(days=1)

    result = get_fire_risk_with_time_range(location, start_time, end_time)
    df = pd.DataFrame(result["data"])
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df = df.sort_values("time").reset_index(drop=True)
    
    print(df.tail(20))