"""Deterministic, fading CPCB-to-forecast bias correction."""
from __future__ import annotations
from datetime import datetime, timedelta
from math import exp
from typing import Any
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
MAX_DISTANCE_KM = 25
MAX_OBSERVATION_AGE_S = 2 * 3600

def _observed_age_s(observed_at: Any, now: datetime) -> float | None:
    """Age of the station's own timestamp, if it parses (CPCB uses dd-mm-YYYY HH:MM:SS)."""
    if not observed_at: return None
    for fmt in ("%d-%m-%Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try: return (now.replace(tzinfo=None) - datetime.strptime(str(observed_at), fmt)).total_seconds()
        except ValueError: continue
    return None

def observation_usable(obs: dict[str, Any] | None, now: datetime | None = None) -> bool:
    """Only a live (or cached <2h) reading from a station within 25 km may calibrate the forecast."""
    if not obs or obs.get("pm25") is None: return False
    source = obs.get("source")
    if source == "cached":
        if float(obs.get("age_s", MAX_OBSERVATION_AGE_S)) >= MAX_OBSERVATION_AGE_S: return False
    elif source != "live": return False  # fixture, unknown, or missing source
    if obs.get("distance_km") is None or float(obs["distance_km"]) > MAX_DISTANCE_KM: return False
    age = _observed_age_s(obs.get("observed_at"), now or datetime.now(IST))
    return age is None or age < MAX_OBSERVATION_AGE_S

def calibrate(hourly: list[dict[str, Any]], observed_now: dict[str, Any] | None, now: datetime | None = None) -> list[dict[str, Any]]:
    """Add calibrated PM values using the §3.2 clipped, 12-hour decay factor.

    The ratio is anchored on the forecast row for the current IST hour (not midnight) and fades with distance from it.
    """
    now = now or datetime.now(IST)
    anchor = next((i for i, r in enumerate(hourly) if str(r.get("time", ""))[:13] == now.strftime("%Y-%m-%dT%H")), 0)
    usable = observation_usable(observed_now, now) and bool(hourly) and hourly[anchor].get("pm25", 0) > 0
    ratio = min(2.0, max(0.5, float(observed_now["pm25"]) / float(hourly[anchor]["pm25"]))) if usable else 1.0
    result=[]
    for h,row in enumerate(hourly):
        factor = 1 + (ratio - 1) * exp(-abs(h - anchor) / 12)
        result.append({**row,"pm25_cal":round(float(row["pm25"])*factor,2),"pm10_cal":round(float(row["pm10"])*factor,2),"factor":round(factor,6),"calibrated":bool(usable)})
    return result
