"""Strands agent. Tools return planner output; the LLM only explains it."""
from __future__ import annotations

import os

from .calibrate import calibrate
from .notices import build_notice
from .planner import best_day, plan_day
from .sources import CpcbClient, OpenMeteoClient
from .store import get_store

SYSTEM_PROMPT = (
    "You are Saans, an assistant for school air-safety in India. Only state AQI numbers that a tool "
    "returned, and cite the source and time. Safety actions come from get_day_plan; never override or "
    "soften them. If unsure, say so. Answer in the user's language (English or Hindi). Be brief."
)


def _forecast(school):
    hourly = OpenMeteoClient().hourly(school.lat, school.lon)
    obs = CpcbClient().latest_near(school.lat, school.lon)
    src = {"forecast": hourly[0].get("source", "open-meteo") if hourly else "open-meteo",
           "observation": obs.get("source", "none"), "station": obs.get("station"), "distance_km": obs.get("distance_km")}
    return calibrate(hourly, obs), src


def _school(school_id: str):
    school = get_store().get(school_id)
    if school is None:
        raise ValueError(f"Unknown school {school_id}")
    return school


def get_school(school_id: str) -> dict:
    """Return the school profile and timetable."""
    return _school(school_id).model_dump()


def get_day_plan(school_id: str, date: str = "") -> dict:
    """Return the deterministic per-period AQI plan (actions, swaps) for a date (YYYY-MM-DD, default today)."""
    school = _school(school_id)
    rows, src = _forecast(school)
    return plan_day(school, rows, date or rows[0]["time"][:10], src).model_dump()


def get_hourly_forecast(school_id: str, date: str = "") -> list[dict]:
    """Return calibrated hourly PM2.5/PM10 forecast points for a date."""
    rows, _ = _forecast(_school(school_id))
    d = date or rows[0]["time"][:10]
    return [r for r in rows if r["time"].startswith(d)]


def find_best_day(school_id: str, start: str = "09:00", end: str = "12:00") -> dict:
    """Rank the coming days by worst calibrated AQI inside the HH:MM window."""
    rows, _ = _forecast(_school(school_id))
    return best_day(_school(school_id), rows, start, end)


def draft_notice(school_id: str, date: str = "", lang: str = "en") -> dict:
    """Return the deterministic parent notice text and WhatsApp URL."""
    return build_notice(DayPlanAdapter(school_id, date), lang)


def DayPlanAdapter(school_id: str, date: str):
    from .models import DayPlan
    return DayPlan(**get_day_plan(school_id, date))


TOOLS = [get_school, get_day_plan, get_hourly_forecast, find_best_day, draft_notice]


def ask(school_id: str, question: str, lang: str = "en") -> dict:
    """Run the Strands agent. Raises on model failure; caller falls back."""
    from strands import Agent, tool
    from strands.models import BedrockModel

    model = BedrockModel(model_id=os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0"),
                         region_name=os.getenv("AWS_REGION", "us-east-1"))
    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=[tool(f) for f in TOOLS])
    result = agent(f"[school_id={school_id}] [lang={lang}] {question}")
    used = [name for name in getattr(result.metrics, "tool_metrics", {}) or {}]
    return {"answer": str(result), "tools_used": used}
