"""Authentication helpers for the task management REST API."""

from requests.auth import HTTPBasicAuth


def basic_auth(username: str, password: str) -> HTTPBasicAuth:
    """Build HTTP Basic auth credentials.

    Args:
        username: Username to authenticate with.
        password: Password to authenticate with.

    Returns:
        The resulting `HTTPBasicAuth` object.
    """
    return HTTPBasicAuth(username, password)


def token_auth(token: str) -> HTTPBasicAuth:
    """Build token auth, with the token passed as the Basic Auth username.

    Args:
        token: Token to authenticate with.

    Returns:
        The resulting `HTTPBasicAuth` object.
    """
    return HTTPBasicAuth(token, "unused")
