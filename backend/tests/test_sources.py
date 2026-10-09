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


def _aq(value, la, lo, local="2026-10-09T18:30:00+05:30", loc=1):
    return {"value": value, "coordinates": {"latitude": la, "longitude": lo}, "datetime": {"utc": "2026-10-09T13:00:00Z", "local": local}, "locationsId": loc, "sensorsId": loc * 10}


def test_openaq_picks_nearest_fresh_sensor_within_25km() -> None:
    from datetime import datetime
    from saans.sources import IST, parse_openaq_results
    now = datetime(2026, 10, 9, 19, 0, tzinfo=IST)
    results = [_aq(80, 28.80, 77.316, loc=1),            # ~17 km
               _aq(60, 28.66, 77.316, loc=2),            # ~1.5 km, nearest
               _aq(55, 28.65, 77.316, local="2026-10-09T10:00:00+05:30", loc=3),  # nearest but stale
               _aq(-1, 28.647, 77.316, loc=4),           # invalid
               _aq(70, 29.50, 77.316, loc=5)]            # >25 km
    r = parse_openaq_results(results, 28.647, 77.316, now)
    assert r["station"].endswith("2") and r["pm25"] == 60 and r["distance_km"] < 3 and r["provider"] == "openaq" and r["source"] == "live"
    assert r["observed_at"] == "2026-10-09 18:30:00"


def test_openaq_raises_with_reason_when_none_usable() -> None:
    import pytest
    from datetime import datetime
    from saans.sources import IST, parse_openaq_results
    with pytest.raises(RuntimeError, match="no fresh PM2.5"):
        parse_openaq_results([_aq(60, 40.0, 70.0)], 28.647, 77.316, datetime(2026, 10, 9, 19, 0, tzinfo=IST))


def test_openaq_client_requires_key_and_sends_header(monkeypatch) -> None:
    import pytest
    monkeypatch.delenv("OPENAQ_API_KEY", raising=False)
    _Cache.values.clear()
    from saans.sources import OpenAqClient
    with pytest.raises(RuntimeError, match="OPENAQ_API_KEY"):
        OpenAqClient(api_key=None).latest_near(1, 2)
    seen = {}
    def handler(req):
        if not req.url.path.endswith("/latest"):
            return httpx.Response(404)
        seen["key"] = req.headers.get("x-api-key"); seen["q"] = dict(req.url.params)
        from datetime import datetime
        from saans.sources import IST
        return httpx.Response(200, json={"results": [_aq(60, 28.66, 77.316, local=datetime.now(IST).isoformat())]})
    r = OpenAqClient(api_key="abc", client=httpx.Client(transport=httpx.MockTransport(handler))).latest_near(28.647, 77.316)
    assert seen["key"] == "abc" and seen["q"]["radius"] == "25000" and r["pm25"] == 60


def _patch_chain(monkeypatch, cpcb, openaq):
    import saans.forecast as fc
    monkeypatch.setattr(fc.OpenMeteoClient, "hourly", lambda self, la, lo, days=5: [{"time": "2026-10-09T09:00", "pm25": 50, "pm10": 60, "source": "live"}])
    def run(client_result):
        def f(self, la, lo):
            if isinstance(client_result, Exception): raise client_result
            return client_result
        return f
    monkeypatch.setattr(fc.CpcbClient, "latest_near", run(cpcb)); monkeypatch.setattr(fc.OpenAqClient, "latest_near", run(openaq))
    return fc


def _school():
    from saans.store import SEED_SCHOOLS
    return SEED_SCHOOLS[0]


_LIVE_CPCB = {"station": "S", "distance_km": 2, "pm25": 100, "source": "live", "provider": "cpcb"}
_LIVE_AQ = {"station": "OpenAQ location 9", "distance_km": 3, "pm25": 75, "source": "live", "provider": "openaq"}


def test_chain_prefers_cpcb_then_openaq_then_uncalibrated(monkeypatch) -> None:
    from datetime import datetime
    import saans.calibrate as cal
    monkeypatch.setattr(cal, "datetime", type("D", (datetime,), {"now": classmethod(lambda cls, tz=None: datetime(2026, 10, 9, 9, 30, tzinfo=cal.IST))}))
    fc = _patch_chain(monkeypatch, _LIVE_CPCB, _LIVE_AQ)
    rows, src, mode = fc.load_forecast(_school())
    assert src["observation"] == "live:cpcb" and rows[0]["calibrated"] is True
    fc = _patch_chain(monkeypatch, RuntimeError("down"), _LIVE_AQ)
    rows, src, _ = fc.load_forecast(_school())
    assert src["observation"] == "live:openaq" and src["station"] == "OpenAQ location 9" and rows[0]["calibrated"] is True
    fc = _patch_chain(monkeypatch, {**_LIVE_CPCB, "distance_km": 60}, _LIVE_AQ)  # CPCB too far -> OpenAQ
    assert fc.load_forecast(_school())[1]["observation"] == "live:openaq"
    fc = _patch_chain(monkeypatch, {**_LIVE_CPCB, "source": "fixture"}, RuntimeError("no key"))
    rows, src, mode = fc.load_forecast(_school())
    assert src["observation"] == "fixture:cpcb" and rows[0]["calibrated"] is False and mode == "live"
    fc = _patch_chain(monkeypatch, RuntimeError("down"), RuntimeError("no key"))
    rows, src, _ = fc.load_forecast(_school())
    assert src["observation"] == "none" and rows[0]["calibrated"] is False


def test_cpcb_connect_timeout_is_3s() -> None:
    c = CpcbClient(api_key="k")
    assert c.client.timeout.connect == 3


def test_openaq_station_is_location_name(monkeypatch) -> None:
    from datetime import datetime
    from saans.sources import IST, OpenAqClient
    monkeypatch.delenv("OPENAQ_API_KEY", raising=False); _Cache.values.clear()
    def handler(req):
        if req.url.path.endswith("/latest"):
            return httpx.Response(200, json={"results": [_aq(60, 28.66, 77.316, local=datetime.now(IST).isoformat(), loc=8118)]})
        assert req.url.path == "/v3/locations/8118"
        return httpx.Response(200, json={"results": [{"id": 8118, "name": "Anand Vihar, Delhi - DPCC"}]})
    r = OpenAqClient(api_key="k", client=httpx.Client(transport=httpx.MockTransport(handler))).latest_near(28.647, 77.316)
    assert r["station"] == "Anand Vihar, Delhi - DPCC"


def test_openaq_name_lookup_failure_keeps_reading(monkeypatch) -> None:
    from datetime import datetime
    from saans.sources import IST, OpenAqClient
    _Cache.values.clear()
    def handler(req):
        if req.url.path.endswith("/latest"):
            return httpx.Response(200, json={"results": [_aq(60, 28.66, 77.316, local=datetime.now(IST).isoformat(), loc=7)]})
        return httpx.Response(500)
    r = OpenAqClient(api_key="k", client=httpx.Client(transport=httpx.MockTransport(handler))).latest_near(28.647, 77.316)
    assert r["pm25"] == 60 and r["station"] == "OpenAQ location 7"
