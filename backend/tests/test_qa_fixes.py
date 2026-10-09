"""Fixes from the judge/QA pass (2026-10-10)."""
from fastapi.testclient import TestClient

import app as api
from saans.models import Period, School
from saans.planner import best_day, plan_day


def _hr(h, pm):
    return {"time": f"2026-10-09T{h:02d}:00", "pm25": pm, "pm10": pm, "pm25_cal": pm, "pm10_cal": pm}


def test_demo_schools_are_read_only() -> None:
    c = TestClient(api.app)
    school = c.get("/api/schools/delhi-anand-vihar").json()
    school["timetable"] = []
    r = c.post("/api/schools", json=school)
    assert r.status_code == 403
    assert c.get("/api/schools/delhi-anand-vihar").json()["timetable"]  # unchanged


def test_period_ending_on_the_hour_excludes_that_hour() -> None:
    p = Period(id="c", label="P2", start="09:20", end="10:00", type="class", intensity="low", outdoor=True, swappable=True)
    s = School(id="z", name="Z", city="D", lat=0, lon=0, timetable=[p])
    plan = plan_day(s, [_hr(9, 20), _hr(10, 300)], "2026-10-09")
    assert plan.periods[0].aqi < 100  # the 10:00 hour belongs to the next period


def test_severe_pe_swaps_into_clean_morning_class() -> None:
    t = lambda i, s, e, typ, inten, out: Period(id=i, label=i, start=s, end=e, type=typ, intensity=inten, outdoor=out, swappable=True)
    s = School(id="z", name="Z", city="D", lat=0, lon=0, timetable=[t("p2", "09:20", "10:00", "class", "low", False), t("pe", "13:00", "13:40", "pe", "high", True)])
    plan = plan_day(s, [_hr(9, 30), _hr(10, 300), _hr(13, 400)], "2026-10-09")
    assert plan.periods[1].swap and plan.periods[1].swap.with_period_id == "p2"


def test_best_day_band_matches_max_aqi() -> None:
    from saans.aqi import band_for_aqi
    rows = [{"time": f"2026-10-{d}T{h:02d}:00", "pm25": pm, "pm10": pm} for d, pm in (("09", 70), ("10", 100)) for h in range(24)]
    rows += [{"time": f"2026-10-09T03:00", "pm25": 400, "pm10": 400}]  # night spike outside the window must not set the band
    for r in best_day(School(id="z", name="Z", city="D", lat=0, lon=0, timetable=[]), rows, "09:00", "12:00")["ranking"]:
        assert r["band"] == band_for_aqi(r["max_aqi"])


def test_in_memory_forecast_cache_is_not_labelled_cached(monkeypatch) -> None:
    import saans.forecast as fc
    monkeypatch.setattr(fc.OpenMeteoClient, "hourly", lambda self, la, lo, days=5: [{"time": "2026-10-09T09:00", "pm25": 50, "pm10": 60, "source": "cached"}])
    monkeypatch.setattr(fc, "observe", lambda la, lo: (None, "Not calibrated: test"))
    _, src, mode = fc.load_forecast(api._store().list()[0])
    assert mode == "live" and src["forecast"] == "live"
