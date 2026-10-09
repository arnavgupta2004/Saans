from fastapi.testclient import TestClient

import app as api


def _rows() -> list[dict]:
    return [
        {"time": "2026-10-09T08:00", "pm25": 140, "pm10": 200, "pm25_cal": 140, "pm10_cal": 200, "calibrated": True},
        {"time": "2026-10-09T09:00", "pm25": 130, "pm10": 190, "pm25_cal": 130, "pm10_cal": 190, "calibrated": True},
        {"time": "2026-10-09T13:00", "pm25": 25, "pm10": 40, "pm25_cal": 25, "pm10_cal": 40, "calibrated": True},
    ]


def test_school_and_planning_endpoints(monkeypatch) -> None:
    monkeypatch.setattr(api, "_forecast", lambda school: (_rows(), {"forecast": "fixture", "observation": "fixture"}, "fixture"))
    client = TestClient(api.app)

    schools = client.get("/api/schools")
    assert schools.status_code == 200
    school_id = schools.json()[0]["id"]
    assert client.get(f"/api/schools/{school_id}").status_code == 200
    assert client.get(f"/api/schools/{school_id}/today").json()["mode"] == "fixture"
    assert client.get(f"/api/schools/{school_id}/week").status_code == 200
    assert client.get(f"/api/schools/{school_id}/best-day?start=09:00&end=12:00").status_code == 200
    assert client.post("/api/ask", json={"school_id": school_id, "question": "Is PE safe?"}).json()["tools_used"] == []


def test_unknown_school_is_404() -> None:
    assert TestClient(api.app).get("/api/schools/missing").status_code == 404


def test_ask_falls_back_when_agent_fails(monkeypatch) -> None:
    import saans.agent as agent
    monkeypatch.setattr(agent, "ask", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no bedrock")))
    c = TestClient(api.app)
    sid = c.get("/api/schools").json()[0]["id"]
    r = c.post("/api/ask", json={"school_id": sid, "question": "x"})
    assert r.status_code == 200 and r.json()["tools_used"] == []


def test_mode_reflects_forecast_not_observation(monkeypatch) -> None:
    import saans.forecast as fc
    monkeypatch.setattr(fc.OpenMeteoClient, "hourly", lambda self, la, lo, days=5: [{"time": "2026-10-09T09:00", "pm25": 50, "pm10": 60, "source": "live"}])
    monkeypatch.setattr(fc.CpcbClient, "latest_near", lambda self, la, lo: {"station": "S", "distance_km": 1, "pm25": 500, "pm10": 5, "source": "fixture"})
    rows, source, mode = fc.load_forecast(api._store().list()[0])
    assert mode == "live" and source["observation"] == "fixture" and rows[0]["calibrated"] is False and rows[0]["pm25_cal"] == 50


def test_agent_failure_is_logged_with_traceback(monkeypatch, caplog) -> None:
    import saans.agent as agent
    monkeypatch.setattr(agent, "ask", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom-bedrock")))
    c = TestClient(api.app)
    sid = c.get("/api/schools").json()[0]["id"]
    with caplog.at_level("ERROR"):
        c.post("/api/ask", json={"school_id": sid, "question": "x"})
    assert any(r.exc_info and "boom-bedrock" in str(r.exc_info[1]) for r in caplog.records)


def test_replay_delhi_nov_shows_indoors_and_a_swap() -> None:
    c = TestClient(api.app)
    r = c.get("/api/schools/delhi-anand-vihar/today?replay=delhi-nov")
    assert r.status_code == 200
    plan = r.json()
    assert plan["mode"] == "replay" and plan["replay_date"] == "2025-11-19" and plan["date"] == "2025-11-19"
    assert plan["sources"]["forecast"] == "recorded" and plan["now"]["time"] == "2025-11-19T08:00"
    assert any(p["action"]["level"] == "indoors" for p in plan["periods"])
    assert any(p["swap"] for p in plan["periods"])
    assert plan["generated_at"].endswith("+05:30")


def test_unknown_replay_is_404() -> None:
    assert TestClient(api.app).get("/api/schools/delhi-anand-vihar/today?replay=nope").status_code == 404


def test_live_plan_has_no_replay_date(monkeypatch) -> None:
    monkeypatch.setattr(api, "_forecast", lambda school: (_rows(), {"forecast": "live", "observation": "none"}, "live"))
    assert TestClient(api.app).get("/api/schools/delhi-anand-vihar/today").json()["replay_date"] is None



def test_ask_passes_replay_and_returns_verified(monkeypatch) -> None:
    import saans.agent as agent
    seen = {}
    def fake(school_id, question, lang="en", replay=None):
        seen["replay"] = replay
        return {"answer": "ok", "tools_used": [], "verified": True}
    monkeypatch.setattr(agent, "ask", fake)
    r = TestClient(api.app).post("/api/ask", json={"school_id": "delhi-anand-vihar", "question": "x", "replay": "delhi-nov"})
    assert seen["replay"] == "delhi-nov" and r.json()["verified"] is True


def test_ask_unknown_replay_404() -> None:
    assert TestClient(api.app).post("/api/ask", json={"school_id": "delhi-anand-vihar", "question": "x", "replay": "nope"}).status_code == 404


def test_ask_agent_failure_returns_deterministic_plan(monkeypatch) -> None:
    import saans.agent as agent
    monkeypatch.setattr(agent, "ask", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("404 model gone")))
    r = TestClient(api.app).post("/api/ask", json={"school_id": "delhi-anand-vihar", "question": "x", "replay": "delhi-nov"}).json()
    assert r["verified"] is False and r["fallback"] is True and "351" in r["answer"]
