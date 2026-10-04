---
name: run-tests-with-allure
description: Run the task-management pytest suite or a filtered subset and generate a fresh Allure HTML report. Use when asked to run tests, run all tests, filter by pytest marker or Allure feature, change xdist workers, choose browsers/resolutions, or create/open an Allure report.
metadata:
  version: 1.0.0
  author: Oleksandr Lukianov
---

# Run Tests with Allure

Runs pytest from the repository root, starts each run with clean Allure results, generates a clean
static HTML report even when tests fail, and returns the report path and test/report exit status.

## Defaults

- Run the entire suite (`tests/`) in one pytest invocation.
- Use 2 pytest-xdist workers (`-n 2`).
- Use Chrome at Full HD (`--browser=chrome --resolution=fullhd`). These are the default UI matrix values.
- Set `RESET_BEFORE_RUN=true` for the run only when the target is a private or otherwise explicitly
  authorized instance. The configured `test` environment points to the shared persistent candidate
  instance; do not reset it without explicit authorization. If authorization is absent, use
  `RESET_BEFORE_RUN=false` and say why.
- Delete only `reports/allure-results/` before pytest. Generate into `reports/allure-report/` with
  Allure `--clean` so old test results or report pages cannot leak into the new report.

## Workflow

1. Read `.github/copilot-instructions.md` if the target or test configuration is unclear.
2. Resolve the target environment from `config.ini`, `ENVIRONMENT`, or an explicit
   `--environment` option. Before enabling reset, verify the target is private/single-user or that
   the user has explicitly authorized wiping it. The test hook calls `GET /reset` once in the
   pytest controller before xdist workers start; it is not a per-worker or per-test reset.
3. Check that the Python environment has the project dependencies and that the Allure CLI is
   installed. Do not install packages or change the environment unless requested; report a missing
   prerequisite and its documented install option.
4. Remove and recreate only the results directory. In PowerShell:

   ```powershell
   Remove-Item reports\allure-results -Recurse -Force -ErrorAction SilentlyContinue
   New-Item -ItemType Directory -Path reports\allure-results -Force | Out-Null
   ```

5. Set `RESET_BEFORE_RUN` for this process and run pytest once. Capture `$LASTEXITCODE` immediately
   after pytest, before running another native command. Use the command in **Default full run** or
   compose the requested filters as described below.
6. Regardless of pytest's exit code, run:

   ```powershell
   allure generate reports/allure-results -o reports/allure-report --clean
   ```

  Run this as a separate terminal command after pytest has exited. Confirm Allure prints
  `Report successfully generated`; do not rely on a multi-line command submission to continue from
  pytest to report generation. Do not use `allure serve` for generation; it creates a temporary
  report instead of the stable HTML output.
7. Start the generated report in a persistent/async terminal session:

  ```powershell
  allure open reports/allure-report
  ```

  Capture and return the exact `Server started at <http://...>` URL printed by Allure. Keep that
  terminal session running while the user views the report. Report pytest status accurately; if
  HTML generation succeeded despite failed tests, still open and link the report.

## Default Full Run

After the reset safety check, execute from the repository root in PowerShell:

Run the setup and pytest command in the active terminal. Capture the pytest exit code immediately:

```powershell
$env:RESET_BEFORE_RUN = "true"
Remove-Item reports\allure-results -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path reports\allure-results -Force | Out-Null
pytest -n 2 --browser=chrome --resolution=fullhd
$testExitCode = $LASTEXITCODE
Write-Output "pytest exit code: $testExitCode"
```

After that command exits, run report generation separately:

```powershell
allure generate reports/allure-results -o reports/allure-report --clean
$allureExitCode = $LASTEXITCODE
Write-Output "Allure exit code: $allureExitCode"
```

Then start `allure open reports/allure-report` in a persistent/async terminal session and return
the exact HTTP URL printed by Allure. Do not stop the server before returning the link.

If the target must not be reset, replace the first line with
`$env:RESET_BEFORE_RUN = "false"`. If pytest fails or is interrupted, still generate the report
from the results it produced and clearly label it as partial when appropriate.

## Filters and Run Options

Keep the default full-suite command unless the user asks for a subset or a different matrix. Omit
unneeded options from the command; the Allure clean/generate steps remain the same.

### Pytest markers

Available markers from `pyproject.toml`: `api`, `ui`, `smoke`, `regression`, `auth`, `negative`,
`boundary`, `idempotency`, and `security`. Use `-m` with a quoted pytest expression:

```powershell
pytest -n 2 -m "api and (auth or negative)"
pytest -n 2 -m "ui and smoke"
```

### Allure features

Use `--allure-features` to select by the `@allure.feature` labels, independently of pytest markers.
Known labels in this suite include `Tasks`, `Tags`, `Users`, `Authentication`, `Authorization`, and
`Platform Health`. For multiple feature labels, pass the comma-separated values as one option:

```powershell
pytest -n 2 --allure-features="Tasks,Tags"
```

Pytest markers and Allure feature filters can be combined; both filters apply:

```powershell
pytest -n 2 -m "api and negative" --allure-features="Tasks,Tags"
```

### Workers

- `-n 2` is the default. Change the count with `-n 4`, for example.
- `-n 0` disables xdist and runs serially, useful for isolating state or debugging.
- Keep UI concurrency conservative if the machine or shared target is under load.

### Browsers and resolutions

The pytest flags are repeatable. Supported browsers are `chrome` and `safari`; supported
resolutions are `fullhd` (1920x1080) and `4k` (3840x2160). The UI suite forms the browser x
resolution matrix for tests that use the `driver` fixture.

```powershell
pytest -n 2 --browser=chrome --browser=safari --resolution=fullhd
pytest -n 2 --browser=chrome --resolution=fullhd --resolution=4k
pytest -n 2 --browser=chrome --browser=safari --resolution=fullhd --resolution=4k
```

Safari requires macOS and `safaridriver`; combinations unsupported on the current OS are skipped.
Chrome is the default and is managed by Selenium Manager. The default full-suite run uses Chrome
Full HD only.

## Failure and Report Handling

- Do not delete `reports/` wholesale; it also contains the tracked `.gitkeep` and may contain other
  local artifacts. Remove only `reports/allure-results/` before the run.
- Allure test results are generated through `pyproject.toml`'s `--alluredir` setting. Do not add a
  second results directory to the pytest command.
- Generate the static report even if some tests fail, so failures and attachments remain inspectable.
- If `allure generate` fails, preserve the raw `reports/allure-results/` directory and report the
  CLI error. Do not claim the HTML report exists.
- Start `allure open reports/allure-report` after generation in a persistent/async terminal session
  and keep it running. Return its printed URL as a clickable Markdown link. If the server cannot be
  started, use `[Allure report](reports/allure-report/index.html)` as a fallback and explain that
  opening the file directly may be blocked by browser `file://` restrictions.