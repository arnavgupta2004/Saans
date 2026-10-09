from saans.calibrate import calibrate

def test_ratio_is_clipped_at_two() -> None:
    result=calibrate([{"pm25":10,"pm10":20}],{"pm25":100,"distance_km":1})[0]
    assert result["factor"] == 2 and result["pm25_cal"] == 20

def test_correction_decays_over_time() -> None:
    result=calibrate([{"pm25":10,"pm10":20}]*13,{"pm25":20,"distance_km":1})
    assert result[0]["factor"] == 2 and 1.36 < result[12]["factor"] < 1.38

def test_missing_or_distant_observation_is_uncalibrated() -> None:
    assert calibrate([{"pm25":10,"pm10":20}],None)[0]["calibrated"] is False
    assert calibrate([{"pm25":10,"pm10":20}],{"pm25":20,"distance_km":26})[0]["factor"] == 1
