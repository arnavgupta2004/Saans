"""Shared forecast loader: fetch, calibrate, and label provenance honestly."""
from __future__ import annotations
from typing import Any
from .calibrate import calibrate
from .models import School
from .sources import CpcbClient, OpenMeteoClient

def load_forecast(school: School) -> tuple[list[dict[str, Any]], dict[str, Any], str]:
    """Return (calibrated rows, sources, mode). `mode` is the FORECAST source (live/cached/fixture);
    the CPCB observation source is reported separately in `sources["observation"]`."""
    hourly = OpenMeteoClient().hourly(school.lat, school.lon)
    try:
        obs: dict[str, Any] | None = CpcbClient().latest_near(school.lat, school.lon)
    except Exception:
        obs = None
    forecast = hourly[0].get("source", "live") if hourly else "fixture"
    source = {"forecast": forecast, "observation": (obs or {}).get("source", "none"), "station": (obs or {}).get("station"), "distance_km": (obs or {}).get("distance_km")}
    return calibrate(hourly, obs), source, forecast
