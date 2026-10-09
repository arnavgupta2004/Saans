import pytest


@pytest.fixture(autouse=True)
def _isolated_plan_cache(monkeypatch, tmp_path):
    """Never read or write the developer's local plan cache during tests."""
    monkeypatch.setenv("PLAN_CACHE_PATH", str(tmp_path / "plan_cache.json"))
