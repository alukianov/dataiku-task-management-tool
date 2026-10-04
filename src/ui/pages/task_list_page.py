"""Page Object for the task list / management screen."""

import allure

from src.ui import urls
from src.ui.components.add_task_modal_component import AddTaskModalComponent
from src.ui.components.edit_task_modal_component import EditTaskModalComponent
from src.ui.components.navbar_component import NavbarComponent
from src.ui.components.task_table_component import TaskTableComponent
from src.ui.pages.base_page import BasePage


class TaskListPage(BasePage):
    """Page Object for the task list / management screen (web/index.html).

    Composes the `navbar`, `task_table`, `add_modal`, and `edit_modal` Component Objects and exposes
    thin delegating methods for the common case.
    """

    def __init__(self, driver, base_url: str):
        super().__init__(driver, base_url)
        self.navbar = NavbarComponent(driver)
        self.task_table = TaskTableComponent(driver)
        self.add_modal = AddTaskModalComponent(driver)
        self.edit_modal = EditTaskModalComponent(driver)

    @property
    def url(self) -> str:
        """Return the full URL of the task list page for the bound environment."""
        return f"{self.base_url}{urls.TASK_LIST}"

    @allure.step("Open the task list page")
    def load(self) -> "TaskListPage":
        """Navigate to the task list page and wait for the app to finish initial rendering.

        Returns:
            This page object, for chaining.
        """
        self.open(self.url)
        self.navbar.wait_until_rendered(timeout=20)
        return self

    @allure.step("Verify the task list page has loaded")
    def verify_loaded(self) -> None:
        """Assert the task table is present and the navbar brand text rendered."""
        assert self.task_table.is_loaded(), "expected the task table to be loaded"
        brand_text = self.navbar.brand_text()
        assert (
            brand_text == "Dataiku QA Interview"
        ), f"expected navbar brand 'Dataiku QA Interview', got {brand_text!r}"

    def sign_in(self, username: str, password: str) -> None:
        """Fill the navbar sign-in form and submit it.

        Args:
            username: Username to sign in with.
            password: Password to sign in with.
        """
        self.navbar.sign_in(username, password)

    def sign_out(self) -> None:
        """Click the navbar sign-out button."""
        self.navbar.sign_out()

    def is_authenticated(self, timeout: int = BasePage.DEFAULT_TIMEOUT) -> bool:
        """Wait for the navbar to switch to the signed-in state.

        Args:
            timeout: Maximum seconds to wait.

        Returns:
            `True` if the navbar is in the signed-in state.
        """
        return self.navbar.is_authenticated(timeout)

    def verify_authenticated(
        self, expected: bool = True, username: str | None = None, timeout: int = BasePage.DEFAULT_TIMEOUT
    ) -> None:
        """Assert the navbar's signed-in state matches `expected`.

        Args:
            expected: Expected signed-in state.
            username: If given, also assert this username is shown.
            timeout: Maximum seconds to wait.
        """
        self.navbar.verify_authenticated(expected, username, timeout)

    def verify_warning(self, expected_message: str, expected_status: str = "401") -> None:
        """Assert a warning banner is visible with the given message and status.

        Args:
            expected_message: Expected banner message text.
            expected_status: Expected banner HTTP status text.
        """
        self.navbar.verify_warning(expected_message, expected_status)

    def has_task(self, title: str, timeout: int = BasePage.DEFAULT_TIMEOUT) -> bool:
        """Wait for a task row matching `title` to render.

        Args:
            title: Task title to look for.
            timeout: Maximum seconds to wait.

        Returns:
            `True` if a matching row rendered.
        """
        return self.task_table.has_task(title, timeout)

    def verify_task_visible(self, title: str, owner: str | None = None) -> None:
        """Assert a task matching `title` is visible.

        Args:
            title: Task title to look for.
            owner: If given, also assert the row's owner matches.
        """
        self.task_table.verify_task_visible(title, owner)

    def verify_done(self, title: str) -> None:
        """Assert the row matching `title` shows Done.

        Args:
            title: Task title to look for.
        """
        self.task_table.verify_done(title)

    def verify_in_progress(self, title: str) -> None:
        """Assert the row matching `title` shows In Progress.

        Args:
            title: Task title to look for.
        """
        self.task_table.verify_in_progress(title)

    def verify_tags(self, title: str, expected_tags: list[str]) -> None:
        """Assert the row matching `title` shows exactly `expected_tags`.

        Args:
            title: Task title to look for.
            expected_tags: Tag names expected to be displayed, in order.
        """
        self.task_table.verify_tags(title, expected_tags)

    def verify_authorized_actions(self, title: str, *, can_edit: bool, can_delete: bool) -> None:
        """Assert the row matching `title` shows or hides its Edit/Delete buttons as expected.

        Args:
            title: Task title to look for.
            can_edit: Whether the Edit button is expected to be visible.
            can_delete: Whether the Delete button is expected to be visible.
        """
        self.task_table.verify_authorized_actions(title, can_edit=can_edit, can_delete=can_delete)

    def is_done(self, title: str) -> bool:
        """Check whether the row matching `title` shows Done.

        Args:
            title: Task title to look for.

        Returns:
            `True` if the row shows Done.
        """
        return self.task_table.is_done(title)

    def delete_task(self, title: str) -> None:
        """Delete the row matching `title`.

        Args:
            title: Task title to delete.
        """
        self.task_table.delete_task(title)

    def mark_done(self, title: str) -> None:
        """Mark the row matching `title` done.

        Args:
            title: Task title to mark done.
        """
        self.task_table.mark_done(title)

    def mark_in_progress(self, title: str) -> None:
        """Mark the row matching `title` in progress.

        Args:
            title: Task title to mark in progress.
        """
        self.task_table.mark_in_progress(title)

    def add_task(self, title: str, tags: list[str] | None = None) -> None:
        """Add a task via the Add Task modal.

        Args:
            title: Title of the task to create.
            tags: Tag names to assign to the task.
        """
        self.add_modal.add(title, tags)

    @allure.step("Edit task '{current_title}' title to '{new_title}'")
    def edit_task_title(self, current_title: str, new_title: str) -> None:
        """Open the row matching `current_title` for editing and save it with `new_title`.

        Args:
            current_title: Title of the task to edit.
            new_title: New title to save.
        """
        self.task_table.begin_edit(current_title)
        self.edit_modal.save_title(new_title)
