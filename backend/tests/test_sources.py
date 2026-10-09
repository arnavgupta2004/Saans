import httpx
from saans.sources import CpcbClient, OpenMeteoClient, _Cache

def test_fixture_is_never_cached_or_relabelled_cached() -> None:
    _Cache.values.clear(); client=OpenMeteoClient(httpx.Client(transport=httpx.MockTransport(lambda r: (_ for _ in ()).throw(httpx.ConnectError("no net")))))
    assert client.hourly(28.647,77.316)[0]["source"] == "fixture"
    assert client.hourly(28.647,77.316)[0]["source"] == "fixture"
    assert CpcbClient(api_key=None).latest_near(28.647,77.316)["source"] == "fixture"
    assert CpcbClient(api_key=None).latest_near(28.647,77.316)["source"] == "fixture"

def test_live_open_meteo_is_cached() -> None:
    _Cache.values.clear(); body={"hourly":{"time":["2026-10-09T08:00"],"pm2_5":[10],"pm10":[20]}}
    client=OpenMeteoClient(httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200,json=body))))
    assert client.hourly(1,2)[0]["source"] == "live" and client.hourly(1,2)[0]["source"] == "cached"

def test_cpcb_fixture_is_grouped_by_nearest_station() -> None:
    _Cache.values.clear(); result=CpcbClient(api_key=None).latest_near(28.647,77.316)
    assert result["station"] == "Anand Vihar, Delhi" and result["pm25"] == 142.0 and result["source"] == "fixture"
