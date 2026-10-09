import json
import time
from datetime import datetime

from fastapi.testclient import TestClient

import app as api
from jobs import daily
from saans.planner import IST
from saans.store import JsonPlanCache


def _fixture_rows(day: str) -> list[dict]:
    """A full 24-hour day built from the recorded Open-Meteo fixture values (the fixture itself has 6 hours)."""
    h = json.load(open("fixtures/open_meteo_delhi_anand_vihar.json"))["hourly"]
    n = len(h["pm2_5"])
    return [{"time": f"{day}T{i:02d}:00", "pm25": h["pm2_5"][i % n], "pm10": h["pm10"][i % n], "source": "live",
             "pm25_cal": h["pm2_5"][i % n], "pm10_cal": h["pm10"][i % n], "calibrated": False} for i in range(24)]


def _setup(monkeypatch, tmp_path):
    cache = JsonPlanCache(tmp_path / "plans.json")
    today = datetime.now(IST).date().isoformat()
    src = {"forecast": "live", "observation": "none", "station": None, "distance_km": None, "note": "Not calibrated: test"}
    monkeypatch.setattr(daily, "get_plan_cache", lambda: cache)
    monkeypatch.setattr(api, "get_plan_cache", lambda: cache)
    monkeypatch.setattr(daily, "load_forecast", lambda school: (_fixture_rows(today), src, "live"))
    return cache, today


def test_handler_stores_plan_per_school(monkeypatch, tmp_path) -> None:
    cache, today = _setup(monkeypatch, tmp_path)
    out = daily.handler({}, None)
    assert out["ok"] is True and out["failed"] == [] and len(out["stored"]) == 3
    item = cache.get(f"delhi-anand-vihar#{today}")
    assert item and item["plan"]["school_id"] == "delhi-anand-vihar" and item["plan"]["date"] == today and item["rows"]
    assert time.time() - item["stored_at"] < 60


def test_handler_continues_when_one_school_fails(monkeypatch, tmp_path) -> None:
    cache, today = _setup(monkeypatch, tmp_path)
    good = daily.load_forecast
    def flaky(school):
        if school.id == "delhi-dwarka": raise RuntimeError("open-meteo down")
        return good(school)
    monkeypatch.setattr(daily, "load_forecast", flaky)
    out = daily.handler({}, None)
    assert out["failed"] == ["delhi-dwarka"] and len(out["stored"]) == 2 and out["ok"] is False


def test_today_serves_fresh_cache_as_cached(monkeypatch, tmp_path) -> None:
    cache, today = _setup(monkeypatch, tmp_path)
    daily.handler({}, None)
    monkeypatch.setattr(api, "_forecast", lambda school: (_ for _ in ()).throw(AssertionError("live should not be called")))
    plan = TestClient(api.app).get("/api/schools/delhi-anand-vihar/today").json()
    assert plan["mode"] == "cached" and plan["date"] == today and plan["sources"]["note"] == "Not calibrated: test"
    assert plan["now"]["time"][11:13] == f"{datetime.now(IST).hour:02d}"  # now = current hour, not 06:00


def test_today_ignores_stale_cache(monkeypatch, tmp_path) -> None:
    cache, today = _setup(monkeypatch, tmp_path)
    daily.handler({}, None)
    item = cache.get(f"delhi-anand-vihar#{today}"); item["stored_at"] -= 4 * 3600; cache.put(f"delhi-anand-vihar#{today}", item)
    rows = _fixture_rows(today)
    monkeypatch.setattr(api, "_forecast", lambda school: (rows, {"forecast": "live", "observation": "none"}, "live"))
    assert TestClient(api.app).get("/api/schools/delhi-anand-vihar/today").json()["mode"] == "live"


def test_today_goes_live_when_cache_broken(monkeypatch, tmp_path) -> None:
    _, today = _setup(monkeypatch, tmp_path)
    class Broken:
        def get(self, key): raise RuntimeError("dynamo down")
    monkeypatch.setattr(api, "get_plan_cache", lambda: Broken())
    rows = _fixture_rows(today)
    monkeypatch.setattr(api, "_forecast", lambda school: (rows, {"forecast": "live", "observation": "none"}, "live"))
    r = TestClient(api.app).get("/api/schools/delhi-anand-vihar/today")
    assert r.status_code == 200 and r.json()["mode"] == "live"
