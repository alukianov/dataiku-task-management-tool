"""UI authorization tests: cross-user task visibility and client-side ownership gating."""

import allure
import pytest


@allure.feature("Authorization")
@pytest.mark.ui
@pytest.mark.auth
def test_other_users_task_is_visible_in_shared_list(make_user_auth, create_task, task_list_page, unique_name):
    """Verifies that a task created by a different user still appears in the list, with its owner shown."""
    other_auth = make_user_auth()
    title = unique_name()
    created = create_task(title, auth=other_auth).json()

    page = task_list_page.load()
    page.verify_loaded()
    page.verify_task_visible(title, owner=created["username"])


@allure.feature("Authorization")
@pytest.mark.ui
@pytest.mark.auth
def test_non_owner_cannot_see_edit_or_delete_buttons(
    task_list_page, settings, make_user_auth, create_task, unique_name
):
    """Verifies that a signed-in non-owner sees no Edit/Delete/Mark buttons on another user's task."""
    other_auth = make_user_auth()
    other_title = unique_name()
    create_task(other_title, auth=other_auth)

    own_title = unique_name()
    user = settings.user()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.add_task(own_title)

    page.verify_task_visible(other_title)
    page.verify_authorized_actions(other_title, can_edit=False, can_delete=False)
    page.verify_authorized_actions(own_title, can_edit=True, can_delete=True)

    page.delete_task(own_title)
