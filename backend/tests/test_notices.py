from urllib.parse import unquote

import app as api
from saans.models import DayPlan
from saans.notices import build_notice
from saans.planner import plan_day
from saans.store import get_store
from tests.test_app import _rows


def _plan(mode="live") -> DayPlan:
    school = get_store().list()[0]
    return plan_day(school, _rows(), "2026-10-09", {"forecast": "x", "observation": "y"}, mode)


def test_notice_en_numbers_match_plan() -> None:
    plan = _plan()
    n = build_notice(plan, "en")
    assert any(str(p.aqi) in n["text"] for p in plan.periods if p.period.outdoor)
    assert unquote(n["whatsapp_url"].split("text=")[1]) == n["text"]
    assert n["mode"] == "live"


def test_notice_hi_and_mode_label() -> None:
    n = build_notice(_plan("fixture"), "hi")
    assert "प्रिय अभिभावकगण" in n["text"] and "नमूना डेटा" in n["text"]


def test_notice_endpoint(monkeypatch) -> None:
    from fastapi.testclient import TestClient
    monkeypatch.setattr(api, "_forecast", lambda s: (_rows(), {"forecast": "x", "observation": "y"}, "live"))
    c = TestClient(api.app)
    sid = c.get("/api/schools").json()[0]["id"]
    r = c.get(f"/api/schools/{sid}/notice?lang=hi")
    assert r.status_code == 200 and "whatsapp_url" in r.json()
