# Test Traceability Matrix

Confirms two things with the existing automated suite: every atomic requirement derived from
[`specification/task-management-app.md`](../specification/task-management-app.md) has test coverage,
and every test type defined in [`test-strategy.md`](test-strategy.md) is actually exercised.

## Specification coverage

Each row is one independently-testable rule pulled from the spec's API table, attribute list, or
Authentication section — finer-grained than "this endpoint has tests" (one endpoint can encode
several distinct rules, e.g. `PATCH /<task_id>` requires both auth *and* ownership).

### Task & tag model

| ID | Requirement | Covered by |
|---|---|---|
| REQ-01 | Task title max 20 characters | `test_task_title_within_limit_is_accepted`; over-limit case is `xfail` (`test_task_title_exceeding_limit_is_rejected`, TM-07) |
| REQ-02 | Tag name max 20 characters | `test_tag_name_within_limit_is_accepted`; over-limit case is `xfail` (`test_tag_name_exceeding_limit_is_rejected`, TM-07) |
| REQ-03 | Task `done` status, defaults to false, toggles both ways | `test_task_done_flag_toggles_both_directions` |
| REQ-04 | Task has a creation time | **Gap** — only implicit, via full-object equality in `test_get_task_returns_matching_task`; no test asserts it directly (see TM-02) |
| REQ-05 | Task has an owner (= authenticated creator) | `test_create_task_returns_created_task` (asserts the `username` field); exact field naming/settability is an assumption, see TM-02 |
| REQ-06 | Tags are optional on task creation | `test_add_task_with_untouched_tags_field_is_still_created` (UI); tagless creates elsewhere in `test_tasks.py` |
| REQ-07 | Non-existing tags are auto-created on task creation | `test_list_tags_includes_newly_created_tag` |
| REQ-08 | Existing tags are reused, not duplicated | `test_tag_is_deduplicated_across_tasks` |

### Authentication

| ID | Requirement | Covered by |
|---|---|---|
| REQ-09 | Basic auth accepted on protected endpoints | `test_basic_auth_allows_task_creation` |
| REQ-10 | Token auth accepted; password value ignored | `test_token_auth_allows_task_creation`, `test_token_auth_ignores_password_value` |
| REQ-11 | `/authenticate` returns a token for valid credentials | `test_authenticate_with_valid_credentials_returns_token` |
| REQ-12 | Invalid credentials rejected on `/authenticate` | `test_authenticate_with_wrong_password_is_rejected` |
| REQ-13 | Tokens expire after 10 minutes | `test_expired_token_is_rejected` |
| REQ-14 | Invalid/missing auth rejected on protected endpoints | `test_missing_auth_is_rejected_on_protected_endpoint`, `test_invalid_token_is_rejected` |

### API endpoints

| ID | Requirement | Covered by |
|---|---|---|
| REQ-15 | `GET /` lists tasks, no auth needed | `test_root_endpoint_is_reachable` |
| REQ-16 | `PUT /` creates a task, auth required | `test_create_task_returns_created_task`, `test_missing_auth_is_rejected_on_protected_endpoint` |
| REQ-17 | `GET /<task_id>` returns task detail, no auth needed | `test_get_task_returns_matching_task` |
| REQ-18 | `PATCH /<task_id>` requires auth AND ownership | `test_non_owner_cannot_patch_task` |
| REQ-19 | `DELETE /<task_id>` requires auth AND ownership | `test_non_owner_cannot_delete_task` — **currently failing** (`xfail`; TM-12, ownership not enforced) |
| REQ-20 | `GET /tags` lists tags, no auth needed | `test_tags_endpoint_is_reachable` |
| REQ-21 | `GET /tags/<tag_id>` returns tag detail, no auth needed | `test_get_tag_by_id_returns_tag_detail` |
| REQ-22 | `POST /users` creates a user, no auth needed | `test_register_user_succeeds` |

### Web UI

| ID | Requirement | Covered by |
|---|---|---|
| REQ-23 | Add / edit / mark done / delete exposed via the web app | `test_add_task_appears_in_list`, `test_edit_task_title_updates_row`, `test_mark_done_then_mark_in_progress_toggles_label`, `test_delete_task_removes_row` |
| REQ-24 | Sign-in/out via the web app reflects authentication state | `test_sign_in_with_valid_credentials_shows_signed_in_state`, `test_sign_out_hides_authenticated_controls` |
| REQ-25 | Shared task list is visible without authentication | `test_other_users_task_is_visible_in_shared_list` |
| REQ-26 | Mutation controls (Edit/Delete) hidden for non-owners | `test_non_owner_cannot_see_edit_or_delete_buttons` |
| REQ-27 | Web app loads and renders the task table | `test_web_app_loads` |

### Out of scope

| ID | Requirement | Covered by |
|---|---|---|
| REQ-28 | `/reset` drops all data, recreates the default user | Not tested — explicitly out of scope per the assignment |

## Testing type coverage

| Testing type (from `test-strategy.md`) | Covered by | Example test |
|---|---|---|
| Functional (positive) | All modules | `test_create_task_returns_created_task` |
| Functional (negative) | `test_tasks.py`, `test_tags.py`, `test_users.py`, `test_authentication.py` | `test_missing_auth_is_rejected_on_protected_endpoint` |
| Boundary | `test_tasks.py`, `test_tags.py` | `test_task_title_within_limit_is_accepted` |
| State transition | `test_tasks.py`, `test_task_management_ui.py` | `test_task_done_flag_toggles_both_directions` |
| Idempotency | `test_tasks.py`, `test_authentication.py` | `test_delete_is_idempotent_in_effect` |
| Authentication & Authorization | `test_authentication.py`, `test_authorization.py`, `test_authentication_ui.py`, `test_authorization_ui.py` | `test_non_owner_cannot_patch_task` |
| Security (light, black-box) | `test_users.py`, `test_authentication.py` | `test_register_user_response_does_not_echo_password` |
| Compatibility | Every `tests/ui/` module, via the Chrome/Safari × Full HD/4K matrix (`src/config/browsers.py`) | `test_web_app_loads` |
| Regression | Full suite, run on every CI PR | — |
| Exploratory (manual, AI-assisted) | Surfaced defects/assumptions tracked in `known-defects-and-improvements.md` | — |

## Notes

- `/reset` has no tests by design — explicitly out of scope per the specification.
- Tests that reproduce a currently-confirmed defect are marked `xfail(strict=True)`: they assert the
  *correct* expected behavior and will start failing loudly (`XPASS`) once the underlying bug is
  fixed, which is the signal to remove the marker. See `known-defects-and-improvements.md` for the
  full list and evidence per finding.
- Findings categorized as Ambiguity, Design Issue, or Improvement there intentionally have **no**
  automated test — they document a product/spec clarification or a suggestion, not a behavioral
  defect a test could assert against.

