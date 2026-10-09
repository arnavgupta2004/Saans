#!/usr/bin/env bash
# Smoke test for the deployed Saans API + frontend. Prints PASS/FAIL per check; exits 1 if any check fails.
# Usage: scripts/smoke.sh [API_BASE] [FRONTEND_URL]
set -u
API="${1:-https://qcx2qrt6bj.execute-api.us-east-1.amazonaws.com}/api"
WEB="${2:-https://main.d6f34l6r9rpi9.amplifyapp.com}"
SCHOOLS="delhi-anand-vihar delhi-dwarka bengaluru-indiranagar"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
pass=0; fail=0

# check NAME EXPECTED_STATUS PY_ASSERT curl-args...   (PY_ASSERT gets `d` = parsed JSON, `t` = raw text, `h` = headers)
check() {
  local name="$1" want="$2" assertion="$3"; shift 3
  local code secs
  read -r code secs < <(curl -s -m 40 -D "$TMP/h" -o "$TMP/b" -w "%{http_code} %{time_total}" "$@")
  if [ "$code" = "$want" ] && python3 - "$TMP/b" "$TMP/h" "$assertion" <<'PY'
import json, sys
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
h = open(sys.argv[2], encoding="utf-8", errors="replace").read().lower()
try: d = json.loads(t)
except Exception: d = None
sys.exit(0 if eval(sys.argv[3]) else 1)
PY
  then printf "PASS  %-58s %s %5.2fs\n" "$name" "$code" "$secs"; pass=$((pass+1))
  else printf "FAIL  %-58s %s %5.2fs  %s\n" "$name" "$code" "$secs" "$(head -c 120 "$TMP/b" | tr '\n' ' ')"; fail=$((fail+1)); fi
}

check "health"                                  200 "d['ok'] is True"                                   "$API/health"
check "schools list"                            200 "len(d) == 3"                                       "$API/schools"
for s in $SCHOOLS; do
  check "$s today (live)"                       200 "d['mode'] in ('live','cached','fixture') and d['periods'] and d['now']" "$API/schools/$s/today"
  check "$s today (replay)"                     200 "d['mode']=='replay' and d['replay_date']=='2025-11-19' and d['impact']['swaps']>=1" "$API/schools/$s/today?replay=delhi-nov"
  check "$s week"                               200 "d['days'] and 'impact' in d"                       "$API/schools/$s/week"
  check "$s best-day 09:00-12:00"               200 "d['ranking'] and all(r['band'] for r in d['ranking'])" "$API/schools/$s/best-day?start=09:00&end=12:00"
  check "$s notice EN"                          200 "d['text'].startswith('Dear Parents') and 'wa.me' in d['whatsapp_url']" "$API/schools/$s/notice?lang=en"
  check "$s notice HI (replay)"                 200 "'प्रिय अभिभावकगण' in d['text'] and d['mode']=='replay'" "$API/schools/$s/notice?lang=hi&replay=delhi-nov"
done
check "replay swap: 7B PE <-> Period 8, 351 -> 127" 200 "any(p['swap'] and p['aqi']==351 and p['swap']['to_aqi']==127 for p in d['periods'])" "$API/schools/delhi-anand-vihar/today?replay=delhi-nov"
check "ask (replay) answers"                    200 "d['answer'] and (d.get('verified') or d.get('fallback'))" \
  -X POST "$API/ask" -H 'Content-Type: application/json' -d '{"school_id":"delhi-anand-vihar","question":"Is PE at 8:40 safe?","lang":"en","replay":"delhi-nov"}'
check "unknown school -> 404"                   404 "True"                                              "$API/schools/nope/today"
check "unknown replay key -> 404 (no echo)"     404 "'zzz' not in t"                                    "$API/schools/delhi-anand-vihar/today?replay=zzz"
check "question > 300 chars -> 422"             422 "'300' in d['detail']" \
  -X POST "$API/ask" -H 'Content-Type: application/json' -d "{\"school_id\":\"delhi-anand-vihar\",\"question\":\"$(printf 'x%.0s' $(seq 1 301))\"}"
check "demo school is read-only -> 403"         403 "True" \
  -X POST "$API/schools" -H 'Content-Type: application/json' -d '{"id":"delhi-anand-vihar","name":"x","city":"x","lat":0,"lon":0,"timetable":[]}'
check "CORS preflight from Amplify allowed"     200 "'access-control-allow-origin: $WEB' in h" \
  -X OPTIONS "$API/ask" -H "Origin: $WEB" -H 'Access-Control-Request-Method: POST' -H 'Access-Control-Request-Headers: content-type'
check "CORS from unknown origin not allowed"    400 "'access-control-allow-origin' not in h" \
  -X OPTIONS "$API/ask" -H 'Origin: https://evil.example.com' -H 'Access-Control-Request-Method: POST' -H 'Access-Control-Request-Headers: content-type'
check "frontend loads"                          200 "'<div id=\"root\">' in t"                          "$WEB/"

echo "----"; echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
