"""Tasks resource: list/get/create/update/delete against the `/` and `/<task_id>` endpoints."""

from dataclasses import dataclass

from src.api import endpoints
from src.api.base_client import BaseAPIClient


@dataclass
class TaskUpdate:
    """Fields accepted by PATCH /<task_id>; only fields that are not None are sent."""

    title: str | None = None
    tags: list[str] | None = None
    done: bool | None = None


class Tasks:
    """Tasks resource actions, bound to a shared `BaseAPIClient`."""

    def __init__(self, http: BaseAPIClient):
        self.http = http

    def list_tasks(self):
        """List all existing tasks.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self.http.get(endpoints.TASKS)

    def get_task(self, task_id):
        """Fetch a single task.

        Args:
            task_id: ID of the task to fetch.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self.http.get(endpoints.build_path(endpoints.TASK, task_id=task_id))

    def create_task(self, title, tags=None, auth=None):
        """Create a task owned by the authenticated caller.

        Args:
            title: Title of the task to create.
            tags: Tag names to assign to the task.
            auth: Auth object to send with the request.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self.http.put(endpoints.TASKS, json={"title": title, "tags": tags or []}, auth=auth)

    def update_task(self, task_id, update: TaskUpdate = None, auth=None):
        """Update a task's title, tags, and/or done state.

        Args:
            task_id: ID of the task to update.
            update: Fields to update; only non-`None` fields are sent.
            auth: Auth object to send with the request.

        Returns:
            The `requests.Response` returned by the server.
        """
        update = update or TaskUpdate()
        payload = {}
        if update.title is not None:
            payload["title"] = update.title
        if update.tags is not None:
            payload["tags"] = update.tags
        if update.done is not None:
            payload["done"] = update.done
        return self.http.patch(endpoints.build_path(endpoints.TASK, task_id=task_id), json=payload, auth=auth)

    def delete_task(self, task_id, auth=None):
        """Delete a task.

        Args:
            task_id: ID of the task to delete.
            auth: Auth object to send with the request.

        Returns:
            The `requests.Response` returned by the server.
        """
        return self.http.delete(endpoints.build_path(endpoints.TASK, task_id=task_id), auth=auth)
