"""UI authentication tests: navbar sign-in/sign-out and warning-banner behavior."""

import allure
import pytest


@allure.feature("Authentication")
@pytest.mark.ui
@pytest.mark.auth
def test_sign_in_with_valid_credentials_shows_signed_in_state(task_list_page, settings):
    """Verifies that signing in with valid credentials switches the navbar to the signed-in state."""
    user = settings.user()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.verify_authenticated(username=user.username)


@allure.feature("Authentication")
@pytest.mark.ui
@pytest.mark.auth
@pytest.mark.negative
def test_sign_in_with_wrong_password_shows_warning(task_list_page, settings):
    """Verifies that signing in with a wrong password shows the warning banner and stays signed out."""
    user = settings.user()
    page = task_list_page.load()
    page.sign_in(user.username, f"not-{user.password}")
    page.verify_warning("Your login is invalid or session has expired")
    page.verify_authenticated(False)


@allure.feature("Authentication")
@pytest.mark.ui
@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-17 (docs/known-defects-and-improvements.md): each failed sign-in clones every currently-"
    "visible .alert-warning banner instead of just the hidden template, so the count grows "
    "exponentially (2^n - 1) rather than staying at one. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_repeated_failed_sign_in_does_not_stack_duplicate_warnings(task_list_page, settings):
    """Verifies that two consecutive failed sign-ins still show exactly one warning banner."""
    user = settings.user()
    page = task_list_page.load()
    page.sign_in(user.username, f"not-{user.password}")
    page.sign_in(user.username, f"not-{user.password}")
    actual_count = page.navbar.warning_alert_count()
    assert (
        actual_count == 1
    ), f"expected exactly one warning banner after two failed sign-ins, got {actual_count}"


@allure.feature("Authentication")
@pytest.mark.ui
@pytest.mark.auth
def test_sign_out_hides_authenticated_controls(task_list_page, settings):
    """Verifies that signing out switches the navbar back to the signed-out form."""
    user = settings.user()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.verify_authenticated()

    page.sign_out()
    page.verify_authenticated(False)


@allure.feature("Authentication")
@pytest.mark.ui
@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-22 (docs/known-defects-and-improvements.md): logout() only clears the auth cookies, it never "
    "resets the navbar's username/password input values, leaving the previous credentials visible "
    "in the DOM after sign-out. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_sign_out_clears_credential_inputs(task_list_page, settings):
    """Verifies that signing out clears the username/password inputs, not just the signed-in state."""
    user = settings.user()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.verify_authenticated()

    page.sign_out()
    page.verify_authenticated(False)

    assert (
        page.navbar.credential_inputs_are_empty()
    ), "expected the username/password inputs to be cleared after sign-out"


@allure.feature("Authentication")
@pytest.mark.ui
@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-33 (docs/known-defects-and-improvements.md): an invalid/expired auth cookie on PUT / "
    "crashes with 500 instead of 401, so the client shows the generic .alert-danger banner instead "
    "of the .alert-warning session-expired message. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_expired_session_shows_warning_during_action(driver, signed_in_page, settings, unique_name):
    """Verifies that an action taken with an invalid/expired session shows the same 401 warning."""
    user = settings.user()
    title = unique_name()
    page = signed_in_page
    page.add_task(title)
    assert not page.is_done(title), f"expected newly added task '{title}' to start In Progress, not Done"

    # Simulate an expired/invalid session by corrupting the token cookie the app sends as Basic auth.
    # Selenium's add_cookie()/delete_cookie() don't reliably override this app's own cookie (likely a
    # domain-attribute mismatch with how web/models.js's setCookie() writes it) - set it exactly the
    # same way the app itself does instead: `document.cookie = "token=...;path=/"`.
    driver.execute_script("document.cookie = 'token=deliberately-invalid-token;path=/';")

    page.task_table.click_mark_done(title)

    try:
        page.verify_warning("Your login is invalid or session has expired")
        assert not page.is_done(
            title
        ), f"expected the rejected PATCH to leave task '{title}' In Progress, not Done"
    finally:
        # The app's own error handler deletes the (now-invalid) cookies and flips back to signed-out -
        # sign back in with the real credentials to clean up the task afterward.
        page.sign_in(user.username, user.password)
        page.delete_task(title)
