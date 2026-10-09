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


def _row(station, la, lo, pol, avg, upd="09-10-2026 19:00:00"):
    return {"country": "India", "state": "Delhi", "city": "Delhi", "station": station, "last_update": upd, "latitude": la, "longitude": lo,
            "pollutant_id": pol, "pollutant_min": "NA", "pollutant_max": "NA", "pollutant_avg": avg}


def test_parse_real_shape_strings_na_and_nearest_station_with_pm25() -> None:
    from saans.sources import parse_cpcb_records
    records = [
        _row("Anand Vihar, Delhi - DPCC", "28.6468", "77.3160", "PM2.5", "NA"),   # nearest, but no PM2.5 value -> skipped
        _row("Anand Vihar, Delhi - DPCC", "28.6468", "77.3160", "PM10", "228"),
        _row("Vivek Vihar, Delhi - DPCC", "28.6720", "77.3150", "PM2.5", "118"),
        _row("Vivek Vihar, Delhi - DPCC", "28.6720", "77.3150", "PM10", "NA"),
        _row("Dwarka-Sector 8, Delhi - DPCC", "28.5710", "77.0710", "PM2.5", "98.5"),
        _row("Broken", "NA", "NA", "PM2.5", "50"),
    ]
    r = parse_cpcb_records(records, 28.647, 77.316)
    assert r["station"] == "Vivek Vihar, Delhi - DPCC" and r["pm25"] == 118.0 and r["pm10"] is None
    assert r["distance_km"] < 5 and r["observed_at"] == "09-10-2026 19:00:00" and r["provider"] == "cpcb"


def test_parse_raises_when_no_pm25_numeric() -> None:
    import pytest
    from saans.sources import parse_cpcb_records
    with pytest.raises(RuntimeError, match="PM2.5"):
        parse_cpcb_records([_row("A", "28.6", "77.3", "PM2.5", "NA")], 28.6, 77.3)


def test_live_failure_reason_is_logged_and_falls_back_to_fixture(caplog) -> None:
    _Cache.values.clear()
    bad = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(403, json={"message": "Invalid API key"})))
    with caplog.at_level("WARNING"):
        r = CpcbClient(api_key="k", client=bad).latest_near(28.647, 77.316)
    assert r["source"] == "fixture" and any("403" in m for m in caplog.messages)


def test_live_response_is_parsed_and_cached() -> None:
    _Cache.values.clear()
    body = {"records": [_row("Vivek Vihar, Delhi - DPCC", "28.6720", "77.3150", "PM2.5", "118")]}
    c = CpcbClient(api_key="k", client=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json=body))))
    assert c.latest_near(28.647, 77.316)["source"] == "live" and c.latest_near(28.647, 77.316)["source"] == "cached"
