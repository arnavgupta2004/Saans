from saans.calibrate import calibrate

def test_ratio_is_clipped_at_two() -> None:
    result=calibrate([{"pm25":10,"pm10":20}],{"pm25":100,"distance_km":1,"source":"live"})[0]
    assert result["factor"] == 2 and result["pm25_cal"] == 20

def test_correction_decays_over_time() -> None:
    result=calibrate([{"pm25":10,"pm10":20}]*13,{"pm25":20,"distance_km":1,"source":"live"})
    assert result[0]["factor"] == 2 and 1.36 < result[12]["factor"] < 1.38

def test_missing_or_distant_observation_is_uncalibrated() -> None:
    assert calibrate([{"pm25":10,"pm10":20}],None)[0]["calibrated"] is False
    assert calibrate([{"pm25":10,"pm10":20}],{"pm25":20,"distance_km":26,"source":"live"})[0]["factor"] == 1

def _hourly(): return [{"pm25":10,"pm10":20}]

def test_fixture_or_unlabelled_observation_never_calibrates() -> None:
    for src in ("fixture", None):
        obs={"pm25":100,"distance_km":1,**({"source":src} if src else {})}
        r=calibrate(_hourly(),obs)[0]; assert r["calibrated"] is False and r["factor"] == 1

def test_cached_observation_only_when_fresh() -> None:
    obs={"pm25":20,"distance_km":1,"source":"cached"}
    assert calibrate(_hourly(),{**obs,"age_s":600})[0]["calibrated"] is True
    assert calibrate(_hourly(),{**obs,"age_s":3*3600})[0]["calibrated"] is False

def test_stale_station_timestamp_does_not_calibrate() -> None:
    from datetime import datetime
    from saans.calibrate import IST
    now=datetime(2026,10,9,12,0,tzinfo=IST)
    obs={"pm25":20,"distance_km":1,"source":"live"}
    assert calibrate(_hourly(),{**obs,"observed_at":"09-10-2026 11:00:00"},now)[0]["calibrated"] is True
    assert calibrate(_hourly(),{**obs,"observed_at":"08-10-2026 11:00:00"},now)[0]["calibrated"] is False

def test_ratio_is_anchored_on_current_hour() -> None:
    from datetime import datetime
    from saans.calibrate import IST
    rows=[{"time":f"2026-10-09T{h:02d}:00","pm25":10,"pm10":20} for h in range(24)]
    r=calibrate(rows,{"pm25":20,"distance_km":1,"source":"live"},datetime(2026,10,9,9,30,tzinfo=IST))
    assert r[9]["factor"] == 2 and r[0]["factor"] < r[9]["factor"]
