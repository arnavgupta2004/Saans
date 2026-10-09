# STATE.md — Live handoff log

> Every agent: update this file at every commit and before your usage runs out (AGENTS.md §6).
> Statuses: `TODO` · `IN PROGRESS (<tool>, <time IST>)` · `DONE` · `BLOCKED (<why>)` · `CUT`

**Last updated:** Codex — Fri 9 Oct 2026, 16:42 IST (T03 complete; T04 next)
**Submission deadline (confirm on event page):** Sun 11 Oct, ____ IST  ·  **Feature freeze:** Sun 11 Oct, 12:00 IST
**Deployed API URL:** _(none yet)_
**Deployed frontend URL:** _(none yet)_
**Repo:** _(add GitHub URL)_

---

## ▶ Resume here
- **Task:** T04 — NAQI calculations
- **Where:** `backend/saans/aqi.py`
- **Done so far:** T03 scaffolded FastAPI/Mangum backend, a health endpoint test, Vite React TypeScript Tailwind frontend, and a local backend virtual environment.
- **Next concrete step:** implement CPCB PM2.5/PM10 breakpoint interpolation and its boundary tests.
- **Commands:** `cd backend && .venv/bin/python -m pytest -q`; `cd frontend && npm run build`

---

## Test status
| When | Tool | Backend `pytest -q` | Frontend `npm run build` |
|---|---|---|---|
| — | — | not run | not run |
| Fri 9 Oct 2026, 16:35 IST | Codex | unavailable — `backend/` absent | unavailable — `frontend/` absent |
| Fri 9 Oct 2026, 16:42 IST | Codex | 1 passed | passed |

---

## Task board
| ID | Task | Owner (default) | Depends on | Status | Notes |
|---|---|---|---|---|---|
| T01 | Builder Center verification, Avishi joins | Human | — | TODO | |
| T02 | Keys: data.gov.in, AWS CLI/SAM, Bedrock Nova Lite access, $5 budget | Human | — | TODO | |
| T03 | Scaffold repo | Any | — | DONE | FastAPI/Mangum health endpoint + test; Vite React TypeScript Tailwind placeholder; local `.venv` created. Tests: 1 passed; frontend build passed. |
| T04 | aqi.py + tests | Cursor | T03 | TODO | |
| T05 | sources.py + fixtures + tests | Cursor | T03 | TODO | needs data.gov.in key for live recording |
| T06 | calibrate.py + tests | Cursor | T04, T05 | TODO | |
| T07 | rules.py + tests | Cursor | T04 | TODO | |
| T08 | models.py + store.py + seed schools | Cursor | T03 | TODO | |
| T09 | planner.py + tests | Cursor | T06, T07, T08 | TODO | |
| T10 | app.py endpoints | Cursor | T09 | TODO | |
| T11 | notices.py EN/HI + WhatsApp URL | Cursor | T09 | TODO | |
| T12 | SAM deploy walking skeleton | Cursor + Human | T10, T02 | TODO | |
| T13 | Frontend Today view | Antigravity | T10 | TODO | |
| T14 | Frontend onboarding | Antigravity | T10 | TODO | |
| T15 | Frontend Week + Best day | Antigravity | T10 | TODO | |
| T16 | Frontend Notice + EN/HI toggle | Antigravity | T11 | TODO | |
| T17 | agent.py (Strands + Bedrock) | Cursor | T09, T02 | TODO | |
| T18 | /api/ask + polished notice | Cursor | T17 | TODO | |
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

## Known issues / surprises
- _(none yet)_

## Handoff history (append only)
| Time (IST) | From → To | Summary |
|---|---|---|
| Fri 16:00 | Claude → humans | Kit created. Start with T01–T03. |
| Fri 16:42 | Codex → Codex | T03 complete. Begin T04 in `backend/saans/aqi.py`. |
