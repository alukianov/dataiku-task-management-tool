# Test Plan

Concrete scope, schedule, and deliverables for testing the Dataiku QA take-home task management
application, applying the approach defined in [`test-strategy.md`](test-strategy.md).

## Test items

- REST API at `https://luk-ole.rnd1.candidates.ondku.net/` — all endpoints in
  [`specification/task-management-app.md`](../specification/task-management-app.md) except `/reset`.
- Single-page web application at `.../web/index.html` — add, edit, mark as done, delete flows.

## Features to be tested

| Feature | API tests | UI tests | Priority |
|---|---|---|---|
| List tasks (`GET /`) | Yes | Yes (task list rendering) | P1 |
| Create task (`PUT /`) incl. auto tag creation | Yes | Yes (add form) | P0/P1 |
| Get single task (`GET /<id>`) | Yes | — | P1 |
| Delete task (`DELETE /<id>`) — auth + ownership | Yes (confirmed broken, TM-12) | Yes (delete action) | P0 |
| Update task (`PATCH /<id>`) — auth + ownership, `done` toggle | Yes (confirmed correct) | Yes (edit form, mark done) | P0 |
| Cross-user task visibility (shared list, not isolated) | — | Yes (confirmed correct) | P1 |
| List tags (`GET /tags`) | Yes | Yes (tags list column) | P1/P2 |
| Get single tag (`GET /tags/<id>`) | Yes | — | P2 |
| Create user (`POST /users`) | Yes | — | P1 |
| Authenticate — Basic and token (`POST /authenticate`) | Yes | — | P0 |
| Boundary: title/tag length (19/20/21 chars) | Yes | Yes (form validation, if any) | P1 |
| Idempotency: repeated `PUT /` with identical body (TM-14), repeated `PATCH`, repeated `DELETE` | Yes (`tests/api/test_tasks.py`) | — | P1 |
| Negative: missing required fields (`PUT /` no title — confirmed `500`, TM-14; `POST /users` no username/password — confirmed clean `400`) | Yes | — | P1 |
| Security: auth-error parity (no username enumeration on `/authenticate`), password never echoed by `POST /users` | Yes (`tests/api/test_authentication.py`, `tests/api/test_users.py`) | — | P1 |
| Authorization matrix: unauth / non-owner / owner on DELETE & PATCH | Yes (see `tests/api/test_authorization.py`; DELETE confirmed broken - TM-12) | — | P0 |
| IDOR probe on sequential IDs (if applicable) | Yes | — | P0 |

## Exploratory testing scope (manual, AI-assisted)

Scenarios the specification doesn't fully describe, time-boxed and covered via the exploratory
approach in `test-strategy.md` before deciding whether each belongs in the automated suite:

| Scenario | Outcome |
|---|---|
| Web UI look-and-feel across the task table and both modals (labels, title reset, date formatting) | TM-23, TM-24, TM-26 — tracked, some now automated (`xfail`) |
| Unusual input combinations (untouched Tags field, boundary-length titles/tags, empty title) | TM-07, TM-18 — automated (`xfail`) |
| Collision scenarios on the shared, never-reset instance (duplicate title/tag, repeated failed sign-in) | TM-13, TM-14, TM-17 — automated (`xfail` where still broken) |
| Rendered DOM structure, driving the Selenium locator strategy | TM-29, TM-30 — documented, informs `src/ui/locators/` |
| Authorization edge cases beyond the documented contract (non-owner DELETE) | TM-12 — automated (`xfail`) |
| Application purpose/ownership model (shared vs. per-user task list) | TM-19 — ambiguity, raised as a Specification Clarification, no automated test |

Every outcome above that isn't an explicit spec statement is an **assumption** pending
business/stakeholder confirmation — see `known-defects-and-improvements.md` for the full write-up per
finding.

## Features not to be tested (and why)

| Feature | Reason |
|---|---|
| `/reset` | Explicitly out of scope per the assignment. |
| Load / performance testing | Not requested; shared single instance makes it unsafe to stress-test without risking other users' sessions. |
| Full cross-browser / cross-resolution matrix in CI (Safari, 4K) | A basic implementation exists (`src/config/browsers.py`, Chrome+Safari × Full HD+4K) and can be run on demand via `--browser`/`--resolution`; the decision was to keep CI on the Chrome+Full HD default rather than run the full matrix every time, given the size/risk of this single-page application. |
| Mobile/tablet viewport testing | Not mentioned in the assignment; only desktop resolutions (Full HD, 4K) are covered. Noted as a possible future improvement. |
| Penetration testing beyond black-box OWASP-style probes | Requires authorization beyond this assignment's scope; only non-intrusive checks (IDOR read probes, TLS check, input handling) are included. |

## Approach

1. **Static + exploratory testing** (done first, before any automation) — spec review plus AI-assisted
   exploratory probing of flows the spec doesn't fully describe (see `test-strategy.md`); findings and
   assumptions recorded in `known-defects-and-improvements.md`.
2. **API test implementation** — functional, negative, boundary, auth/authorization; each test uses a
   uniquely-prefixed title/tag to avoid collisions on the shared instance.
3. **UI test implementation** — Page Object Model, smoke test first to validate framework wiring, then
   the four exposed flows (add/edit/mark done/delete).
4. **Execution & triage** — run locally and in CI, capture Allure evidence, convert confirmed findings
   into GitHub issues.
5. **Reporting** — summarize results, residual risk, and suggested improvements not implemented.

## Deliverables

- Test automation code: `tests/api/`, `tests/ui/`, supporting `src/`.
- Allure HTML report (generated on demand, uploaded as a CI artifact).
- This document set (`docs/`).
- GitHub issues for confirmed bugs and open specification clarifications.

## Schedule

Infra & static testing → strategy/plan → API test implementation → UI test implementation →
execution & triage → issue filing → summary. No fixed calendar dates are set beyond the assignment's
one-week guideline.

## Entry criteria

- Repository infrastructure merged (tooling, CI, docs skeleton).
- Instance reachable (`GET /` returns 200) and default `QA` credentials valid.

## Exit criteria

- All P0 and P1 cases from the table above automated and either passing or linked to an open issue.
- CI green on `main`.
- No Critical-severity defect left undocumented.
- Known defects/improvements each have a `Status` other than `Open` in `known-defects-and-improvements.md`.

## Suspension / resumption criteria

- **Suspend** if the shared instance becomes unreachable, or if `/reset` is triggered by someone else
  and invalidates in-flight test data — re-run the smoke tests before resuming.
- **Resume** once smoke tests (`pytest -m smoke`) pass again.

## Risks and mitigations

| Risk | Related finding | Mitigation |
|---|---|---|
| Shared instance data collisions between test runs / other testers | TM-11 | Unique title/tag prefixes per run; never call `/reset` from automated code |
| No documented error contract — assertions may encode incidental behavior as "expected" | TM-06 | Document observed contract explicitly in test docstrings/Allure steps; flag surprising codes as bugs, not silently assert them |
| Sequential/guessable IDs enabling IDOR | TM-10 | Dedicated authorization test suite (`auth` marker) run as P0 |
| Token expiry (10 min) causing flaky long-running suites | Authentication section | Re-authenticate per test via fixture scoped to `function`, not `session` |
| 4x parallel workers increasing load on an already-flaky dev server | TM-13 | `create_task` arrange-fixture retries once on `5xx`; each worker is a separate process (no shared session/state) |
| Duplicate title/tag name against the never-reset shared instance deterministically `500`s | TM-14 | All new tests use the `unique_name` fixture (`tests/conftest.py`) instead of fixed literal titles/tags |

## Suggested improvements (not implemented in this exercise)

_Populated progressively during execution._
