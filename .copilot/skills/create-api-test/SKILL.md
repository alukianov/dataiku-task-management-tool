---
name: create-api-test
description: Scaffolds a new pytest API test for this task management REST API suite, following the project's test strategy, fixtures, Allure step conventions, and docstring template. Use when asked to "create an API test", "add a test for PUT /", "write an API test case", or "add negative/boundary/idempotency coverage for an endpoint".
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

# Create API Test

Scaffolds or extends a pytest test in `tests/api/` for this REST API suite, matching the project's
established conventions instead of free-form test code.

## Prerequisites

- Venv already set up at `.venv\Scripts\python.exe` (see `README.md` setup section)

---

## Step-by-step workflow

### 1. Confirm scope before writing anything

Read, in this order:

1. `.github/copilot-instructions.md` — repo structure, API client layering, docstring templates,
   conventions ("Never disable a pylint rule", "Config/credentials are never hardcoded").
2. `docs/test-strategy.md` — the **Test types** table (Functional positive/negative, Boundary, State
   transition, Idempotency, Authentication & Authorization, Security, Regression, Exploratory) and the
   **Test design techniques** section. Pick the exact type(s) the new test exercises — this drives the
   `@pytest.mark` markers.
3. `docs/test-plan.md` — the **Features to be tested** table and the **Exploratory testing scope**
   table, to confirm the behavior is in scope and find its priority (P0–P3).
4. `docs/test-traceability.md` — the **Specification coverage** (REQ-xx) and **Testing type coverage**
   tables. Check whether the requirement you're about to test already has a `REQ-xx` row and an
   `Example test` — don't duplicate coverage; if it's a genuinely new atomic requirement, you'll add a
   `REQ-xx` row at the end (see step 8).
5. `docs/known-defects-and-improvements.md` — grep for the endpoint/behavior. If this test reproduces
   an already-known issue, you'll write it as an `xfail` (see step 6); if it's new behavior you're
   confirming works, it's a normal passing test.

### 2. Pick the right module and layer

- One test module per REST resource, mirroring `src/api/resources/`:
  `tests/api/test_tasks.py`, `test_tags.py`, `test_users.py`, `test_authentication.py`,
  `test_authorization.py`, `test_health_smoke.py`. Only create a new module for a genuinely new
  resource.
- If the endpoint action doesn't exist yet on the client, add it first in
  `src/api/resources/<resource>.py` (method + Google-style docstring, see
  `.github/copilot-instructions.md` "Docstring conventions") and wire it through
  `src/api/client.py` if it's a new resource class. **Tests never call `api_client.http.<verb>()` or
  `requests` directly** — only `api_client.<resource>.<action>(...)`.

### 3. Use the existing fixtures — never hand-roll setup

From `tests/conftest.py`:

| Fixture | Use for |
|---|---|
| `api_client` | Unauthenticated client bound to the active environment |
| `qa_auth` / `qa_token_auth` | Basic/token auth for the default configured user |
| `unique_name` | Collision-safe title/tag/username generator (≤20 chars) — **always** use this instead of a fixed literal; the shared instance is never reset (TM-11) and fixed literals cause deterministic 500s (TM-14/TM-28) |
| `create_task` | Arrange-phase factory that also tracks/deletes the task during teardown |
| `make_user` / `make_user_auth` | Register a brand-new scenario-only user |
| `other_users_task` | Factory bundling `make_user_auth` + `create_task` for non-owner scenarios |
| `verify_response` | Status + optional body/message assertion, wrapped in its own Allure step |

### 4. Mark the test

```python
@allure.feature("Tasks")        # or Tags / Users / Authentication / Authorization / Platform Health
@pytest.mark.api
@pytest.mark.negative           # add boundary / idempotency / auth / security / smoke as applicable
def test_<behavior>(<fixtures>):
    """Verifies that <scenario/behavior under test>."""
    ...
```

Markers come straight from the Test types table in `test-strategy.md` — don't invent new ones.

### 5. Allure steps — what already exists vs. what you add

- Every HTTP call made through `api_client.<resource>.<action>()` is **automatically** attached to
  Allure (`src/api/base_client.py` → `log_http_call`) — you never add your own request/response
  logging.
- `verify_response(...)` already wraps its assertions in `@allure.step("Verify response ({expected_status})")`
  — use it instead of bare `assert response.status_code == ...` whenever a status/body check is
  needed.
- Only add a **new** `@allure.step` if you're introducing a new *reusable, multi-call* fixture/helper
  (like `other_users_task` or `_authenticate` in `tests/conftest.py`) — a single test function itself
  does not get its own `@allure.step`.

### 6. If this test documents a known defect

```python
@pytest.mark.xfail(
    reason="TM-xx (docs/known-defects-and-improvements.md): <one-line summary>. "
    "Remove xfail once the defect is fixed.",
    strict=True,
)
def test_<ideal_behavior>(...):
    """Verifies that <ideal behavior>, not <observed broken behavior>."""
    response = ...
    # Ideal-behavior placeholder - the real response currently <does X> instead (TM-xx).
    verify_response(response, <expected_status>, expected_message="...")
```

Use `strict=True` always — an unexpectedly-passing `xfail` (`XPASS`) is the signal the defect was
fixed and the marker should be removed.

### 7. Docstring

One line only, per `.github/copilot-instructions.md`'s test template:

```python
"""Verifies that <scenario/behavior under test>."""
```

No `Args:`/`Returns:` — fixture parameters aren't documented as args, tests return `None`.

### 8. Update traceability if coverage changed

- New atomic requirement → add a `REQ-xx` row to the matching section of
  `docs/test-traceability.md` → **Specification coverage**.
- New defect reproduction → confirm/add the row in `docs/known-defects-and-improvements.md` (use the
  `allure-report-analyst` skill if you're documenting it from an actual failed run rather than from
  static/exploratory analysis).

### 9. Validate

```powershell
.venv\Scripts\python.exe -m pytest -m "api and <marker>" -q
.venv\Scripts\python.exe -m black --check src tests scripts
.venv\Scripts\python.exe -m pylint src tests scripts   # must stay >= 9.0/10, zero # pylint: disable
```
