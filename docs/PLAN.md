# Saans — Winning Plan for Environmental Hacks 2026

**Event:** Environmental Hacks — Bharat Builds Tour, Event 02 (WeMakeDevs × AWS), Oct 8–11, 2026
**Team:** Chernobyl (Arnav Gupta — leader; Avishi — invited) · Team code R8TMST
**Track:** 01 — Air · Sub-problem: *School safety on bad days*
**Submissions open:** Sun 11 Oct, 08:00 IST · **Deadline:** the page showed "ends in 2 days, 4 hours" — confirm the exact time on the event page and write it at the top of STATE.md. This plan assumes **Sun 11 Oct ~20:00 IST** and targets submitting by **18:00**.
**You cannot change the team after submitting** → get Avishi to accept the invite before submitting.

---

## 1. The idea in one line

> **Saans turns tomorrow's hour-by-hour air forecast into today's school timetable decisions — which period moves indoors, which one moves to a cleaner hour, and what to tell parents, in their language.**

### Why this wins (mapped to the five judging criteria)

| Criterion | How Saans scores |
|---|---|
| **1. Idea & impact** | A specific user (school principal / PE teacher), a specific daily decision, a specific vulnerable group (children, esp. kids with asthma). "A small problem solved well beats a big one solved vaguely" — this is exactly that. October is when North India's AQI climbs with stubble burning, so the problem is live *during judging*. |
| **2. Built on AWS** | Double-qualified: **Strands Agents SDK + AWS SAM** (open source) *and* deployed on **Lambda, API Gateway, DynamoDB, EventBridge Scheduler, Amplify Hosting, Bedrock, CloudWatch**. Architecture diagram in README and video. |
| **3. Design & usability** | One screen: "Today at your school" — each period as a colour card with the action. Mobile-first. Hindi toggle. One-tap WhatsApp notice. A principal can use it with zero training. |
| **4. Execution** | Core is deterministic and tested (NAQI math, rules, planner). Every external dependency has a fallback. Live URL that works. |
| **5. Demo video** | The "swap" moment is visual and instantly understood: *PE at 08:40 → AQI 312 → moved to 13:30 → AQI 198.* Then the parent notice in Hindi, then the agent answering "best day for Sports Day". |

### What makes it different from the 100 other AQI dashboards
1. **Decisions, not dashboards.** Nobody needs another AQI number. They need "what do I do with period 3".
2. **Hour-level timetable swaps.** PM2.5 in Indian cities often peaks in the early morning (temperature inversion) and drops in the afternoon. Moving a PE class by five hours genuinely changes exposure. Most teams will show daily AQI only.
3. **Calibrated forecast.** Global model forecasts (CAMS via Open-Meteo) are often biased for Indian cities. Saans corrects the forecast with the nearest live CPCB station reading. Shows data-science rigour without a fragile ML pipeline.
4. **Explainable + honest.** Every recommendation shows the number, the band, the source, and the rule that fired.
5. **Last mile:** bilingual parent notice via WhatsApp share link — no SMS/DLT registration needed.

---

## 2. Users and the core flow

**Primary user:** Principal / PE coordinator. **Secondary:** Parents (receive the notice).

1. **Onboard school (1 min):** name, pick location on a map (or choose city preset), add the outdoor parts of the timetable (assembly, PE periods, recess, sports), number of students with asthma (a count only — no names, no health records).
2. **Today view (the hero screen):** banner with current AQI (calibrated) + band colour; then each outdoor period as a card: time, activity, forecast AQI for that hour, band, **action**, and a **"Swap to 13:30 (AQI 198)"** suggestion where a better slot exists the same day.
3. **Week view:** 5-day strip with daily worst/best hours; "Best day for an outdoor event" picker.
4. **Parent notice:** generated in English + Hindi; buttons: Copy, Share on WhatsApp (`https://wa.me/?text=...`).
5. **Ask Saans:** chat box → Strands agent with tools (e.g., "Can we take Class 5 to the zoo on Wednesday morning?").
6. **Daily automation:** EventBridge runs the daily job at 06:00 IST, computes every school's plan, stores it — the principal opens the app and it is ready.

---

## 3. The science (put this in README — judges like it)

### 3.1 NAQI from pollutant concentration (CPCB method)
Sub-index for each pollutant by linear interpolation within its breakpoint band; overall AQI = max sub-index.

| AQI | Category | PM2.5 (µg/m³, 24h) | PM10 (µg/m³, 24h) |
|---|---|---|---|
| 0–50 | Good | 0–30 | 0–50 |
| 51–100 | Satisfactory | 31–60 | 51–100 |
| 101–200 | Moderate | 61–90 | 101–250 |
| 201–300 | Poor | 91–120 | 251–350 |
| 301–400 | Very Poor | 121–250 | 351–430 |
| 401–500 | Severe | 250+ | 430+ |

Formula: `I = (I_hi - I_lo) / (B_hi - B_lo) * (C - B_lo) + I_lo`. Cap at 500.
**Note for README (honesty):** official NAQI uses 24-hour averages; Saans applies the same breakpoints to hourly forecasts as an *hour-level exposure indicator*, and says so in the UI ("hourly indicator").

### 3.2 Calibration (bias correction)
- `forecast_now` = Open-Meteo PM2.5 for the current hour at the school.
- `observed_now` = latest PM2.5 at the nearest CPCB station (data.gov.in).
- `ratio = clip(observed_now / forecast_now, 0.5, 2.0)`.
- For each future hour `h` hours ahead: `factor(h) = 1 + (ratio - 1) * exp(-h / 12)` (correction fades over ~a day).
- Corrected forecast = raw × factor. Show both raw and calibrated on a small chart (good demo visual).
- If CPCB is unavailable or the station is > 25 km away: ratio = 1, UI says "uncalibrated".

### 3.3 School protocol (rules.py) — deterministic
Based on CPCB health-advisory categories; the thresholds for school actions are Saans' own conservative design (say this in README).

| Band | High-intensity outdoor (PE, sports) | Low-intensity outdoor (assembly, recess) | Students with asthma |
|---|---|---|---|
| Good / Satisfactory (≤100) | Go ahead | Go ahead | Normal; inhaler available |
| Moderate (101–200) | Go ahead, shorter warm-up, water breaks | Go ahead | Avoid strenuous; can stay in |
| Poor (201–300) | **Move indoors** or swap to cleaner slot | Keep short (≤15 min) | **Indoors** |
| Very Poor (301–400) | **Indoors** | **Indoors** (assembly over PA/classroom) | Indoors; inform parents |
| Severe (>400) | **Indoors** | **Indoors** | Indoors; escalate to management; follow state/GRAP directives |

Only **outdoor** periods get protocol actions (indoor periods are `go` / "Indoor class — no change needed", rule `SAANS-INDOOR`).

Swap rule (exchange): only outdoor periods with `swappable=true` can be moved; non-swappable outdoor periods (assembly, recess) only get their rules.py action. A swap is an EXCHANGE with an **indoor, swappable class period** (`outdoor=false`) the same day, starting 08:00–15:00, whose hours give the activity a better action level — never another outdoor period. `indoors` → target must give `go`/`caution`; `caution` → target must give `go` (`optional=true`, "Better slot available"). Each target is used at most once per day: assign greedily, worst period (highest AQI) first, to the lowest-AQI free target. `gain_bands` = band difference; Swap carries `with_period_id` and `with_label`.

### 3.4 Best day finder
For an activity with a duration and preferred hours (e.g., Sports Day 09:00–12:00), score each of the next 5 days by **max calibrated hourly AQI** in that window (lower is better), tie-break by mean. Return ranking + reason.

---

## 4. Architecture

```mermaid
flowchart LR
  U[Principal - mobile web] --> AMP[Amplify Hosting - React app]
  AMP --> APIGW[API Gateway HTTP API]
  APIGW --> L1[Lambda: FastAPI via Mangum]
  L1 --> DDB[(DynamoDB: schools, cache)]
  L1 --> OM[Open-Meteo Air Quality API]
  L1 --> CPCB[data.gov.in CPCB live AQI]
  L1 --> AG[Strands Agent]
  AG --> BR[Amazon Bedrock - Nova Lite]
  EB[EventBridge Scheduler 06:00 IST] --> L2[Lambda: daily job]
  L2 --> DDB
  L1 --> CW[CloudWatch logs]
  P[Parents] <-.WhatsApp share link.- U
```

Region: **us-east-1** for everything (simplest Bedrock model access). Latency is fine for this app.

**AWS cost check:** all of this fits comfortably in the free tier / starter credits. Bedrock calls are a few cents. Set a **$5 AWS Budget alert** in T03.

---

## 5. Task board (definitions)

Status is tracked in `docs/STATE.md`, not here. Each task: ≤ ~45 min of agent work. **Done = acceptance criteria met + tests pass + committed + STATE.md updated.**

Suggested tool split (either tool can do any task; this is just the default):
- **Cursor** → backend logic, tests, SAM/infra (T04–T12, T17–T19).
- **Antigravity** → frontend, browser testing of the UI, polish (T13–T16, T22–T24).
- **Human (Arnav/Avishi)** → accounts, keys, AWS console clicks, video, blog, submission (T01–T03, T25–T30).

### Phase 0 — Setup (Fri 16:00–18:00)
- **T01 [Human] Accounts.** Both teammates verify student status on **AWS Builder Center** (required to compete). Avishi accepts the team invite. Join WeMakeDevs Discord. ✅ when both profiles verified + team shows 2/4.
- **T02 [Human] Keys.** Get a free data.gov.in API key. Create AWS account (or use existing), enable **Bedrock model access for Amazon Nova Lite in us-east-1**, install AWS CLI + SAM CLI, `aws configure`. Create **AWS Budget alert at $5**. Put keys in `backend/.env` (not committed). ✅ when `aws sts get-caller-identity` works and a test Bedrock call works.
- **T03 [Any] Scaffold repo.** Create the layout in AGENTS.md §3, `.gitignore`, `.env.example`, `backend/requirements.txt` (fastapi, mangum, httpx, pydantic, python-dotenv, pytest, boto3, strands-agents), Vite React TS + Tailwind in `frontend/`. GitHub repo (public at submission). ✅ when `pytest` runs (0 tests OK) and `npm run build` succeeds.

### Phase 1 — Core engine, local only (Fri 18:00–Sat 01:00)
- **T04 aqi.py** — breakpoint tables (§3.1), `sub_index(pollutant, conc)`, `naqi(pm25, pm10) -> (aqi, band, dominant)`, band metadata (name, colour hex, CPCB health line). **Tests:** boundaries (30, 31, 60, 90, 120, 250, 251), PM10 dominance, cap at 500.
- **T05 sources.py** — `OpenMeteoClient.hourly(lat, lon, days=5)` → list of `{time, pm25, pm10}` in Asia/Kolkata; `CpcbClient.latest_near(lat, lon)` → `{station, distance_km, pm25, pm10, observed_at}`. In-memory + store cache (TTL 60 min). Record real responses into `fixtures/`. On error → fixture fallback flagged `source="fixture"`. **Tests** use fixtures (no network in tests).
  - Open-Meteo: `https://air-quality-api.open-meteo.com/v1/air-quality?latitude=..&longitude=..&hourly=pm2_5,pm10&forecast_days=5&timezone=Asia%2FKolkata` (verify against docs at open-meteo.com/en/docs/air-quality-api).
  - CPCB: data.gov.in "Real time Air Quality Index from various locations" dataset (find resource ID on data.gov.in; it returns per-station pollutant rows with lat/lon). Compute nearest station with haversine.
- **T06 calibrate.py** — §3.2. `calibrate(hourly, observed_now) -> hourly with pm25_cal, pm10_cal, factor, calibrated: bool`. **Tests:** ratio clipping, decay, no-observation path.
- **T07 rules.py** — §3.3. `action_for(activity_type, intensity, aqi_band, sensitive=False) -> Action{level: go|caution|indoors, text_en, text_hi_key, rule_id}`. **Tests:** every cell of the table.
- **T08 models.py + store.py** — pydantic `School, Period, PeriodPlan, DayPlan, WeekPlan`; `SchoolStore` protocol with `JsonStore` (file `backend/data/schools.json`) and `DynamoStore` (boto3). Selected by env `STORE=json|dynamo`. Seed 3 demo schools (Delhi – near Anand Vihar; Delhi – Dwarka; Bengaluru – Indiranagar) with realistic timetables.
- **T09 planner.py** — `plan_day(school, hourly_cal, date) -> DayPlan` (per period: forecast AQI over the period's hours = max, band, action, swap suggestion), `plan_week(...)`, `best_day(school, window_start, window_end, days=5)`. **Tests:** swap suggested when 2+ bands better; never into non-swappable slots; best-day ordering.

### Phase 2 — API + UI skeleton (Sat 08:00–14:00)
- **T10 app.py** — FastAPI endpoints per §6; CORS; `/api/health`; Mangum `handler`. Run locally with uvicorn. ✅ curl examples in README return sensible JSON.
- **T11 notices.py** — deterministic EN + HI templates built from DayPlan (works with zero LLM). Include a WhatsApp share URL builder.
- **T12 SAM walking skeleton → AWS (do NOT postpone).** `template.yaml`: HttpApi + FastAPI Lambda (python3.12, 30s timeout, 512 MB) + 2 DynamoDB tables (on-demand) + env vars. `sam build && sam deploy --guided`. ✅ when deployed `/api/health` and `/api/schools/{id}/today` work from the internet. Record URL in STATE.md.
- **T13 Frontend: Today view.** Header (school name, date, calibrated AQI pill + band colour), period cards (time, activity, AQI, band chip, action text, swap button), "data source + last updated" footer, Replay-mode badge when applicable. Mobile-first (test at 375 px).
- **T14 Frontend: onboarding.** Form: name, city preset or map pick (Leaflet + OSM tiles), timetable editor (add/remove rows: label, start, end, type, intensity, outdoor, swappable), asthma count. Saves via API.
- **T15 Frontend: Week + Best day.** 5-day strip (worst hour colour per day + hourly mini chart with raw vs calibrated lines — use Recharts), best-day picker form.

### Phase 3 — Agent + notices (Sat 14:00–20:00)
- **T16 Frontend: Notice + Language.** Notice panel with EN/HI tabs, Copy, "Share on WhatsApp". Global EN/हिंदी toggle for UI strings (simple dictionary; don't over-engineer i18n).
- **T17 agent.py (Strands).** Tools: `get_school(school_id)`, `get_day_plan(school_id, date)`, `get_hourly_forecast(school_id, date)`, `find_best_day(school_id, start, end)`, `draft_notice(school_id, date, lang)`. Model: `BedrockModel` with Amazon Nova Lite (us-east-1). System prompt: you are Saans, an assistant for school air-safety; **only state AQI numbers that a tool returned; cite the source and time; safety actions come from get_day_plan — never override them; if unsure say so; answer in the user's language.** Fallback: if Bedrock errors, return the deterministic notice / a "couldn't reach the model" message. **Tests:** tools return correct shapes (agent itself smoke-tested manually).
- **T18 /api/ask + /api/notice (LLM-polished).** `/notice?polish=true` asks the agent to make the template warmer and clearer *without changing any numbers or actions*; verify numbers in output match the plan (simple regex check) else fall back to template.
- **T19 Daily job.** `jobs/daily.py` + EventBridge Scheduler (cron `0 30 0 * * ?` UTC = 06:00 IST) in SAM; stores today's DayPlan per school in cache table. Today endpoint reads cached plan first.
- **T20 Frontend: Ask Saans chat.** Simple chat box with 3 suggested questions: "Is it safe for Class 7 PE at 8:40 today?", "Best day this week for Sports Day 9–12?", "Write today's notice for parents in Hindi."

### Phase 4 — Deploy + harden (Sat 20:00–Sun 02:00)
- **T21 Amplify Hosting.** Connect GitHub repo (monorepo `frontend/` app root) or manual zip deploy; set `VITE_API_URL`. ✅ public HTTPS URL works on phone.
- **T22 Replay mode.** `?replay=delhi-nov` loads a recorded severe-day dataset (pull real historical data from Open-Meteo for a known bad day in Nov 2025 if the API's date range allows — verify; otherwise a recorded fixture). Banner: "Replay: recorded data from <date>". Purpose: guaranteed dramatic demo even if today's air is clean. Never shown as live.
- **T23 Resilience pass.** Kill network to each source → UI still renders with clear "cached/fixture" labels. Loading + error states. No console errors. Lighthouse mobile ≥ 85.
- **T24 UI polish.** Consistent band colours (CPCB palette), clean typography, empty states, favicon, app title, 375 px check, Hindi strings reviewed by a human.

### Phase 5 — Ship (Sun 08:00–18:00) — FEATURE FREEZE 12:00
- **T25 README.** Problem (2–3 lines, with a cited stat you looked up), solution, screenshots/GIF, architecture diagram, **AWS services used and why**, science (§3), how to run locally, how to deploy, limitations (hourly indicator vs 24h NAQI; CAMS forecast uncertainty), team.
- **T26 Demo video (3:00)** — script in §8. Record Sun 12:00–15:00.
- **T27 Blog on AWS Builder Center** (top-5 blogs win AirPods): problem → design → stack → what fought back (e.g., calibration, Lambda packaging) → what's next. Link in submission.
- **T28 Final checks** — §9 checklist.
- **T29 Submit** by 18:00 (submissions open 08:00 Sun).
- **T30 Buffer.** Keep 2 hours free. Things break.

### Scope cuts if behind (cut in this order)
1. T20 chat UI (keep `/api/ask` and show it via the notice polish instead)
2. T15 hourly chart (keep best-day picker)
3. T14 map picker (use city presets)
4. T19 scheduler (compute on request with cache)
5. T21 Amplify (serve the built frontend from S3+CloudFront, or keep local + deployed API)
**Never cut:** T04–T09 tests, T12 deployed API, T13 Today view, T11 notices, T26 video.

---

## 6. Contracts (do not change without a Decision entry)

### Models (pydantic, JSON uses snake_case)
```text
Period:      id, label, start "HH:MM", end "HH:MM", type: assembly|pe|recess|sports|class,
             intensity: high|low, outdoor: bool, swappable: bool, grade?: str
School:      id, name, city, lat, lon, timetable: [Period], sensitive_count: int, languages: ["en","hi"]
HourPoint:   time ISO, pm25, pm10, pm25_cal, pm10_cal, aqi, band, calibrated: bool
Action:      level: go|caution|indoors, text_en, text_hi, rule_id
Swap:        to_start, to_end, to_aqi, to_band, gain_bands: int
PeriodPlan:  period: Period, aqi, band, action: Action, sensitive_action: Action, swap?: Swap
DayPlan:     school_id, date, now: HourPoint?, periods: [PeriodPlan], worst_hour, best_hour,
             sources: {forecast, observation, station?, distance_km?}, mode: live|cached|fixture|replay,
             generated_at
```

### Endpoints
| Method | Path | Returns |
|---|---|---|
| GET | `/api/health` | `{ok, version}` |
| GET | `/api/schools` | `[School]` |
| POST | `/api/schools` | `School` |
| GET | `/api/schools/{id}` | `School` |
| GET | `/api/schools/{id}/today?replay=` | `DayPlan` |
| GET | `/api/schools/{id}/week` | `{days: [{date, worst_aqi, worst_band, best_hour, worst_hour}], hourly: [HourPoint]}` |
| GET | `/api/schools/{id}/best-day?start=09:00&end=12:00` | `{ranking: [{date, max_aqi, mean_aqi, band}], reason}` |
| GET | `/api/schools/{id}/notice?lang=en|hi&polish=false` | `{text, whatsapp_url, mode}` |
| POST | `/api/ask` `{school_id, question, lang?}` | `{answer, tools_used: [str]}` |

---

## 7. Timeline at a glance (IST)

| When | Goal | Exit check |
|---|---|---|
| Fri 16–18 | Phase 0 | Keys work, repo scaffolded, both verified on Builder Center |
| Fri 18–01 | Phase 1 | `pytest` green on aqi/calibrate/rules/planner with real fixtures |
| Sat 08–14 | Phase 2 | Deployed API URL returns a DayPlan; Today view renders it |
| Sat 14–20 | Phase 3 | Hindi notice + agent answers best-day question |
| Sat 20–02 | Phase 4 | Public frontend URL works on a phone; replay mode works |
| Sun 08–12 | Polish + README | **Feature freeze 12:00** |
| Sun 12–15 | Video | 3:00 exactly, uploaded |
| Sun 15–17 | Blog + checklist | Blog published |
| Sun 17–18 | **Submit** | Confirmation received |

Sleep at least 5–6 hours Friday and Saturday night. A tired team at 4 AM writes the bugs that ruin the demo.

---

## 8. Demo video script (3:00, no live demo — this is what judges see)

| Time | On screen | Voice-over (short sentences) |
|---|---|---|
| 0:00–0:20 | Delhi haze footage/photo (own or free-licensed) → app logo | "Every winter morning, children in North India run laps when the air is at its worst. Schools have no tool that tells them what to do with *their* timetable." |
| 0:20–0:40 | Problem framing slide: AQI peaks at morning; one stat from a credible source | "Air quality changes hour by hour. A PE class at 8:40 and one at 1:30 can mean very different exposure." |
| 0:40–1:30 | **Today view** for the Delhi school. Point at PE card: AQI 312 Very Poor → "Swap to 13:30 (198)". Tap swap. Show asthma line. | "Saans reads the hourly forecast, calibrates it against the nearest government monitor, and turns it into decisions for each period." |
| 1:30–1:55 | Parent notice EN → toggle Hindi → Share on WhatsApp | "One tap sends parents a clear notice, in their language." |
| 1:55–2:25 | Ask Saans: "Best day this week for Sports Day, 9 to 12?" → answer with numbers + tools used | "An AI agent built with Strands Agents on Amazon Bedrock answers planning questions — using real numbers from tools, never made-up ones." |
| 2:25–2:50 | Architecture diagram | "Built on AWS: Lambda, API Gateway, DynamoDB, EventBridge for the 6 AM daily run, Amplify, Bedrock, and AWS SAM." |
| 2:50–3:00 | Live URL + team name | "Saans. Cleaner hours for every child. Team Chernobyl." |

Tips: record screen at 1080p, use a phone-sized browser window for the app, write the voice-over first and read it, add captions (many judges watch muted). If live air is clean on recording day, use **Replay mode** and say "recorded data from <date>" on screen.

---

## 9. Final submission checklist
- [ ] Both members verified as students on AWS Builder Center
- [ ] Avishi accepted the invite (team locks after submit)
- [ ] Repo public; README complete with architecture + AWS services + run instructions
- [ ] Deployed frontend URL + API URL work on mobile data (not just Wi-Fi)
- [ ] No secrets in git history (`git log -p | grep -i key` spot-check)
- [ ] Demo video ≤ 3:00, public/unlisted, link works in incognito
- [ ] Blog published on AWS Builder Center and linked
- [ ] Track selected: **Air**
- [ ] Submitted before deadline; screenshot of confirmation saved

---

## 10. Risks and fallbacks

| Risk | Fallback |
|---|---|
| Bedrock model access delayed | Strands with another provider via API key (still qualifies: Strands is AWS open source + rest is on AWS). Deterministic notices work with no LLM at all. |
| CPCB API down/slow | Uncalibrated forecast, labelled. Cache last good reading. |
| Open-Meteo down | Cached → fixture, labelled. |
| Lambda package too large / import errors | Use a Lambda layer for deps, or switch to container image via SAM; last resort App Runner. |
| Air is clean on demo day | Replay mode with labelled recorded data. |
| Tool usage limits hit mid-task | Handoff ritual (AGENTS.md §6); tasks are small; STATE.md has "Resume here". |
| Running late | Scope-cut list in §5. Feature freeze 12:00 Sunday is non-negotiable. |
