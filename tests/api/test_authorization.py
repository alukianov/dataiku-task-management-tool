"""Authorization tests: ownership enforcement on mutating endpoints (PATCH/DELETE)."""

import allure
import pytest

from src.api.resources.tasks import TaskUpdate


@allure.feature("Authorization")
@pytest.mark.api
@pytest.mark.auth
def test_non_owner_cannot_patch_task(api_client, qa_auth, other_users_task, verify_response):
    """Verifies that a non-owner PATCH is rejected with 403 and the task is left unmodified."""
    created, title = other_users_task()

    response = api_client.tasks.update_task(created["id"], TaskUpdate(title="Hijacked"), auth=qa_auth)
    verify_response(response, 403, expected_message="You're not the owner of this task")

    unchanged = api_client.tasks.get_task(created["id"]).json()
    assert unchanged["title"] == title, (
        f"expected the task title to stay {title!r} after a rejected non-owner PATCH, got "
        f"{unchanged['title']!r}"
    )


@allure.feature("Authorization")
@pytest.mark.api
@pytest.mark.auth
@pytest.mark.xfail(
    reason="TM-12 (docs/known-defects-and-improvements.md): DELETE does not enforce task ownership - a "
    "non-owner currently gets 200 instead of 403. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_non_owner_cannot_delete_task(api_client, qa_auth, other_users_task, verify_response):
    """Verifies that a non-owner DELETE is rejected, per the spec's ownership requirement."""
    created, _ = other_users_task()

    response = api_client.tasks.delete_task(created["id"], auth=qa_auth)
    # Ideal-behavior placeholder (mirrors the PATCH contract) - the real message is unconfirmed since
    # DELETE never actually enforces ownership yet (TM-12); only reached once the defect is fixed.
    verify_response(response, 403, expected_message="You're not the owner of this task")


@allure.feature("Authorization")
@pytest.mark.api
@pytest.mark.auth
def test_non_owner_cannot_patch_task_via_token_auth(
    api_client, qa_token_auth, other_users_task, verify_response
):
    """Verifies that ownership enforcement on PATCH holds regardless of the auth scheme used."""
    created, title = other_users_task()

    response = api_client.tasks.update_task(created["id"], TaskUpdate(title="Hijacked"), auth=qa_token_auth)
    verify_response(response, 403, expected_message="You're not the owner of this task")

    unchanged = api_client.tasks.get_task(created["id"]).json()
    assert unchanged["title"] == title, (
        f"expected the task title to stay {title!r} after a rejected non-owner PATCH (token auth), got "
        f"{unchanged['title']!r}"
    )


@allure.feature("Authorization")
@pytest.mark.api
@pytest.mark.auth
@pytest.mark.xfail(
    reason="TM-12 (docs/known-defects-and-improvements.md): DELETE does not enforce task ownership, "
    "reproduced here via token auth too - the bug is in the ownership check, not auth-scheme-specific. "
    "Remove xfail once the defect is fixed.",
    strict=True,
)
def test_non_owner_cannot_delete_task_via_token_auth(
    api_client, qa_token_auth, other_users_task, verify_response
):
    """Verifies that ownership enforcement on DELETE holds regardless of the auth scheme used."""
    created, _ = other_users_task()

    response = api_client.tasks.delete_task(created["id"], auth=qa_token_auth)
    # Ideal-behavior placeholder - see test_non_owner_cannot_delete_task above.
    verify_response(response, 403, expected_message="You're not the owner of this task")
