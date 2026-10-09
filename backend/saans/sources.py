"""Resilient Open-Meteo and CPCB source clients (with fixture fallback)."""
from __future__ import annotations

import json, logging, math, os, time
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any
import httpx

logger = logging.getLogger(__name__)
IST = ZoneInfo("Asia/Kolkata")
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
OPEN_METEO_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
CPCB_RESOURCE_ID = "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
CPCB_URL = f"https://api.data.gov.in/resource/{CPCB_RESOURCE_ID}"

class _Cache:
    values: dict[str, tuple[float, Any]] = {}
    @classmethod
    def get(cls, key: str) -> Any | None:
        item = cls.values.get(key)
        return item[1] if item and time.time() - item[0] < 3600 else None
    @classmethod
    def age(cls, key: str) -> float:
        item = cls.values.get(key)
        return time.time() - item[0] if item else 0.0
    @classmethod
    def put(cls, key: str, value: Any) -> Any:
        cls.values[key] = (time.time(), value); return value

def _load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text())

class OpenMeteoClient:
    def __init__(self, client: httpx.Client | None = None): self.client = client or httpx.Client(timeout=15)
    def hourly(self, lat: float, lon: float, days: int = 5) -> list[dict[str, Any]]:
        key = f"om:{lat}:{lon}:{days}"; cached = _Cache.get(key)
        if cached: return [{**row, "source": "cached"} for row in cached]  # only live data is ever cached
        try:
            data = self.client.get(OPEN_METEO_URL, params={"latitude":lat,"longitude":lon,"hourly":"pm2_5,pm10","forecast_days":days,"timezone":"Asia/Kolkata"}).json()
            source = "live"
        except Exception:
            data = _load("open_meteo_delhi_anand_vihar.json"); source = "fixture"
        h = data["hourly"]
        rows = [{"time": t, "pm25": p25, "pm10": p10, "source": source} for t,p25,p10 in zip(h["time"],h["pm2_5"],h["pm10"])]
        # Fixture data is never cached, so the next request retries the live API.
        return _Cache.put(key, rows) if source == "live" else rows

_MISSING = {"", "na", "n/a", "nan", "null", "none", "-", "--"}

def _num(value: Any) -> float | None:
    """Parse API numbers that may be int/float, numeric strings, or placeholders like "NA"."""
    if value is None or isinstance(value, bool): return None
    if isinstance(value, str) and value.strip().lower() in _MISSING: return None
    try: number = float(value)
    except (TypeError, ValueError): return None
    return number if math.isfinite(number) else None

def _field(row: dict[str, Any], *names: str) -> Any:
    normalized = {str(k).lower().replace(" ", "_"): v for k,v in row.items()}
    for name in names:
        if name in normalized: return normalized[name]
    return None

def _distance(a: float, b: float, c: float, d: float) -> float:
    p = math.pi/180; x = math.sin((c-a)*p/2)**2 + math.cos(a*p)*math.cos(c*p)*math.sin((d-b)*p/2)**2
    return 6371 * 2 * math.asin(math.sqrt(x))

_PM25 = {"pm2.5", "pm2_5", "pm25"}
_PM10 = {"pm10", "pm_10"}

def parse_cpcb_records(records: list[dict[str, Any]], lat: float, lon: float) -> dict[str, Any]:
    """Group data.gov.in rows by station and return the nearest station that has a PM2.5 value."""
    groups: dict[tuple[str,float,float],dict[str,Any]]={}
    for row in records:
        station=_field(row,"station","station_name","stationname"); la=_num(_field(row,"latitude","lat")); lo=_num(_field(row,"longitude","lon","lng")); pollutant=str(_field(row,"pollutant_id","pollutant","pollutantid") or "").strip().lower()
        # Real resource: pollutant_avg (older shapes: avg_value / value). "NA" values are skipped.
        value=_num(_field(row,"pollutant_avg","avg_value","avg_value_24hr","value","concentration"))
        if not station or la is None or lo is None or value is None: continue
        group=groups.setdefault((str(station),la,lo),{"station":str(station),"latitude":la,"longitude":lo,"observed_at":_field(row,"last_update","last_updated","updated_at")})
        if pollutant in _PM25: group["pm25"]=value
        if pollutant in _PM10: group["pm10"]=value
    choices=[g for g in groups.values() if g.get("pm25") is not None]
    if not choices: raise RuntimeError(f"No CPCB station with a numeric PM2.5 value in {len(records)} records")
    chosen=min(choices,key=lambda g:_distance(lat,lon,g["latitude"],g["longitude"]))
    return {"station":chosen["station"],"distance_km":round(_distance(lat,lon,chosen["latitude"],chosen["longitude"]),2),"pm25":chosen["pm25"],"pm10":chosen.get("pm10"),"observed_at":chosen.get("observed_at"),"provider":"cpcb"}

class CpcbClient:
    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None): self.api_key, self.client = api_key or os.getenv("DATA_GOV_IN_API_KEY"), client or httpx.Client(timeout=15)
    def _live_records(self) -> list[dict[str, Any]]:
        if not self.api_key: raise RuntimeError("DATA_GOV_IN_API_KEY missing")
        response=self.client.get(CPCB_URL,params={"api-key":self.api_key,"format":"json","limit":10000})
        response.raise_for_status()
        body=response.json()
        if not isinstance(body,dict) or not isinstance(body.get("records"),list):
            raise RuntimeError(f"Unexpected response shape (keys: {list(body)[:6] if isinstance(body,dict) else type(body).__name__}; message: {body.get('message') or body.get('error') if isinstance(body,dict) else None})")
        return body["records"]
    def latest_near(self, lat: float, lon: float) -> dict[str, Any]:
        key=f"cpcb:{lat}:{lon}"; cached=_Cache.get(key)
        if cached: return {**cached,"source":"cached","age_s":round(_Cache.age(key))}
        try:
            result={**parse_cpcb_records(self._live_records(),lat,lon),"source":"live","age_s":0}
        except Exception as exc:
            logger.warning("CPCB live call failed (%s: %s); using documented fixture", type(exc).__name__, exc)
            result={**parse_cpcb_records(_load("cpcb_documented_response.json")["records"],lat,lon),"source":"fixture","age_s":0}
            return result  # fixtures are never cached
        return _Cache.put(key,result)


REPLAYS = {"delhi-nov": "replay_delhi_nov.json"}

def load_replay(key: str) -> tuple[list[dict[str, Any]], str]:
    """Recorded real bad-air day. Returns (hourly rows labelled source='replay', recorded date). KeyError if unknown."""
    data = _load(REPLAYS[key]); h = data["hourly"]
    return [{"time": t, "pm25": a, "pm10": b, "source": "replay"} for t, a, b in zip(h["time"], h["pm2_5"], h["pm10"])], data["date"]


OPENAQ_URL = "https://api.openaq.org/v3/parameters/2/latest"  # parameter 2 = PM2.5
OPENAQ_RADIUS_M = 25000
OPENAQ_MAX_AGE_S = 2 * 3600

class OpenAqClient:
    """Nearest OpenAQ v3 PM2.5 sensor within 25 km of the school, latest value (free API key)."""
    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None):
        self.api_key, self.client = api_key or os.getenv("OPENAQ_API_KEY"), client or httpx.Client(timeout=15)
    def latest_near(self, lat: float, lon: float) -> dict[str, Any]:
        key = f"openaq:{lat}:{lon}"; cached = _Cache.get(key)
        if cached: return {**cached, "source": "cached", "age_s": round(_Cache.age(key))}
        if not self.api_key: raise RuntimeError("OPENAQ_API_KEY missing")
        response = self.client.get(OPENAQ_URL, headers={"X-API-Key": self.api_key}, params={"coordinates": f"{lat},{lon}", "radius": OPENAQ_RADIUS_M, "limit": 1000})
        response.raise_for_status()
        results = response.json().get("results")
        if not isinstance(results, list): raise RuntimeError("OpenAQ: unexpected response shape (no 'results' list)")
        return _Cache.put(key, parse_openaq_results(results, lat, lon))

def parse_openaq_results(results: list[dict[str, Any]], lat: float, lon: float, now: datetime | None = None) -> dict[str, Any]:
    """Pick the nearest fresh sensor reading (<2h old, ≤25 km, numeric non-negative value)."""
    now = now or datetime.now(IST); best: tuple[float, dict[str, Any], datetime] | None = None
    for row in results:
        value = _num(row.get("value")); coords = row.get("coordinates") or {}
        la, lo = _num(coords.get("latitude")), _num(coords.get("longitude"))
        stamp = (row.get("datetime") or {}).get("local") or (row.get("datetime") or {}).get("utc")
        if value is None or value < 0 or la is None or lo is None or not stamp: continue
        try: observed = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
        except ValueError: continue
        if observed.tzinfo is None: observed = observed.replace(tzinfo=IST)
        distance = _distance(lat, lon, la, lo)
        if distance > OPENAQ_RADIUS_M / 1000 or (now - observed).total_seconds() >= OPENAQ_MAX_AGE_S: continue
        if best is None or distance < best[0]: best = (distance, row, observed)
    if best is None: raise RuntimeError(f"OpenAQ: no fresh PM2.5 sensor within 25 km in {len(results)} results")
    distance, row, observed = best
    return {"station": f"OpenAQ location {row.get('locationsId', row.get('sensorsId', '?'))}", "distance_km": round(distance, 2), "pm25": _num(row["value"]), "pm10": None,
            "observed_at": observed.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S"), "source": "live", "age_s": 0, "provider": "openaq"}
