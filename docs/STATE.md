# STATE.md — Live handoff log

> Every agent: update this file at every commit and before your usage runs out (AGENTS.md §6).
> Statuses: `TODO` · `IN PROGRESS (<tool>, <time IST>)` · `DONE` · `BLOCKED (<why>)` · `CUT`

**Last updated:** Claude — Fri 9 Oct 2026 (planner honesty + swap rule fixes)
**Submission deadline (confirm on event page):** Sun 11 Oct, ____ IST  ·  **Feature freeze:** Sun 11 Oct, 12:00 IST
**Deployed API URL:** https://qcx2qrt6bj.execute-api.us-east-1.amazonaws.com
**Deployed frontend URL:** https://main.d6f34l6r9rpi9.amplifyapp.com (Amplify app d6f34l6r9rpi9, Git-connected, branch main)
**Repo:** _(add GitHub URL)_

---

## ▶ Resume here
- **Task:** Redeploy with the "planner honesty + swap rule" fixes, re-seed DynamoDB (schools changed), then T21 Amplify. Commands:
```
cd backend
sam build --use-container
sam deploy --stack-name saans --resolve-s3 --capabilities CAPABILITY_IAM --region us-east-1 --no-confirm-changeset --parameter-overrides DataGovInApiKey=$DATA_GOV_IN_API_KEY ModelProvider=gemini GeminiModelId=gemini-3.8-flash GeminiApiKey=$GEMINI_API_KEY OpenAqApiKey=$OPENAQ_API_KEY
AWS_DEFAULT_REGION=us-east-1 STORE=dynamo .venv/bin/python scripts/seed_dynamo.py saans-schools   # or ../.venv/bin/python
```
- Then Amplify (manual deploy): `cd frontend && VITE_API_URL=$URL npm run build && (cd dist && zip -r ../dist.zip .)`, upload `frontend/dist.zip` in Amplify → app → Deploy updates. Needed: capture real CPCB sample into `backend/fixtures/cpcb_live_sample.json` (item 2 unverified).
- (older notes below)
- **Done:** frontend wired to API (VITE_API_URL, default http://localhost:8000); `backend/template.yaml`, `backend/scripts/seed_dynamo.py` written. Not deployed: `aws` session expired and `docker` is not installed.
- **Next (human):** `aws login` (or `aws configure`), install/start Docker Desktop, then from repo root:
```
cd backend
sam build --use-container
sam deploy --stack-name saans --resolve-s3 --capabilities CAPABILITY_IAM --region us-east-1 --no-confirm-changeset --parameter-overrides DataGovInApiKey=$DATA_GOV_IN_API_KEY
.venv/bin/python scripts/seed_dynamo.py
URL=$(aws cloudformation describe-stacks --stack-name saans --region us-east-1 --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)
curl $URL/api/health; curl $URL/api/schools/delhi-anand-vihar/today
```
- Caveat: `CodeUri: .` also packages `backend/.venv`; if the build is slow, build from a copy without `.venv`.
- Then record URL above, set `VITE_API_URL` in Amplify, do T21.

---

## Test status
| When | Tool | Backend `pytest -q` | Frontend `npm run build` |
|---|---|---|---|
| — | — | not run | not run |
| Fri 9 Oct 2026, 16:35 IST | Codex | unavailable — `backend/` absent | unavailable — `frontend/` absent |
| Fri 9 Oct 2026, 16:42 IST | Codex | 1 passed | passed |
| Fri 9 Oct 2026, 16:47 IST | Codex | 20 passed | passed |
| Fri 9 Oct 2026, 16:51 IST | Codex | 41 passed | passed |
| Fri 9 Oct 2026, 17:45 IST | Antigravity | not run | passed |
| Fri 9 Oct 2026, 17:55 IST | Antigravity | not run | passed |
| Fri 9 Oct 2026, 19:00 IST | Claude | 56 passed | not run |
| Fri 9 Oct 2026 (fix commit) | Claude | 75 passed | not run |
| Fri 9 Oct 2026 (OpenAQ commit) | Claude | 94 passed | passed |
| Fri 9 Oct 2026 (swap exchange / sources / README) | Claude | 106 passed | passed |
| Fri 9 Oct 2026 (monitors + number guard) | Claude | 118 passed | passed |
| Fri 9 Oct 2026 (calibration note) | Claude | 125 passed | passed |
| Fri 9 Oct 2026 (T19) | Claude | 138 passed | passed |
| Fri 9 Oct 2026 (T23) | Claude | 144 passed | passed (+ vitest 4 passed) |
| Fri 9 Oct 2026 (attempt timeout) | Claude | 148 passed | — |
| Fri 9 Oct 2026 (replay tool dates) | Claude | 151 passed | — |
| Sat 10 Oct 2026 (null hours / no-data) | Claude | 155 passed | — |
| Fri 9 Oct 2026, 18:05 IST | Cursor | collection error (`mangum` missing in this env; PYTHONPATH=. needed) | passed |

---

## Task board
| ID | Task | Owner (default) | Depends on | Status | Notes |
|---|---|---|---|---|---|
| T01 | Builder Center verification, Avishi joins | Human | — | TODO | |
| T02 | Keys: data.gov.in, AWS CLI/SAM, Bedrock Nova Lite access, $5 budget | Human | — | TODO | |
| T03 | Scaffold repo | Any | — | DONE | FastAPI/Mangum health endpoint + test; Vite React TypeScript Tailwind placeholder; local `.venv` created. Tests: 1 passed; frontend build passed. |
| T04 | aqi.py + tests | Cursor | T03 | DONE | CPCB PM2.5/PM10 NAQI interpolation, metadata, caps, and invalid-input handling. Tests: 20 passed; frontend build passed. |
| T05 | sources.py + fixtures + tests | Cursor | T03 | DONE (CPCB live unverified) | Open-Meteo response verified (`hourly.time`, `pm2_5`, `pm10`); client/cache/fallback and fixtures added. Tests: 43 passed. |
| T06 | calibrate.py + tests | Cursor | T04, T05 | DONE | Bias ratio clipping, 12-hour decay, and uncalibrated distant/missing observation path tested. |
| T07 | rules.py + tests | Cursor | T04 | DONE | Deterministic activity/sensitive-student protocol actions with simple Hindi text; every table cell tested. Tests: 41 passed; frontend build passed. |
| T08 | models.py + store.py + seed schools | Cursor | T03 | TODO | |
| T09 | planner.py + tests | Cursor | T06, T07, T08 | DONE | Planner rules tested (51 passed). Fixture E2E table: `PE | 362 | Very Poor | indoors | 13:00–13:40 (AQI 33, Good)`. |
| T10 | app.py endpoints | Cursor | T09 | DONE | §6 endpoints + CORS + Mangum; /api/ask is a stub until T18; notice polish returns 501. |
| T11 | notices.py EN/HI + WhatsApp URL | Cursor | T09 | DONE | Deterministic EN/HI, mode label, wa.me URL; 3 tests. |
| T12 | SAM deploy walking skeleton | Cursor + Human | T10, T02 | DONE | Verified 9 Oct 21:20 IST: /today live (calibrated live:openaq, 8.4 km), replay=delhi-nov (PE ⇄ Period 8, 351→127), /api/ask via Gemini used get_day_plan. |
| T13 | Frontend Today view | Antigravity | T10 | DONE | Built with mock data flag. Mobile-first, CPCB colors, action reasons included. |
| T14 | Frontend onboarding | Antigravity | T10 | IN PROGRESS (Cursor, 18:05 IST) | Reduced scope: city presets + geolocation, no map. |
| T15 | Frontend Week + Best day | Antigravity | T10 | DONE | Ranking comes from `getBestDay` (planner.best_day); frontend only displays. Mock until T10. |
| T16 | Frontend Notice + EN/HI toggle | Antigravity | T11 | DONE | Notice view with WhatsApp share and EN/HI tabs. Global language context added. |
| T17 | agent.py (Strands + Bedrock) | Cursor | T09, T02 | DONE (Bedrock call untested) | 5 tool fns + tests (58 pass); `ask()` uses BedrockModel Nova Lite; needs T02 Bedrock access for a manual smoke test. |
| T18 | /api/ask + polished notice | Cursor | T17 | CUT | /api/ask wired to agent with deterministic fallback; `polish=true` cut (stays 501). |
| T19 | Daily EventBridge job | Cursor | T12 | DONE (deployed + invoked OK 22:38 IST) | `DailyFunction` (jobs/daily.py) via EventBridge Scheduler `cron(0 6 * * ? *)` Asia/Kolkata → saans-cache `school_id#date` {rows, sources, plan, stored_at}. /today serves it as mode "cached" if < 3 h old (re-planned so `now` is current; generated_at = fetch time), else live; cache errors → live. |
| T20 | Frontend Ask Saans chat | Antigravity | T18 | DONE | `AskView.tsx`: question box, answer, "✓ numbers checked" when verified; shares replay toggle with Today (state lifted to App). |
| T21 | Amplify Hosting | Human + Any | T13 | TODO | |
| T22 | Replay mode | Any | T09, T13 | DONE | `/today?replay=delhi-nov` → recorded Open-Meteo day 2025-11-19 (`fixtures/replay_delhi_nov.json`), mode=replay, `replay_date`; frontend banner + "Try a bad-air day" link. Morning Very Poor (351) → PE swap to 13:00 (Moderate). |
| T23 | Resilience pass | Antigravity | T21 | DONE | backend/tests/test_resilience.py: Open-Meteo, CPCB/OpenAQ, Gemini down one at a time and all together → 200 with honest mode/source/note. Frontend: `modeBanner()` (replay/fixture/cached) + vitest; error screen has Retry (never blank); empty timetable message. |
| T24 | UI polish | Antigravity | T13–T16 | DONE (Claude) | Calm stone/teal palette, Saans wordmark header (school picker + EN/हिंदी), Today: big AQI in band colour, 500+ beyond-scale line, one-line verdict, go/caution/indoors icons, outdoor cards only (indoor classes collapsed), swap cards (required sky, optional grey), banners, amber calibration note. Ask: chat, progress steps, typing dots, "Show plan summary now" after 8 s (client-side from /today), ✓ numbers checked, model name. Notice follows global language + replay. Week: honest chart. Deep links ?replay=delhi-nov&tab=ask&lang=hi&school=… |
| T25 | README | Any | T21 | TODO | |
| T26 | Demo video | Human | T24 | TODO | |
| T27 | AWS Builder Center blog | Human (+agent draft) | T25 | TODO | |
| T28 | Final checklist | Human | all | TODO | |
| T29 | Submit | Human | T28 | TODO | |

---

## Decisions log (append only)
- 2026-10-09 — Track 01 Air, sub-problem "School safety on bad days". Product: Saans. Stack per AGENTS.md §2. (Claude)
- 2026-10-09 — Planner honesty + swap rule (Claude): (1) only outdoor periods get rules.py actions/swaps; indoor = `go`, "Indoor class — no change needed", `SAANS-INDOOR`. (2) Calibrate only with a live (or cached <2h) CPCB reading ≤25 km and station timestamp <2h; fixtures are never cached or relabelled "cached"; `DayPlan.mode` = FORECAST source, `sources.observation` separate; calibration ratio anchored on the current IST hour (was hour 0). (3) Swap rule changed (PLAN §3.3): outdoor+`indoors` period → cheapest same-day swappable slot (08:00–15:00) giving `go`/`caution`; replaces "2+ bands better". (4) `DayPlan.now` = current IST hour; worst/best hour over 07:00–16:00; `generated_at` IST with offset. (5) Seed PE labels match grade; two grades/school; period ids now `p0..p9` (re-seed Dynamo). (6) Agent failures logged via `logger.exception`. (7) `MODEL_PROVIDER=gemini` uses Strands `GeminiModel` (`strands-agents[gemini]`, `GEMINI_API_KEY` NoEcho SAM param, `GEMINI_MODEL_ID` default gemini-2.5-flash); Bedrock stays default. Added `saans/forecast.py` (shared loader for app + agent).
- 2026-10-09 — aqi.py bugfix (Claude): CPCB breakpoint gaps (60→61, 100→101, 250→251…) made decimal concentrations such as PM2.5 60.1 return AQI 500/Severe; bands are now contiguous. Found in live /today output. Needs redeploy.
- 2026-10-09 — CPCB parser (Claude): real data.gov.in rows use `pollutant_avg` (+ "NA" strings); old parser only knew `avg_value`, so live always fell to the fixture silently. Now handles pollutant_avg/avg_value, "NA", groups by station, nearest with PM2.5, and logs the exact failure reason (logger.warning). UNVERIFIED against a real response: `backend/fixtures/cpcb_live_sample.json` was missing from the repo and api.data.gov.in is unreachable from the agent sandbox. Human: capture a sample (see chat) and commit it.
- 2026-10-09 — Replay (Claude): `replay` query param is now a recording key (`delhi-nov`), not a date; unknown key → 404. Replay uses sources.forecast="recorded", observation "none", uncalibrated; `now` = 08:00 reading. Footer no longer claims "calibrated" unless `now.calibrated`.
- 2026-10-09 — Optional swap (Claude): `Swap.optional` (default false). `caution` outdoor period + same-day swappable slot giving `go` → swap with optional=true; frontend renders it as "Better slot available". PLAN §3.3 updated.
- 2026-10-09 — Incident (Claude): commit 6fddeeb accidentally included `backend/.aws-sam/` build output (5.5k library files, no secrets). Untracked in the next commit and added to .gitignore; history not rewritten (AGENTS.md §7). Always `git add` explicit paths.
- 2026-10-09 — Calibration source chain (Claude): data.gov.in CPCB → OpenAQ v3 (`OPENAQ_API_KEY`, NoEcho SAM param `OpenAqApiKey`; `GET /v3/parameters/2/latest?coordinates&radius=25000`, nearest fresh PM2.5 sensor, header X-API-Key) → uncalibrated. `sources.observation` = `<source>:<provider>` e.g. `live:openaq`, `fixture:cpcb`, `none`. OpenAQ parser UNVERIFIED against a real response (no key/network in agent sandbox); parser is defensive and logs reasons via logger.warning.
- 2026-10-09 — Swap = exchange (Claude): only swappable outdoor periods move; target must be an indoor swappable class period 08:00–15:00; each target used once (greedy, worst AQI first, lowest-AQI free target); optional (caution→go) follows the same rules. Swap gains `with_period_id`, `with_label`. Replay: Class 7B PE 08:40 ⇄ Period 8 13:40 · AQI 351 → 127. PLAN §3.3 rewritten.
- 2026-10-09 — Model ids from env only (Claude): live error 404 "models/gemini-2.5-flash is no longer available to new users". `GeminiModelId` SAM param (default gemini-3.8-flash) → `GEMINI_MODEL_ID`; `BEDROCK_MODEL_ID` likewise required from env. No model names in code; missing env → RuntimeError → logged + deterministic fallback.
- 2026-10-09 — Sources (Claude): data.gov.in refuses connections from AWS (ConnectError 111) → CPCB client connect timeout 3 s (read 10 s); chain unchanged CPCB → OpenAQ → uncalibrated. OpenAQ `sources.station` = location `name` via `GET /v3/locations/{id}` (cached; falls back to "OpenAQ location <id>" if lookup fails).
- 2026-10-09 — Live verification (Claude): OpenAQ picked station "Air Check" (8.42 km) — possibly a low-cost/community sensor, not a CPCB reference monitor; README says "CPCB station data via OpenAQ". Consider restricting OpenAQ to reference monitors (locations `monitor=true` / CPCB provider). Agent phrased the source as "Air Check station forecast" (it is an Open-Meteo forecast calibrated with that station) — SYSTEM_PROMPT could be tightened.
- 2026-10-09 — Reference monitors + grounded Ask (Claude): (1) OpenAQ now `GET /v3/locations?coordinates&radius=25000&monitor=true&parameters_id=2`, client-side `isMonitor is True` too (low-cost sensors like "Air Check" never used), CPCB provider ("CPCB"/"Central Pollution Control Board") preferred then nearest, latest via `/v3/locations/{id}/latest` (fresh < 2h); none within 25 km → uncalibrated. station = "<name> (CPCB via OpenAQ)" or "<name> (reference monitor via OpenAQ)". (2) SYSTEM_PROMPT: Open-Meteo (CAMS) forecast calibrated with the named station's latest reading; never "station forecast"; always state time + calibrated or not; replay = recorded data. (3) `/api/ask` accepts `replay`; tools are built per request (`make_tools(replay, sink)`) so every tool uses the screen's context; unknown replay → 404. (4) Number guard: every number ≥ 20 in the answer must appear in that request's tool outputs, the question, or the school profile; otherwise logger.warning + deterministic plan summary (`deterministic_answer`). Response adds `verified` (and `fallback` when deterministic). Model failure now also returns the deterministic plan summary instead of a generic message.
- 2026-10-09 — Ask time budget (Claude): live /api/ask hit the 30 s Lambda/API Gateway limit (Gemini; earlier call 15.8 s) → "Service Unavailable". Agent now runs with `AGENT_TIMEOUT_S` (default 20 s, set in template.yaml); on timeout logger.warning + deterministic plan summary (`timed_out: true`).
- 2026-10-09 — OpenAQ diagnostics (Claude): live logs: "no reference monitor with fresh PM2.5 within 25 km (71 locations returned)" → reason unknown. Failure message now counts rejections (not_monitor, no_pm25_sensor, too_far, no_latest_for_pm25_sensor, stale + ages, bad_value/timestamp); tries 8 candidates. `scripts/openaq_probe.py` prints raw fields per location. `sources.station`/`distance_km` now null unless that observation actually calibrated the forecast. NEXT: human runs the probe locally and pastes output.
- 2026-10-09 — Calibration honesty (Claude): probe showed OpenAQ code is correct but its CPCB feed is ~50 h behind (newest 2026-10-07 20:00 IST) and data.gov.in refuses AWS → no fresh reading, so live is uncalibrated. Decision: keep the 2 h freshness rule (a 2-day-old reading must not correct today's hourly forecast). Added `sources.note` (e.g. "Not calibrated: CPCB (data.gov.in) unreachable; nearest CPCB monitor via OpenAQ last reported 50 h ago"), shown in the Today footer; README wording fixed. Possible later: non-AWS fetcher for data.gov.in → saans-cache, or WAQI (needs AQI→concentration conversion).
- 2026-10-09 — Live verification #2 (Claude, ~22:00 IST): /today = live, uncalibrated, station null, note "Not calibrated: CPCB (data.gov.in) unreachable; nearest CPCB monitor via OpenAQ last reported 50 h ago". Pending: re-check POST /api/ask (20 s budget) and upload new frontend to Amplify.
- 2026-10-09 — rules.py text fix (Claude): Very Poor non-assembly activities said "use the PA system or classroom for assembly" (seen in live Ask fallback for PE). Now PA text only for assembly; others "Hold <activity> indoors." Levels/rule_ids unchanged. Live Ask (replay) returned fallback — cause (timeout vs number guard) to be read from CloudWatch. Amplify app `d6f34l6r9rpi9` is Git-connected (auto-builds on push; no manual upload).
- 2026-10-09 — Amplify (Claude): Git-connected app builds on every push (job 20 SUCCEED). Branch had no env vars, so `frontend/.env.production` now sets public `VITE_API_URL`. Live Ask fallback cause: Gemini 503 "high demand" (transient); deterministic fallback worked.
- 2026-10-09 — Gemini reliability (Claude): Strands' built-in retry (6 attempts from 4 s) disabled via `retry_strategy=None`; our policy: retry 503/429/500/504/timeouts up to 2× (0.5 s, 1.5 s) within the 20 s budget, then `GEMINI_FALLBACK_MODEL_ID` (new SAM param `GeminiFallbackModelId`, default `gemini-3.8-flash-lite` — UNVERIFIED: GEMINI_API_KEY not in agent shell, human to check models list), then plan summary. Non-retryable (e.g. 404) skips to fallback model. Logs which model answered; /api/ask returns `model`.
- 2026-10-09 — T19 (Claude): template env vars moved to `Globals.Function` (shared by ApiFunction + DailyFunction); output `DailyFunctionName`. Plan cache = `PlanCache` protocol in store.py (`JsonPlanCache` local at data/plan_cache.json, git-ignored; `DynamoPlanCache` stores body as JSON string). tests/conftest.py isolates the local cache.
- 2026-10-09 — T23 (Claude): new frontend devDependency `vitest@3.2.4` (`npm test`) for `src/utils/banner.ts`. No backend code changes were needed — all failure scenarios already returned 200 with honest labels.
- 2026-10-09 — Alarms (Claude): CloudWatch alarms `saans-api-errors` and `saans-daily-errors` (Lambda Errors Sum ≥ 5 in 300 s, missing data = not breaching). No notification action yet (no email/SNS configured) — visible in CloudWatch console.
- 2026-10-09 — Gemini fallback model (Claude): human listed models with their key; `gemini-3.8-flash-lite` does not exist (only `-tts`). `GeminiFallbackModelId` default → `gemini-3.5-flash-lite` (stable text model, different generation from primary). Note: being listed ≠ usable (gemini-2.5-flash is listed but 404s for new users).
- 2026-10-09 — Deploy verification #3 (Claude, 22:35–22:40 IST, after human deploy of 8d7f728): live /today OK (live, uncalibrated, note "…51 h ago"); replay OK (PE "Hold PE indoors." ⇄ Period 8 13:40, 351→127); daily job invoke OK (3 stored, 0 failed) → /today mode "cached"; Amplify index + bundle reference qcx2qrt6bj API, no localhost. Ask ×2 = timed_out fallback: Gemini took ~18 s to return 503 / hung, so retries + fallback model never ran.
- 2026-10-09 — Gemini per-attempt timeout (Claude): `GEMINI_ATTEMPT_TIMEOUT_S` (6 s, template env) → genai `http_options.timeout`; retry only if remaining budget covers retry + one attempt per later model; start an attempt only if one fits. NEEDS REDEPLOY.
- 2026-10-09 — Gemini deadline fix (Claude): live Ask after 11f8b98 returned the plan summary in 1.7–8 s because Gemini rejects request deadlines < 10 s (400 INVALID_ARGUMENT "Minimum allowed deadline is 10s"). Per-attempt timeout now floored at 10 s (`GEMINI_ATTEMPT_TIMEOUT_S` 10); `AGENT_TIMEOUT_S` 20 → 24 so primary (≤10 s) + fallback model (≤10 s) fit under API Gateway's 30 s. NEEDS REDEPLOY.
- 2026-10-09 — Live Ask after f48f9af (Claude, 23:09 IST): #1 primary gemini-3.8-flash failed (~18 s, overloaded) → 6 s left → plan summary at 22 s (as designed); #2 answered by fallback gemini-3.5-flash-lite in 14 s but said it "cannot retrieve plan data" — model passed the replay key as `date`. Fix: replay tools ignore `date`; live tools return {"error": "...Available dates: ..."} for unknown dates instead of raising; replay prompt context names the recorded date (2025-11-19), not the key. NEEDS REDEPLOY.
- 2026-10-09 — Live Ask verified (Claude, 23:20 IST, after e6393c8): #1 primary ReadTimeout (10 s) → fallback gemini-3.5-flash-lite answered in 19.6 s, verified, tools get_hourly_forecast+get_day_plan, correct (AQI 351, Hold PE indoors, replay date stated). #2 gemini-3.8-flash answered in 8.6 s, verified, incl. swap ⇄ Period 8 13:40 AQI 127 and "uncalibrated". Item 1 (retry → fallback model → plan summary) confirmed live.
- 2026-10-09 — Alarm notifications (Claude): `AlertEmail` SAM param (default empty) → condition HasAlertEmail → SNS topic `saans-alerts` + email subscription; both alarms' AlarmActions → topic. Subscription must be confirmed from the inbox. Agent deploy attempts failed twice with S3 UploadPart RequestTimeout from the agent sandbox; human to run `sam deploy ... --parameter-overrides AlertEmail=<email>` (other params keep previous values via SAM UsePreviousValue).
- 2026-10-10 — SNS alerts live (Claude, ~00:30 IST): topic saans-alerts, email subscription CONFIRMED (has subscription ARN), both alarms → topic; Ask still OK (gemini-3.5-flash-lite, verified) so keys survived the param-only deploy.
- 2026-10-10 — LIVE BUG /today 500 after midnight (Claude): Open-Meteo returns null PM for the last horizon hours (2026-10-14 06:00–23:00) → calibrate float(None) TypeError. Fix: OpenMeteoClient drops null hours. Safety fix found alongside: planner treated a period with no forecast rows as AQI 0 "Good"/go → now band "No data", `NO_DATA_ACTION` (caution, rule SAANS-NO-DATA), never moved/targeted by swaps; plan_week/best_day only use `complete_days` (all hours 07–16 present). NEEDS REDEPLOY.
- 2026-10-10 — Gemini model choice (human decision, Claude): gemini-3.8-flash kept failing under load (~19 s per failed attempt = 2 calls × 10 s), starving the fallback. Primary → `gemini-3.5-flash-lite`, fallback → `gemini-3.1-flash-lite` (both in the account's models list). Template defaults updated. Deployed by agent (param-only, code artifacts unchanged → no upload) ~01:05 IST. Verified: 4/4 Asks answered by gemini-3.5-flash-lite, verified=true, 2.4–9 s, incl. Hindi; correct replay facts (AQI 351, Hold PE indoors, recorded 2025-11-19).
- 2026-10-10 — CORS bug (Claude): Ask never worked from the hosted site — browser preflight OPTIONS /api/ask got 400 because API Gateway forwards OPTIONS to FastAPI, whose CORSMiddleware allowed only localhost (curl tests skip preflight). Now allow_origins ["*"], allow_credentials False. Found by Playwright screenshots. NEEDS BACKEND DEPLOY.
- 2026-10-10 — Notice honesty (Claude, found in screenshots): notice said "moved to 09:20" for OPTIONAL swaps and announced required swaps as done. Now: optional swaps not mentioned; required swaps offered ("Hold PE indoors, or move it to 13:40 (Moderate, AQI 127)."); asthma line labelled "Students with asthma:"; GET /notice accepts `replay`. NEEDS BACKEND DEPLOY.
- 2026-10-10 — Screenshots (Claude): frontend devDependency `playwright@1.55.0` (+ `npx playwright install chromium`); `npm run shots [url]` → docs/img/*.png at 375×812 against the deployed app.
- 2026-10-09 — Added lucide-react and recharts dependencies for frontend UI components.

## Known issues / surprises
- T05: Open-Meteo live schema and three location forecasts verified. data.gov.in resource `3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69` could not be reached from this environment and no private API key was present, so CPCB uses a clearly labelled documented-shape fixture; live parser remains unverified.
- Frontend baseline regressed after T05 due to unrelated concurrent files: `src/api.ts` needs Vite `ImportMeta.env` typing and `src/TodayView.tsx` imports missing `lucide-react`. Backend remains green.
- Cursor session: `pytest` collection fails here without installed backend deps (`mangum`). Frontend `npm run build` passed after `npm install`.

## Handoff history (append only)
| Time (IST) | From → To | Summary |
|---|---|---|
| Fri 16:00 | Claude → humans | Kit created. Start with T01–T03. |
| Fri 16:42 | Codex → Codex | T03 complete. Begin T04 in `backend/saans/aqi.py`. |
| Fri 16:47 | Codex → Codex | T04 complete. Begin T07 in `backend/saans/rules.py`. |
| Fri 16:51 | Codex → Antigravity | T07 complete. Resume with T05 in `backend/saans/sources.py`. |
| Fri 17:00 | Antigravity → next agent | T13 complete in frontend/ with mock data. Ready for T14 or T15. |
| Fri 17:45 | Antigravity → next agent | T15 and T16 complete. Bottom tab navigation added. |
| Fri 17:55 | Antigravity → next agent | T14 complete. Best day fixed to use API purely. |
| Fri 18:05 | Cursor → Cursor | Best-day ranking typed and displayed from `getBestDay` only (no frontend ranking). T14 reduced-scope next. |
| Fri 18:20 | Codex → next agent | T09 complete. Resume with T10 in `backend/app.py`. |
