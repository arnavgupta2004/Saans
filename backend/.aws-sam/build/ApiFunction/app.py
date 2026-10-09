"""Saans HTTP API; decisions are produced only by the deterministic planner."""
from __future__ import annotations

import logging
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel

from saans.forecast import load_forecast
from saans.models import DayPlan, School
from saans.planner import best_day, plan_day, plan_week
from saans.store import SchoolStore, get_store


logger = logging.getLogger(__name__)
app = FastAPI(title="Saans", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:8000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


def _store() -> SchoolStore:
    return get_store()


def _school_or_404(school_id: str) -> School:
    school = _store().get(school_id)
    if school is None:
        raise HTTPException(status_code=404, detail="School not found")
    return school


def _forecast(school: School) -> tuple[list[dict], dict, str]:
    return load_forecast(school)


def _day_plan(school: School, replay: str | None = None) -> DayPlan:
    rows, source, mode = _forecast(school)
    date = replay or rows[0]["time"][:10]
    try:
        return plan_day(school, rows, date, source, "replay" if replay else mode)
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
def notice(school_id: str, lang: Literal["en", "hi"] = "en", polish: bool = False) -> dict:
    if polish:
        raise HTTPException(status_code=501, detail="Notice polishing is not available yet")
    from saans.notices import build_notice
    return build_notice(_day_plan(_school_or_404(school_id)), lang)


class AskRequest(BaseModel):
    school_id: str
    question: str
    lang: Literal["en", "hi"] = "en"


@app.post("/api/ask")
def ask(request: AskRequest) -> dict:
    _school_or_404(request.school_id)
    try:
        from saans.agent import ask as agent_ask
        return agent_ask(request.school_id, request.question, request.lang)
    except Exception:
        logger.exception("Agent failed for school %s; returning deterministic fallback", request.school_id)
        answer = "Saans' assistant is unavailable right now. Please use today's deterministic safety plan."
        if request.lang == "hi":
            answer = "Saans सहायक अभी उपलब्ध नहीं है। कृपया आज की निर्धारित सुरक्षा योजना देखें।"
        return {"answer": answer, "tools_used": []}


handler = Mangum(app)
