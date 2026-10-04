---
name: allure-report-analyst
description: Reviews an Allure run (reports/allure-results) after test execution, distinguishes known xfail defects from genuinely new failures, and documents new findings into docs/known-defects-and-improvements.md and docs/test-traceability.md following the project's established format. Use when asked to "analyze the allure report", "check why tests failed", "review the latest test run", or "document this defect from the test run".
metadata:
  version: 1.0.0
  author: Oleksandr Lukianov
allowed-tools:
  - read_file
  - grep_search
  - list_dir
  - file_search
  - run_in_terminal
  - replace_string_in_file
  - multi_replace_string_in_file
---

# Allure Report Analyst

Turns a raw Allure results directory into a triaged list of pass/known-xfail/new-failure, and writes up
any genuinely new finding using the project's finding format — without re-stating what's already
tracked.

## Prerequisites

- A completed test run with results in `reports/allure-results/` (gitignored; generated on demand)
- Optional: `allure` commandline installed, to render the HTML report for visual review
  (`allure serve reports/allure-results`)

---

## Step-by-step workflow

### 1. Get the shape of the run first

`reports/allure-results/` holds one `*-result.json` per test, plus `*-container.json` (setup/teardown)
and `*-attachment.json`/`*-attachment.txt`/`*-attachment.png` files referenced from each result.

```powershell
Get-ChildItem reports\allure-results\*-result.json | Measure-Object
```

For each `*-result.json`, the fields that matter: `name`, `fullName`, `status`
(`passed`/`failed`/`broken`/`skipped`), `statusDetails.message`/`trace`, and `attachments` (each with a
`source` filename pointing at the matching attachment file).

### 2. Separate expected `xfail` results from real failures

- A test marked `@pytest.mark.xfail(strict=True)` that is still broken reports as `skipped` with an
  `xfail` status detail in Allure/pytest — **this is expected, not a new finding**. Don't re-document
  it; it's already tracked under its `TM-xx` in `docs/known-defects-and-improvements.md`.
- A test marked `xfail(strict=True)` that now reports as `failed`/`broken` with an `XPASS` reason is
  the signal a tracked defect was **fixed** — see step 6.
- Any other `failed`/`broken` result is either a genuinely new defect or environment/flakiness noise
  (see step 3 before writing anything up).

### 3. Pull the evidence for each real failure

- **API tests**: read the `Request headers`/`Request body`/`Response headers`/`Response body`
  attachments (`src/api/base_client.py` → `log_http_call` attaches these automatically to every HTTP
  call) plus the `Failure reason` attachment.
- **UI tests**: read `Failure reason`, `Screenshot on failure`, `Page source on failure`, and `Browser
  console log` (when Chrome) — all wired in automatically via `src/reporting/allure_logging.py` →
  `log_failure`.
- Compare against the **observed** behavior described in `docs/known-defects-and-improvements.md` for
  reliability-only findings (**TM-13**: intermittent `500`s on this shared dev-server instance) before
  concluding it's a new defect — a single flaky `500` with no deterministic trigger is noise, not a new
  finding, unless it reproduces consistently.

### 4. Classify before writing anything

For each genuinely new, reproducible finding, decide (same taxonomy as the doc):

| Dimension | Values |
|---|---|
| **Area** | API / UI / Design / Process |
| **Category** | Bug / Gap / Ambiguity / Security / Reliability / Design Issue / Improvement / Process risk |
| **Priority** | P0 (security/data-corruption) / P1 (functional correctness) / P2 (inconsistent contract/minor UI) / P3 (cosmetic/no real impact) — per the Likelihood × Impact model in `docs/test-strategy.md` |
| **Testing type** | Static review / Exploratory / API testing / UI testing / Process |

### 5. Check it isn't already tracked

```powershell
Select-String -Path docs\known-defects-and-improvements.md -Pattern "<symptom keyword>"
Select-String -Path docs\test-traceability.md -Pattern "<test name or endpoint>"
```

If a matching `TM-xx` already exists, update its **Evidence** with the new reproduction (date +
pytest/Allure reference) instead of creating a duplicate entry.

### 6. Write up a genuinely new finding

Find the next free `TM-xx` id (check both the master table **and** any `TM-xx` already referenced in
`tests/**` `xfail` reasons that might not have a doc entry yet — that mismatch is itself worth flagging
to the user rather than silently inventing an id that collides).

- Add one row to the **Summary** table in `docs/known-defects-and-improvements.md`, in priority order
  (see the existing P0→P1→P2→P3→Resolved grouping), with a `Test(s)` entry naming the failing test.
- Add a matching `## TM-xx — <title>` section, in the same order as the table, with:
  - `**Category**:` (not "Confirmed bug:" — findings are raised from the QA point of view, not
    officially confirmed; see the doc's intro paragraph)
  - `**Spec location**:` (or `N/A` for frontend-only/process findings)
  - `**Description**:` what was observed
  - `**Evidence**:` cite the Allure run date and attachment type (e.g. "Reproduced via Allure run on
    <date>, see `Response body` attachment on `test_x`")
  - `**Suggested action**:` Bug Report / Specification Clarification / Design Improvement, matching
    the Category

### 7. If it's fixable-and-testable now, wire it into the suite

If the finding is a confirmed app Bug (not an Ambiguity/Gap/Design Issue/Improvement), hand off to the
`create-api-test` or `create-ui-test` skill to add the `xfail(strict=True)` regression test, rather than
leaving it as prose-only.

### 8. If a tracked `xfail` started `XPASS`ing

That means the underlying bug was fixed:
- Remove the `xfail` marker from the test (and tidy the "Ideal-behavior placeholder" comment).
- Update the finding's **Status** in `docs/known-defects-and-improvements.md` to `Resolved`.
- Update `docs/test-traceability.md` if the row's wording referenced the defect as still-open.

### 9. Never fabricate a finding

If a failure is inconclusive (couldn't reproduce on a second run, looks like shared-instance noise),
don't invent an `TM-xx` for it — note it under **"Manual testing items investigated and not
reproduced"** in `docs/known-defects-and-improvements.md` instead, same as existing entries there.
