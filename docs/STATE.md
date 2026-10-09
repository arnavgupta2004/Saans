# STATE.md — Live handoff log

> Every agent: update this file at every commit and before your usage runs out (AGENTS.md §6).
> Statuses: `TODO` · `IN PROGRESS (<tool>, <time IST>)` · `DONE` · `BLOCKED (<why>)` · `CUT`

**Last updated:** Claude — Fri 9 Oct 2026, 19:20 IST (T17 done)
**Submission deadline (confirm on event page):** Sun 11 Oct, ____ IST  ·  **Feature freeze:** Sun 11 Oct, 12:00 IST
**Deployed API URL:** _(none yet)_
**Deployed frontend URL:** _(none yet)_
**Repo:** _(add GitHub URL)_

---

## ▶ Resume here
- **Task:** T18 — `/notice?polish=true`
- **Where:** `backend/app.py` `notice()` + `saans/agent.py`
- **Done so far:** T09–T11, T17; /api/ask calls agent, falls back on error. 58 tests pass.
- **Next concrete step:** polish=true: ask agent to rewrite template without changing numbers; regex-verify all numbers present, else return template. Then T12 SAM template (needs human AWS keys, T02).
- **Commands:** `cd backend && .venv/bin/python -m pytest -q`

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
| T12 | SAM deploy walking skeleton | Cursor + Human | T10, T02 | TODO | |
| T13 | Frontend Today view | Antigravity | T10 | DONE | Built with mock data flag. Mobile-first, CPCB colors, action reasons included. |
| T14 | Frontend onboarding | Antigravity | T10 | IN PROGRESS (Cursor, 18:05 IST) | Reduced scope: city presets + geolocation, no map. |
| T15 | Frontend Week + Best day | Antigravity | T10 | DONE | Ranking comes from `getBestDay` (planner.best_day); frontend only displays. Mock until T10. |
| T16 | Frontend Notice + EN/HI toggle | Antigravity | T11 | DONE | Notice view with WhatsApp share and EN/HI tabs. Global language context added. |
| T17 | agent.py (Strands + Bedrock) | Cursor | T09, T02 | DONE (Bedrock call untested) | 5 tool fns + tests (58 pass); `ask()` uses BedrockModel Nova Lite; needs T02 Bedrock access for a manual smoke test. |
| T18 | /api/ask + polished notice | Cursor | T17 | CUT | /api/ask wired to agent with deterministic fallback; `polish=true` cut (stays 501). |
| T19 | Daily EventBridge job | Cursor | T12 | TODO | |
| T20 | Frontend Ask Saans chat | Antigravity | T18 | TODO | cut #1 if late |
| T21 | Amplify Hosting | Human + Any | T13 | TODO | |
| T22 | Replay mode | Any | T09, T13 | TODO | |
| T23 | Resilience pass | Antigravity | T21 | TODO | |
| T24 | UI polish | Antigravity | T13–T16 | TODO | |
| T25 | README | Any | T21 | TODO | |
| T26 | Demo video | Human | T24 | TODO | |
| T27 | AWS Builder Center blog | Human (+agent draft) | T25 | TODO | |
| T28 | Final checklist | Human | all | TODO | |
| T29 | Submit | Human | T28 | TODO | |

---

## Decisions log (append only)
- 2026-10-09 — Track 01 Air, sub-problem "School safety on bad days". Product: Saans. Stack per AGENTS.md §2. (Claude)
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
