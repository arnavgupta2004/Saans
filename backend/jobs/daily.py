"""EventBridge Scheduler entry point (06:00 IST): compute today's DayPlan for every school and cache it.

Cache item (saans-cache, key "<school_id>#<YYYY-MM-DD>"): the calibrated hourly rows, sources and mode used,
the plan computed at 06:00, and stored_at. /today re-plans from the cached rows (so `now` stays current)
and serves it as mode "cached" while it is < 3 h old.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime

from saans.forecast import load_forecast
from saans.planner import IST, plan_day
from saans.store import get_plan_cache, get_store

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def cache_key(school_id: str, date: str) -> str:
    return f"{school_id}#{date}"


def handler(event: dict, context: object) -> dict:
    today = datetime.now(IST).date().isoformat()
    cache = get_plan_cache()
    stored: list[str] = []
    failed: list[str] = []
    for school in get_store().list():
        try:
            rows, source, mode = load_forecast(school)
            day_rows = [r for r in rows if r["time"].startswith(today)]
            plan = plan_day(school, day_rows, today, source, mode)
            cache.put(cache_key(school.id, today), {"plan": plan.model_dump(mode="json"), "rows": day_rows, "sources": source,
                                                     "mode": mode, "stored_at": time.time()})
            stored.append(school.id)
        except Exception:
            logger.exception("Daily plan failed for school %s", school.id)
            failed.append(school.id)
    logger.info("Daily job %s: stored=%s failed=%s", today, stored, failed)
    return {"ok": not failed, "date": today, "stored": stored, "failed": failed}
