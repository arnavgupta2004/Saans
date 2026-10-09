"""Public-deployment hardening: input limits, rate limit, CORS, validation, no stack traces."""
from fastapi.testclient import TestClient

import app as api

AMPLIFY = "https://main.d6f34l6r9rpi9.amplifyapp.com"
SID = "delhi-anand-vihar"


def _client():
    return TestClient(api.app, raise_server_exceptions=False)


def test_question_longer_than_300_chars_is_rejected_cleanly() -> None:
    r = _client().post("/api/ask", json={"school_id": SID, "question": "x" * 301})
    assert r.status_code == 422
    body = r.json()
    assert "300" in body["detail"] and "x" * 50 not in r.text  # no echo of the input


def test_ask_rate_limit_per_ip(monkeypatch) -> None:
    import saans.agent as agent
    monkeypatch.setattr(agent, "ask", lambda *a, **k: {"answer": "ok", "tools_used": [], "verified": True, "model": "m"})
    api.RATE_LIMITER.reset()
    c = _client()
    h = {"X-Forwarded-For": "203.0.113.7"}
    codes = [c.post("/api/ask", json={"school_id": SID, "question": "q"}, headers=h).status_code for _ in range(11)]
    assert codes[:10] == [200] * 10 and codes[10] == 429
    r = c.post("/api/ask", json={"school_id": SID, "question": "q"}, headers=h)
    assert "minute" in r.json()["detail"] and r.headers.get("retry-after")
    # another IP is unaffected
    assert c.post("/api/ask", json={"school_id": SID, "question": "q"}, headers={"X-Forwarded-For": "198.51.100.1"}).status_code == 200


def test_rate_limiter_fails_open_when_store_breaks(monkeypatch) -> None:
    import saans.agent as agent
    monkeypatch.setattr(agent, "ask", lambda *a, **k: {"answer": "ok", "tools_used": [], "verified": True, "model": "m"})
    monkeypatch.setattr(api.RATE_LIMITER, "hit", lambda key: (_ for _ in ()).throw(RuntimeError("dynamo down")))
    assert _client().post("/api/ask", json={"school_id": SID, "question": "q"}).status_code == 200


def test_dynamo_rate_counter_uses_ttl() -> None:
    from saans.ratelimit import DynamoRateLimiter
    calls = {}
    class Table:
        def update_item(self, **kw):
            calls.update(kw)
            return {"Attributes": {"n": 3}}
    rl = DynamoRateLimiter(table=Table(), limit=10, window_s=60)
    assert rl.hit("1.2.3.4") == 3
    assert calls["Key"]["key"].startswith("rl#ask#1.2.3.4#") and ":ttl" in calls["ExpressionAttributeValues"]


def test_cors_only_amplify_and_localhost() -> None:
    c = _client()
    pre = lambda origin: c.options("/api/ask", headers={"Origin": origin, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"})
    assert pre(AMPLIFY).headers.get("access-control-allow-origin") == AMPLIFY
    assert pre("http://localhost:5173").headers.get("access-control-allow-origin") == "http://localhost:5173"
    bad = pre("https://evil.example.com")
    assert bad.status_code == 400 and "access-control-allow-origin" not in bad.headers


def test_bad_school_ids_and_replay_keys_404() -> None:
    c = _client()
    assert c.get("/api/schools/nope/today").status_code == 404
    assert c.get("/api/schools/" + "a" * 200 + "/today").status_code == 404
    assert c.get("/api/schools/Bad_ID!/week").status_code == 404
    r = c.get(f"/api/schools/{SID}/today?replay=<script>")
    assert r.status_code == 404 and "<script>" not in r.text
    assert c.get(f"/api/schools/{SID}/notice?replay=nope").status_code == 404
    assert c.post("/api/ask", json={"school_id": SID, "question": "q", "replay": "nope"}).status_code == 404
    assert c.post("/api/ask", json={"school_id": "nope", "question": "q"}).status_code == 404


def test_save_school_rejects_bad_ids_and_huge_timetables() -> None:
    c = _client()
    base = {"name": "N", "city": "C", "lat": 0, "lon": 0, "timetable": []}
    assert c.post("/api/schools", json={**base, "id": "Bad ID!"}).status_code == 422
    big = [{"id": f"p{i}", "label": "L", "start": "08:00", "end": "08:40", "type": "class", "intensity": "low", "outdoor": False, "swappable": True} for i in range(41)]
    assert c.post("/api/schools", json={**base, "id": "custom-x", "timetable": big}).status_code == 422
    assert c.post("/api/schools", json={**base, "id": "custom-ok"}).status_code == 200


def test_unhandled_errors_never_echo_tracebacks(monkeypatch) -> None:
    monkeypatch.setattr(api, "_day_plan", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("SECRET internal detail /var/task/app.py")))
    r = _client().get(f"/api/schools/{SID}/today")
    assert r.status_code == 500 and r.json() == {"detail": "Internal error"} and "SECRET" not in r.text and "Traceback" not in r.text
