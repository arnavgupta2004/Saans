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


def _replay_plan() -> DayPlan:
    from saans.sources import load_replay
    rows, day = load_replay("delhi-nov")
    return plan_day(get_store().get("delhi-anand-vihar"), rows, day, {"forecast": "recorded", "observation": "none"}, "replay", replay_date=day)


def test_notice_never_says_moved_for_optional_swap() -> None:
    plan = _plan()
    plan.periods = [p for p in plan.periods]
    from saans.models import Swap
    pe = next(p for p in plan.periods if p.period.type == "pe")
    pe.swap = Swap(to_start="10:00", to_end="10:40", to_aqi=88, to_band="Satisfactory", gain_bands=1, optional=True, with_period_id="p3", with_label="Period 3")
    for lang in ("en", "hi"):
        text = build_notice(plan, lang)["text"]
        assert "moved" not in text and "स्थानांतरित" not in text and "10:00" not in text


def test_required_swap_is_offered_not_announced() -> None:
    en = build_notice(_replay_plan(), "en")["text"]
    assert "Class 7B PE (08:40): Hold PE indoors, or move it to 13:40 (Moderate, AQI 127)." in en
    hi = build_notice(_replay_plan(), "hi")["text"]
    assert "13:40" in hi and "स्थानांतरित" not in hi


def test_sensitive_line_is_labelled() -> None:
    assert "• Students with asthma: Keep sensitive students indoors and inform parents." in build_notice(_replay_plan(), "en")["text"]
    assert "• अस्थमा वाले विद्यार्थी:" in build_notice(_replay_plan(), "hi")["text"]


def test_notice_endpoint_supports_replay() -> None:
    from fastapi.testclient import TestClient
    r = TestClient(api.app).get("/api/schools/delhi-anand-vihar/notice?lang=en&replay=delhi-nov")
    assert r.status_code == 200 and "AQI 351" in r.json()["text"] and r.json()["mode"] == "replay"
