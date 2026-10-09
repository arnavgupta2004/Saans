"""Show why OpenAQ monitors near a school are accepted/rejected.
Usage (from backend/): OPENAQ_API_KEY=... ../.venv/bin/python scripts/openaq_probe.py [lat lon]   (default: Anand Vihar)"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from saans.sources import IST, OPENAQ_LOCATIONS_URL, OPENAQ_RADIUS_M, OpenAqClient, _distance, _is_cpcb, rank_openaq_monitors  # noqa: E402

lat, lon = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) > 2 else (28.647, 77.316)
c = OpenAqClient()
locs = c._get(OPENAQ_LOCATIONS_URL, coordinates=f"{lat},{lon}", radius=OPENAQ_RADIUS_M, monitor="true", parameters_id=2, limit=100)
print(f"{len(locs)} locations; first one's keys: {sorted(locs[0]) if locs else []}")
for loc in locs[:15]:
    co = loc.get("coordinates") or {}
    print(f"- {loc.get('id')} {loc.get('name')!r} provider={(loc.get('provider') or {}).get('name')!r} isMonitor={loc.get('isMonitor')!r} "
          f"dist={_distance(lat, lon, co.get('latitude', 0), co.get('longitude', 0)):.1f}km datetimeLast={(loc.get('datetimeLast') or {}).get('local')} "
          f"sensors={[(s.get('id'), (s.get('parameter') or {}).get('id'), (s.get('parameter') or {}).get('name')) for s in loc.get('sensors') or []]}")
print("\nRanked candidates (CPCB first, then nearest):")
now = datetime.now(IST)
for loc, d, sensors in rank_openaq_monitors(locs, lat, lon)[:8]:
    latest = c._get(f"{OPENAQ_LOCATIONS_URL}/{loc['id']}/latest")
    rows = [r for r in latest if r.get("sensorsId") in sensors]
    print(f"* {loc.get('name')!r} cpcb={_is_cpcb(loc)} {d:.1f}km pm25_sensors={sensors} latest_rows={len(latest)} matching={rows[:2]}")
print(f"\nnow (IST) = {now.isoformat()}")
try:
    print("\nlatest_near ->", OpenAqClient().latest_near(lat, lon))
except Exception as exc:
    print("\nlatest_near FAILED ->", exc)
