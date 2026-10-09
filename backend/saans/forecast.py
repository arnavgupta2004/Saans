"""Shared forecast loader: fetch, calibrate, and label provenance honestly."""
from __future__ import annotations
import logging
from typing import Any
from .calibrate import calibrate, observation_usable
from .models import School
from .sources import CpcbClient, OpenAqClient, OpenAqUnavailable, OpenMeteoClient

logger = logging.getLogger(__name__)

def _label(obs: dict[str, Any] | None) -> str:
    """e.g. "live:openaq", "live:cpcb", "fixture:cpcb", or "none"."""
    if not obs: return "none"
    return f"{obs.get('source', 'none')}:{obs['provider']}" if obs.get("provider") else obs.get("source", "none")

def observe(lat: float, lon: float) -> tuple[dict[str, Any] | None, str | None]:
    """Calibration source chain: data.gov.in CPCB, then OpenAQ, then nothing (uncalibrated).
    Returns (observation, note). The observation is the first usable reading, else the CPCB result (e.g. fixture)
    so the UI can say what happened; `note` explains in one line why the forecast is not calibrated (None if it is)."""
    cpcb: dict[str, Any] | None = None
    try: cpcb = CpcbClient().latest_near(lat, lon)
    except Exception as exc: logger.warning("CPCB observation failed: %s: %s", type(exc).__name__, exc)
    if observation_usable(cpcb): return cpcb, None
    cpcb_why = "CPCB (data.gov.in) unreachable" if not cpcb or cpcb.get("source") == "fixture" else "CPCB (data.gov.in) reading too old or too far"
    try:
        openaq = OpenAqClient().latest_near(lat, lon)
        if observation_usable(openaq): return openaq, None
        openaq_why = "OpenAQ reading too old or too far"
    except OpenAqUnavailable as exc:
        logger.warning("OpenAQ observation unavailable: %s", exc); openaq_why = exc.note
    except Exception as exc:
        logger.warning("OpenAQ observation unavailable: %s: %s", type(exc).__name__, exc); openaq_why = "OpenAQ unavailable"
    return cpcb, f"Not calibrated: {cpcb_why}; {openaq_why}"

def load_forecast(school: School) -> tuple[list[dict[str, Any]], dict[str, Any], str]:
    """Return (calibrated rows, sources, mode). `mode` is the FORECAST source (live/cached/fixture);
    the observation source used for calibration is reported separately in `sources["observation"]`."""
    hourly = OpenMeteoClient().hourly(school.lat, school.lon)
    obs, note = observe(school.lat, school.lon)
    forecast = hourly[0].get("source", "live") if hourly else "fixture"
    used = obs if observation_usable(obs) else None  # only name a station that actually calibrated the forecast
    source = {"forecast": forecast, "observation": _label(obs), "station": (used or {}).get("station"), "distance_km": (used or {}).get("distance_km"), "note": note}
    return calibrate(hourly, obs), source, forecast
