import pytest


@pytest.fixture(autouse=True)
def _isolated_plan_cache(monkeypatch, tmp_path):
    """Never read or write the developer's local plan cache or school store during tests."""
    monkeypatch.setenv("PLAN_CACHE_PATH", str(tmp_path / "plan_cache.json"))
    # Writes go to a temp copy of the seed store, never to the committed data/schools.json.
    import shutil
    from pathlib import Path
    seed = Path(__file__).resolve().parents[1] / "data" / "schools.json"
    shutil.copy(seed, tmp_path / "schools.json")
    monkeypatch.setenv("SCHOOLS_PATH", str(tmp_path / "schools.json"))
    # Each test starts with an empty /api/ask rate-limit window.
    import app as api
    api.RATE_LIMITER.reset()
