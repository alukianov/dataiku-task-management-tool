---
applyTo: "src/ui/**,tests/ui/**"
---

# UI Page Object / Component conventions

## Web app DOM reference (`web/index.html`)
Knockout.js SPA; interactive elements mostly bind via `data-bind` (no `id`/`name`) - see
`src/ui/locators/task_list_locators.py` for the exact `By.ID`/`By.NAME`/`By.XPATH` per element (never
`By.CSS_SELECTOR` - prefer a real `id`/`name` first, else `By.XPATH`). Captured live on 2026-10-02:

| Area | Container | Real `id`/`name` | No id - located via |
|---|---|---|---|
| Navbar auth | `<nav>` | `name="username"`, `name="password"` | sign-in: `data-bind='click: authenticate'`; sign-out: `data-bind='click: logout'` |
| Add button | — | `id="btn-add"` | — |
| Add modal | `id="add"` | (container only) | title `data-bind='value: title'`, tags `data-bind='value: tags'`, submit `data-bind='click:addTask'` |
| Edit modal | `id="edit"` | (container only) | title/done/submit via `data-bind`; one `<input id="inputTags">` **per tag** (see TM-29) |
| Task table | `<table>` (only one) | — | no id/class needed, `//table` is unique |
| Task row | `<tr>` | — | `row_by_title(title)`: XPath matching the `<b>` title cell text |
| Row buttons | within a row | — | class only: `glyphicon-pencil`/`-trash`/`-ok`/`-list-alt` |
| Alerts | `<div>` | — | class only: `alert-warning`/`alert-danger` |

**Known DOM defects** (see `docs/known-defects-and-improvements.md`):
- TM-23/TM-29: both modal titles share `id="myModalLabel"`; every rendered Edit-modal tag input shares
  `id="inputTags"` - both invalid (duplicate ids), so `find_element`/`By.ID` only ever returns the
  first match. Always scope modal-internal locators off the container's `id` (`add`/`edit`, each
  unique), not the duplicated inner ids.
- Row-scoped locators (`ROW_*` in `task_list_locators.py`) must start their XPath with `.` (e.g.
  `.//button[...]`) - a bare `//` is always document-absolute even when queried from a WebElement.

## Where new code goes
Follow this when adding any new Page Object, Component Object, or locator - not just for
`task_list_page.py`/`task_list_locators.py`, but for any future page this app (or a different one)
might add.

- A new **Page Object** (one per URL) goes in `src/ui/pages/<name>_page.py`, subclasses `BasePage`,
  owns `url`/`load()`, and composes whatever Component Objects it needs in `__init__` (e.g.
  `self.navbar = NavbarComponent(driver)`).
- A new **Component Object** (a reusable widget *within* a page - navbar, a table, a modal) goes in
  `src/ui/components/<name>_component.py` and subclasses `BaseComponent` (or `BaseModalComponent` for
  a Bootstrap modal, to inherit its shared `close()`). A component never owns a URL and never calls
  `self.open(...)`.
- Every locator is a tuple added to `src/ui/locators/task_list_locators.py` - never inline a `By....`
  call in a page/component file. Reuse the `xpath()` helper and any existing base-path string constant
  (`ADD_MODAL`/`EDIT_MODAL`-style) via plain f-string concatenation; don't write new per-element
  locator-building functions (see that file's own docstring for the reasoning).

## Locator strategy
(full catalogue in the DOM reference above)

1. Inspect the *live* rendered DOM before writing a locator - never guess a selector from memory or
   from the static HTML alone (Knockout renders/duplicates elements the static markup doesn't show,
   e.g. one `<input id="inputTags">` per tag). Use the attached browser tools, or fetch the page's own
   JS (e.g. `web/models.js`) directly when behavior - not just markup - needs confirming.
2. Priority order: `By.ID` > `By.NAME` > `By.XPATH`. Never `By.CSS_SELECTOR`.
3. Watch for duplicate `id`s (this app has several - see TM-23/TM-29) - scope modal-internal locators
   off the modal's own unique container `id` instead of a duplicated inner one.
4. Any locator meant to be queried relative to an already-found element (not the driver) must start
   its XPath with `.` (`.//...`) - a bare `//` always re-searches the whole document.

## Function-definition conventions
- Build every method out of the inherited `DriverBound` helpers - never call
  `self.driver.find_element(...)` directly outside of those helpers themselves or a genuine one-off
  query that doesn't fit an existing helper.
- **Only `src/ui/pages/base_page.py` imports raw Selenium types** (`By`, `expected_conditions`,
  `TimeoutException`, `WebDriverWait`, `WebElement`) - a Page or Component file should never contain a
  `from selenium...` import. If an existing `DriverBound` helper doesn't cover what a component needs
  (e.g. counting children by tag name, or a "wait but don't raise" variant of some condition), add a
  new named helper to `DriverBound` instead of importing Selenium locally - do this even for a single
  call site (see `count_tag_within`/`is_present`, each added for exactly one caller at the time). This
  also means any repeated `try: ... except TimeoutException: return False/None` block in a component
  is a sign it should be rewritten on top of `wait_until` (or promoted into a new named boolean-return
  helper alongside it) rather than importing `TimeoutException` to handle it locally.
- Every **action** method (clicks/types/submits - anything that changes app state) gets
  `@allure.step("...")` with its own arguments interpolated into the message, e.g.
  `@allure.step("Add task '{title}'")`. This is this project's one form of "input logging" - don't
  add separate `print()`/`logging` calls; the Allure report already captures the call args via the
  step title, plus a screenshot/page source/console log on failure (see `log_failure` in
  `src/reporting/allure_logging.py`).
- Pure **query/getter** methods (`is_*`, `has_*`, or anything returning `bool`/`str`/`list` without
  changing state) do **not** get `@allure.step` - only state-changing actions do.
- Docstrings explain *why*, not what - reference the relevant `TM-xx` finding whenever a method exists
  to work around, or test, a known app defect.
- Only add cross-component orchestration logic at the Page level, and only when an action genuinely
  spans two components (e.g. `TaskListPage.edit_task_title` = `task_table.begin_edit()` +
  `edit_modal.save_title()`). Otherwise, a Page method is a one-line delegation to its component.
- **Grouped verification** methods (`verify_*`) that bundle several related assertions into one named
  check (e.g. `NavbarComponent.verify_warning` = banner count + message + status) *do* get
  `@allure.step` - the one exception to "queries don't get steps", since the point is one named Allure
  entry instead of N bare `assert`s scattered in the test. Prefer adding/extending a `verify_*` over
  writing multiple raw `assert`s in a test when the same combination of checks would otherwise repeat
  across tests (see `verify_task_visible`/`verify_authorized_actions`/`verify_loaded` for the pattern).

## Layering: what belongs in tests vs pages vs components
This is the most important rule in this file - violating it is how `By`/`WebDriverWait`/raw locators
end up back in test files:

- **Tests** (`tests/ui/*.py`) call Page/Component methods only, and read as business-level steps +
  assertions. A test file must never import `selenium.webdriver.*` (`By`, `Keys`,
  `expected_conditions`, `WebDriverWait`) or `task_list_locators` - if a test needs one of those to
  express what it's checking, that's a signal the check belongs in a new component method instead
  (e.g. `test_edit_modal_supports_adding_and_removing_tags` needed to count buttons inside the Tags
  section - that became `EditTaskModalComponent.tag_section_button_count()`, not inline
  `find_elements(By.TAG_NAME, "button")` in the test). This applies even to tests reproducing a very
  specific, one-off app defect (see `add_with_untouched_tags`/`title_label_text`/`field_values` on
  `AddTaskModalComponent` for the TM-18/23/24 precedent) - there's no "it's just this one weird test"
  exception.
- **Pages** (`src/ui/pages/*_page.py`) own navigation (`url`/`load()`) and cross-component
  orchestration only. A Page method's body is composed of calls into `self.<component>.*` - never a
  raw locator or `self.driver.find_element(...)`. (`load()` used to reach into a navbar locator
  directly to wait for initial render; that moved into `NavbarComponent.wait_until_rendered()` for
  exactly this reason - a Page should have zero reason to import `task_list_locators`.)
- **Components** (`src/ui/components/*_component.py`) own every locator, every
  `self.driver.find_element(...)`/`find_elements(...)` call, every wait, and every assertion grouping
  for the one widget they represent. This is the only layer that should import `task_list_locators` -
  it should *not* import raw Selenium types itself (see the `DriverBound` rule above); build on the
  inherited helpers, or add a new one to `base_page.py` if none fits yet.

## Conftest conventions
- `tests/conftest.py` — cross-cutting fixtures shared by API and UI suites (`settings`, `api_client`,
  `make_user`/`make_user_auth`, CLI options).
- `tests/ui/conftest.py` — UI-only fixtures (`driver`, `task_list_page`), plus any higher-level
  "already in a given state" fixture shared by multiple tests (e.g. `signed_in_page`).
- Any fixture that might also be used as *another fixture's parameter name* in the same file must be
  registered via `@pytest.fixture(name="x")` on a function named `_x` (see `settings`/`api_client`/
  `driver`/`task_list_page`) - otherwise pylint correctly flags `redefined-outer-name`, because it's a
  real name-shadowing risk, not just a style nag.
- When two or more tests share a non-trivial setup sequence, extract it into a fixture (see
  `signed_in_page`) instead of letting pylint's `duplicate-code` check catch it later - per the
  **Never disable a pylint rule** rule in `.github/copilot-instructions.md`, that's never an option.
