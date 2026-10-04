"""Tags resource: list/get against the `/tags` and `/tags/<tag_id>` endpoints."""

from src.api import endpoints
from src.api.base_client import BaseAPIClient


class Tags:
    """Tags resource actions, bound to a shared `BaseAPIClient`."""

    def __init__(self, http: BaseAPIClient):
        self.http = http

    def list_tags(self):
        """List all existing tags.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self.http.get(endpoints.TAGS)

    def get_tag(self, tag_id):
        """Fetch a single tag.

        Args:
            tag_id: ID of the tag to fetch.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self.http.get(endpoints.build_path(endpoints.TAG, tag_id=tag_id))
