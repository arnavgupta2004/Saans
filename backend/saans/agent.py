"""Strands agent. Tools return planner output; the LLM only explains it, and every number it states is checked."""
from __future__ import annotations

import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from typing import Any, Callable

from .forecast import load_forecast
from .models import DayPlan
from .notices import BAND_HI, build_notice
from .planner import best_day, plan_day
from .sources import load_replay
from .store import get_store

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are Saans, an assistant for school air-safety in India. "
    "Data provenance: the hourly forecast comes from Open-Meteo (CAMS model). When a plan says it is calibrated, "
    "it was bias-corrected with the latest reading from the named monitoring station (sources.station). "
    "Never call it a \"station forecast\": stations give current readings, Open-Meteo gives the forecast. "
    "Always state the forecast time or date and whether it is calibrated (and with which station) or uncalibrated. "
    "If the plan mode is 'replay', say it is recorded data from replay_date, not today. "
    "Only state AQI values, times, and counts that a tool returned; never estimate or compute new numbers. "
    "Safety actions and swaps come from get_day_plan; never override or soften them. If unsure, say so. "
    "Answer in the user's language (English or Hindi). Be brief."
)


def _forecast(school, replay: str | None = None):
    if replay:
        rows, _ = load_replay(replay)
        return rows, {"forecast": "recorded", "observation": "none"}
    rows, src, _ = load_forecast(school)
    return rows, src


def _school(school_id: str):
    school = get_store().get(school_id)
    if school is None:
        raise ValueError(f"Unknown school {school_id}")
    return school


def make_tools(replay: str | None = None, sink: list | None = None) -> list[Callable]:
    """Agent tools bound to one request's context (live or a replay key). Every output is recorded in `sink`
    so the answer's numbers can be checked against exactly what the model saw."""
    def _out(value):
        if sink is not None:
            sink.append(value)
        return value

    def _plan(school_id: str, date: str = "") -> DayPlan:
        school = _school(school_id)
        rows, src = _forecast(school, replay)
        day = date or rows[0]["time"][:10]
        if replay:
            return plan_day(school, rows, day, src, "replay", replay_date=rows[0]["time"][:10])
        return plan_day(school, rows, day, src)

    def get_school(school_id: str) -> dict:
        """Return the school profile and timetable."""
        return _out(_school(school_id).model_dump())

    def get_day_plan(school_id: str, date: str = "") -> dict:
        """Return the deterministic per-period AQI plan (actions, swaps) for a date (YYYY-MM-DD, default today)."""
        return _out(_plan(school_id, date).model_dump())

    def get_hourly_forecast(school_id: str, date: str = "") -> list[dict]:
        """Return calibrated hourly PM2.5/PM10 forecast points for a date."""
        rows, _ = _forecast(_school(school_id), replay)
        d = date or rows[0]["time"][:10]
        return _out([r for r in rows if r["time"].startswith(d)])

    def find_best_day(school_id: str, start: str = "09:00", end: str = "12:00") -> dict:
        """Rank the coming days by worst calibrated AQI inside the HH:MM window."""
        school = _school(school_id)
        rows, _ = _forecast(school, replay)
        return _out(best_day(school, rows, start, end))

    def draft_notice(school_id: str, date: str = "", lang: str = "en") -> dict:
        """Return the deterministic parent notice text and WhatsApp URL."""
        return _out(build_notice(_plan(school_id, date), lang))

    return [get_school, get_day_plan, get_hourly_forecast, find_best_day, draft_notice]


TOOLS = make_tools()
get_school, get_day_plan, get_hourly_forecast, find_best_day, draft_notice = TOOLS

_NUMBER = re.compile(r"\d+(?:\.\d+)?")


def _numbers(text: str) -> set[float]:
    return {float(n) for n in _NUMBER.findall(text)}


def unverified_numbers(answer: str, context: list[str], minimum: float = 20) -> list[float]:
    """Numbers >= `minimum` in the answer that appear nowhere in the context (tool outputs, question, school)."""
    allowed: set[float] = set().union(*(_numbers(c) for c in context)) if context else set()
    seen: list[float] = []
    for n in _NUMBER.findall(answer):
        value = float(n)
        if value >= minimum and value not in allowed and value not in seen:
            seen.append(value)
    return seen


def deterministic_answer(school_id: str, lang: str = "en", replay: str | None = None) -> dict:
    """Plan summary straight from the planner (no LLM): every number comes from the DayPlan."""
    get_plan = make_tools(replay)[1]
    plan = DayPlan(**get_plan(school_id))
    hi = lang == "hi"
    when = f"recorded data from {plan.replay_date}" if plan.mode == "replay" else f"{plan.date}, {plan.mode} forecast"
    if hi:
        when = f"{plan.replay_date} का रिकॉर्ड किया गया डेटा" if plan.mode == "replay" else f"{plan.date}, {plan.mode} पूर्वानुमान"
    lines = [("आज की योजना" if hi else "Today's plan") + f" ({when}):"]
    for p in plan.periods:
        if not p.period.outdoor:
            continue
        band = BAND_HI.get(p.band, p.band) if hi else p.band
        text = p.action.text_hi if hi else p.action.text_en
        line = f"• {p.period.label} {p.period.start}–{p.period.end}: AQI {p.aqi} ({band}) — {text}"
        if p.swap:
            line += f" ⇄ {p.swap.with_label} {p.swap.to_start} (AQI {p.swap.to_aqi})"
        lines.append(line)
    return {"answer": "\n".join(lines), "tools_used": [], "verified": False, "fallback": True, "model": None}


def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not set (configure it via the SAM template parameters)")
    return value


def _model(model_id: str | None = None):
    """Bedrock by default; MODEL_PROVIDER=gemini uses Strands' Gemini provider. Model ids come only from env (SAM params)."""
    if _provider() == "gemini":
        from strands.models.gemini import GeminiModel
        # Per-request timeout: an overloaded Gemini can take ~18 s just to return 503, which would eat the whole budget.
        return GeminiModel(client_args={"api_key": _env("GEMINI_API_KEY"), "http_options": {"timeout": int(_attempt_timeout_s() * 1000)}},
                           model_id=model_id or _env("GEMINI_MODEL_ID"))
    from strands.models import BedrockModel
    return BedrockModel(model_id=model_id or _env("BEDROCK_MODEL_ID"), region_name=os.getenv("AWS_REGION", "us-east-1"))


def _attempt_timeout_s() -> float:
    return float(os.getenv("GEMINI_ATTEMPT_TIMEOUT_S", "6"))


def _provider() -> str:
    return os.getenv("MODEL_PROVIDER", "bedrock").lower()


def _candidate_models() -> list[str]:
    """Primary model, then (Gemini only) the lighter GEMINI_FALLBACK_MODEL_ID if configured."""
    if _provider() != "gemini":
        return [_env("BEDROCK_MODEL_ID")]
    fallback = os.getenv("GEMINI_FALLBACK_MODEL_ID", "").strip()
    primary = _env("GEMINI_MODEL_ID")
    return [primary] + ([fallback] if fallback and fallback != primary else [])


_RETRY_CODES = {429, 500, 503, 504}
_BACKOFF_S = (0.5, 1.5)
_sleep = time.sleep


def _retryable(exc: BaseException) -> bool:
    """Overload / rate-limit / timeout errors worth retrying (Gemini 503 UNAVAILABLE, 429 RESOURCE_EXHAUSTED)."""
    for e in (exc, exc.__cause__):
        if e is None:
            continue
        code = getattr(e, "code", None) or getattr(e, "status_code", None)
        if code in _RETRY_CODES or isinstance(e, TimeoutError) or type(e).__name__ in {"ModelThrottledException", "TimeoutException", "ReadTimeout", "ConnectTimeout"}:
            return True
        if any(word in str(e) for word in ("UNAVAILABLE", "RESOURCE_EXHAUSTED", "high demand")):
            return True
    return False


def _invoke(model_id: str, tools: list[Callable], prompt: str) -> tuple[str, list[str]]:
    from strands import Agent, tool

    # retry_strategy=None turns off Strands' own retries (6 attempts from 4 s) so our budgeted policy decides.
    agent = Agent(model=_model(model_id), system_prompt=SYSTEM_PROMPT, tools=[tool(f) for f in tools], retry_strategy=None)
    result = agent(prompt)
    return str(result), [name for name in getattr(result.metrics, "tool_metrics", {}) or {}]


def _run_agent(tools: list[Callable], prompt: str, deadline: float | None = None) -> tuple[str, list[str], str]:
    """Try each candidate model; retry transient errors up to 2 times (0.5 s, 1.5 s) while the deadline allows.
    Budget rule: retry a model only if the remaining time still covers the retry plus one attempt for every later
    model; start an attempt only if one attempt (GEMINI_ATTEMPT_TIMEOUT_S) fits. Non-retryable errors (e.g. 404)
    move straight to the next model. Raises the last error."""
    last: BaseException | None = None
    per = _attempt_timeout_s()
    left = (lambda: deadline - time.monotonic()) if deadline is not None else (lambda: float("inf"))
    models = _candidate_models()
    for i, model_id in enumerate(models):
        later = len(models) - i - 1
        for attempt in range(len(_BACKOFF_S) + 1):
            if last is not None and attempt == 0 and left() < per:
                logger.warning("Skipping model %s: %.1fs left, attempt needs %.1fs", model_id, left(), per)
                assert last is not None
                raise last
            try:
                answer, used = _invoke(model_id, tools, prompt)
                logger.info("Agent answered with model %s (attempt %d)", model_id, attempt + 1)
                return answer, used, model_id
            except Exception as exc:
                last = exc
                logger.warning("Model %s attempt %d failed: %s: %s", model_id, attempt + 1, type(exc).__name__, exc)
                if not _retryable(exc) or attempt == len(_BACKOFF_S):
                    break
                delay = _BACKOFF_S[attempt]
                if left() < delay + per * (1 + later):
                    break  # retrying would starve the fallback model (or overrun); move on
                _sleep(delay)
    assert last is not None
    raise last


def ask(school_id: str, question: str, lang: str = "en", replay: str | None = None) -> dict:
    """Run the Strands agent in the screen's context (live or replay). Raises on model failure; caller logs and falls back.
    Number guard: any number >= 20 not found in this request's tool outputs, the question, or the school profile
    makes us return the deterministic answer instead."""
    sink: list[Any] = []
    context = f"[school_id={school_id}] [lang={lang}]" + (f" [context: recorded replay day '{replay}', not today]" if replay else "")
    # API Gateway cuts requests at 30 s; give the model a budget and fall back to the plan summary if it is slow.
    budget = float(os.getenv("AGENT_TIMEOUT_S", "20"))
    pool = ThreadPoolExecutor(max_workers=1)
    future = pool.submit(_run_agent, make_tools(replay, sink), f"{context} {question}", time.monotonic() + budget)
    try:
        answer, used, model = future.result(timeout=budget)
    except FutureTimeout:
        logger.warning("Agent timed out after %.1fs for school %s; returning deterministic answer", budget, school_id)
        return {**deterministic_answer(school_id, lang, replay), "timed_out": True}
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
    evidence = [json.dumps(x, default=str, ensure_ascii=False) for x in sink] + [question, json.dumps(_school(school_id).model_dump())]
    bad = unverified_numbers(answer, evidence)
    if bad:
        logger.warning("Agent answer had numbers not in tool outputs %s; returning deterministic answer. Answer was: %r", bad, answer)
        return deterministic_answer(school_id, lang, replay)
    return {"answer": answer, "tools_used": used, "verified": True, "model": model}
