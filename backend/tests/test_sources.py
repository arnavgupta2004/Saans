import httpx
from saans.sources import CpcbClient, OpenMeteoClient, _Cache

def test_open_meteo_fixture_fallback_and_cache() -> None:
    _Cache.values.clear(); client=OpenMeteoClient(httpx.Client(transport=httpx.MockTransport(lambda r: (_ for _ in ()).throw(httpx.ConnectError("no net")))))
    assert client.hourly(28.647,77.316)[0]["source"] == "fixture"
    assert client.hourly(28.647,77.316)[0]["source"] == "cached"

def test_cpcb_fixture_is_grouped_by_nearest_station() -> None:
    _Cache.values.clear(); result=CpcbClient(api_key=None).latest_near(28.647,77.316)
    assert result["station"] == "Anand Vihar, Delhi" and result["pm25"] == 142.0 and result["source"] == "fixture"
