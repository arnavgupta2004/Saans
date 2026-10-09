"""Saans HTTP API; decisions are produced only by the deterministic planner."""
from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel

from saans.forecast import load_forecast
from saans.models import DayPlan, School
from saans.sources import load_replay
from saans.planner import IST, best_day, plan_day, plan_week
from saans.store import SchoolStore, get_plan_cache, get_store


logger = logging.getLogger(__name__)
app = FastAPI(title="Saans", version="0.1.0")
# Public, cookie-less API: any origin (Amplify, localhost). API Gateway forwards OPTIONS preflights to this app,
# so a restrictive list here made browsers fail POST /api/ask from the hosted site (preflight 400).
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])


def _store() -> SchoolStore:
    return get_store()


def _school_or_404(school_id: str) -> School:
    school = _store().get(school_id)
    if school is None:
        raise HTTPException(status_code=404, detail="School not found")
    return school


def _forecast(school: School) -> tuple[list[dict], dict, str]:
    return load_forecast(school)


CACHE_MAX_AGE_S = 3 * 3600


def _cached_day_plan(school: School) -> DayPlan | None:
    """Plan precomputed by the 06:00 IST daily job, if < 3 h old. Re-planned from the cached rows so `now` is
    the current hour and timetable edits apply; generated_at keeps the time the data was fetched."""
    today = datetime.now(IST).date().isoformat()
    try:
        item = get_plan_cache().get(f"{school.id}#{today}")
    except Exception as exc:
        logger.warning("Plan cache unavailable (%s: %s); using live forecast", type(exc).__name__, exc)
        return None
    if not item or time.time() - float(item.get("stored_at", 0)) >= CACHE_MAX_AGE_S or not item.get("rows"):
        return None
    plan = plan_day(school, item["rows"], today, item.get("sources"), "cached")
    return plan.model_copy(update={"generated_at": item["plan"]["generated_at"]})


def _day_plan(school: School, replay: str | None = None) -> DayPlan:
    if replay:
        try:
            rows, recorded = load_replay(replay)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown replay '{replay}'") from exc
        source = {"forecast": "recorded", "observation": "none"}
        return plan_day(school, rows, recorded, source, "replay", replay_date=recorded)
    cached = _cached_day_plan(school)
    if cached:
        return cached
    rows, source, mode = _forecast(school)
    date = rows[0]["time"][:10]
    try:
        return plan_day(school, rows, date, source, mode)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=f"No forecast for {date}") from exc


@app.get("/api/health")
def health() -> dict[str, bool | str]:
    return {"ok": True, "version": "0.1.0"}


@app.get("/api/schools", response_model=list[School])
def list_schools() -> list[School]:
    return _store().list()


@app.post("/api/schools", response_model=School)
def save_school(school: School) -> School:
    return _store().save(school)


@app.get("/api/schools/{school_id}", response_model=School)
def get_school(school_id: str) -> School:
    return _school_or_404(school_id)


@app.get("/api/schools/{school_id}/today", response_model=DayPlan)
def today(school_id: str, replay: str | None = None) -> DayPlan:
    return _day_plan(_school_or_404(school_id), replay)


@app.get("/api/schools/{school_id}/week")
def week(school_id: str) -> dict:
    school = _school_or_404(school_id)
    rows, source, mode = _forecast(school)
    return plan_week(school, rows, source, mode)


@app.get("/api/schools/{school_id}/best-day")
def get_best_day(school_id: str, start: str = Query("09:00", pattern=r"^([01]\d|2[0-3]):[0-5]\d$"), end: str = Query("12:00", pattern=r"^([01]\d|2[0-3]):[0-5]\d$")) -> dict:
    school = _school_or_404(school_id)
    rows, _, _ = _forecast(school)
    return best_day(school, rows, start, end)


@app.get("/api/schools/{school_id}/notice")
def notice(school_id: str, lang: Literal["en", "hi"] = "en", polish: bool = False, replay: str | None = None) -> dict:
    if polish:
        raise HTTPException(status_code=501, detail="Notice polishing is not available yet")
    from saans.notices import build_notice
    return build_notice(_day_plan(_school_or_404(school_id), replay), lang)


class AskRequest(BaseModel):
    school_id: str
    question: str
    lang: Literal["en", "hi"] = "en"
    replay: str | None = None


@app.post("/api/ask")
def ask(request: AskRequest) -> dict:
    _school_or_404(request.school_id)
    if request.replay:
        try:
            load_replay(request.replay)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown replay '{request.replay}'") from exc
    from saans import agent
    try:
        return agent.ask(request.school_id, request.question, request.lang, replay=request.replay)
    except Exception:
        logger.exception("Agent failed for school %s; returning deterministic fallback", request.school_id)
    try:
        return agent.deterministic_answer(request.school_id, request.lang, request.replay)
    except Exception:
        logger.exception("Deterministic answer failed for school %s", request.school_id)
    answer = "Saans' assistant is unavailable right now. Please use today's deterministic safety plan."
    if request.lang == "hi":
        answer = "Saans सहायक अभी उपलब्ध नहीं है। कृपया आज की निर्धारित सुरक्षा योजना देखें।"
    return {"answer": answer, "tools_used": [], "verified": False, "fallback": True, "model": None}


handler = Mangum(app)
