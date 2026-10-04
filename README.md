# Task Management — QA Automation

Test automation framework for the Dataiku QA take-home assignment: a task management REST API and its
companion single-page web application.

- **Instance under test**: https://luk-ole.rnd1.candidates.ondku.net/
- **Specification**: [specification/task-management-app.md](specification/task-management-app.md)

## Scope

This repository covers:
1. Automated **API tests** (`tests/api/`) — `pytest` + `requests`
2. Automated **UI tests** (`tests/ui/`) — `pytest` + `Selenium`
3. **Static testing** findings and confirmed defects raised as GitHub issues
4. SDLC documentation (`docs/`) — test strategy, test plan

See [docs/test-strategy.md](docs/test-strategy.md) / [docs/test-plan.md](docs/test-plan.md) for what
is tested, where, and how.

## Repository structure

```
specification/        assignment brief (requirements baseline)
docs/                  known defects/improvements, test strategy, test plan
config.ini             environments and test users (non-secret structural config)
src/
  config/              Settings dataclasses + config.ini/.env loader
  api/                 REST client + auth helpers
  ui/pages/            Page Object Model for the web app
tests/
  api/                 pytest API suite
  ui/                  pytest Selenium UI suite
reports/               gitignored Allure results/report output
```

## Prerequisites

- Python 3.11+
- Google Chrome (UI tests; the driver is managed automatically by Selenium Manager — no manual
  driver download needed)
- Safari (macOS only) — Safari's WebDriver support must be enabled once per machine:
  `safaridriver --enable` (requires admin rights). Safari automation only runs on macOS; it is
  auto-skipped on Windows/Linux (see "Browsers and resolutions" below).
- Allure commandline (to render HTML reports) — install one of:
  - `npm install -g allure-commandline`
  - `scoop install allure` (Windows)
  - `brew install allure` (macOS)
  - or download from https://github.com/allure-framework/allure2/releases

## Setup

```powershell
git clone <repository-url>
cd <repository-directory>
python -m venv .venv
```

Activate the environment and create the local settings file.

```powershell
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

On macOS/Linux:

```sh
source .venv/bin/activate
cp .env.example .env
```

Install Python dependencies:

```sh
python -m pip install -r requirements.txt
```

`.env` holds secrets (passwords) and machine-local run knobs (browser, headless, timeout); environments
and test users are structural config in [config.ini](config.ini) and are safe to commit. Set
`QA_PASSWORD` in `.env` to the credential provided for the selected environment. The default `test`
environment points at a shared, persistent candidate instance; coordinate access and never enable
`RESET_BEFORE_RUN` against it.

## Environments and users

`config.ini` defines one or more named **environments** (name → base URL), each with its own
pre-provisioned **test user(s)** declared under `[environment.<name>.user.<username>]` (the matching
password comes from `.env` as `<USERNAME_UPPER>_PASSWORD`). Today there's one environment
(`test`) with one declared user (`QA`). The active environment/user for a run resolve in this order:
CLI flag → env var → `config.ini [default]`.

```powershell
pytest                                  # uses config.ini [default]: test / QA
pytest --environment=test --user=QA     # explicit
```

Inside a test, request the `settings` fixture to reach the active environment/user. Identities needed
only *within* a scenario (e.g. a second or third user for cross-user/ownership checks) are **not**
declared in `config.ini` — create them on demand with the `make_user`/`make_user_auth` factory
fixtures, which register a fresh, randomly-named user via `POST /users` for that test:

```python
def test_non_owner_cannot_delete(api_client, qa_auth, make_user_auth):
    other_auth = make_user_auth()  # call again for a third identity if a scenario needs one
    ...
```

Adding a new environment or a new *pre-provisioned* user is a `config.ini` edit only — no code
changes required.

## Browsers and resolutions

UI tests run across a **browser x resolution matrix**, defined in
[`src/config/browsers.py`](src/config/browsers.py):

- Browsers: `chrome`, `safari` (the two most popular desktop browsers)
- Resolutions: `fullhd` (1920x1080), `4k` (3840x2160)

By default a plain `pytest` run only exercises `chrome`/`fullhd`; the rest of the matrix is opt-in via
`--browser`/`--resolution` (repeatable):

```powershell
pytest -m ui                                                  # chrome, fullhd only (default)
pytest -m ui --browser=chrome --browser=safari                # both browsers, fullhd
pytest -m ui --browser=chrome --resolution=fullhd --resolution=4k  # chrome, both resolutions
pytest -m ui --browser=chrome --browser=safari --resolution=fullhd --resolution=4k  # full matrix
```

Safari only runs on macOS (`safaridriver`) and has no headless mode; Safari combinations are
automatically skipped (not failed) when run on Windows/Linux. The scheduled regression pipeline
currently only exercises Chrome/Full HD (see [CI/CD](#cicd) below) — the rest of the matrix is for
local/manual runs.

## Running the tests

`pytest-xdist` is installed, but `pyproject.toml` does not set a worker count: plain `pytest` runs
serially. For the recommended full local run, use 2 workers with the default Chrome/Full HD UI
configuration. Each worker is a separate process — fixtures, sessions, and in-memory state are not
shared; Allure result writes are safe across workers (see `tests/conftest.py`).

The shared candidate instance is persistent. `RESET_BEFORE_RUN` is opt-in and calls `GET /reset`,
wiping instance data once before workers start. Keep it unset/false for the default shared environment;
only enable it for an isolated instance or with explicit authorization.

```powershell
pytest                                      # full suite, serial
pytest -n 2 --browser=chrome --resolution=fullhd  # recommended full local run
pytest -n 0                                 # force serial execution
pytest -n 4                                 # override worker count
pytest -n 2 -m api                          # API suite only
pytest -n 2 -m ui                           # UI suite only
pytest -n 2 -m smoke                        # fast sanity subset
pytest -n 2 -m "api and negative"            # combine markers
pytest -n 2 --allure-features="Tasks,Tags"  # select Allure features
```

## Reporting

For a clean report, remove the prior raw results before the test run. Do not delete `reports/`
wholesale; it also contains the tracked `.gitkeep`.

```powershell
Remove-Item reports\allure-results -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path reports\allure-results -Force | Out-Null
pytest -n 2 --browser=chrome --resolution=fullhd
```

After pytest exits, generate the static report in a separate command, even if some tests failed:

```powershell
allure generate reports/allure-results -o reports/allure-report --clean
```

Then serve the generated report over HTTP:

```powershell
allure open reports/allure-report
```

Use the `Server started at` URL printed by Allure and leave that terminal running while viewing the
report. Opening `reports/allure-report/index.html` directly with `file://` may fail because browsers
restrict local-file requests.

## CI/CD

[.github/workflows/](.github/workflows/):

- **`linter.yml`** — `black --check` + `pylint`, runs on every pull request to any branch.
- **`test-api.yml`** / **`test-ui.yml`** — reusable (`workflow_call`) suites, each also runnable
  standalone via `workflow_dispatch`. `test-api.yml` sets `RESET_BEFORE_RUN=true` to wipe the shared
  instance once before the run. Dispatch inputs support a pytest marker expression (intersected with
  `api` or `ui`) and comma-separated Allure feature names. UI runs remain fixed to Chrome/Full HD.
- **`publish-allure-report.yml`** — reusable; merges uploaded `allure-results-*` artifacts, regenerates
  the Allure report (preserving history for trend graphs), and publishes it to the `gh-pages` branch.
- **`regression.yml`** — orchestrator; runs nightly on a schedule and via manual `workflow_dispatch`,
  chaining `test-api` → `test-ui` → `publish-allure-report` into one combined report.

Published reports live on the `gh-pages` branch: the full regression run under `regression/`, and
standalone `test-api.yml`/`test-ui.yml` dispatches under their own `regression-api/`/`regression-ui/`
paths so they never overwrite the combined report's history.

Secrets required in the repo: `QA_PASSWORD` (the `QA` test user's password; see
[Environments and users](#environments-and-users)).

> **Reset safety:** `regression.yml` runs `test-api.yml` nightly, and that workflow currently resets
> its selected environment before tests. The default environment is documented as shared. Do not
> schedule or dispatch these workflows against the shared instance; point CI at an isolated
> environment or gate the reset before enabling automated runs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branching, commit, issue, and PR conventions.

## Known findings / open questions

Static review of the specification surfaced several ambiguities and candidate defects before any test
was implemented — tracked in [docs/known-defects-and-improvements.md](docs/known-defects-and-improvements.md) and
converted into issues, using the
[Bug Report](.github/ISSUE_TEMPLATE/bug_report.yml) /
[Specification Clarification](.github/ISSUE_TEMPLATE/spec_clarification.yml) templates, as they are
confirmed.