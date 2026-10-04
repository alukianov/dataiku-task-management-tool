"""Users resource: registration against the `/users` endpoint."""

from src.api import endpoints
from src.api.base_client import BaseAPIClient


class Users:
    """Users resource actions, bound to a shared `BaseAPIClient`."""

    def __init__(self, http: BaseAPIClient):
        self.http = http

    def create_user(self, username, password):
        """Create a new user.

        Args:
            username: Username for the new user.
            password: Password for the new user.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self.http.post(endpoints.USERS, json={"username": username, "password": password})
