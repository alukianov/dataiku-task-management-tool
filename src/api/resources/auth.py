"""Auth resource: token issuance against the `/authenticate` endpoint."""

from src.api import endpoints
from src.api.base_client import BaseAPIClient


class Auth:
    """Auth resource actions, bound to a shared `BaseAPIClient`."""

    def __init__(self, http: BaseAPIClient):
        self.http = http

    def authenticate(self, username, password):
        """Exchange credentials for a token.

        Args:
            username: Username to authenticate with.
            password: Password to authenticate with.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self.http.post(endpoints.AUTHENTICATE, json={"username": username, "password": password})
