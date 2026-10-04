"""HTTP client resolving GET/POST/PUT/PATCH/DELETE requests against a base URL."""

import logging

import requests

from src.reporting.allure_logging import log_http_call

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """Thin wrapper around a shared `requests.Session`, binding every verb to a base URL + timeout."""

    def __init__(self, base_url: str, timeout: int):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _request(self, method: str, path: str, **kwargs):
        """Issue an HTTP request and attach the request/response pair to the Allure report.

        Args:
            method: HTTP method, e.g. "GET".
            path: Path to request, relative to the base URL.

        Returns:
            The `requests.Response` returned by the server.
        """
        response = self.session.request(method, self._url(path), timeout=self.timeout, **kwargs)
        logger.debug("%s %s -> %s", method, path, response.status_code)
        log_http_call(response)
        return response

    def get(self, path: str, **kwargs):
        """Issue a GET request.

        Args:
            path: Path to request, relative to the base URL.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        """Issue a POST request.

        Args:
            path: Path to request, relative to the base URL.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs):
        """Issue a PUT request.

        Args:
            path: Path to request, relative to the base URL.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self._request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs):
        """Issue a PATCH request.

        Args:
            path: Path to request, relative to the base URL.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self._request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs):
        """Issue a DELETE request.

        Args:
            path: Path to request, relative to the base URL.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self._request("DELETE", path, **kwargs)
