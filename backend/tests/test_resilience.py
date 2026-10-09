"""T23: force each external dependency to fail; the API must still answer 200 with honest labels."""
import httpx
import pytest
from fastapi.testclient import TestClient

import app as api
import saans.agent as agent
import saans.forecast as fc
from saans.sources import OpenAqUnavailable, _Cache

SID = "delhi-anand-vihar"


@pytest.fixture(autouse=True)
def _fresh(monkeypatch):
    _Cache.values.clear()
    monkeypatch.setattr(agent, "_sleep", lambda s: None)
    monkeypatch.setenv("MODEL_PROVIDER", "gemini"); monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GEMINI_MODEL_ID", "primary"); monkeypatch.setenv("GEMINI_FALLBACK_MODEL_ID", "lite")
    monkeypatch.delenv("OPENAQ_API_KEY", raising=False); monkeypatch.delenv("DATA_GOV_IN_API_KEY", raising=False)


class _Gemini503(Exception):
    code = 503


def _gemini_down(monkeypatch):
    calls = []
    def invoke(model_id, tools, prompt):
        calls.append(model_id); raise _Gemini503("This model is currently experiencing high demand")
    monkeypatch.setattr(agent, "_invoke", invoke)
    return calls


def _network_down(monkeypatch):
    """Every outbound HTTP call fails (Open-Meteo, data.gov.in, OpenAQ)."""
    def boom(self, *a, **k): raise httpx.ConnectError("[Errno 111] Connection refused")
    monkeypatch.setattr(httpx.Client, "get", boom)


def _live_open_meteo(monkeypatch):
    rows = [{"time": f"2026-10-09T{h:02d}:00", "pm25": 80 + h, "pm10": 120 + h, "source": "live"} for h in range(24)]
    monkeypatch.setattr(fc.OpenMeteoClient, "hourly", lambda self, la, lo, days=5: [dict(r) for r in rows])


def test_open_meteo_down_today_is_fixture_labelled(monkeypatch) -> None:
    _network_down(monkeypatch)
    r = TestClient(api.app).get(f"/api/schools/{SID}/today")
    assert r.status_code == 200
    d = r.json()
    assert d["mode"] == "fixture" and d["sources"]["forecast"] == "fixture" and d["now"]["calibrated"] is False
    assert d["sources"]["station"] is None and d["sources"]["note"].startswith("Not calibrated")


def test_openaq_down_today_is_live_but_uncalibrated(monkeypatch) -> None:
    _live_open_meteo(monkeypatch)
    monkeypatch.setattr(fc.CpcbClient, "latest_near", lambda self, la, lo: (_ for _ in ()).throw(httpx.ConnectError("refused")))
    monkeypatch.setattr(fc.OpenAqClient, "latest_near", lambda self, la, lo: (_ for _ in ()).throw(httpx.ConnectError("openaq down")))
    d = TestClient(api.app).get(f"/api/schools/{SID}/today").json()
    assert d["mode"] == "live" and d["now"]["calibrated"] is False and d["sources"]["observation"] == "none"
    assert d["sources"]["note"] == "Not calibrated: CPCB (data.gov.in) unreachable; OpenAQ unavailable"


def test_openaq_stale_note(monkeypatch) -> None:
    _live_open_meteo(monkeypatch)
    monkeypatch.setattr(fc.CpcbClient, "latest_near", lambda self, la, lo: (_ for _ in ()).throw(httpx.ConnectError("refused")))
    monkeypatch.setattr(fc.OpenAqClient, "latest_near", lambda self, la, lo: (_ for _ in ()).throw(OpenAqUnavailable("x", "nearest CPCB monitor via OpenAQ last reported 50 h ago")))
    assert TestClient(api.app).get(f"/api/schools/{SID}/today").json()["sources"]["note"].endswith("50 h ago")


def test_gemini_down_ask_returns_plan_summary(monkeypatch) -> None:
    calls = _gemini_down(monkeypatch)
    r = TestClient(api.app).post("/api/ask", json={"school_id": SID, "question": "Is PE safe?", "replay": "delhi-nov"})
    assert r.status_code == 200
    d = r.json()
    assert d["fallback"] is True and d["verified"] is False and d["model"] is None and "351" in d["answer"]
    assert calls == ["primary"] * 3 + ["lite"] * 3  # 2 retries each, then fallback model, then plan summary


def test_gemini_down_live_ask_labels_forecast_source(monkeypatch) -> None:
    _gemini_down(monkeypatch); _network_down(monkeypatch)
    d = TestClient(api.app).post("/api/ask", json={"school_id": SID, "question": "Is PE safe?"}).json()
    assert d["fallback"] is True and "fixture forecast" in d["answer"]


def test_everything_down_still_200(monkeypatch) -> None:
    _gemini_down(monkeypatch); _network_down(monkeypatch)
    c = TestClient(api.app)
    for path in (f"/api/schools/{SID}/today", f"/api/schools/{SID}/today?replay=delhi-nov", f"/api/schools/{SID}/week", f"/api/schools/{SID}/notice"):
        assert c.get(path).status_code == 200, path
    assert c.post("/api/ask", json={"school_id": SID, "question": "x"}).status_code == 200
