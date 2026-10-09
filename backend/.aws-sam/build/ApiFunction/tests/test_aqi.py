import pytest

from saans.aqi import BAND_METADATA, band_for_aqi, naqi, sub_index


@pytest.mark.parametrize(
    ("concentration", "expected"),
    [(30, 50), (31, 51), (60, 100), (61, 101), (90, 200), (91, 201), (120, 300), (121, 301), (250, 400), (251, 401)],
)
def test_pm25_band_boundaries(concentration: int, expected: int) -> None:
    assert sub_index("pm25", concentration) == expected


def test_pm10_can_be_the_dominant_pollutant() -> None:
    assert naqi(20, 300) == (250, "Poor", "pm10")


@pytest.mark.parametrize("pollutant", ["pm25", "pm10"])
def test_sub_index_caps_at_500(pollutant: str) -> None:
    assert sub_index(pollutant, 10_000) == 500  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [None, -1, float("nan"), float("inf")])
def test_missing_or_invalid_concentrations_return_no_sub_index(value: float | None) -> None:
    assert sub_index("pm25", value) is None


def test_naqi_uses_available_pollutant_and_handles_no_readings() -> None:
    assert naqi(None, 50) == (50, "Good", "pm10")
    assert naqi(None, -1) == (None, None, None)


def test_band_metadata_covers_every_aqi_band() -> None:
    assert set(BAND_METADATA) == {"Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"}
    assert band_for_aqi(400) == "Very Poor"
    assert band_for_aqi(401) == "Severe"


def test_decimal_values_in_breakpoint_gaps_are_not_severe() -> None:
    from saans.aqi import naqi, sub_index
    assert naqi(60.1, 158.8) == (139, "Moderate", "pm10")
    assert sub_index("pm25", 30.5) == 50 and sub_index("pm25", 0) == 0
    assert sub_index("pm25", 350.0) == 500 and sub_index("pm25", 351) == 500


def test_pm25_60_9_is_satisfactory() -> None:
    from saans.aqi import naqi
    aqi, band, _ = naqi(60.9, 0)
    assert aqi <= 100 and band == "Satisfactory"


def test_pm10_100_5_is_at_most_100() -> None:
    from saans.aqi import naqi
    aqi, band, _ = naqi(0, 100.5)
    assert aqi <= 100 and band == "Satisfactory"


def test_pm25_250_5_is_very_poor() -> None:
    from saans.aqi import naqi
    aqi, band, _ = naqi(250.5, 0)
    assert aqi <= 400 and band == "Very Poor"


def test_band_follows_final_aqi_number() -> None:
    from saans.aqi import band_for_aqi, naqi
    for pm25 in (x / 10 for x in range(0, 3600, 7)):
        aqi, band, _ = naqi(pm25, None)
        assert band == band_for_aqi(aqi)
