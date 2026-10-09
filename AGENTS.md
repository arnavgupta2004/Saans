# AGENTS.md — Rules for every AI coding agent on this repo

> Cursor, Antigravity, Claude, or anyone else: **read this file, then `docs/STATE.md`, before you touch any code.**
> More than one tool works on this repo in turns. When one tool runs out of usage, the next one carries on. The repo itself is the only memory you have, so keep it accurate.

## 1. What we are building (30-second version)

**Saans** ("breath") — *AQI-smart timetables for schools.*
Environmental Hacks (WeMakeDevs × AWS, Bharat Builds Tour event 02), **Track 01: Air → "School safety on bad days"**. Team: **Chernobyl**.

Every morning Saans looks at the **hour-by-hour** PM2.5/PM10 forecast for a school's location, calibrates it against the nearest live CPCB station, converts it to India's **NAQI**, and turns it into **decisions for that school's actual timetable**:

- "Move Class 7B PE from 08:40 to 13:30 — forecast AQI drops from 312 (Very Poor) to 198 (Moderate)."
- "Hold morning assembly indoors."
- "38 students with asthma: keep them indoors during recess."
- "Best day this week for Sports Day: Thursday."

It then drafts a **parent notice in English + Hindi** that the principal sends with one tap (WhatsApp share link). A **Strands agent** answers questions like "Can we do the field trip on Wednesday?" by calling the same tools.

**Golden rule of the product:** safety decisions come from deterministic, tested code (`rules.py`). The LLM only explains, translates, and answers questions using tool outputs. **The LLM must never invent an AQI number.**

Full plan, task board, and timeline: `docs/PLAN.md`.

## 2. Stack (do not change without logging a decision in STATE.md)

| Layer | Choice |
|---|---|
| Backend | Python 3.12, FastAPI, Mangum (FastAPI → AWS Lambda), httpx, pydantic v2, pytest |
| Agent | **Strands Agents SDK** (`strands-agents`, AWS open source) with **Amazon Bedrock** model (Amazon Nova Lite, region `us-east-1`). Fallback model provider allowed if Bedrock access is blocked — Strands stays. |
| Data | Open-Meteo Air Quality API (hourly PM2.5/PM10 forecast, no key) + data.gov.in CPCB real-time AQI (free API key) for calibration |
| Storage | DynamoDB (`saans-schools`, `saans-cache`) — local dev uses a JSON file store behind the same interface |
| Frontend | React + Vite + TypeScript + Tailwind, mobile-first |
| Infra | **AWS SAM** (open source) → Lambda + API Gateway (HTTP API) + DynamoDB + EventBridge Scheduler (daily 06:00 IST run). Frontend on **Amplify Hosting**. |

## 3. Repo layout

```
saans/
  AGENTS.md                 ← you are here
  README.md                 ← judges read this; keep it current
  docs/
    PLAN.md                 ← the plan + task board definitions (read-only unless a decision changes it)
    STATE.md                ← LIVE handoff log. Update it constantly.
    PROMPTS.md              ← copy-paste prompts for the human
  backend/
    saans/
      aqi.py                ← NAQI sub-index math (CPCB breakpoints)
      sources.py            ← Open-Meteo + CPCB clients (with caching + fixture fallback)
      calibrate.py          ← forecast bias correction using live station reading
      rules.py              ← school protocol: AQI band × activity → action
      planner.py            ← per-period plan, slot swaps, best-day finder
      notices.py            ← deterministic EN/HI notice templates (fallback for the agent)
      agent.py              ← Strands agent + tools
      store.py              ← SchoolStore interface: JsonStore (local) / DynamoStore (AWS)
      models.py             ← pydantic models (School, Period, PeriodPlan, DayPlan...)
    app.py                  ← FastAPI app (+ Mangum handler)
    jobs/daily.py           ← EventBridge daily job
    fixtures/               ← recorded API responses for tests + "Replay mode"
    tests/
    template.yaml           ← SAM template
    requirements.txt
  frontend/
    src/...
```

## 4. Session START ritual (every time, every tool)

1. Read `AGENTS.md` (this file) and `docs/STATE.md` fully.
2. Run `git status` and `git log --oneline -15`.
3. If `git status` shows uncommitted changes you did not make: **do not delete them.** Inspect them, then either finish the task they belong to (see "Resume here" in STATE.md) or commit them as `WIP <task-id>: recovered changes`.
4. Run the tests: `cd backend && pytest -q` (and `cd frontend && npm run build` if frontend exists). Note failures in STATE.md before changing anything.
5. Pick up the **"Resume here"** item in STATE.md. If it is empty, take the lowest-numbered `TODO` task whose dependencies are `DONE`.
6. Set that task to `IN PROGRESS` in STATE.md with your tool name and the time.

## 5. While working

- **Small steps.** Work in chunks of ≤ 30–45 minutes. A tool can run out of usage at any moment; small steps mean little is lost.
- **Commit after every finished task** and at every meaningful checkpoint: `git commit -m "T07: rules engine + tests"`. Push if a remote exists.
- **Update STATE.md every time you commit.** Mark the task `DONE`, write one line of notes.
- **Tests are mandatory** for `aqi.py`, `calibrate.py`, `rules.py`, `planner.py`. These are the safety logic.
- **Respect contracts.** API shapes and models are defined in `docs/PLAN.md §6`. Do not rename endpoints, fields, or files. If you must change one, log it under *Decisions* in STATE.md and update PLAN.md §6 in the same commit.
- **No new dependencies** without adding them to `requirements.txt` / `package.json` and noting them in STATE.md.
- **Do not refactor or "clean up" another tool's working code.** Only change what your task needs.
- **Secrets:** never commit keys. Use `.env` (git-ignored) and `.env.example` with placeholder names.
- **Every external call has a fallback.** If Open-Meteo/CPCB/Bedrock fails, the app falls back to cached data or fixtures and *says so in the UI* — it never crashes on demo day.
- **Honesty in UI:** every recommendation shows *why* (AQI value, band, source, forecast time). Replay/fixture data is always labelled as such.

## 6. Session END / HANDOFF ritual

Do this when (a) a task is done and the session is ending, (b) the human says **"HANDOFF"**, or (c) you sense you are near your usage limit. **Do it before you run out, not after.**

1. Stop starting new work. Get the code into a state that at least imports/builds.
2. Run tests. Record pass/fail counts.
3. `git add -A && git commit -m "WIP T0X: <what state it is in>"` (or a normal commit if finished).
4. Update `docs/STATE.md`:
   - Task board statuses.
   - **"Resume here"** block: task ID, the exact file + function you were in, what is done, the very next concrete step, and any command to run.
   - Known issues / anything surprising.
   - Last updated: tool name + time (IST).
5. Commit STATE.md: `git commit -m "STATE: handoff from <tool>"`.

## 7. Never do

- Never let the LLM decide whether an activity is safe. `rules.py` decides; the agent explains.
- Never fake data in the live view. Fixtures appear only in tests and in clearly labelled "Replay mode".
- Never `git reset --hard`, `git push --force`, or delete branches.
- Never rewrite STATE.md history — append and update; keep the Decisions log.
- Never expand scope past the current phase in PLAN.md. **Feature freeze: Sunday 11 Oct, 12:00 IST.**
