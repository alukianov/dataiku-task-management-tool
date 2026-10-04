"""Tasks resource tests: `GET`/`PUT /` and `GET`/`PATCH`/`DELETE /<task_id>`.

Functional, boundary, state-transition, and idempotency coverage. Authentication/authorization and
cross-user visibility are covered separately in `test_authentication.py`, `test_authorization.py`, and
`tests/ui/test_cross_user_visibility.py`.
"""

import allure
import pytest

from src.api import endpoints
from src.api.resources.tasks import TaskUpdate

NONEXISTENT_TASK_ID = 999999999  # well-formed integer id that will never exist on this instance


@allure.feature("Tasks")
@pytest.mark.api
def test_create_task_returns_created_task(create_task, qa_auth, settings, unique_name, verify_response):
    """Verifies that creating a task with a title and tags returns it with server-assigned defaults."""
    title = unique_name()
    tag = unique_name()
    response = create_task(title, tags=[tag], auth=qa_auth)
    verify_response(
        response,
        200,
        expected_body={
            "title": title,
            "done": False,
            "username": settings.user().username,  # owner = authenticated caller
        },
    )
    body = response.json()
    assert isinstance(body["id"], int), f"expected an integer id, got {body['id']!r} ({type(body['id'])})"
    actual_tags = [t["name"] for t in body["tags"]]
    assert actual_tags == [tag], f"expected tags {[tag]}, got {actual_tags}"


@allure.feature("Tasks")
@pytest.mark.api
def test_get_task_returns_matching_task(create_task, qa_auth, api_client, unique_name, verify_response):
    """Verifies that fetching a task by id (no auth needed) returns the task that was created."""
    title = unique_name()
    created = create_task(title, auth=qa_auth).json()

    response = api_client.tasks.get_task(created["id"])
    verify_response(response, 200, expected_body=created)


@allure.feature("Tasks")
@pytest.mark.api
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-15 (docs/known-defects-and-improvements.md): the 404 body is an empty {} with no 'message' "
    "key - every error response must explain what went wrong. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_get_nonexistent_task_returns_404(api_client, verify_response):
    """Verifies that fetching a well-formed but never-created id returns 404 with an explanatory message."""
    response = api_client.tasks.get_task(NONEXISTENT_TASK_ID)
    # Ideal-behavior placeholder - the real body is currently an empty {} (TM-15), no message yet.
    verify_response(response, 404, expected_message="Task not found")


@allure.feature("Tasks")
@pytest.mark.api
@pytest.mark.boundary
@pytest.mark.parametrize("length", [19, 20])
def test_task_title_within_limit_is_accepted(create_task, qa_auth, unique_name, verify_response, length):
    """Verifies that titles at or under the documented 20-char limit are accepted unmodified."""
    title = unique_name(length)
    response = create_task(title, auth=qa_auth)
    verify_response(response, 200, expected_body={"title": title})


@allure.feature("Tasks")
@pytest.mark.api
@pytest.mark.boundary
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-07 (docs/known-defects-and-improvements.md): a 21-char title is silently accepted instead of "
    "being rejected - the documented 20-char limit is not enforced. Remove xfail once the defect is "
    "fixed.",
    strict=True,
)
def test_task_title_exceeding_limit_is_rejected(create_task, qa_auth, unique_name, verify_response):
    """Verifies that a title over the documented 20-char limit is rejected, not silently accepted."""
    response = create_task(unique_name(21), auth=qa_auth)
    # Ideal-behavior placeholder - a 21-char title is currently silently accepted instead (TM-07).
    verify_response(response, 400, expected_message="Title must be at most 20 characters")


@allure.feature("Tasks")
@pytest.mark.api
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-07 (docs/known-defects-and-improvements.md): an empty-string title is silently accepted "
    "instead of being rejected. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_task_empty_title_is_rejected(create_task, qa_auth, verify_response):
    """Verifies that an empty title is rejected, not silently accepted as a valid task."""
    response = create_task("", auth=qa_auth)
    # Ideal-behavior placeholder - an empty title is currently silently accepted instead (TM-07).
    verify_response(response, 400, expected_message="Title must not be empty")


@allure.feature("Tasks")
@pytest.mark.api
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-14 (docs/known-defects-and-improvements.md): PUT / with the required 'title' field omitted "
    "crashes with 500 instead of a clean 400 (contrast: POST /users validates missing fields "
    "correctly). Remove xfail once the defect is fixed.",
    strict=True,
)
def test_create_task_missing_title_field_is_rejected(api_client, qa_auth, verify_response):
    """Verifies that omitting the required 'title' field is a clean validation error, not a server crash."""
    response = api_client.http.put(endpoints.TASKS, json={"tags": []}, auth=qa_auth)
    # Ideal-behavior placeholder - a missing 'title' key currently crashes with 500 instead (TM-14).
    verify_response(response, 400, expected_message="Title must be provided")


@allure.feature("Tasks")
@pytest.mark.api
def test_task_done_flag_toggles_both_directions(
    create_task, qa_auth, api_client, unique_name, verify_response
):
    """Verifies that PATCH can flip `done` false->true and back to false, returning the updated task."""
    title = unique_name()
    created = create_task(title, auth=qa_auth).json()
    task_id = created["id"]
    assert created["done"] is False, f"expected a newly created task to start not-done, got {created}"

    marked_done = api_client.tasks.update_task(task_id, TaskUpdate(done=True), auth=qa_auth)
    verify_response(marked_done, 200, expected_body={"id": task_id, "title": title, "done": True})

    marked_not_done = api_client.tasks.update_task(task_id, TaskUpdate(done=False), auth=qa_auth)
    verify_response(marked_not_done, 200, expected_body={"id": task_id, "done": False})


@allure.feature("Tasks")
@pytest.mark.api
@pytest.mark.idempotency
def test_patch_same_update_twice_is_idempotent_in_effect(
    create_task, qa_auth, api_client, unique_name, verify_response
):
    """Verifies that applying the exact same PATCH body twice leaves the task in the same end state."""
    created = create_task(unique_name(), auth=qa_auth).json()
    task_id = created["id"]

    first = api_client.tasks.update_task(task_id, TaskUpdate(done=True), auth=qa_auth)
    second = api_client.tasks.update_task(task_id, TaskUpdate(done=True), auth=qa_auth)

    verify_response(first, 200, expected_body={"done": True})
    verify_response(second, 200, expected_body={"done": True})


@allure.feature("Tasks")
@pytest.mark.api
@pytest.mark.idempotency
@pytest.mark.xfail(
    reason="TM-14 (docs/known-defects-and-improvements.md): PUT / is not idempotent by design (two identical "
    "calls create two distinct tasks) - but currently the second call doesn't even succeed, it "
    "crashes with 500 instead of returning 200 with a new id. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_put_duplicate_title_in_quick_succession(create_task, qa_auth, unique_name, verify_response):
    """Verifies that two creates with the identical body both succeed, each creating a distinct task."""
    title = unique_name()
    first = create_task(title, auth=qa_auth)
    second = create_task(title, auth=qa_auth)

    verify_response(first, 200, expected_body={"title": title})
    verify_response(second, 200, expected_body={"title": title})
    first_id = first.json()["id"]
    second_id = second.json()["id"]
    assert (
        first_id != second_id
    ), f"expected two distinct task ids for duplicate creates, both were {first_id}"


@allure.feature("Tasks")
@pytest.mark.api
@pytest.mark.idempotency
def test_delete_is_idempotent_in_effect(create_task, qa_auth, api_client, unique_name, verify_response):
    """Verifies that deleting a task twice leaves it gone both times, even if the status codes differ."""
    created = create_task(unique_name(), auth=qa_auth).json()
    task_id = created["id"]

    first_delete = api_client.tasks.delete_task(task_id, auth=qa_auth)
    verify_response(first_delete, 200)

    second_delete = api_client.tasks.delete_task(task_id, auth=qa_auth)
    # Observed contract: a repeat DELETE returns 400 (not 404, unlike GET's not-found response).
    verify_response(second_delete, 400, expected_message="Task not found")

    gone = api_client.tasks.get_task(task_id)
    verify_response(gone, 404)


@allure.feature("Tasks")
@pytest.mark.api
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-15 (docs/known-defects-and-improvements.md): same empty-body bug as "
    "test_get_nonexistent_task_returns_404, reproduced here via a task that existed and was deleted "
    "rather than one that was never created - the 404 body is still an empty {} with no 'message'. "
    "Remove xfail once the defect is fixed.",
    strict=True,
)
def test_get_deleted_task_returns_404_with_message(
    create_task, qa_auth, api_client, unique_name, verify_response
):
    """Verifies that fetching a deleted task still returns a 404 with an explanatory message, not {}."""
    created = create_task(unique_name(), auth=qa_auth).json()
    api_client.tasks.delete_task(created["id"], auth=qa_auth)

    response = api_client.tasks.get_task(created["id"])
    # Ideal-behavior placeholder - the real body is currently an empty {} (TM-15), no message yet.
    verify_response(response, 404, expected_message="Task not found")


@allure.feature("Tasks")
@pytest.mark.api
@pytest.mark.xfail(
    reason="TM-16 (docs/known-defects-and-improvements.md): DELETE returns an empty body ({}) instead of "
    "identifying which resource was deleted - the spec itself says the result is 'N/A', but the team "
    "has adopted a stricter contract for this suite. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_delete_response_includes_deleted_task_id(
    create_task, qa_auth, api_client, unique_name, verify_response
):
    """Verifies that deleting a task identifies the deleted resource in its response, not an empty body."""
    created = create_task(unique_name(), auth=qa_auth).json()
    task_id = created["id"]

    response = api_client.tasks.delete_task(task_id, auth=qa_auth)
    # Ideal-behavior placeholder - the real body is currently empty {} instead (TM-16).
    verify_response(response, 200, expected_body={"id": task_id})
