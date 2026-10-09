# PROMPTS.md — Copy-paste prompts for the humans

Use these exactly. They keep Cursor and Antigravity working off the same plan, and make switching between them painless.

---

## 0. One-time setup

1. Create a folder `saans/`, copy this kit into it (keep the paths: `AGENTS.md`, `docs/…`, `.cursor/rules/…`, `.agent/rules/…`, `GEMINI.md`).
2. `git init && git add -A && git commit -m "Kit: plan, rules, state"`. Create a GitHub repo and push. **Always push** — it is your backup if a laptop dies.
3. Open the same folder in Cursor *and* in Antigravity. Only **one tool edits at a time** (or each works on its own task in separate files, and you commit between switches).

Both tools should pick up the rules automatically (Cursor reads `AGENTS.md` and `.cursor/rules/`; Antigravity reads `.agent/rules/` / `GEMINI.md`). If a tool seems not to know the rules, paste **Prompt 1** — it works regardless.

**Model choice:** use the strongest model each tool offers for T04–T09 and T17 (the logic). Faster models are fine for UI polish and README.

---

## Prompt 1 — START a session (any tool, every time)

```
Read AGENTS.md and docs/STATE.md fully, then follow the Session START ritual in AGENTS.md §4.
Pick up the "Resume here" task (or the next TODO whose dependencies are DONE).
Read that task's definition in docs/PLAN.md §5 and the contracts in §6.
Before writing code, tell me in 3–5 lines: which task, which files you'll touch, and how you'll know it's done.
Then do it. Work in small steps, run tests, commit when the task is done, and update docs/STATE.md.
```

## Prompt 2 — Do a specific task

```
Follow AGENTS.md. Do task T__ from docs/PLAN.md §5 exactly as defined, respecting §6 contracts.
Set it IN PROGRESS in docs/STATE.md first. When the acceptance criteria are met and tests pass,
commit with "T__: <summary>" and update STATE.md (status DONE + one-line note + Resume here → next task).
```

## Prompt 3 — HANDOFF (say this when the usage meter is ~85–90%, not at 100%)

```
HANDOFF. Follow AGENTS.md §6 now. Stop starting new work. Make the code import/build,
run tests, commit (WIP if unfinished), and update docs/STATE.md "Resume here" with:
task ID, exact file + function, what's done, the very next concrete step, and any command to run.
Add a row to Handoff history. Then commit STATE.md and tell me it's safe to switch.
```

**If the tool died before you could hand off:** in the *next* tool, paste Prompt 4.

## Prompt 4 — RECOVER after a tool cut out mid-task

```
The previous agent ran out of usage mid-task and did NOT hand off cleanly.
Follow AGENTS.md §4. Run git status and git diff to see unfinished changes — do not delete them.
Work out which task they belong to (check STATE.md IN PROGRESS rows), finish that task,
run tests, commit, and update STATE.md including a note in Known issues about what you found.
```

## Prompt 5 — Review before moving on (use after T09, T12, T18, T24)

```
Act as a strict reviewer. Without changing code yet, check the work for task(s) T__ against
docs/PLAN.md §3 (science), §5 (acceptance criteria) and §6 (contracts), and AGENTS.md §7 (never do).
List concrete problems with file:line. Then fix only the real ones, run tests, commit, update STATE.md.
```

## Prompt 6 — Verify the UI in a browser (Antigravity is good at this)

```
Start the backend (cd backend && uvicorn app:app --reload) and frontend (cd frontend && npm run dev).
Open the app at 375px width. Walk through: onboarding → Today → swap suggestion → Week → Best day →
Notice (EN, then Hindi) → WhatsApp share link → Ask Saans. Screenshot each step.
Report anything broken, confusing, or unlabeled data. Fix the top issues, commit, update STATE.md.
```

## Prompt 7 — Draft the README / blog (Phase 5)

```
Using docs/PLAN.md and the actual code, write README.md for judges: problem (cite a real source —
leave a [CITE] placeholder if unsure, never invent statistics), what Saans does, screenshots placeholders,
architecture (mermaid), AWS services used and why, the science (NAQI, calibration, rules),
run locally, deploy, limitations, team. Keep it scannable. Then draft a blog post version
in docs/BLOG.md: problem → design → stack → what fought back → what's next.
```

---

## Switching tools — the 30-second routine
1. Old tool: **Prompt 3** (HANDOFF). Wait for "safe to switch".
2. `git log --oneline -3` — confirm the STATE commit is there. `git push`.
3. New tool: **Prompt 1**.

## Splitting work between Arnav and Avishi
- Two people, two tools, at the same time is fine **if** they work on different tasks in different folders (e.g. Cursor on `backend/`, Antigravity on `frontend/`). Each pulls before starting and pushes after each task. Only one person edits `docs/STATE.md` at a time — resolve conflicts by keeping both rows' updates.
- The frontend can start before the backend is done: build against the §6 contracts with a mock JSON file (`frontend/src/mock/dayplan.json`), then swap to the real API.
