import saans.agent as agent
from tests.test_app import _rows


def test_tool_shapes(monkeypatch) -> None:
    monkeypatch.setattr(agent, "_forecast", lambda s, replay=None: (_rows(), {"forecast": "fixture", "observation": "fixture"}))
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



# --- replay context + number guard ---
SID = "delhi-anand-vihar"


def test_tools_bound_to_replay_use_replay_plan() -> None:
    sink = []
    tools = {f.__name__: f for f in agent.make_tools(replay="delhi-nov", sink=sink)}
    plan = tools["get_day_plan"](SID)
    assert plan["mode"] == "replay" and plan["replay_date"] == "2025-11-19"
    assert all(r["time"].startswith("2025-11-19") for r in tools["get_hourly_forecast"](SID))
    assert tools["find_best_day"](SID)["ranking"][0]["date"] == "2025-11-19"
    assert len(sink) == 3


def test_tool_names_and_docs_are_preserved() -> None:
    names = [f.__name__ for f in agent.make_tools()]
    assert names == ["get_school", "get_day_plan", "get_hourly_forecast", "find_best_day", "draft_notice"]
    assert all(f.__doc__ for f in agent.make_tools())


def test_unverified_numbers() -> None:
    ctx = ['{"aqi": 351, "start": "08:40", "to_aqi": 127, "date": "2025-11-19"}']
    assert agent.unverified_numbers("PE at 08:40: AQI 351, swap to 127 on 2025-11-19. PM2.5 is the main pollutant; Class 7B.", ctx) == []
    assert agent.unverified_numbers("AQI is 83 at 13:40", ctx) == [83.0]  # 13 < 20 ignored; 40 appears in 08:40


def _fake_agent(answer_fn):
    def run(tools, prompt, deadline=None):
        t = {f.__name__: f for f in tools}
        plan = t["get_day_plan"](SID)
        return answer_fn(plan), ["get_day_plan"], "fake-model"
    return run


def test_invented_aqi_is_replaced_by_deterministic_answer(monkeypatch, caplog) -> None:
    monkeypatch.setattr(agent, "_run_agent", _fake_agent(lambda plan: "Class 7B PE can swap to Period 8 where AQI is 83."))
    with caplog.at_level("WARNING"):
        r = agent.ask(SID, "Is PE safe?", "en", replay="delhi-nov")
    assert r["verified"] is False and r["fallback"] is True and "83" not in r["answer"]
    assert "Class 7B PE" in r["answer"] and "351" in r["answer"] and "127" in r["answer"]
    assert any("83" in m for m in caplog.messages)


def test_grounded_answer_is_verified(monkeypatch) -> None:
    def answer(plan):
        pe = next(p for p in plan["periods"] if p["period"]["label"] == "Class 7B PE")
        return f"Class 7B PE at {pe['period']['start']} has AQI {pe['aqi']}; swap to {pe['swap']['to_start']} (AQI {pe['swap']['to_aqi']})."
    monkeypatch.setattr(agent, "_run_agent", _fake_agent(answer))
    r = agent.ask(SID, "Is PE safe?", "en", replay="delhi-nov")
    assert r["verified"] is True and "351" in r["answer"] and r.get("fallback") is not True


def test_numbers_from_question_and_school_are_allowed(monkeypatch) -> None:
    monkeypatch.setattr(agent, "_run_agent", lambda tools, prompt, deadline=None: ("38 students with asthma; you asked about 45 minutes.", [], "fake-model"))
    assert agent.ask(SID, "Can we do 45 minutes?", "en", replay="delhi-nov")["verified"] is True


def test_deterministic_answer_hindi() -> None:
    r = agent.deterministic_answer(SID, "hi", "delhi-nov")
    assert "351" in r["answer"] and "Class 7B PE" in r["answer"] and r["fallback"] is True


def test_system_prompt_wording() -> None:
    p = agent.SYSTEM_PROMPT
    assert "Open-Meteo" in p and "station forecast" in p and "calibrated" in p


def test_slow_agent_times_out_to_deterministic_answer(monkeypatch, caplog) -> None:
    import time
    monkeypatch.setenv("AGENT_TIMEOUT_S", "0.3")
    monkeypatch.setattr(agent, "_run_agent", lambda tools, prompt, deadline=None: (time.sleep(2), ("late", [], "m"))[1])
    t0 = time.monotonic()
    with caplog.at_level("WARNING"):
        r = agent.ask(SID, "Is PE safe?", "en", replay="delhi-nov")
    assert time.monotonic() - t0 < 1.5
    assert r["fallback"] is True and r["verified"] is False and r.get("timed_out") is True and "351" in r["answer"]
    assert any("timed out" in m for m in caplog.messages)


# --- Gemini reliability: retries, fallback model ---
class _Fake503(Exception):
    code = 503


class _Fake429(Exception):
    code = 429


class _Fake404(Exception):
    code = 404


def _calls(monkeypatch, script):
    """script: model_id -> list of outcomes (Exception instance or answer str), consumed in order."""
    calls = []
    def invoke(model_id, tools, prompt):
        calls.append(model_id)
        outcome = script[model_id].pop(0)
        if isinstance(outcome, Exception): raise outcome
        return outcome, ["get_day_plan"]
    monkeypatch.setattr(agent, "_invoke", invoke)
    monkeypatch.setattr(agent, "_sleep", lambda s: calls.append(f"sleep {s}"))
    monkeypatch.setenv("MODEL_PROVIDER", "gemini"); monkeypatch.setenv("GEMINI_MODEL_ID", "primary"); monkeypatch.setenv("GEMINI_FALLBACK_MODEL_ID", "lite")
    return calls


def test_retries_503_with_backoff_then_succeeds(monkeypatch) -> None:
    calls = _calls(monkeypatch, {"primary": [_Fake503("busy"), _Fake429("slow"), "fine"]})
    assert agent._run_agent([], "q") == ("fine", ["get_day_plan"], "primary")
    assert calls == ["primary", "sleep 0.5", "primary", "sleep 1.5", "primary"]


def test_falls_back_to_lighter_model_after_retries(monkeypatch, caplog) -> None:
    calls = _calls(monkeypatch, {"primary": [_Fake503("a"), _Fake503("b"), _Fake503("c")], "lite": ["from lite"]})
    with caplog.at_level("INFO"):
        assert agent._run_agent([], "q")[2] == "lite"
    assert calls[-1] == "lite" and calls.count("primary") == 3
    assert any("lite" in m and "answered" in m for m in caplog.messages)


def test_non_retryable_error_goes_straight_to_fallback_model(monkeypatch) -> None:
    calls = _calls(monkeypatch, {"primary": [_Fake404("model gone")], "lite": ["ok"]})
    assert agent._run_agent([], "q")[2] == "lite" and calls == ["primary", "lite"]


def test_all_models_fail_raises(monkeypatch) -> None:
    import pytest
    _calls(monkeypatch, {"primary": [_Fake503("a")] * 3, "lite": [_Fake503("b")] * 3})
    with pytest.raises(_Fake503):
        agent._run_agent([], "q")


def test_real_genai_server_error_is_retryable() -> None:
    from google.genai import errors
    assert agent._retryable(errors.ServerError(503, {"error": {"code": 503, "message": "high demand", "status": "UNAVAILABLE"}}))
    assert agent._retryable(TimeoutError()) and not agent._retryable(ValueError("x"))


def test_backoff_skipped_when_deadline_too_close(monkeypatch) -> None:
    import time
    calls = _calls(monkeypatch, {"primary": [_Fake503("a"), "never"], "lite": ["lite ok"]})
    assert agent._run_agent([], "q", deadline=time.monotonic() + 0.1)[2] == "lite"
    assert not any(str(c).startswith("sleep") for c in calls)


def test_ask_response_includes_model(monkeypatch) -> None:
    monkeypatch.setattr(agent, "_run_agent", lambda tools, prompt, deadline=None: ("Fine.", [], "lite"))
    r = agent.ask(SID, "q", "en", replay="delhi-nov")
    assert r["model"] == "lite" and r["verified"] is True
    assert agent.deterministic_answer(SID, "en", "delhi-nov")["model"] is None
