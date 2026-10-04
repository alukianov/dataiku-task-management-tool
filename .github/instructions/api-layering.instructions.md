---
applyTo: "src/api/**,tests/api/**"
---

# API client layering

Four layers, each with exactly one job - mirrors the UI's Page/Component/`DriverBound` split (see
`.github/instructions/ui-conventions.instructions.md`):

- **`src/api/base_client.py`** (`BaseAPIClient`) - owns the `requests.Session`, base URL, timeout, and
  the raw HTTP verbs (`get`/`post`/`put`/`patch`/`delete`), all funneled through one private
  `_request()`. This is the *only* place that calls `requests` directly, and the *only* place a
  request/response pair gets logged - both the persistent Allure attachment (`log_http_call`, headers/
  body) and the DEBUG-level console summary (`logger.debug("%s %s -> %s", method, path, status)`) live
  here exactly once, so every resource method gets both for free without its own logging code.
- **`src/api/resources/*.py`** (`Tasks`/`Tags`/`Users`/`Auth`/`System`) - one class per REST resource,
  each holding that resource's business actions (e.g. `Tasks.create_task()`, `Tasks.update_task()`).
  A resource method's body builds the request payload from its arguments and endpoint path from
  `src/api/endpoints.py`'s constants/`build_path()`, then calls `self.http.<verb>(...)` - never
  `requests` directly, never its own Allure/logging (that's `BaseAPIClient`'s job, not duplicated per
  resource).
- **`src/api/client.py`** (`TaskManagementAPIClient`) - composes every resource class into one object
  bound to a single `BaseAPIClient`, exposed as namespaces (`client.tasks`, `client.tags`, ...). Pure
  composition - no business logic of its own.
- **`src/api/auth.py`** (`basic_auth`/`token_auth`) - pure auth-object builders, independent of the
  client/resource chain; passed into resource methods via their `auth=` kwarg.
- **Tests** (`tests/api/*.py`) call `api_client.<resource>.<action>(...)` only - never
  `api_client.http.<verb>(...)`, never `requests` directly, and never import `BaseAPIClient`/
  `src.api.endpoints`. If a test needs a new action, that's a signal to add a method to the matching
  resource class (or a new resource class + facade wiring), not to reach past it.
- New endpoint coverage: add the path to `src/api/endpoints.py`, a method to the matching resource
  class (new resource class + `TaskManagementAPIClient` wiring if it's a new resource), then a test
  module under `tests/api/`.
