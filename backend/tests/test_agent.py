import saans.agent as agent
from tests.test_app import _rows


def test_tool_shapes(monkeypatch) -> None:
    monkeypatch.setattr(agent, "_forecast", lambda s: (_rows(), {"forecast": "fixture", "observation": "fixture"}))
    sid = agent.get_store().list()[0]["id"] if isinstance(agent.get_store().list()[0], dict) else agent.get_store().list()[0].id
    assert agent.get_school(sid)["id"] == sid
    plan = agent.get_day_plan(sid)
    assert plan["periods"] and "aqi" in plan["periods"][0]
    assert agent.get_hourly_forecast(sid, "2026-10-09")
    assert "ranking" in agent.find_best_day(sid)
    assert "whatsapp_url" in agent.draft_notice(sid, "", "hi")
