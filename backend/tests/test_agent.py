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


def test_model_provider_gemini(monkeypatch) -> None:
    from strands.models.gemini import GeminiModel
    monkeypatch.setenv("MODEL_PROVIDER", "gemini"); monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL_ID", "some-gemini-id")
    m = agent._model()
    assert isinstance(m, GeminiModel) and m.config["model_id"] == "some-gemini-id"


def test_gemini_model_id_must_come_from_env(monkeypatch) -> None:
    import pytest
    monkeypatch.setenv("MODEL_PROVIDER", "gemini"); monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.delenv("GEMINI_MODEL_ID", raising=False)
    with pytest.raises(RuntimeError, match="GEMINI_MODEL_ID"):
        agent._model()


def test_no_hard_coded_gemini_model_names() -> None:
    import re
    from pathlib import Path
    src = Path(agent.__file__).read_text()
    assert not re.search(r"gemini-\d", src)


def test_model_provider_defaults_to_bedrock(monkeypatch) -> None:
    from strands.models import BedrockModel
    monkeypatch.delenv("MODEL_PROVIDER", raising=False)
    monkeypatch.setenv("BEDROCK_MODEL_ID", "some-bedrock-id")
    for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"): monkeypatch.setenv(k, "x")
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    assert isinstance(agent._model(), BedrockModel)
