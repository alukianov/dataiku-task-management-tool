"""Users resource tests: `POST /users`."""

import allure
import pytest

from src.api import endpoints


@allure.feature("Users")
@pytest.mark.api
def test_register_user_succeeds(api_client, unique_name, verify_response):
    """Verifies that registering a user with a fresh username/password succeeds."""
    username = f"qa_{unique_name()}"
    response = api_client.users.create_user(username, unique_name())
    verify_response(response, 200, expected_body={"username": username})


@allure.feature("Users")
@pytest.mark.api
@pytest.mark.security
def test_register_user_response_does_not_echo_password(api_client, unique_name, verify_response):
    """Verifies that the response body never reflects the submitted password back to the caller."""
    username = f"qa_{unique_name()}"
    password = unique_name()
    response = api_client.users.create_user(username, password)
    verify_response(response, 200)
    assert (
        "password" not in response.json()
    ), f"expected no 'password' key in response body, got {response.json()}"
    assert (
        password not in response.text
    ), "expected the submitted password to never be echoed back in the response body"


@allure.feature("Users")
@pytest.mark.api
@pytest.mark.negative
def test_register_user_missing_password_is_rejected(api_client, unique_name, verify_response):
    """Verifies that registering with no 'password' key is a clean validation error."""
    response = api_client.http.post(endpoints.USERS, json={"username": f"qa_{unique_name()}"})
    verify_response(response, 400, expected_message="Username and password must be provided")


@allure.feature("Users")
@pytest.mark.api
@pytest.mark.negative
def test_register_user_missing_username_is_rejected(api_client, verify_response):
    """Verifies that registering with no 'username' key is a clean validation error."""
    response = api_client.http.post(endpoints.USERS, json={"password": "x"})
    verify_response(response, 400, expected_message="Username and password must be provided")


@allure.feature("Users")
@pytest.mark.api
@pytest.mark.negative
@pytest.mark.idempotency
@pytest.mark.xfail(
    reason="TM-09 (docs/known-defects-and-improvements.md): re-registering an existing username crashes with "
    "500 instead of a clean 400/409. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_register_duplicate_username_is_rejected_cleanly(api_client, unique_name, verify_response):
    """Verifies that registering an already-taken username twice is a clean 4xx, not a server crash."""
    username = f"qa_{unique_name()}"
    first = api_client.users.create_user(username, unique_name())
    verify_response(first, 200, expected_body={"username": username})

    second = api_client.users.create_user(username, unique_name())
    # Ideal-behavior placeholder - the second call currently crashes with 500 instead (TM-09).
    verify_response(second, (400, 409), expected_message="Username already exists")


@allure.feature("Users")
@pytest.mark.api
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-28 (docs/known-defects-and-improvements.md): POST /users crashes with 500 whenever the "
    "submitted password matches an already-registered user's password, regardless of username. "
    "Remove xfail once the defect is fixed.",
    strict=True,
)
def test_register_user_with_password_matching_existing_user_is_rejected_cleanly(
    api_client, unique_name, settings
):
    """Verifies that reusing another user's password on a new username is a clean 4xx, not a server crash."""
    existing_password = settings.user().password
    username = f"qa_{unique_name()}"

    response = api_client.users.create_user(username, existing_password)
    assert response.status_code in (200, 400, 409), (
        f"expected a clean 200/400/409 for a reused password, got {response.status_code} "
        f"(body: {response.text})"
    )
    if response.status_code != 200:
        assert response.json().get(
            "message"
        ), f"expected a non-empty error message on a {response.status_code} response, got {response.json()}"
