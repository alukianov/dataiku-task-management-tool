# Task Management QA Automation — Copilot Instructions

## What this repo does
Test automation framework (API + UI) for the Dataiku QA take-home task management application.
Instance under test: https://luk-ole.rnd1.candidates.ondku.net/
Specification (as given): `specification/task-management-app.md`

## Repository structure
- `specification/` — the assignment brief, treated as the requirements baseline
- `docs/` — SDLC artifacts:
  - `known-defects-and-improvements.md` — defects/improvements (TM-xx), pending conversion to GitHub issues
  - `test-strategy.md` — approach, levels, types, techniques, tooling, risk model
  - `test-plan.md` — scope, in/out of scope, schedule, entry/exit criteria for this engagement
  - `test-traceability.md` — requirement-to-test and testing-type coverage matrix
- `src/config/` — `Settings`/`EnvironmentConfig`/`UserConfig` dataclasses (`config.ini` + `.env`) and
  supported browsers/resolutions for the UI test matrix
- `src/api/` — REST client (`TaskManagementAPIClient`, one resource class per endpoint group). See
  `.github/instructions/api-layering.instructions.md` for the layering rules — it auto-applies
  whenever you're editing `src/api/**` or `tests/api/**`.
- `src/ui/` — Page Object Model for the web app (`src/ui/pages/`, `src/ui/components/`,
  `src/ui/locators/`). See `.github/instructions/ui-conventions.instructions.md` for the DOM
  reference, locator strategy, and Page/Component/test layering rules — it auto-applies whenever
  you're editing `src/ui/**` or `tests/ui/**`.
- Docstring conventions (module/function/test templates) live in
  `.github/instructions/docstrings.instructions.md` — auto-applies to any `.py` file.
- `tests/conftest.py` — cross-cutting fixtures shared by API and UI suites (`settings`, `api_client`,
  `make_user`/`make_user_auth`, CLI options)
- `tests/api/`, `tests/ui/` — pytest suites
- `reports/` — gitignored Allure results/report output (dir tracked via `.gitkeep`)

## Conventions
- Tests are pytest, tagged with one or more markers: `api`, `ui`, `smoke`, `regression`, `auth`, `negative`
  (defined in `pyproject.toml` `[tool.pytest.ini_options]`).
- Config/credentials are never hardcoded in tests — always via the `settings` fixture (environments/
  users in `config.ini`, passwords/browser/timeouts in `.env`).
- To test as a *different* user (e.g. ownership/authorization/cross-user checks), use the
  `make_user`/`make_user_auth` factory fixtures (`tests/conftest.py`) rather than hardcoding a second
  set of credentials or adding a new `config.ini` user — they register a fresh, randomly-named user
  via `POST /users` for that scenario only. Call them more than once if a scenario needs 2+ extra
  identities.
- Adding a new environment or a new *pre-provisioned* user is a `config.ini` edit only — never add new
  env vars for base URLs/usernames.
- The candidate instance is shared and persistent — test code must never call `/reset`; use the
  `unique_name` fixture for collision-safe titles/tags/usernames instead. Only the `reset` job in
  `regression.yml` (via `scripts/reset_instance.py`) wipes the instance, once before both suites.
- Allure annotations (`@allure.feature`, `@allure.story`, `@allure.step`) keep reports navigable as the
  suite grows.
- **Never disable a pylint rule** (inline `# pylint: disable=...` or via `pyproject.toml`) — fix the
  underlying issue instead (add the docstring, cut the argument count, drop the unused parameter,
  reorder the import). The suite must stay at a clean pylint run with zero suppressions.
- The pylint score must stay at or above **9/10** — `fail-under = 9` in `pyproject.toml`
  `[tool.pylint.main]` makes the `lint` CI job fail the PR if it drops below that.

## Running the suite
See `README.md` ("Running the tests", "Reporting") for setup, markers, and Allure report commands —
not duplicated here to avoid the two drifting apart.
For an end-to-end test run with a clean Allure report, use
`.copilot/skills/run-tests-with-allure/SKILL.md`.

## Process
Follow `docs/test-strategy.md` / `docs/test-plan.md` for scope and approach before adding new test
types or pages.
