# Test Strategy

Generic, reusable approach for testing the task management application (API + web UI). Defines *how*
we test, independent of the specific engagement schedule (see `docs/test-plan.md` for that).

## References

- Specification: [`specification/task-management-app.md`](../specification/task-management-app.md)
- Known defects and improvements: [`known-defects-and-improvements.md`](known-defects-and-improvements.md)

## Test levels

| Level | What it covers | Tooling |
|---|---|---|
| API / integration | Every documented REST endpoint, called directly (no UI in the loop) | `pytest` + `requests` |
| System (UI) | User-facing flows through the single-page web app (add/edit/mark done/delete) | `pytest` + `Selenium` |

No unit-level testing is in scope — the application is treated as a black box (the source is not
available to us), so verification happens at the API and UI boundaries only.

## Test types

| Type | Purpose | Example |
|---|---|---|
| Functional (positive) | Confirm documented behavior works | Create a task, retrieve it, see it in the list |
| Functional (negative) | Confirm invalid input / unauthorized calls are rejected sensibly | PATCH without auth, PUT with no title |
| Boundary | Exercise length/size limits | Title/tag name at 19/20/21 characters |
| State transition | Exercise a resource's valid state changes | Task `done` flag: create (false) → true → false |
| Idempotency | Repeating the same request leaves the resource in the same end state (or confirms/documents where it doesn't) | Two identical `PUT /` calls, two identical `PATCH` calls, two `DELETE` calls on the same id |
| Authentication & Authorization | Both auth schemes, token expiry, ownership rules | Basic auth, token-as-username, non-owner DELETE |
| Security (light, black-box) | OWASP-relevant checks reachable without source access | IDOR via sequential IDs, authentication-error parity (no username enumeration), TLS enforcement, injection in title/tag fields, password never echoed back |
| Compatibility | Cross-browser/resolution coverage of the web app | Chrome + Safari x Full HD + 4K matrix (see `src/config/browsers.py`); Safari auto-skips off macOS |
| Regression | Re-run of the full suite on every change | CI on every PR |
| Exploratory (manual, AI-assisted, time-boxed) | Cover gaps where the specification doesn't fully describe a flow/process; anything not economical to automate first | Web UI look-and-feel, unusual input combos, concurrent/collision scenarios |

### Exploratory testing approach (manual + AI-assisted)

The specification does not fully describe every flow/process in the application (tag lifecycle,
shared-vs-per-user ownership, error contract, DOM structure) — exploratory testing was used to close
those gaps before committing to a test design or automation strategy. It was run as a **context-given**
collaboration with an AI assistant rather than unstructured manual poking:

1. **Context** — gave the assistant the system under test, the test levels/types in scope (see tables
   above), and the specification itself.
2. **Collision/behavior analysis** — analyzed possible collision scenarios (duplicate titles/tags on
   the shared, never-reset instance; concurrent requests; repeated failed sign-ins) and observed the
   actual resulting behavior via live, read-only probes.
3. **DOM analysis** — inspected the rendered DOM/Knockout bindings of the web app to choose a resilient
   automation strategy (locator priority, duplicate-`id` workarounds — see "Web app DOM reference" in
   `.github/copilot-instructions.md`).
4. **Framework instructions** — turned the analysis into the project's core conventions
   (`.github/copilot-instructions.md`): API/UI layering, responsibility and ownership per layer, and
   docstring/comment conventions.
5. **Implementation order** — smoke tests first to validate the framework end-to-end, then full
   functional/boundary/negative/security coverage per the specification and `test-plan.md`.

Any behavior confirmed this way that the specification doesn't explicitly state is recorded as an
**assumption** in `known-defects-and-improvements.md` (Ambiguity/Gap categories), not asserted as
correct or incorrect — each needs confirmation from the business/stakeholders before it can be treated
as a Specification Clarification or a Bug Report.

### Test data lifecycle (no `/reset`, self-cleaning tests)

The instance is shared and persistent and `/reset` is never called from automated code (TM-11). Instead:

- Every test creates whatever data it needs via the `unique_name` fixture (collision-safe title/tag
  names) and the `create_task`/`make_user` fixtures — nothing relies on pre-seeded or leftover state.
- `create_task` tracks every task it successfully creates and deletes each one again during teardown,
  using the same auth it was created with, so tasks don't accumulate run over run. Cleanup is
  best-effort (it doesn't assert) since some tests delete the task themselves as part of the scenario
  (idempotency/ownership checks) and a redundant repeat `DELETE` is expected to no-op harmlessly.
  Tests that create tasks via a path other than this fixture are responsible for their own cleanup.
- Tags and users have no delete endpoint in the spec, so those are intentionally left behind — this is
  an accepted, documented limitation, not an oversight.

## Test design techniques

- **Equivalence Partitioning** — valid/invalid title length, valid/invalid auth, owner/non-owner.
- **Boundary Value Analysis** — the two documented 20-character limits (task title, tag name).
- **Decision Table** — authentication × ownership combinations for DELETE/PATCH
  (unauthenticated / authenticated-non-owner / authenticated-owner).
- **Error Guessing** — informed by `docs/known-defects-and-improvements.md` (e.g. empty-collection shape,
  tag dedup rules).
- **State transition** (light) — task `done` flag across create → update → delete.

## Tooling choices and rationale

| Tool | Why |
|---|---|
| `pytest` | De-facto standard Python test runner; fixtures, markers, and plugin ecosystem (Allure) cover this project's needs without extra infrastructure. |
| `requests` | Minimal, well-known synchronous HTTP client — sufficient for a REST API with no streaming/async requirements. |
| `Selenium` (4.x) | Industry-standard, free, cross-browser; Selenium Manager removes the need for manual driver management. |
| `allure-pytest` | Free, rich HTML reporting (steps, attachments, history trends) that scales as the suite grows — more informative than plain pytest/JUnit XML for showing *how* something failed. |
| `pytest-xdist` | Distributes tests across 4 worker processes by default (`-n 4`) for faster feedback; each worker is a separate process, so fixtures/sessions are never shared across tests running concurrently. |
| GitHub Actions | Free CI minutes for this scope, native to the hosting repo, no extra account/service needed. |
| `black` + `pylint` | Widely-adopted, free formatter/linter pair; enforced in CI on every PR. |

All tools are free/open-source and require no paid license, per the assignment constraint.

## Risk-based prioritization

Findings and test cases are prioritized by **Likelihood × Impact**:

| Impact →<br>Likelihood ↓ | Low | Medium | High |
|---|---|---|---|
| **High** | P2 | P1 | P0 |
| **Medium** | P3 | P2 | P1 |
| **Low** | P3 | P3 | P2 |

- **P0** — security/authorization gaps (e.g. IDOR, auth bypass), data corruption.
- **P1** — functional correctness of create/edit/delete, boundary violations silently accepted.
- **P2** — inconsistent error shapes/status codes, minor UI issues.
- **P3** — cosmetic issues, edge cases with no realistic user impact.

## Environments

- Single shared, persistent instance: https://luk-ole.rnd1.candidates.ondku.net/
- No isolated per-run environment is available; `/reset` is out of scope for automated use (see
  TM-11). Test data must be self-isolating (unique prefixes per run).

## Defect management

- GitHub Issues, using the **Bug Report** and **Specification Clarification** templates.
- Severity scale: Critical / Major / Minor / Cosmetic (matches the issue template dropdown).
- Every issue links back to the specification section and, where applicable, the failing test.

## Entry / exit criteria (generic)

**Entry** (per test level): endpoint/page implemented and reachable; base URL and credentials
resolvable from `.env`.

**Exit** (per test level): all planned P0/P1 cases automated and passing or linked to an open issue;
CI green on `main`; no known Critical severity defect without a filed issue.

## Roles

This is a solo technical exercise — one person performs test analysis, design, automation, and
execution. In a larger enterprise setting these responsibilities would typically be split across a
test lead, automation engineers, and manual/exploratory testers; that separation is noted here for
completeness but not applied in this repository.

## Metrics

- Pass/fail counts per marker (`api`, `ui`, `smoke`, `regression`) via Allure.
- Findings count by category and severity (`docs/known-defects-and-improvements.md`).
- Trend across CI runs (Allure history, when retained across builds).
