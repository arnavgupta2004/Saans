"""CPCB National Air Quality Index (NAQI) calculations.

Saans applies the 24-hour CPCB breakpoints to hourly concentrations as an
exposure indicator. It is not presented as an official 24-hour NAQI reading.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

Pollutant = Literal["pm25", "pm10"]


@dataclass(frozen=True)
class BandMetadata:
    """Display and health-advisory information for a CPCB NAQI band."""

    name: str
    colour_hex: str
    health_advisory: str


BAND_METADATA: dict[str, BandMetadata] = {
    "Good": BandMetadata("Good", "#00E400", "Air quality is satisfactory; enjoy usual outdoor activities."),
    "Satisfactory": BandMetadata(
        "Satisfactory", "#FFFF00", "Unusually sensitive people may reduce prolonged outdoor exertion."
    ),
    "Moderate": BandMetadata(
        "Moderate", "#FF7E00", "People with breathing or heart conditions should reduce prolonged outdoor exertion."
    ),
    "Poor": BandMetadata("Poor", "#FF0000", "Sensitive people should avoid prolonged or heavy outdoor exertion."),
    "Very Poor": BandMetadata(
        "Very Poor", "#8F3F97", "Children, older adults, and people with illness should avoid outdoor exertion."
    ),
    "Severe": BandMetadata("Severe", "#7E0023", "Everyone should avoid outdoor exertion and remain indoors where possible."),
}

# (concentration low, concentration high, AQI low, AQI high). The final
# concentration range interpolates the 401–500 NAQI range; higher values cap.
BREAKPOINTS: dict[Pollutant, tuple[tuple[float, float, int, int], ...]] = {
    "pm25": ((0, 30, 0, 50), (31, 60, 51, 100), (61, 90, 101, 200), (91, 120, 201, 300), (121, 250, 301, 400), (251, 350, 401, 500)),
    "pm10": ((0, 50, 0, 50), (51, 100, 51, 100), (101, 250, 101, 200), (251, 350, 201, 300), (351, 430, 301, 400), (431, 500, 401, 500)),
}


def sub_index(pollutant: Pollutant, conc: float | int | None) -> int | None:
    """Return the capped CPCB sub-index for one pollutant concentration."""
    if pollutant not in BREAKPOINTS:
        raise ValueError(f"Unsupported pollutant: {pollutant}")
    if conc is None:
        return None
    concentration = float(conc)
    if concentration < 0 or not isfinite(concentration):
        return None

    # Bands are treated as contiguous: a decimal in a gap (e.g. 60.1 between 60 and 61) belongs to the band below.
    bands = BREAKPOINTS[pollutant]
    if concentration > bands[-1][1]:
        return 500
    concentration_low, concentration_high, index_low, index_high = next(b for b in reversed(bands) if concentration >= b[0])
    index = (index_high - index_low) / (concentration_high - concentration_low) * (concentration - concentration_low) + index_low
    return min(500, round(index))


def band_for_aqi(aqi: int) -> str:
    """Return the NAQI category name for a valid AQI value."""
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Satisfactory"
    if aqi <= 200:
        return "Moderate"
    if aqi <= 300:
        return "Poor"
    if aqi <= 400:
        return "Very Poor"
    return "Severe"


def naqi(pm25: float | int | None, pm10: float | int | None) -> tuple[int | None, str | None, Pollutant | None]:
    """Return ``(AQI, band, dominant pollutant)`` from PM2.5 and PM10."""
    pm25_index = sub_index("pm25", pm25)
    pm10_index = sub_index("pm10", pm10)
    valid = [("pm25", pm25_index), ("pm10", pm10_index)]
    valid = [(pollutant, index) for pollutant, index in valid if index is not None]
    if not valid:
        return None, None, None
    dominant, aqi = max(valid, key=lambda item: item[1])
    assert aqi is not None
    return aqi, band_for_aqi(aqi), dominant  # type: ignore[return-value]
