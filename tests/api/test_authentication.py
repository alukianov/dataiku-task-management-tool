"""Authentication tests: both documented auth schemes (Basic, token-as-username) and their rejection
paths, plus parity checks confirming ownership enforcement does not depend on which scheme was used.
"""

import base64
import json

import allure
import pytest
from requests.auth import HTTPBasicAuth

from src.api.auth import token_auth


def _b64url_decode(segment: str) -> bytes:
    """Decode a base64url-encoded JWT segment.

    Args:
        segment: Base64url-encoded segment, without padding.

    Returns:
        The decoded bytes.
    """
    return base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4))


def _b64url_encode(data: bytes) -> str:
    """Encode bytes as an unpadded base64url JWT segment.

    Args:
        data: Bytes to encode.

    Returns:
        The base64url-encoded segment, without padding.
    """
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


# A real, server-issued JWT (HS256), captured once via /authenticate, past its 10-minute TTL. The
# `exp` claim is an absolute Unix timestamp, so it stays rejected regardless of when tests run.
EXPIRED_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsImV4cCI6MTc5MDg2NzMxNSwiaWF0IjoxNzkwODY2NzE1fQ."
    "eyJpZCI6MX0.h0SKFtFo8xJGKB60ryEaIvsXoVUWMTb9idszrcxUtGU"
)


@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
def test_authenticate_with_valid_credentials_returns_token(api_client, settings, verify_response):
    """Verifies that authenticating with correct credentials returns a token and the documented TTL."""
    user = settings.user()
    response = api_client.auth.authenticate(user.username, user.password)
    verify_response(response, 200, expected_body={"expires": 600})  # 600s = "10 minutes" per the spec
    assert response.json()["token"], "expected a non-empty token in the /authenticate response body"


@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
@pytest.mark.negative
def test_authenticate_with_wrong_password_is_rejected(api_client, settings, verify_response):
    """Verifies that authenticating with a wrong password is rejected, not silently given a token."""
    user = settings.user()
    response = api_client.auth.authenticate(user.username, f"not-{user.password}")
    verify_response(response, 401, expected_message="Bad authentication")


@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
def test_basic_auth_allows_task_creation(create_task, qa_auth, unique_name, verify_response):
    """Verifies that Basic auth is accepted on a protected endpoint."""
    title = unique_name()
    response = create_task(title, auth=qa_auth)
    verify_response(response, 200, expected_body={"title": title, "done": False})


@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
def test_token_auth_allows_task_creation(create_task, qa_token_auth, unique_name, verify_response):
    """Verifies that token auth (token-as-username) is accepted on a protected endpoint."""
    title = unique_name()
    response = create_task(title, auth=qa_token_auth)
    verify_response(response, 200, expected_body={"title": title, "done": False})


@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
def test_token_auth_ignores_password_value(create_task, api_client, settings, unique_name, verify_response):
    """Verifies that token auth succeeds regardless of the password value sent alongside the token."""
    user = settings.user()
    token = api_client.auth.authenticate(user.username, user.password).json()["token"]

    title_one = unique_name()
    title_two = unique_name()
    first = create_task(title_one, auth=HTTPBasicAuth(token, "any-value-1"))
    second = create_task(title_two, auth=HTTPBasicAuth(token, "a-totally-different-value"))

    verify_response(first, 200, expected_body={"title": title_one, "done": False})
    verify_response(second, 200, expected_body={"title": title_two, "done": False})


@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
@pytest.mark.negative
def test_invalid_token_is_rejected(create_task, verify_response):
    """Verifies that a garbage/never-issued token is rejected on a protected endpoint."""
    response = create_task("InvalidTokenCreate", auth=token_auth("not-a-real-token-12345"))
    verify_response(response, 401)


@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
@pytest.mark.negative
def test_basic_auth_with_wrong_password_is_rejected(create_task, settings, verify_response):
    """Verifies that Basic auth with a wrong password is rejected on a protected endpoint."""
    user = settings.user()
    response = create_task("WrongPasswordCreate", auth=HTTPBasicAuth(user.username, f"not-{user.password}"))
    verify_response(response, 401)


@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
@pytest.mark.negative
def test_missing_auth_is_rejected_on_protected_endpoint(create_task, verify_response):
    """Verifies that no auth at all on a protected endpoint is rejected, not silently defaulted."""
    response = create_task("NoAuthCreate", auth=None)
    verify_response(response, 401)


@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
def test_expired_token_is_rejected(create_task, verify_response):
    """Verifies that an expired token is rejected, not silently honored."""
    response = create_task("ExpiredTokenCreate", auth=token_auth(EXPIRED_TOKEN))
    verify_response(response, 401)


@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
@pytest.mark.security
def test_forged_token_with_tampered_exp_is_rejected(create_task, api_client, settings, verify_response):
    """Verifies that a token with a tampered or stripped signature is rejected, not silently honored."""
    user = settings.user()
    token = api_client.auth.authenticate(user.username, user.password).json()["token"]
    header_b64, payload_b64, _signature_b64 = token.split(".")
    header = json.loads(_b64url_decode(header_b64))

    tampered_header = {**header, "exp": 1}  # far in the past
    tampered_header_b64 = _b64url_encode(json.dumps(tampered_header, separators=(",", ":")).encode())

    none_alg_header = {**tampered_header, "alg": "none"}
    none_alg_header_b64 = _b64url_encode(json.dumps(none_alg_header, separators=(",", ":")).encode())

    forged_tokens = [
        f"{tampered_header_b64}.{payload_b64}.{_signature_b64}",  # tampered exp, stale signature
        f"{none_alg_header_b64}.{payload_b64}.",  # alg=none, empty signature segment
        f"{none_alg_header_b64}.{payload_b64}",  # alg=none, signature segment removed entirely
    ]
    for forged_token in forged_tokens:
        response = create_task("ForgedTokenCreate", auth=token_auth(forged_token))
        verify_response(response, 401)


@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
@pytest.mark.security
def test_unknown_username_and_wrong_password_return_identical_error(api_client, settings, unique_name):
    """Verifies that an unknown username fails the same way as a wrong password, preventing enumeration."""
    user = settings.user()
    wrong_password = api_client.auth.authenticate(user.username, f"not-{user.password}")
    unknown_username = api_client.auth.authenticate(f"nonexistent-{unique_name()}", "whatever")

    # A distinct error for either case would be a username enumeration vulnerability
    # (OWASP API2:2023 Broken Authentication / CWE-203).
    assert wrong_password.status_code == unknown_username.status_code == 401, (
        f"expected both wrong-password and unknown-username to return 401, got "
        f"{wrong_password.status_code} and {unknown_username.status_code}"
    )
    assert wrong_password.json() == unknown_username.json(), (
        f"expected identical error bodies to avoid username enumeration, got "
        f"{wrong_password.json()} vs {unknown_username.json()}"
    )


@allure.feature("Authentication")
@pytest.mark.api
@pytest.mark.auth
@pytest.mark.idempotency
@pytest.mark.xfail(
    reason="TM-34 (docs/known-defects-and-improvements.md): repeated /authenticate calls mint a fresh token "
    "per call and token reuse is unspecified. Remove xfail once the contract is clarified.",
    # Non-strict: calls landing in the same second return identical tokens, so this can XPASS.
    strict=False,
)
def test_repeated_authenticate_returns_the_same_token(api_client, settings):
    """Verifies that calling authenticate twice in a row with the same credentials returns the same token."""
    user = settings.user()
    first = api_client.auth.authenticate(user.username, user.password)
    second = api_client.auth.authenticate(user.username, user.password)

    assert (
        first.status_code == 200
    ), f"expected first /authenticate call to return 200, got {first.status_code}"
    assert (
        second.status_code == 200
    ), f"expected second /authenticate call to return 200, got {second.status_code}"
    first_token = first.json()["token"]
    second_token = second.json()["token"]
    assert (
        first_token == second_token
    ), f"expected the same token on repeated authenticate calls, got {first_token!r} then {second_token!r}"
