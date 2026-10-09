"""Shared forecast loader: fetch, calibrate, and label provenance honestly."""
from __future__ import annotations
import logging
from typing import Any
from .calibrate import calibrate, observation_usable
from .models import School
from .sources import CpcbClient, OpenAqClient, OpenMeteoClient

logger = logging.getLogger(__name__)

def _label(obs: dict[str, Any] | None) -> str:
    """e.g. "live:openaq", "live:cpcb", "fixture:cpcb", or "none"."""
    if not obs: return "none"
    return f"{obs.get('source', 'none')}:{obs['provider']}" if obs.get("provider") else obs.get("source", "none")

def observe(lat: float, lon: float) -> dict[str, Any] | None:
    """Calibration source chain: data.gov.in CPCB, then OpenAQ, then nothing (uncalibrated).
    Returns the first usable reading; otherwise the CPCB result (e.g. fixture) so the UI can say what happened."""
    cpcb: dict[str, Any] | None = None
    try: cpcb = CpcbClient().latest_near(lat, lon)
    except Exception as exc: logger.warning("CPCB observation failed: %s: %s", type(exc).__name__, exc)
    if observation_usable(cpcb): return cpcb
    try:
        openaq = OpenAqClient().latest_near(lat, lon)
        if observation_usable(openaq): return openaq
    except Exception as exc: logger.warning("OpenAQ observation unavailable: %s: %s", type(exc).__name__, exc)
    return cpcb

def load_forecast(school: School) -> tuple[list[dict[str, Any]], dict[str, Any], str]:
    """Return (calibrated rows, sources, mode). `mode` is the FORECAST source (live/cached/fixture);
    the observation source used for calibration is reported separately in `sources["observation"]`."""
    hourly = OpenMeteoClient().hourly(school.lat, school.lon)
    obs = observe(school.lat, school.lon)
    forecast = hourly[0].get("source", "live") if hourly else "fixture"
    used = obs if observation_usable(obs) else None  # only name a station that actually calibrated the forecast
    source = {"forecast": forecast, "observation": _label(obs), "station": (used or {}).get("station"), "distance_km": (used or {}).get("distance_km")}
    return calibrate(hourly, obs), source, forecast
