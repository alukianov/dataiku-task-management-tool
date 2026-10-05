# Known Defects and Improvements

Findings from reviewing `specification/task-management-app.md`, a minimal read-only probe of the live
instance (`GET /`, `GET /tags`, `GET /web/index.html`) performed before any test was implemented, and
defects/improvement ideas confirmed or surfaced while implementing and running the automated suite.
Each finding is structured so it can be copied directly into a GitHub issue (Bug Report or
Specification Clarification template) once confirmed/reproduced with a full test.

The specification does not fully describe the application's flows and processes (e.g. tag lifecycle,
shared-vs-per-user task ownership, error contract) — closing those gaps is exactly what the
**Exploratory (manual, AI-assisted)** test type (see `test-strategy.md`) is for. Behavior surfaced this
way, rather than stated explicitly in the spec, is recorded below under the **Ambiguity**/**Gap**
categories as an **assumption** inferred from observed behavior, not a confirmed requirement — each one
needs sign-off from the business/stakeholders before being treated as either "working as intended" or
"a bug to fix."

Status legend: `Open` (not yet converted to an issue) · `Issue Raised` (linked) · `Resolved` (no longer
applicable) · `Won't Fix` (accepted as intended design)

## Finding structure

Every finding starts with the same header line —
`**Type** · **Priority** · **Area** · **Status**` followed by `**Spec reference**` — and then uses the
fixed set of sections for its type, in this order:

| Type | Sections | GitHub issue template |
|---|---|---|
| Bug / Security | Description · Steps to reproduce · Expected result · Actual result · Root cause · Test coverage · Suggested fix · Notes | Bug Report |
| Design Issue / Improvement | Current behavior · Problem / impact · Proposed improvement · Test coverage · Notes | Design Issue / Improvement |
| Gap / Ambiguity / Assumption | Open question · Observed behavior · Impact · Suggested resolution · Test coverage · Notes | Specification Clarification |
| Process risk / Reliability | Risk · Observed behavior · Impact · Mitigation · Notes | — (internal) |

A section with nothing to report is written as `None`/`Unknown` rather than dropped. `Notes` is
optional and holds cross-references, priority rationale, and follow-up observations.

## Summary

Priority follows the Likelihood × Impact model in `test-strategy.md` (P0 = security/data-corruption
risk, P1 = functional correctness, P2 = inconsistent contract/minor UI, P3 = cosmetic/no real impact).
Area is the layer the finding lives in; Testing type is how it was surfaced/is verified.

| ID | Title | Area | Testing type | Category | Priority | Status | Test(s) |
|---|---|---|---|---|---|---|---|
| TM-19 | Application purpose ambiguity — shared global task list vs. per-user task list | Design | Exploratory | Ambiguity | P0 | Open | None |
| TM-10 | Task/tag ID scheme unknown (IDOR risk) | API | Exploratory | Security | P0 | Open | None (see TM-12 tests) |
| TM-12 | `DELETE` does not enforce task ownership | API | API testing | Bug (Critical), Security | P0 | Open | `test_non_owner_cannot_delete_task`, `test_non_owner_cannot_delete_task_via_token_auth` |
| TM-14 | Duplicate title/missing required field crashes with `500` | API | API testing | Bug | P0 | Open | `test_create_task_missing_title_field_is_rejected`, `test_put_duplicate_title_in_quick_succession` |
| TM-05 | No documented behavior for expired token / non-owner access (JWT forgery confirmed not viable) | API | API testing | Gap | P1 | Open | `test_expired_token_is_rejected`, `test_forged_token_with_tampered_exp_is_rejected` |
| TM-07 | Title/tag length validation not enforced | API | API testing | Bug | P1 | Open | `test_task_title_exceeding_limit_is_rejected`, `test_task_empty_title_is_rejected`, `test_tag_name_exceeding_limit_is_rejected` |
| TM-09 | `/users` — no auth, no documented uniqueness/password policy | API | API testing | Gap, Security | P1 | Open | `test_register_duplicate_username_is_rejected_cleanly` |
| TM-18 | Add Task silently fails when the Tags field is left untouched | UI | UI testing | Bug | P1 | Open | `test_add_task_with_untouched_tags_field_is_still_created` |
| TM-25 | Edit modal can't add or remove tags, only rename existing ones in place | UI | UI testing | Bug | P1 | Open | `test_edit_modal_supports_adding_and_removing_tags` |
| TM-28 | `POST /users` crashes with `500` when the password matches another user's | API | API testing | Bug (Critical) | P1 | Open | `test_register_user_with_password_matching_existing_user_is_rejected_cleanly` |
| TM-31 | Inconsistent capitalization in the page `<title>` ("ToDo" vs "ToDO") | UI | UI testing | Bug (Branding) | P1 | Open | `test_page_title_is_spelled_consistently` |
| TM-33 | Invalid/expired auth cookie on `PUT /` crashes with `500` instead of `401` | API | UI testing | Bug | P1 | Open | `test_expired_session_shows_warning_during_action` |
| TM-01 | "status" attribute vs. boolean `done` field | API | Static review | Ambiguity | P2 | Open | None |
| TM-02 | Owner/creation-time not settable via `PUT /` | API | Static review | Ambiguity | P2 | Open | `test_create_task_returns_created_task` (confirms owner assignment) |
| TM-03 | Empty-collection shape inconsistency (`[]` vs `{}`) | API | Static review | Bug (Potential) | P2 | Open | `test_list_tags_includes_newly_created_tag` (documents the shape) |
| TM-06 | No documented HTTP status/error contract | API | Static review | Gap | P2 | Open | `test_delete_is_idempotent_in_effect` (documents the status-code inconsistency) |
| TM-08 | Tag lifecycle (dedup scope, orphan cleanup) unspecified | API | Static review | Gap | P2 | Open | `test_tag_is_deduplicated_across_tasks` |
| TM-13 | Intermittent `500` on otherwise-valid requests | API | Exploratory | Reliability | P2 | Open | None (mitigated via `create_task` fixture retry, `tests/conftest.py`) |
| TM-15 | Not-found responses have an empty body, no error message | API | API testing | Bug | P2 | Open | `test_get_nonexistent_task_returns_404`, `test_get_nonexistent_tag_returns_404`, `test_get_deleted_task_returns_404_with_message` |
| TM-34 | Repeated `/authenticate` token stability is unspecified | API | API testing | Gap | P2 | Open | `test_repeated_authenticate_returns_the_same_token` |
| TM-17 | Failed sign-in stacks exponentially duplicating warning banners | UI | UI testing | Bug | P2 | Open | `test_repeated_failed_sign_in_does_not_stack_duplicate_warnings` |
| TM-21 | No pagination on `GET /`, `/tags`, `/users`, or the UI task table | Design | Exploratory | Improvement | P2 | Open | None |
| TM-22 | Sign-out doesn't clear the navbar username/password inputs | UI | UI testing | Bug | P2 | Open | `test_sign_out_clears_credential_inputs` |
| TM-23 | Add Task modal is mislabeled "Update a task" | UI | UI testing | Bug | P2 | Open | `test_add_task_modal_has_its_own_title` |
| TM-24 | Add Task modal retains the previous title/tags after a successful submit | UI | UI testing | Bug | P2 | Open | `test_add_task_modal_inputs_are_cleared_after_submit` |
| TM-27 | No confirmation prompt before Delete | UI | Exploratory | Design Issue | P2 | Open | None |
| TM-29 | Duplicate `id` attributes in the rendered DOM (`myModalLabel`, `inputTags`) | UI | Exploratory | Bug | P2 | Open | None (informs `src/ui/locators/` design) |
| TM-35 | Status label behaves inconsistently between Done and In Progress | UI | Manual | Design Issue | P2 | Open | None |
| TM-36 | Task table is not responsive on small resolutions | UI | Manual | Design Issue | P2 | Open | None |
| TM-04 | Token-as-username auth scheme — security implications | API | Static review | Security | P3 | Open | None |
| TM-16 | `DELETE` response doesn't identify the deleted resource | API | API testing | Bug (policy), Improvement | P3 | Open | `test_delete_response_includes_deleted_task_id` |
| TM-20 | API design: tasks resource has no `/tasks` path, creation uses `PUT` instead of `POST` | API | Static review | Design Issue | P3 | Open | None |
| TM-26 | Date column shows a raw, unformatted ISO-8601 timestamp | UI | Exploratory | Design Issue | P3 | Open | None |
| TM-30 | No stable `id`/`data-testid` attributes on most interactive elements - forces brittle XPath/`data-bind` selectors | UI | Exploratory | Design Issue, Improvement | P3 | Open | None (informs `src/ui/locators/` design) |
| TM-37 | No UI design system — buttons have inconsistent size/colour/style | Design | Manual | Design Issue | P3 | Open | None |
| TM-11 | Shared single live instance — test isolation risk (self-cleaning tests implemented) | Process | Process | Process risk | — | Resolved | None (mitigated via `unique_name`/`create_task` fixtures, `tests/conftest.py`) |

---

## TM-19 — Application purpose ambiguity: shared global task list vs. per-user task list

**Type**: Ambiguity (specification/product, not a code defect) · **Priority**: P0 · **Area**: Design ·
**Status**: Open
**Spec reference**: Task attribute list (an "owner" attribute exists); `/` GET row ("No" auth needed);
`/<task_id>` PATCH/DELETE rows ("Yes, and owner of the task")

**Open question**: The spec never states whether this app models *one shared task list visible to
everyone* (with per-task ownership only gating who can mutate a given task) or *N independent per-user
task lists* (where a user should only ever see/interact with their own tasks).

**Observed behavior**: Specification text and live behavior point firmly at the **shared-list**
reading, but several behaviors/UI choices only make sense if you assumed the other model, which is
almost certainly the source of multiple items reported from manual testing:
- `GET /` explicitly needs **no** auth — a genuinely unauthenticated browser session sees the full task
  list (all tasks from every user) immediately on page load, not an empty list. This **matches the
  written spec** (`/` GET: "Needs authentication: No"), so it is **not a bug** — but it does directly
  contradict the intuitive expectation ("when signed off, I shouldn't see other people's/any tasks")
  raised during manual testing.
- Task titles are unique **globally**, not per-owner (see **TM-14**) — if this were meant to be a
  per-user list, two different users should be able to use the same title; instead the second attempt
  crashes with `500`.
- The table's "Owner" column only makes sense because the list is shared — in a true per-user model it
  would be redundant (you'd already know every row is yours). Manual testing flagged this column as
  "redundant" largely because the mixed signal (shared list + per-task mutation gating) makes its
  purpose unclear at a glance.
- `DELETE` not enforcing ownership (**TM-12**) is a much more severe bug under the shared-list model
  (any user can destroy anyone's data) than it would first appear if one assumed tasks were already
  siloed per user.
- The `PATCH`/`DELETE` split itself is evidence of the ambiguity, not just a severity multiplier:
  `PATCH` *does* check ownership and correctly rejects a non-owner with `403`, leaving the task
  unmodified — so per-task access control is clearly intended for mutation. But if the real intent
  were "each user only manages their own tasks," neither endpoint should need an ownership check *or*
  a non-owner should never be able to reach another user's task id in the first place (no visibility
  into it). The fact that `PATCH` bothers to check, but `DELETE` doesn't, and *both* are reachable at
  all by a non-owner, reads like the shared-list model was assumed for mutation but never fully
  reasoned through — not a one-off oversight isolated to `DELETE`.
- `POST /users` needs no auth at all, so anyone can self-register, and the moment a new account
  exists it can call `GET /` and immediately see every task ever created by every other user — there
  is no onboarding/isolation step of any kind. Under the shared-list reading this is "working as
  intended," but it means the list only grows more mixed and harder to navigate as more users
  register (compounding **TM-21**'s lack of pagination/filtering).

**Impact**: Every other ownership/visibility finding here (TM-12, TM-14, TM-21, TM-27) is only
correctly triaged once this is answered: the same observed behavior is "working as intended" under one
reading and a required fix under the other. It also decides whether per-owner filtering should be
added to the UI/API.

**Suggested resolution**: Raise as a Specification Clarification, not a bug — product/architecture
needs to explicitly confirm the shared-list model (then the UI's unauthenticated visibility and the
Owner column are correct-as-is and just need a one-line doc note), or commit to per-user isolation (in
which case `GET /` needing no auth, global title uniqueness, and DELETE's missing ownership check all
become required fixes, not just TM-12 alone).

**Test coverage**: None.

**Notes**: Escalated to P0, ahead of the usual Likelihood × Impact scoring — this isn't a bug with a
contained blast radius, it's an unresolved fork in the product's core data model. Resolving it first is
a prerequisite for prioritizing everything else, not an optional clarification — treat it as blocking
further development/triage decisions.

## TM-10 — Task/tag ID scheme unknown

**Type**: Security (IDOR) · **Priority**: P0 · **Area**: API · **Status**: Open
**Spec reference**: `/<task_id>`, `/tags/<tag_id>`

**Description**: The spec does not state whether IDs are sequential integers or opaque/UUID.
Sequential IDs make enumeration of other users' tasks trivial once combined with TM-05 (non-owner
access behavior).

**Steps to reproduce**:
1. Create several tasks via `PUT /`.
2. Inspect the `id` of each returned task.

**Expected result**: Not specified. Resource identifiers should not allow other users' data to be
enumerated and acted upon.

**Actual result**: IDs are sequential integers — the first task created during framework validation
was `id=1`, and each subsequent task incremented by one.

**Root cause**: Sequential integer ids are exposed directly as resource identifiers.

**Test coverage**: `tests/api/test_authorization.py` (see TM-12 tests).

**Suggested fix**: Report alongside TM-12.

**Notes**: Combined with **TM-12**, any task's contents can currently be *read* (by design,
`GET /<task_id>` needs no auth) and *deleted* (bug) by guessing a small integer — a materially
exploitable IDOR, not just a theoretical risk.

## TM-12 — `DELETE` does not enforce task ownership

**Type**: Bug (Critical / Security — Broken Access Control, OWASP A01:2021) · **Priority**: P0 ·
**Area**: API · **Status**: Open
**Spec reference**: `/<task_id>` DELETE row: "Yes and owner of the task"

**Description**: Ownership is implemented and enforced for `PATCH`, but the same check is missing on
`DELETE` — an authenticated non-owner can delete another user's task.

**Steps to reproduce**:
1. Register a second user (`QA2`) via `POST /users`.
2. As `QA2`, create a task via `PUT /`.
3. As the original `QA` user (authenticated, but not the owner), call `DELETE /<task_id>` on that task.
4. For comparison, as `QA`, call `PATCH /<task_id>` on a task owned by `QA2`.

**Expected result**: `DELETE` by a non-owner is rejected with `403` and the task is left unmodified —
the same behavior as `PATCH`, which returns `403 {"message": "You're not the owner of this task"}`.

**Actual result**: `DELETE` by the non-owner returns `200` and the task is actually deleted. `PATCH` by
the non-owner correctly returns `403` and leaves the task unchanged.

**Root cause**: The ownership check applied on the `PATCH` path is not applied on the `DELETE` path.

**Test coverage**: `tests/api/test_authorization.py` — `test_non_owner_cannot_patch_task` (passes);
`test_non_owner_cannot_delete_task` and `test_non_owner_cannot_delete_task_via_token_auth` (marked
`xfail(strict=True)` pending a fix — they will loudly fail once `DELETE` starts correctly returning
`403`, as a reminder to remove the marker).

**Suggested fix**: File as a Critical severity Bug Report immediately — apply the same ownership check
to `DELETE` as to `PATCH`. Any authenticated user can currently delete any other user's tasks given the
(sequential, guessable — see TM-10) task ID.

## TM-14 — Duplicate title / missing required field crash with `500`

**Type**: Bug (reliability root cause, not just dev-server noise) · **Priority**: P0 · **Area**: API ·
**Status**: Open
**Spec reference**: `/` PUT row; `/users` POST row (contrast case)

**Description**: Two distinct, **deterministically reproducible** request-handling bugs, both returning
`500 Internal Server Error` instead of a clean `4xx`.

**Steps to reproduce**:
1. Duplicate title: call `PUT /` twice in a row with the identical body (with or without tags).
2. Missing field: call `PUT /` with the required `title` field omitted entirely from the JSON body.

**Expected result**:
1. Duplicate-title creation is a handled case — either allowed (`200` with a new id) or rejected with
   `409`/`400`, never `500`.
2. Missing required field is rejected with a clean `400` and a message — as `POST /users` already does
   for a missing `username`/`password` (`400 {"message": "Username and password must be provided"}`).

**Actual result**:
1. First call `200`, second call `500`. Reproduced 3/3 times, with and without tags, including when the
   *tag* name (not just the title) was reused across the two calls. Also reproduces **across two
   different users**, not just the same user calling `PUT /` twice.
2. `500`.

**Root cause**: Titles are evidently unique across the whole instance (not scoped per-owner), and the
uniqueness violation is not handled. Required-field validation present on `POST /users` is not applied
to `PUT /`.

**Test coverage**: `tests/api/test_tasks.py` — `test_put_duplicate_title_in_quick_succession`
(marked `xfail(strict=True)` pending a fix), `test_create_task_missing_title_field_is_rejected`.

**Suggested fix**: File as a Bug Report — (1) handle duplicate-title creation (either allow it and
return `200` with a new id, consistent with `PUT /` not being keyed by title, or reject with
`409`/`400`, but never `500`); (2) validate missing required fields on `PUT /` the same way
`POST /users` already does.

**Notes**: This finding is the most likely root cause of **TM-13**'s "intermittent" `500`s. The
cross-user reproduction directly feeds **TM-19** (shared task list or per-user?): if tasks are meant to
be per-user, title uniqueness should be scoped per-owner (and shouldn't crash either way); if the list
is meant to be global/shared, this is arguably correct uniqueness semantics with the wrong failure mode
(`500` instead of `409`).

## TM-05 — No documented behavior for expired token / non-owner access

**Type**: Gap (partially resolved) · **Priority**: P1 · **Area**: API · **Status**: Open
**Spec reference**: Authentication + `/<task_id>` DELETE/PATCH rows ("Yes and owner of the task")

**Open question**: No expected status code/body is specified for: (a) an expired token used on any
authenticated endpoint, (b) valid authentication but not the task owner on `DELETE`/`PATCH`.

**Observed behavior**:
- Non-owner `PATCH` correctly returns `403 {"message": "You're not the owner of this task"}` with the
  task left unmodified. Non-owner `DELETE` does **not** match this behavior — see **TM-12**.
- Token format: the token is a 3-segment JWT (`HS256`), e.g.
  `{"alg":"HS256","exp":<unix>,"iat":<unix>}.{"id":1}.<signature>` — `exp`/`iat` live in the header
  segment rather than the payload, which is non-standard JWT shape but doesn't affect behavior.
- Forgery probe: the server **properly validates the signature** — an `alg: none` token (trailing dot
  or segment stripped entirely) and a token with only the header's `exp` claim tampered (original
  signature reused, now mismatched) were both rejected with `401`. A validly-signed, already-expired
  token **cannot be forged without the server's HMAC secret**.
- Expiry: since a JWT's `exp` is an absolute Unix timestamp, a token captured once and confirmed past
  its `exp` stays rejected forever. A real token was minted, the real 10-minute TTL was waited out
  once, and rejection was confirmed (`401 Unauthorized Access`).

**Impact**: Status-code assertions for these paths are based on observed behavior rather than a
written contract.

**Suggested resolution**: Done — forgery confirmed not viable; genuine expiry is a fast, always-run
regression test via a one-time-captured real token; `DELETE` ownership is an open issue (TM-12).

**Test coverage**: `tests/api/test_authorization.py::test_non_owner_cannot_patch_task`;
`tests/api/test_authentication.py::test_expired_token_is_rejected` (the captured token is hardcoded as
`EXPIRED_TOKEN`, so it runs instantly on every CI run — no `skip`/`slow` marker);
`test_forged_token_with_tampered_exp_is_rejected` (complementary fast check that signature verification
itself can't be bypassed).

## TM-07 — Title / tag length validation not enforced

**Type**: Bug · **Priority**: P1 · **Area**: API · **Status**: Open
**Spec reference**: "A title (maximum length 20)", "The name of a tag cannot exceed 20 characters"

**Description**: The documented 20-character limits on task titles and tag names are not enforced, and
the spec doesn't state the behavior for exactly 20 chars, 21+ chars (reject with 400? truncate
silently? accept anyway?), or an empty/missing title.

**Steps to reproduce**:
1. `PUT /` with a 21-char title.
2. `PUT /` with an empty-string title (`""`).
3. `PUT /` with a 21-char **tag** name.
4. `PUT /` with a 20-char title/tag name (the documented boundary).

**Expected result**: 20-char title/tag accepted; over-length title/tag and empty title rejected with a
clean `4xx` and a message.

**Actual result**:
1. `200`, title stored **unmodified** (not rejected, not truncated).
2. `200`, accepted as a valid task.
3. `500 Internal Server Error` — not even a clean rejection, worse than the title case, which at least
   doesn't crash.
4. `200`, correctly accepted.

**Root cause**: No server-side length/emptiness validation on title or tag name.

**Test coverage**: `tests/api/test_tasks.py` — `test_task_title_exceeding_limit_is_rejected`,
`test_task_empty_title_is_rejected` (`xfail` pending a fix); `tests/api/test_tags.py` —
`test_tag_name_exceeding_limit_is_rejected` (`xfail` pending a fix).

**Suggested fix**: File as two Bug Reports — (1) the 20-char limit on titles is not enforced at all
(silent accept), (2) over-length tag names crash the request instead of being rejected or truncated.

## TM-09 — `/users` endpoint has no auth and no documented policy

**Type**: Gap / Security · **Priority**: P1 · **Area**: API · **Status**: Open
**Spec reference**: `/users` POST row

**Open question**: Anyone (unauthenticated) can create a user with any username/password. There is no
documented uniqueness check on username, no password policy (min length, complexity), and no rate
limiting mentioned.

**Observed behavior**: Re-registering an already-existing username (`QA2`) with a *different*
password returns `500 Internal Server Error` rather than a clean `400`/`409` — there is no graceful
duplicate-username handling.

**Impact**: Open self-registration with no documented policy; the `500` itself is a minor robustness
bug (a client-input conflict should not `500`).

**Suggested resolution**: File as a minor bug (duplicate username → `500` instead of `4xx`) alongside a
Specification Clarification for the missing password policy.

**Test coverage**: `test_register_duplicate_username_is_rejected_cleanly`.

## TM-18 — Add Task silently fails when the Tags field is left untouched

**Type**: Bug · **Priority**: P1 · **Area**: UI · **Status**: Open
**Spec reference**: N/A — frontend-only; the spec itself says tags are optional ("Optionally, a list of
tags", `specification/task-management-app.md`)

**Description**: Adding a task without ever touching the Tags field closes the modal but never creates
the task, with no error shown to the user.

**Steps to reproduce**:
1. Sign in and click "+ Add".
2. Fill in only the Title field; leave Tags completely untouched (never focus it).
3. Submit the Add Task modal.

**Expected result**: The task is created (tags are optional) and appears in the table.

**Actual result**: The modal closes but no row is added to the task table and the title never appears
anywhere in the page source. No error is shown. Filling the Tags field (even by focusing and clearing
it, without typing a tag) avoids the crash and the task is created normally.

**Root cause**: In `web/models.js`, `AddTaskViewModel.tags` defaults to a plain JS array
(`self.tags = []`), but `addTask()` unconditionally calls `to_add.tags.split(" ")` on submit, assuming
`tags` is always a string. Knockout's plain-property two-way binding only replaces that array default
with a string once the bound `<input data-bind="value: tags">` field actually fires a change event. If
the field was never touched, `[].split(" ")` throws an uncaught
`TypeError: tags.split is not a function`, and the function aborts **after** the modal has already been
hidden.

**Test coverage**: `test_add_task_with_untouched_tags_field_is_still_created`.

**Suggested fix**: File as a Bug Report — `addTask()` should guard the split with something like
`(to_add.tags || "").split(" ")` or default `self.tags` to `""` (a string) instead of `[]`, and the
failure path should surface a visible error instead of failing silently.

## TM-25 — Edit modal can't add or remove tags, only rename existing ones in place

**Type**: Bug (covers two manually-reported symptoms that share one root cause) · **Priority**: P1 ·
**Area**: UI · **Status**: Open
**Spec reference**: N/A — frontend-only; spec allows tags to be part of the `PATCH` body
(`{title, tags, done}`), implying tags should be fully editable, not just renameable

**Description**: The Edit modal only lets the user rename a task's existing tags in place — there is no
way to add a new tag or remove an existing one.

**Steps to reproduce**:
1. Create a task with 2 tags.
2. Open the Edit modal for that task.
3. Try to add a third tag, then try to remove one by clearing its input and saving.

**Expected result**: Tags can be added and removed, as well as renamed.

**Actual result**: The modal contains exactly 2 `<input id="inputTags">` elements (one per existing
tag) and exactly 2 buttons total ("Close", "Save changes") — no add-tag affordance and no per-tag remove
control. Clearing an input to an empty string doesn't delete that tag entry; it turns it into a tag with
an empty name that remains present and editable.

**Root cause**: The tags section is a Knockout `foreach` over the task's **existing** tags only:
```html
<!-- ko foreach: { data: tags(), as: 'tag' } -->
    <input class="form-control" data-bind="value: tag.name" ... id="inputTags" maxlength="20">
<!-- /ko -->
```

**Test coverage**: `test_edit_modal_supports_adding_and_removing_tags`.

**Suggested fix**: File as a Bug Report — the Edit modal needs an explicit "add tag" input (append a
new entry to the `tags` array) and a per-tag remove/delete button (splice it out of the array), rather
than relying on in-place rename of a fixed-size list as the only tag-editing mechanism.

## TM-28 — `POST /users` crashes with `500` when the password matches another user's

**Type**: Bug (Critical) · **Priority**: P1 · **Area**: API · **Status**: Open
**Spec reference**: `/users` POST row — `{username, password}` → "The created user"; no documented
uniqueness constraint on password

**Description**: Creating a new user whose password matches an **already-registered** user's password
— regardless of username — crashes the server instead of creating the account. The username is not the
trigger, only the password value collision is.

**Steps to reproduce**:
1. `POST /users {"username": "QA1", "password": "willWin"}` (`willWin` already belongs to the seed `QA`
   user).
2. Repeat with a fresh, never-used password.

**Expected result**: The user is created (`200`) in both cases.

**Actual result**: Step 1 → `500 Internal Server Error`; step 2 → `200`.

**Root cause**: Unknown — strongly suggests passwords are stored/compared in a way that doesn't tolerate
duplicates (e.g. a broken unique index or hash-collision-handling bug).

**Test coverage**: `test_register_user_with_password_matching_existing_user_is_rejected_cleanly`.

**Suggested fix**: File as a Critical Bug Report — password values should never cause a server crash
regardless of collisions with other users' credentials; add a dedicated security follow-up on how
passwords are persisted.

**Notes**: Independently reconfirmed as unplanned flakiness in this suite —
`tests/api/test_users.py` originally used fixed literal passwords (`"a-password-123"`,
`"super-secret-password"`) which, once used by an earlier run against this shared/never-reset instance
(TM-11), caused `test_register_user_succeeds` and
`test_register_user_response_does_not_echo_password` to start failing with `500` on every subsequent
run with no code change — i.e. this bug can silently turn a previously-green suite red over time. Both
tests now use `unique_name()` to generate a fresh password per run, which resolves the flakiness
without touching the server.

## TM-31 — Inconsistent capitalization in the page `<title>`

**Type**: Bug (Branding) · **Priority**: P1 · **Area**: UI · **Status**: Open
**Spec reference**: N/A — frontend-only

**Description**: The word "ToDo" is spelled two different ways within the same page title. No test
previously asserted the page/tab title (`driver.title`), so this went unnoticed.

**Steps to reproduce**:
1. Open the application.
2. Read the browser tab text / document `<title>`.

**Expected result**: Consistent spelling: `ToDo or not ToDo`.

**Actual result**: `<title>ToDo or not ToDO</title>` — lowercase `o` the first time, uppercase `O` the
second time.

**Root cause**: Typo in the served `web/index.html`.

**Test coverage**: `tests/ui/test_ui_smoke.py::test_page_title_is_spelled_consistently`
(`xfail`, `strict=True`) — remove the `xfail` once fixed.

**Suggested fix**: File as a Bug Report (flag the branding angle, not just "cosmetic") — fix the second
occurrence to `ToDo`.

**Notes**: Rated P1, not P3 — typo severity alone is cosmetic, but "ToDo" reads as the application's
own product/brand name, and every page load/tab renders the inconsistency to every user, visibly, every
time (High likelihood). If "ToDo" is confirmed as the actual product name, misspelling it is a
brand-consistency defect with real business impact (Medium-High), not just a typo — still not a
functional/security issue, so not P0. This is itself an **assumption** pending confirmation: verify
with the business/stakeholders whether "ToDo" is the product name before communicating this priority
externally.

## TM-33 — Invalid/expired auth cookie on `PUT /` crashes with `500` instead of `401`

**Type**: Bug · **Priority**: P1 · **Area**: API · **Status**: Open
**Spec reference**: `/<task_id>` PATCH row and Authentication section (no documented status for an
invalid/expired credential on a mutating request)

**Description**: The web UI sends the `token` cookie value as a Basic-auth-style credential (not the
JWT used by the token-auth API tests). When that cookie is invalid/corrupted and the UI performs a
mutating `PUT /`, the server responds `500` instead of `401`, so the user never sees the intended
session-expired message.

**Steps to reproduce**:
1. Sign in and add a task.
2. Run `document.cookie = 'token=deliberately-invalid-token;path=/'` (this does correctly overwrite
   the valid cookie — verifiable via `driver.get_cookies()` before/after).
3. Click "Mark Done" on the task.

**Expected result**: The server returns `401`, and the UI shows the `.alert-warning` "Your login is
invalid or session has expired" message — the same as a real session expiry (10-minute JWT TTL, same
mechanism).

**Actual result**: The `PUT /` returns `500`; only the `.alert-danger` "Bad server response status 500"
banner renders (`.alert-warning` count stays `0`). Reproduces deterministically in parallel (`-n 2`)
and isolated (`-n 0`) runs, and in a direct Selenium/CDP network-log probe outside pytest.

**Root cause**: The server's Basic-auth cookie parser does not handle malformed/invalid credentials.
The frontend's generic error handler behaves correctly for a `500` — there is no frontend bug.

**Test coverage**: `tests/ui/test_authentication_ui.py::test_expired_session_shows_warning_during_action`
(`xfail(strict=True)` referencing this finding — remove the `xfail` once fixed).

**Suggested fix**: File as a Bug Report — the Basic-auth cookie parser needs to catch
malformed/invalid credentials and return `401`, matching the JWT bearer-token path's behavior.

**Notes**: Related to **TM-05** (expired *JWT bearer* token, which correctly returns `401`), but a
different auth code path. Same bug family as **TM-07**/**TM-14**/**TM-28** (malformed input crashes with
`500` instead of a clean `4xx`), but on the auth-parsing path rather than the business-payload path.

## TM-01 — "status" attribute vs. boolean `done` field

**Type**: Ambiguity · **Priority**: P2 · **Area**: API · **Status**: Open
**Spec reference**: Task attribute list ("a status") vs. `PATCH /<task_id>` body (`done: <boolean>`)

**Open question**: The task attribute list mentions "a status", but the only status-bearing field
exposed by the API is the boolean `done`. Is "status" just `done`/`not done`, or do more states exist
that aren't reachable through the documented endpoints?

**Observed behavior**: No `status` field observed in any documented request/response.

**Impact**: The set of valid task states (and how the UI should present them) is undefined.

**Suggested resolution**: Confirm via the `GET /<task_id>` response shape once a task exists. Raise as a
Specification Clarification if only `done` exists.

**Test coverage**: None.

**Notes**: See **TM-35** for the UI presentation of status.

## TM-02 — Owner / creation time not settable via `PUT /`

**Type**: Assumption to verify · **Priority**: P2 · **Area**: API · **Status**: Open
**Spec reference**: Task attributes (owner, creation time) vs. `PUT /` body (`title`, `tags` only)

**Open question**: Owner and creation time are listed as task attributes but aren't inputs to task
creation — presumably server-assigned (owner = authenticated caller, creation time = server clock).
Not explicitly stated.

**Observed behavior**: Spec table row `/ PUT` accepts only `title` and `tags`; the created task's
`owner` is assigned by the server.

**Impact**: Server-assignment rules for owner/creation time are an undocumented assumption.

**Suggested resolution**: Verify by creating a task with two different authenticated users and
comparing the `owner` field returned.

**Test coverage**: `test_create_task_returns_created_task` (confirms owner assignment).

## TM-03 — Empty-collection shape inconsistency

**Type**: Bug (Potential) · **Priority**: P2 · **Area**: API · **Status**: Open
**Spec reference**: `/` GET and `/tags` GET, both described as returning "the list of existing X"

**Description**: The same conceptual response ("list of existing X") has two different empty
representations.

**Steps to reproduce**:
1. With no tasks, call `GET /`.
2. With no tags, call `GET /tags`.

**Expected result**: Both "list" endpoints return the same empty representation.

**Actual result**: `GET /` → `[]` (JSON array); `GET /tags` → `{}` (JSON object).

**Root cause**: Unknown — `GET /tags` may be a map keyed by tag id even when populated (see TM-06).

**Test coverage**: `test_list_tags_includes_newly_created_tag` (documents the shape).

**Suggested fix**: Create a tag (via task creation) and re-check the `GET /tags` shape. If it becomes
an array, `{}` for the empty case is inconsistent/a minor bug. If it's a map keyed by tag id even when
populated, the spec's "list" wording is misleading.

## TM-06 — No documented HTTP status/error contract

**Type**: Gap · **Priority**: P2 · **Area**: API · **Status**: Open
**Spec reference**: Entire API table

**Open question**: No endpoint specifies expected success/error status codes or error body shape.

**Observed behavior**: Two concrete inconsistencies:
- `GET /<deleted_task_id>` → `404 {}`, but re-`DELETE`-ing the same already-deleted task →
  `400 {"message": "Task not found"}` (two different status codes for the same "not found" condition).
- `GET /tags` values are bare URL strings (`"backend": "http://localhost:5000/tags/5"`), not tag
  objects with an `id` field — the numeric id must be parsed out of the URL to call `GET /tags/<id>`,
  which then returns a *different* shape again (`{"tag": <name>, "tasks": [<task titles>]}`).

**Impact**: All status-code assertions in the test suite are based on observed behavior, not a written
contract.

**Suggested resolution**: Document the *observed* contract once (e.g. inline in the test strategy) and
flag any status code that looks wrong (e.g. `200` on failure, `500` on validation error) as a bug.

**Test coverage**: `test_delete_is_idempotent_in_effect` (documents the status-code inconsistency).

## TM-08 — Tag lifecycle unspecified

**Type**: Gap · **Priority**: P2 · **Area**: API · **Status**: Open
**Spec reference**: "Non-existing tags are created automatically when the task is created."

**Open question**: No stated dedup scope (global vs per-owner, case sensitivity, whitespace handling)
and no endpoint/behavior for orphaned tags (a tag left with zero referencing tasks after all its tasks
are deleted).

**Observed behavior**: No tag delete/update endpoint exists in the API table.

**Impact**: Tag deduplication and cleanup behavior can't be verified against a contract; orphaned tags
accumulate.

**Suggested resolution**: Create tasks with the same tag name in different cases from different users;
delete all tasks referencing a tag and re-check `GET /tags`.

**Test coverage**: `test_tag_is_deduplicated_across_tasks`.

## TM-13 — Intermittent `500` on otherwise-valid requests

**Type**: Reliability (not a functional/security defect) · **Priority**: P2 · **Area**: API ·
**Status**: Open
**Spec reference**: N/A — operational

**Risk**: The shared instance runs a very old Werkzeug/Flask dev server (`Werkzeug/0.12.2
Python/2.7.18`, per the `Server` response header), not a production WSGI server. Valid, well-formed
requests (`POST /users`, `PUT /`) occasionally return `500 Internal Server Error`.

**Observed behavior**: 2 consecutive `500`s creating a task titled "VisibleAcrossUsers", then 3/3 and
15/15 successes retrying the same and different titles immediately after. Success/failure did not
correlate with brand-new random titles, repeated identical titles, or new vs. duplicate usernames. Not
reproducible on demand; appears to be genuine server-side flakiness (likely a single-threaded/in-memory
dev server under light concurrent or rapid sequential load).

**Impact**: Test setup steps can fail for reasons unrelated to the behavior under test.

**Mitigation**: Not a bug to report against the application's *logic* — it's a property of the
throw-away dev server hosting it. Mitigated in the framework via a `create_task` arrange-phase fixture
(`tests/conftest.py`) that retries once on a `5xx` for test *setup* steps only; assertions under test
never retry, so a genuine defect still fails the test.

**Notes**: See **TM-14** — a significant share of these "intermittent" `500`s are actually the
*deterministic* duplicate-title bug, triggered because this suite reused fixed literal titles (e.g.
`"VisibleAcrossUsers"`) against a shared instance that is never reset (TM-11), so a second run collides
with data left over from the first. Every test added going forward uses the `unique_name` fixture
(`tests/conftest.py`) instead of a fixed literal title/tag name specifically to avoid this.

## TM-15 — Not-found responses have an empty body, no error message

**Type**: Bug · **Priority**: P2 · **Area**: API · **Status**: Open
**Spec reference**: N/A — operational/error-contract (extends TM-06)

**Description**: Per team testing policy, **every** non-2xx response must include a message explaining
what went wrong; a bare empty body is treated as a bug, not just a documentation gap.

**Steps to reproduce**:
1. `GET /<task_id>` for a well-formed but never-created numeric id.
2. `GET /tags/<tag_id>` for a well-formed but never-created numeric id.
3. `GET /<task_id>` for a task that existed and was deleted.

**Expected result**: `404` with a `message` field (e.g. `{"message": "Task not found"}`).

**Actual result**: All three return `404 {}` — an empty JSON object with no `message` key. Contrast
with other error paths (`401`, `403`, most `400`s) which *do* include `{"message": "..."}`, including
the double-`DELETE` case on the same deleted id, which correctly returns
`400 {"message": "Task not found"}`.

**Root cause**: The `GET` not-found path doesn't populate a message.

**Test coverage**: `tests/api/test_tasks.py::test_get_nonexistent_task_returns_404`,
`tests/api/test_tags.py::test_get_nonexistent_tag_returns_404`,
`tests/api/test_tasks.py::test_get_deleted_task_returns_404_with_message` (all `xfail(strict=True)`).

**Suggested fix**: File as a minor Bug Report — add a `message` field (e.g. `"Task not found"`,
mirroring the message already used on the double-`DELETE` `400` case) to both `404` responses.

## TM-34 — Repeated `/authenticate` token stability is unspecified

**Type**: Gap · **Priority**: P2 · **Area**: API · **Status**: Open
**Spec reference**: Authentication and `/authenticate` endpoint. The spec says `/authenticate` returns a
generated token and that tokens expire after 10 minutes; it does not state whether repeated
authentication with unchanged credentials must reuse the same token.

**Open question**: Should repeated authentication with unchanged credentials reuse the same token, or
issue a fresh one per successful call?

**Observed behavior**: Two immediate successful `/authenticate` calls (both `200`) returned different
tokens whose decoded `iat` and `exp` claims each advanced by one second — consistent with minting a
fresh token per request.

**Impact**: `test_repeated_authenticate_returns_the_same_token` (marked `idempotency`) fails whenever the
two calls land in different seconds, so it is marked as a non-strict `xfail` until the contract is
clarified. Since the documented contract does not require token reuse, this alone does not establish an
application bug; it exposes an undocumented contract assumption in the test.

**Suggested resolution**: Confirm the intended token issuance contract. If each call may mint a fresh
token, change the test to assert both tokens are accepted and have the documented lifetime rather than
asserting equality. If repeated calls must return the same token, document that requirement and track
the observed behavior as a Bug Report.

**Test coverage**: `test_repeated_authenticate_returns_the_same_token`.

## TM-17 — Failed sign-in stacks exponentially duplicating warning banners

**Type**: Bug · **Priority**: P2 · **Area**: UI · **Status**: Open
**Spec reference**: N/A — frontend-only, not covered by the REST API spec

**Description**: Each failed sign-in adds warning banners instead of showing a single one, and the
count grows exponentially (`2^n - 1`).

**Steps to reproduce**:
1. Enter username `QA` with a wrong password and click Sign in.
2. Repeat twice more (3 failed attempts in total).

**Expected result**: A single visible warning banner, regardless of how many attempts failed.

**Actual result**: 1, then 3, then 7 visible `.alert-warning` elements (8 total in the DOM — one hidden
template + 7 visible clones).

**Root cause**: In `web/models.js`, the `authenticate()` error handler clones the hidden
`.alert-warning` template and appends it after the table on every failed login
(`$('.alert-warning').clone()` then `$('table').after($alert_box)`), but never removes a previous
instance. Because the clone itself also matches the `.alert-warning` selector, each subsequent failed
attempt clones **all currently-present** warning banners, not just the original template.

**Test coverage**: `test_repeated_failed_sign_in_does_not_stack_duplicate_warnings`.

**Suggested fix**: File as a Bug Report — the handler should either reuse/update a single alert element
instead of cloning, or remove prior clones before appending a new one.

**Notes**: Left unfixed, repeated failed logins (e.g. a user mistyping their password a few times)
visibly clutter and progressively slow down the page.

## TM-21 — No pagination on `GET /`, `/tags`, `/users`, or the UI task table

**Type**: Improvement (not a functional defect — works correctly at today's data volume) ·
**Priority**: P2 · **Area**: Design · **Status**: Open
**Spec reference**: N/A — not mentioned anywhere in the spec

**Current behavior**: `GET /` (tasks), `GET /tags`, and the (unspecified but implied) user list all
return their *entire* collection in one response, with no `limit`/`offset`/`page` parameters. The UI's
task table renders every row returned, unbounded, in a single non-virtualized `<table>` — 28+
accumulated tasks render as 28+ literal `<tr>` elements with no scrolling/pagination control.

**Problem / impact**: This will not scale: response payload size, client-side render time, and the DOM
node count all grow linearly and unboundedly with total tasks ever created (compounded by **TM-11** —
there being no practical way to prune the shared instance).

**Proposed improvement**: Propose as a Design Improvement for a future API version — add
`limit`/`offset` (or cursor-based) pagination to `GET /`, `GET /tags`, and any user-listing endpoint,
and have the UI table page through results instead of rendering an unbounded list.

**Test coverage**: None.

**Notes**: Distinct from **TM-36** (table responsiveness to screen size).

## TM-22 — Sign-out doesn't clear the navbar username/password inputs

**Type**: Bug · **Priority**: P2 · **Area**: UI · **Status**: Open
**Spec reference**: N/A — frontend-only

**Description**: After signing out, the previously-typed credentials remain visible in the navbar
inputs (and in their `value` attribute).

**Steps to reproduce**:
1. Sign in as `QA`/`willWin`.
2. Click Sign out.
3. Inspect `input[name='username']` and `input[name='password']`.

**Expected result**: Both inputs are empty.

**Actual result**: `input[name='username']` still has `value="QA"` and `input[name='password']` still
has `value="willWin"`.

**Root cause**: `self.logout()` in `web/models.js` only deletes the `username`/`token` cookies and
hides the auth modal — it never clears the navbar's `<input name="username">` /
`<input name="password">` fields.

**Test coverage**: `test_sign_out_clears_credential_inputs`.

**Suggested fix**: File as a Bug Report (minor security/UX hygiene issue — leaving a password value
sitting in a DOM input after logout, especially on a shared/public machine, is poor practice) —
`logout()` should also reset both input values to empty.

## TM-23 — Add Task modal is mislabeled "Update a task"

**Type**: Bug · **Priority**: P2 · **Area**: UI · **Status**: Open
**Spec reference**: N/A — frontend-only

**Description**: The Add Task dialog is titled "Update a task" instead of something like "Add a task".

**Steps to reproduce**:
1. Click "+ Add".
2. Read the modal title.

**Expected result**: The Add modal has its own title, e.g. "Add a task".

**Actual result**: `#add .modal-title` and `#edit .modal-title` both render the literal text
`"Update a task"`.

**Root cause**: Both modals use the exact same hardcoded header,
`<h4 class="modal-title" id="myModalLabel">Update a task</h4>` — almost certainly a copy/paste of the
Edit modal's markup used as the starting point for the Add modal, without updating the title.

**Test coverage**: `test_add_task_modal_has_its_own_title`.

**Suggested fix**: File as a Bug Report — give the Add modal its own title text (e.g. "Add a task"),
either via a static string change or a Knockout-bound title driven by which modal is open.

**Notes**: The shared `id="myModalLabel"` is tracked separately in **TM-29**.

## TM-24 — Add Task modal retains the previous title/tags after a successful submit

**Type**: Bug · **Priority**: P2 · **Area**: UI · **Status**: Open
**Spec reference**: N/A — frontend-only

**Description**: Reopening the Add modal after successfully creating a task shows the previous
submission's title and tags instead of a blank form.

**Steps to reproduce**:
1. Create a task with title `89d251545a41` and tag `probetag`.
2. Reopen the Add modal immediately after.

**Expected result**: Title and Tags inputs are empty.

**Actual result**: The Title input still contains `89d251545a41` and the Tags input still contains
`probetag`.

**Root cause**: `AddTaskViewModel.title`/`.tags` are plain (non-observable) properties that get written
to once by the bound inputs and read once by `addTask()` — there is no reset step afterward.

**Test coverage**: `test_add_task_modal_inputs_are_cleared_after_submit`.

**Suggested fix**: File as a Bug Report — `addTask()` (and/or the modal's `shown.bs.modal` handler)
should reset `self.title`/`self.tags` to empty once the task is successfully created, or when the
modal is opened.

## TM-27 — No confirmation prompt before Delete

**Type**: Design Issue (UX safeguard gap, not a functional defect) · **Priority**: P2 · **Area**: UI ·
**Status**: Open
**Spec reference**: N/A — not mentioned anywhere in the spec

**Current behavior**: Clicking a row's Delete button calls `self.remove(task)` immediately, which fires
the `DELETE` request with no "Are you sure?" confirmation step (`web/models.js` —
`self.remove = function(task) { self.ajax(..., 'DELETE')... }`, no confirmation dialog or
`window.confirm()` call anywhere in the delete path).

**Problem / impact**: Combined with **TM-12** (DELETE doesn't enforce ownership), accidental/malicious
data loss is a single misclick away.

**Proposed improvement**: Propose as a UX Improvement — add a confirmation dialog (or an "undo"
affordance) before the destructive `DELETE` call fires.

**Test coverage**: None.

**Notes**: Worth prioritizing higher than a typical cosmetic improvement given TM-12's ownership gap
compounds the blast radius of an accidental click.

## TM-29 — Duplicate `id` attributes in the rendered DOM

**Type**: Bug · **Priority**: P2 · **Area**: UI · **Status**: Open
**Spec reference**: N/A — frontend-only

**Description**: The app renders more than one element with the same `id` in `web/index.html`, which is
invalid HTML (ids must be document-unique) and has real consequences beyond markup validity:
- `id="myModalLabel"` is used on **both** the Add modal's and the Edit modal's
  `<h4 class="modal-title">` — distinct from TM-23's mislabeling: even once the *text* is fixed, the
  duplicate `id` remains invalid, and both modals' `aria-labelledby="myModalLabel"` point at an
  ambiguous target for assistive tech.
- `id="inputTags"` is rendered on **every** tag `<input>` in the Edit modal.
- Related: the "Tags" label in the Edit modal is a `<span for="inputTags">`, not a
  `<label for="inputTags">` — `for` is only meaningful on `<label>`, so that association silently does
  nothing in any browser even before the duplicate-id problem is considered.

**Steps to reproduce**:
1. Open the page and inspect the rendered DOM (`document.querySelector`/`outerHTML`) for both modal
   headers.
2. Open the Edit modal on a task with 2 tags and count `<input id="inputTags">` elements.

**Expected result**: Every `id` in the document is unique.

**Actual result**: Both modal headers share `id="myModalLabel"`; the Edit modal renders 2
`<input id="inputTags">` elements. `document.getElementById`/Selenium `By.ID`/`find_element` (as
opposed to `find_elements`) silently returns only the first match, hiding the rest with no error.

**Root cause**: Static ids in the modal markup; Knockout's `foreach: tags()` repeats the same static
template id once per tag, so a task with N tags renders N elements sharing one id.

**Test coverage**: None (informs `src/ui/locators/` design).

**Suggested fix**: File as a Bug Report — give each modal title its own unique id (e.g.
`addModalLabel`/`editModalLabel`) and each rendered tag input a unique id (e.g. suffixed with the tag's
index), and change the Tags `<span>` to a real `<label>` or drop the stray `for` attribute.

## TM-35 — Status label behaves inconsistently between Done and In Progress

**Type**: Design Issue · **Priority**: P2 · **Area**: UI · **Status**: Open
**Spec reference**: Task attributes — "status" (see also TM-01)

**Current behavior**: Marking a task Done shows a clear "Done" status label, but marking it In Progress
does not give equivalent feedback — the visible effect is that the "Done" label disappears rather than
an "In Progress" status being presented consistently.

**Problem / impact**: The status indicator does not behave symmetrically across the two states, so the
user cannot rely on the label to read a task's status.

**Proposed improvement**: Every status value should have its own label with the same visual treatment
(shape, size, placement, colour contract per state), shown consistently whenever the task is in that
state.

**Test coverage**: None.

**Notes**: Reported during manual testing. Label styling should follow the design system proposed in
**TM-37**.

## TM-36 — Task table is not responsive on small resolutions

**Type**: Design Issue · **Priority**: P2 · **Area**: UI · **Status**: Open
**Spec reference**: N/A — frontend-only

**Current behavior**: The task table has a static layout and does not adapt to the available viewport.

**Problem / impact**: On small resolutions (small laptops, tablets, mobile) the table is not rendered to
fit the screen, so columns and row actions are not displayed according to the space available.

**Proposed improvement**: Make the table responsive (e.g. Bootstrap `.table-responsive` wrapper, column
priority/collapsing, or a card/stacked layout below a breakpoint) and add small resolutions to the
supported UI test matrix (`src/config/`).

**Test coverage**: None.

**Notes**: Reported during manual testing. Distinct from **TM-21** (unbounded row count / no
pagination) — this is about the table's responsiveness to screen size.

## TM-04 — Token-as-username authentication scheme

**Type**: Security (design note — appears intentional, not necessarily a bug) · **Priority**: P3 ·
**Area**: API · **Status**: Open
**Spec reference**: Authentication section

**Current behavior**: Token auth reuses the HTTP Basic Auth username slot to carry the token, with the
password field ignored.

**Problem / impact**: The token travels the same way a username would — Base64 in the `Authorization`
header, not encrypted by Basic Auth itself, only by transport TLS.

**Proposed improvement**: Test TLS enforcement (no plain-HTTP endpoint), confirm arbitrary password
values are indeed accepted alongside a valid token, confirm expired tokens are rejected.

**Test coverage**: None.

**Notes**: Expired-token rejection is covered under **TM-05**.

## TM-16 — `DELETE` response doesn't identify the deleted resource

**Type**: Bug (policy decision, not a literal spec violation) · **Priority**: P3 · **Area**: API ·
**Status**: Open
**Spec reference**: `/<task_id>` DELETE row: "Expected data: N/A, Result: N/A" (the spec explicitly
does not require a response body here)

**Description**: The team has adopted a stricter internal contract for this suite than the spec: every
mutating endpoint (`PUT`, `PATCH`, `DELETE`) should let the caller confirm *which* resource was affected
without a follow-up `GET`.

**Steps to reproduce**:
1. `DELETE /<task_id>` on an existing task.

**Expected result** (team contract): A body identifying the deleted resource, e.g. `{"id": <task_id>}`.

**Actual result**: `200 {}` — an empty body that doesn't echo back the id.

**Root cause**: N/A — the implementation matches the spec, which says `N/A`.

**Test coverage**: `tests/api/test_tasks.py::test_delete_response_includes_deleted_task_id`
(`xfail(strict=True)`).

**Suggested fix**: Propose as an API enhancement (e.g. `{"id": <task_id>}` on success) rather than a
Bug Report against the written spec — flag as a Specification Clarification / improvement suggestion.

## TM-20 — API design: tasks resource has no `/tasks` path, creation uses `PUT` instead of `POST`

**Type**: Design Issue (matches the written spec exactly — not an implementation bug) ·
**Priority**: P3 · **Area**: API · **Status**: Open
**Spec reference**: API table, `/` row: `PUT` → "The created task"

**Current behavior**: Two REST convention deviations, both **specified behavior**:
1. The tasks collection is addressed at the bare root path `/` instead of a resource-named path like
   `/tasks`.
2. Creating a task uses `PUT /` rather than `POST /`.

The client (`web/models.js`) faithfully follows the spec
(`self.ajax(self.tasksURI, 'PUT', task)` where `tasksURI` is exactly the environment's root URL).

**Problem / impact**:
1. Every other resource in this API (`/tags`, `/users`) follows the `/resource` convention, making `/`
   for tasks an outlier.
2. Per REST/HTTP semantics, `PUT` implies an idempotent "create-or-replace-at-this-exact-URI"
   operation, while `POST` is the conventional verb for "create a new resource, server assigns the
   identity/URI" — which is what actually happens here (the server assigns a new sequential id each
   call). Using `PUT` is also awkward combined with **TM-14**: a genuinely idempotent `PUT` shouldn't
   crash on a repeated identical call, but this one does.

**Proposed improvement**: Not a Bug Report (the implementation correctly follows the written spec) —
raise as a Design Improvement for a future API version: add an explicit `/tasks` path and switch
creation to `POST /tasks`, reserving `PUT /tasks/<id>` for true idempotent replace-if-exists semantics.

**Test coverage**: None.

## TM-26 — Date column shows a raw, unformatted ISO-8601 timestamp

**Type**: Design Issue (cosmetic — the data itself is correct, just not human-formatted) ·
**Priority**: P3 · **Area**: UI · **Status**: Open
**Spec reference**: N/A — "Date" isn't even a documented task attribute in the spec's attribute list,
only observed in the live UI/API response

**Current behavior**: The table's Date column renders the task's `date` field completely unformatted:
`<span data-bind="text: date">2026-10-02T02:38:48.226754Z</span>` — every row shows the raw
`YYYY-MM-DDTHH:MM:SS.ffffffZ` string as-is.

**Problem / impact**: A raw ISO-8601 UTC timestamp with microsecond precision is shown instead of a
locale-appropriate, human-readable date/time.

**Proposed improvement**: Format via `toLocaleString()`/a date library instead of binding the raw string
directly.

**Test coverage**: None.

## TM-30 — No stable `id`/`data-testid` attributes on most interactive elements

**Type**: Design Issue (Improvement) · **Priority**: P3 · **Area**: UI · **Status**: Open
**Spec reference**: N/A — frontend-only

**Current behavior**: Almost every interactive element in `web/index.html` (sign-in/out buttons, modal
submit buttons, row Edit/Delete/Mark buttons, status labels, tag chips) carries no `id` or `name` — the
only hooks are Knockout's `data-bind` attribute or Bootstrap's presentational CSS classes
(`glyphicon-pencil`, `label-success`, etc.). Of ~20 interactive elements catalogued, only 3 have a real
`id`/`name` (`btn-add`, navbar `username`/`password` inputs); the rest resolve only through `data-bind`
or class-based XPath.

**Problem / impact**: Neither hook is a safe contract for automation: `data-bind` expressions are
implementation detail (they change if the binding code is refactored, even when the visible behavior
doesn't), and CSS/glyphicon classes are *styling*, not identity (a cosmetic redesign that renames
`glyphicon-pencil` to a different icon class would silently break every locator keyed off it). This is
why `src/ui/locators/task_list_locators.py` has to fall back to XPath expressions matching on
`data-bind`/class content for most elements instead of simple, stable `By.ID`/`By.NAME` lookups (see
the "Web app DOM reference" section in `.github/copilot-instructions.md`).

**Proposed improvement**: Propose as a UX/engineering improvement (not a functional bug) — add a stable,
automation-only attribute (conventionally `data-testid`, ignored by styling and safe to leave in prod)
to every interactive element: sign-in/out buttons, both modals' submit buttons, and each row's
Edit/Delete/Mark-Done/Mark-In-Progress buttons at minimum. Doing so would let every XPath-based locator
in `task_list_locators.py` collapse to a plain attribute-based lookup, simplifying the Page Object layer
and removing its coupling to Knockout binding syntax entirely.

**Test coverage**: None (informs `src/ui/locators/` design).

## TM-37 — No UI design system: buttons have inconsistent size, colour and style

**Type**: Design Issue · **Priority**: P3 · **Area**: Design · **Status**: Open
**Spec reference**: N/A — frontend-only

**Current behavior**: Buttons in the UI do not follow a common visual contract — e.g. the row's Edit
and Delete buttons have different sizes, and there is no consistent mapping of colour/style to action
type across the page.

**Problem / impact**: This points to the absence of a design system (UI style guide / component library
with design tokens): a shared specification for the colour palette per action type (primary, secondary,
destructive, status), component sizes, spacing and typography that the front-end team implements
against.

**Proposed improvement**: Define a design system / UI style guide (design tokens for colours, sizes,
spacing; component specs for buttons, labels, modals, tables) and align all existing components to it.
Once defined, it becomes the baseline for UI visual checks.

**Test coverage**: None.

**Notes**: Reported during manual testing.

## TM-11 — Shared single live instance — test isolation risk

**Type**: Process risk (not an application defect) · **Priority**: — · **Area**: Process ·
**Status**: Resolved
**Spec reference**: N/A — operational

**Risk**: The candidate instance is shared/persistent. `/reset` is destructive and explicitly out of
test scope.

**Observed behavior**: N/A.

**Impact**: Automated tests can collide with data from manual exploration or re-runs (e.g. reusing the
same fixed task titles across runs), and leave created data behind indefinitely since there is no reset
to fall back on.

**Mitigation**: Implemented — the `unique_name` fixture gives every test a collision-safe title/tag, and
the `create_task` fixture (`tests/conftest.py`) tracks and deletes every task it creates during
teardown, using the same auth it was created with (best-effort; a test that already deleted the task
itself just gets a harmless repeat `DELETE`). `/reset` is never called from automated code.

**Notes**: Tags and users have no delete endpoint in the spec, so those are intentionally left behind —
accepted, not an oversight.
