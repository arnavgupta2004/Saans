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
