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


# --- OpenAQ: reference-grade monitors only, CPCB preferred ---
def _loc(id_, name, la, lo, monitor=True, provider="CPCB", sensor=None):
    return {"id": id_, "name": name, "isMonitor": monitor, "provider": {"id": 1, "name": provider},
            "coordinates": {"latitude": la, "longitude": lo},
            "sensors": [{"id": sensor or id_ * 10, "parameter": {"id": 2, "name": "pm25"}}, {"id": (sensor or id_ * 10) + 1, "parameter": {"id": 1, "name": "pm10"}}]}


def _latest(sensor, value, local):
    return {"datetime": {"utc": "x", "local": local}, "value": value, "sensorsId": sensor}


def _openaq(locations, latest_by_loc, seen=None):
    from saans.sources import OpenAqClient
    def handler(req):
        if seen is not None: seen.append((req.url.path, dict(req.url.params), req.headers.get("x-api-key")))
        if req.url.path == "/v3/locations":
            return httpx.Response(200, json={"results": locations})
        loc = int(req.url.path.split("/")[3])
        return httpx.Response(200, json={"results": latest_by_loc.get(loc, [])})
    return OpenAqClient(api_key="k", client=httpx.Client(transport=httpx.MockTransport(handler)))


def _fresh():
    from datetime import datetime
    from saans.sources import IST
    return datetime.now(IST).isoformat()


def test_openaq_low_cost_sensor_nearer_is_ignored_monitor_chosen() -> None:
    _Cache.values.clear(); seen = []
    locs = [_loc(1, "Air Check", 28.650, 77.316, monitor=False, provider="AirGradient"),   # ~0.3 km, low-cost
            _loc(2, "Anand Vihar, Delhi - DPCC", 28.700, 77.316)]                       # ~6 km, monitor
    r = _openaq(locs, {1: [_latest(10, 999, _fresh())], 2: [_latest(20, 88, _fresh()), _latest(21, 300, _fresh())]}, seen).latest_near(28.647, 77.316)
    assert r["pm25"] == 88 and r["station"] == "Anand Vihar, Delhi - DPCC (CPCB via OpenAQ)" and r["provider"] == "openaq"
    path, params, key = seen[0]
    assert path == "/v3/locations" and params["monitor"] == "true" and params["radius"] == "25000" and params["parameters_id"] == "2" and key == "k"


def test_openaq_prefers_cpcb_over_nearer_other_monitor() -> None:
    _Cache.values.clear()
    locs = [_loc(3, "US Embassy", 28.650, 77.316, provider="AirNow"), _loc(4, "Vivek Vihar", 28.690, 77.316, provider="Central Pollution Control Board")]
    r = _openaq(locs, {3: [_latest(30, 70, _fresh())], 4: [_latest(40, 90, _fresh())]}).latest_near(28.647, 77.316)
    assert r["pm25"] == 90 and r["station"] == "Vivek Vihar (CPCB via OpenAQ)"


def test_openaq_non_cpcb_monitor_label() -> None:
    _Cache.values.clear()
    r = _openaq([_loc(3, "US Embassy", 28.650, 77.316, provider="AirNow")], {3: [_latest(30, 70, _fresh())]}).latest_near(28.647, 77.316)
    assert r["station"] == "US Embassy (reference monitor via OpenAQ)"


def test_openaq_no_monitor_within_25km_raises() -> None:
    import pytest
    _Cache.values.clear()
    locs = [_loc(1, "Air Check", 28.650, 77.316, monitor=False), _loc(2, "Far", 29.5, 77.316)]
    with pytest.raises(RuntimeError, match="reference monitor"):
        _openaq(locs, {1: [_latest(10, 50, _fresh())], 2: [_latest(20, 50, _fresh())]}).latest_near(28.647, 77.316)


def test_openaq_stale_monitor_skipped_for_next_one() -> None:
    _Cache.values.clear()
    locs = [_loc(2, "Stale CPCB", 28.660, 77.316), _loc(5, "Fresh CPCB", 28.700, 77.316)]
    r = _openaq(locs, {2: [_latest(20, 50, "2026-01-01T08:00:00+05:30")], 5: [_latest(50, 77, _fresh())]}).latest_near(28.647, 77.316)
    assert r["pm25"] == 77 and r["station"].startswith("Fresh CPCB")


def test_openaq_requires_key(monkeypatch) -> None:
    import pytest
    from saans.sources import OpenAqClient
    monkeypatch.delenv("OPENAQ_API_KEY", raising=False); _Cache.values.clear()
    with pytest.raises(RuntimeError, match="OPENAQ_API_KEY"):
        OpenAqClient(api_key=None).latest_near(1, 2)


def test_openaq_failure_reason_counts() -> None:
    import pytest
    _Cache.values.clear()
    locs = [_loc(1, "Air Check", 28.650, 77.316, monitor=False), _loc(2, "Stale", 28.66, 77.316), _loc(3, "Far", 29.5, 77.316),
            {**_loc(4, "No PM", 28.66, 77.316), "sensors": [{"id": 9, "parameter": {"id": 1, "name": "pm10"}}]}]
    with pytest.raises(RuntimeError) as e:
        _openaq(locs, {2: [_latest(20, 50, "2026-01-01T08:00:00+05:30")]}).latest_near(28.647, 77.316)
    msg = str(e.value)
    for part in ("not_monitor=1", "too_far=1", "no_pm25_sensor=1", "stale=1"):
        assert part in msg


def test_station_blank_when_observation_not_used(monkeypatch) -> None:
    fc = _patch_chain(monkeypatch, {**_LIVE_CPCB, "source": "fixture"}, RuntimeError("no monitor"))
    _, src, _ = fc.load_forecast(_school())
    assert src["observation"] == "fixture:cpcb" and src["station"] is None and src["distance_km"] is None


def test_openaq_stale_error_carries_freshest_age_note() -> None:
    import pytest
    from saans.sources import OpenAqUnavailable
    _Cache.values.clear()
    locs = [_loc(2, "A", 28.66, 77.316), _loc(5, "B", 28.70, 77.316)]
    from datetime import datetime, timedelta
    from saans.sources import IST
    old = (datetime.now(IST) - timedelta(hours=50)).isoformat(); older = "2018-02-22T02:45:00+05:30"
    with pytest.raises(OpenAqUnavailable) as e:
        _openaq(locs, {2: [_latest(20, 50, older), _latest(20, 51, old)], 5: [_latest(50, 60, older)]}).latest_near(28.647, 77.316)
    assert e.value.note == "nearest CPCB monitor via OpenAQ last reported 50 h ago"


def test_openaq_no_monitor_note() -> None:
    import pytest
    from saans.sources import OpenAqUnavailable
    _Cache.values.clear()
    with pytest.raises(OpenAqUnavailable) as e:
        _openaq([_loc(1, "Air Check", 28.65, 77.316, monitor=False)], {}).latest_near(28.647, 77.316)
    assert e.value.note == "no reference monitor within 25 km on OpenAQ"


def test_calibration_note_in_sources(monkeypatch) -> None:
    from saans.sources import OpenAqUnavailable
    fc = _patch_chain(monkeypatch, {**_LIVE_CPCB, "source": "fixture"}, OpenAqUnavailable("x", "nearest CPCB monitor via OpenAQ last reported 50 h ago"))
    _, src, _ = fc.load_forecast(_school())
    assert src["note"] == "Not calibrated: CPCB (data.gov.in) unreachable; nearest CPCB monitor via OpenAQ last reported 50 h ago"
    fc = _patch_chain(monkeypatch, RuntimeError("down"), RuntimeError("OPENAQ_API_KEY missing"))
    assert fc.load_forecast(_school())[1]["note"] == "Not calibrated: CPCB (data.gov.in) unreachable; OpenAQ unavailable"
    fc = _patch_chain(monkeypatch, _LIVE_CPCB, RuntimeError("unused"))
    assert fc.load_forecast(_school())[1]["note"] is None


def test_note_flows_into_dayplan() -> None:
    from saans.planner import plan_day
    from saans.store import SEED_SCHOOLS
    rows = [{"time": "2026-10-09T09:00", "pm25": 50, "pm10": 60}]
    p = plan_day(SEED_SCHOOLS[0], rows, "2026-10-09", {"forecast": "live", "observation": "none", "note": "Not calibrated: x"})
    assert p.sources.note == "Not calibrated: x"
