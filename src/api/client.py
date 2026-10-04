"""Facade REST client composing all per-resource classes into one object."""

from src.api.base_client import BaseAPIClient
from src.api.resources.auth import Auth
from src.api.resources.system import System
from src.api.resources.tags import Tags
from src.api.resources.tasks import Tasks
from src.api.resources.users import Users
from src.config.settings import settings


class TaskManagementAPIClient:
    """Single entry point exposing every resource as a namespace, bound to one base URL/timeout."""

    def __init__(self, base_url: str = settings.base_url, timeout: int = settings.request_timeout):
        self.http = BaseAPIClient(base_url, timeout)
        self.tasks = Tasks(self.http)
        self.tags = Tags(self.http)
        self.users = Users(self.http)
        self.auth = Auth(self.http)
        self.system = System(self.http)

    @property
    def base_url(self) -> str:
        """Return the base URL every resource action is relative to."""
        return self.http.base_url

    @property
    def timeout(self) -> int:
        """Return the request timeout, in seconds, used by every resource action on this client."""
        return self.http.timeout
