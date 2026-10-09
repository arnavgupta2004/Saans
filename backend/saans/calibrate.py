"""Deterministic, fading CPCB-to-forecast bias correction."""
from __future__ import annotations
from math import exp
from typing import Any

def calibrate(hourly: list[dict[str, Any]], observed_now: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Add calibrated PM values using the §3.2 clipped, 12-hour decay factor."""
    usable = observed_now and observed_now.get("pm25") is not None and observed_now.get("distance_km", 0) <= 25 and hourly and hourly[0].get("pm25", 0) > 0
    ratio = min(2.0, max(0.5, float(observed_now["pm25"]) / float(hourly[0]["pm25"]))) if usable else 1.0
    calibrated = bool(usable)
    result=[]
    for h,row in enumerate(hourly):
        factor = 1 + (ratio - 1) * exp(-h / 12)
        result.append({**row,"pm25_cal":round(float(row["pm25"])*factor,2),"pm10_cal":round(float(row["pm10"])*factor,2),"factor":round(factor,6),"calibrated":calibrated})
    return result
