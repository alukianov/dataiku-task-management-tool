"""System resource: the test-data reset endpoint."""

from src.api import endpoints
from src.api.base_client import BaseAPIClient


class System:
    """System resource actions, bound to a shared `BaseAPIClient`."""

    def __init__(self, http: BaseAPIClient):
        self.http = http

    def reset(self):
        """Wipe all data on the instance.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self.http.get(endpoints.RESET)
