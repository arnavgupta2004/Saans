"""Resilient Open-Meteo and CPCB source clients (with fixture fallback)."""
from __future__ import annotations

import json, math, os, time
from pathlib import Path
from typing import Any
import httpx

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
    def put(cls, key: str, value: Any) -> Any:
        cls.values[key] = (time.time(), value); return value

def _load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text())

class OpenMeteoClient:
    def __init__(self, client: httpx.Client | None = None): self.client = client or httpx.Client(timeout=15)
    def hourly(self, lat: float, lon: float, days: int = 5) -> list[dict[str, Any]]:
        key = f"om:{lat}:{lon}:{days}"; cached = _Cache.get(key)
        if cached: return [{**row, "source": "cached"} for row in cached]
        try:
            data = self.client.get(OPEN_METEO_URL, params={"latitude":lat,"longitude":lon,"hourly":"pm2_5,pm10","forecast_days":days,"timezone":"Asia/Kolkata"}).json()
            source = "live"
        except Exception:
            data = _load("open_meteo_delhi_anand_vihar.json"); source = "fixture"
        h = data["hourly"]
        rows = [{"time": t, "pm25": p25, "pm10": p10, "source": source} for t,p25,p10 in zip(h["time"],h["pm2_5"],h["pm10"])]
        return _Cache.put(key, rows)

def _num(value: Any) -> float | None:
    try: return float(value)
    except (TypeError, ValueError): return None

def _field(row: dict[str, Any], *names: str) -> Any:
    normalized = {str(k).lower().replace(" ", "_"): v for k,v in row.items()}
    for name in names:
        if name in normalized: return normalized[name]
    return None

def _distance(a: float, b: float, c: float, d: float) -> float:
    p = math.pi/180; x = math.sin((c-a)*p/2)**2 + math.cos(a*p)*math.cos(c*p)*math.sin((d-b)*p/2)**2
    return 6371 * 2 * math.asin(math.sqrt(x))

class CpcbClient:
    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None): self.api_key, self.client = api_key or os.getenv("DATA_GOV_IN_API_KEY"), client or httpx.Client(timeout=15)
    def latest_near(self, lat: float, lon: float) -> dict[str, Any]:
        key=f"cpcb:{lat}:{lon}"; cached=_Cache.get(key)
        if cached: return {**cached,"source":"cached"}
        source="live"
        try:
            if not self.api_key: raise RuntimeError("DATA_GOV_IN_API_KEY missing")
            records=self.client.get(CPCB_URL,params={"api-key":self.api_key,"format":"json","limit":10000}).json()["records"]
        except Exception:
            records=_load("cpcb_documented_response.json")["records"]; source="fixture"
        groups: dict[tuple[str,float,float],dict[str,Any]]={}
        for row in records:
            station=_field(row,"station","station_name","stationname"); la=_num(_field(row,"latitude","lat")); lo=_num(_field(row,"longitude","lon")); pollutant=str(_field(row,"pollutant_id","pollutant","pollutantid") or "").lower(); value=_num(_field(row,"avg_value","avg_value_24hr","value","concentration"))
            if not station or la is None or lo is None or value is None: continue
            group=groups.setdefault((str(station),la,lo),{"station":station,"latitude":la,"longitude":lo,"observed_at":_field(row,"last_update","last_updated","updated_at")})
            if pollutant in {"pm2.5","pm2_5","pm25"}: group["pm25"]=value
            if pollutant in {"pm10","pm_10"}: group["pm10"]=value
        choices=[g for g in groups.values() if g.get("pm25") is not None]
        if not choices: raise RuntimeError("No CPCB station with PM2.5")
        chosen=min(choices,key=lambda g:_distance(lat,lon,g["latitude"],g["longitude"]))
        result={"station":chosen["station"],"distance_km":round(_distance(lat,lon,chosen["latitude"],chosen["longitude"]),2),"pm25":chosen["pm25"],"pm10":chosen.get("pm10"),"observed_at":chosen.get("observed_at"),"source":source}
        return _Cache.put(key,result)
