---
name: create-ui-test
description: Scaffolds a new pytest Selenium UI test for this web app suite, following the project's Page Object / Component Object layering, Allure step conventions, and docstring template. Use when asked to "create a UI test", "add a Selenium test", "write a test for the Add Task modal", or "add UI coverage for sign-in/sign-out".
metadata:
  version: 1.0.0
  author: Oleksandr Lukianov
allowed-tools:
  - read_file
  - grep_search
  - list_dir
  - file_search
  - create_file
  - replace_string_in_file
  - multi_replace_string_in_file
  - run_in_terminal
  - get_errors
---

# Create UI Test

Scaffolds or extends a pytest Selenium test in `tests/ui/` for this web app, matching the project's
Page Object Model instead of free-form Selenium code.

## Prerequisites

- Chrome installed (driver auto-managed by Selenium Manager); Safari only relevant on macOS

---

## Step-by-step workflow

### 1. Confirm scope before writing anything

Read, in this order:

1. `.github/copilot-instructions.md` — the **"Web app DOM reference"** table (real `id`/`name` vs.
   `data-bind`/class-based locators, known duplicate-id defects TM-23/TM-29) and the full
   **"UI Page Object / Component conventions"** section — this governs where every line of new code
   goes.
2. `docs/test-strategy.md` — **Test types** table, plus the Compatibility row (Chrome/Safari × Full
   HD/4K matrix, `src/config/browsers.py`) to know when a test needs to care about the matrix at all
   (it usually doesn't — the matrix is opt-in via `--browser`/`--resolution`, not per-test).
3. `docs/test-plan.md` — **Features to be tested** and **Exploratory testing scope** tables.
4. `docs/test-traceability.md` — **Specification coverage** (REQ-xx) and **Testing type coverage**
   tables, to avoid duplicating existing UI coverage.
5. `docs/known-defects-and-improvements.md` — grep for the flow/element you're testing; if it's a
   known UI defect, you'll write an `xfail` (step 7).

### 2. Layering — the one rule that matters most

| Layer | Owns | Never does |
|---|---|---|
| **Test** (`tests/ui/*.py`) | Business-level steps + assertions via Page/Component methods | Import `selenium.webdriver.*` or `src.ui.locators.task_list_locators`; call `self.driver.find_element(...)` |
| **Page** (`src/ui/pages/task_list_page.py`) | `url`/`load()`, and orchestration *across* components | Own a raw locator or call `find_element` directly |
| **Component** (`src/ui/components/*.py`) | Every locator, every `find_element`/`find_elements`, every wait, every assertion for its one widget | Import raw Selenium types (`By`, `WebDriverWait`, `expected_conditions`) — build on `DriverBound` helpers in `src/ui/pages/base_page.py` instead |

If a test needs something a Component doesn't expose yet, **add a method to that Component** (or a
new named helper to `DriverBound` if no existing helper fits) — never reach around the layering from
the test.

### 3. Locators

- All locators live in `src/ui/locators/task_list_locators.py` only. Priority: `By.ID` > `By.NAME` >
  `By.XPATH` — never `By.CSS_SELECTOR`.
- Check the live rendered DOM before writing a new locator (Knockout renders things the static HTML
  doesn't show) — don't guess from memory.
- Watch for duplicate `id`s (`myModalLabel`, `inputTags` — TM-29): scope modal-internal locators off
  the modal container's own unique `id` (`add`/`edit`), not the duplicated inner ones.
- Row-scoped locators must start with `.` (`.//...`) when queried off a row `WebElement`, not the
  driver — a bare `//` is always document-absolute.

### 4. Use the existing fixtures

From `tests/ui/conftest.py` + `tests/conftest.py`:

| Fixture | Use for |
|---|---|
| `task_list_page` | `TaskListPage` bound to the active environment, not yet loaded |
| `signed_in_page` | Already `load()`ed and signed in as the default test user |
| `driver` | Raw WebDriver, parametrized across browser × resolution (rarely needed directly) |
| `unique_name`, `make_user_auth`, `create_task` | Same API-side factories as the API suite — use them for cross-user/ownership scenarios and to avoid fixed literal titles/tags |

### 5. Mark the test

```python
@allure.feature("Tasks")        # or Authentication / Authorization / Platform Health
@pytest.mark.ui
@pytest.mark.negative           # add auth / smoke as applicable
def test_<behavior>(task_list_page, settings, unique_name):
    """Verifies that <scenario/behavior under test>."""
    ...
```

### 6. Allure steps on Page/Component methods (not in the test)

- Every **action** method (click/type/submit — anything that changes app state) on a Page/Component
  gets `@allure.step("...")` with its arguments interpolated — this is the project's one form of
  input logging, don't add `print()`/`logging` calls in a test.
- Pure **query/getter** methods (`is_*`, `has_*`, returning bool/str/list) do **not** get
  `@allure.step`.
- **Grouped `verify_*` methods** (bundling several related assertions into one named check) *do* get
  `@allure.step` — prefer extending an existing `verify_*` over writing multiple raw `assert`s in the
  test when the same combination of checks would otherwise repeat across tests.
- If the flow you're testing needs a brand-new action/verification, add the method to the right
  Component (see step 2) with its own `@allure.step` — don't log inside the test itself.

### 7. If this test documents a known UI defect

```python
@pytest.mark.xfail(
    reason="TM-xx (docs/known-defects-and-improvements.md): <one-line summary>. "
    "Remove xfail once the defect is fixed.",
    strict=True,
)
def test_<ideal_behavior>(task_list_page, settings, unique_name):
    """Verifies that <ideal behavior>, not <observed broken behavior>."""
    ...
    # Ideal-behavior placeholder - the real behavior currently <does X> instead (TM-xx).
    ...
```

### 8. Docstring

One line only: `"""Verifies that <scenario/behavior under test>."""` — no `Args:`/`Returns:`.

### 9. Update traceability if coverage changed

Same as the API skill — add/confirm a `REQ-xx` row in `docs/test-traceability.md` →
**Specification coverage**, Web UI section.

### 10. Validate

Run with `-n 0` (no xdist) while developing a new UI test, so failures are easy to diagnose:

```powershell
.venv\Scripts\python.exe -m pytest tests/ui/<module>.py -n 0 -q --browser chrome --resolution fullhd
.venv\Scripts\python.exe -m black --check src tests scripts
.venv\Scripts\python.exe -m pylint src tests scripts   # must stay >= 9.0/10
```
