"""Component Object for the task table: rows, their status, and per-row action buttons."""

import allure

from src.ui.locators import task_list_locators as locators
from src.ui.pages.base_page import BaseComponent


class TaskTableComponent(BaseComponent):
    """The task table itself - row lookup, status queries, and per-row Edit/Delete/Mark buttons."""

    def is_loaded(self) -> bool:
        """Check whether the task table is present in the DOM.

        Returns:
            `True` if the table is present.
        """
        return len(self.driver.find_elements(*locators.TASK_TABLE)) > 0

    def has_task(self, title: str, timeout: int = BaseComponent.DEFAULT_TIMEOUT) -> bool:
        """Wait for a task row matching `title` to render.

        Args:
            title: Task title to look for.
            timeout: Maximum seconds to wait.

        Returns:
            `True` if a matching row rendered.
        """
        # Checks for the real <tr> row, not a page_source substring, since a still-open modal's
        # input can contain the typed text even when the task was never actually submitted.
        return self.is_present(locators.row_by_title(title), timeout)

    def _row(self, title: str, timeout: int = BaseComponent.DEFAULT_TIMEOUT):
        """Find the row matching `title`, waiting for it to render first.

        Args:
            title: Task title to look for.
            timeout: Maximum seconds to wait.

        Returns:
            The matching row `WebElement`.
        """
        self.has_task(title, timeout)
        return self.driver.find_element(*locators.row_by_title(title))

    @allure.step("Begin editing task '{title}'")
    def begin_edit(self, title: str) -> None:
        """Click the row's Edit button, opening the Edit modal.

        Args:
            title: Task title to edit.
        """
        self._row(title).find_element(*locators.ROW_EDIT_BUTTON).click()

    @allure.step("Delete task '{title}'")
    def delete_task(self, title: str) -> None:
        """Click the Delete button on the row matching `title` and wait for it to disappear.

        Args:
            title: Task title to delete.
        """
        self._row(title).find_element(*locators.ROW_DELETE_BUTTON).click()
        self.wait_invisible(locators.row_by_title(title))

    @allure.step("Click Mark Done for task '{title}'")
    def click_mark_done(self, title: str) -> None:
        """Click the Mark Done button, without waiting for the row to flip to Done.

        Args:
            title: Task title to mark done.
        """
        # Use this instead of mark_done() when the click is expected to fail server-side -
        # mark_done()'s wait for the Done flip would otherwise time out.
        self._row(title).find_element(*locators.ROW_MARK_DONE_BUTTON).click()

    @allure.step("Mark task '{title}' done")
    def mark_done(self, title: str) -> None:
        """Click the Mark Done button and wait for the row's status label to flip to Done.

        Args:
            title: Task title to mark done.
        """
        self.click_mark_done(title)
        self.wait().until(lambda _driver: self.is_done(title))

    @allure.step("Mark task '{title}' in progress")
    def mark_in_progress(self, title: str) -> None:
        """Click the Mark In Progress button and wait for the row's status label to flip off Done.

        Args:
            title: Task title to mark in progress.
        """
        self._row(title).find_element(*locators.ROW_MARK_IN_PROGRESS_BUTTON).click()
        self.wait().until(lambda _driver: not self.is_done(title))

    def is_done(self, title: str) -> bool:
        """Check whether the row matching `title` shows the Done label.

        Args:
            title: Task title to look for.

        Returns:
            `True` if the row shows Done.
        """
        return self.is_visible_within(self._row(title), locators.ROW_DONE_LABEL)

    def wait_until_done(self, title: str, expected: bool, timeout: int = 5) -> None:
        """Wait for the row matching `title`'s Done state to reach `expected`.

        Args:
            title: Task title to look for.
            expected: Expected Done state.
            timeout: Maximum seconds to wait.
        """
        self.wait(timeout).until(lambda _driver: self.is_done(title) == expected)

    def tags(self, title: str) -> list[str]:
        """Return the currently displayed tag names for the row matching `title`.

        Args:
            title: Task title to look for.

        Returns:
            Tag names in rendered order.
        """
        return [tag.text for tag in self._row(title).find_elements(*locators.ROW_TAGS)]

    def owner(self, title: str) -> str:
        """Return the displayed owner for the row matching `title`.

        Args:
            title: Task title to look for.

        Returns:
            The displayed owner username.
        """
        return self.get_text_within(self._row(title), locators.ROW_OWNER)

    @allure.step("Verify task '{title}' is visible (owner={owner})")
    def verify_task_visible(self, title: str, owner: str | None = None) -> None:
        """Assert a task matching `title` is visible.

        Args:
            title: Task title to look for.
            owner: If given, also assert the row's Owner column matches.
        """
        assert self.has_task(title), f"expected task '{title}' to be visible"
        if owner is not None:
            actual_owner = self.owner(title)
            assert (
                actual_owner == owner
            ), f"expected task '{title}' to be owned by {owner!r}, got {actual_owner!r}"

    @allure.step("Verify task '{title}' is Done")
    def verify_done(self, title: str) -> None:
        """Assert the row matching `title` currently shows the Done label.

        Args:
            title: Task title to look for.
        """
        assert self.is_done(title), f"expected task '{title}' to show Done"

    @allure.step("Verify task '{title}' is In Progress")
    def verify_in_progress(self, title: str) -> None:
        """Assert the row matching `title` currently shows the In Progress label.

        Args:
            title: Task title to look for.
        """
        assert not self.is_done(title), f"expected task '{title}' to show In Progress"

    @allure.step("Verify task '{title}' tags are {expected_tags}")
    def verify_tags(self, title: str, expected_tags: list[str]) -> None:
        """Assert the row matching `title` currently displays exactly `expected_tags`.

        Args:
            title: Task title to look for.
            expected_tags: Tag names expected to be displayed, in order.
        """
        actual_tags = self.tags(title)
        assert (
            actual_tags == expected_tags
        ), f"expected task '{title}' tags to be {expected_tags}, got {actual_tags}"

    def has_edit_button(self, title: str) -> bool:
        """Check whether the row matching `title` renders a visible Edit button.

        Args:
            title: Task title to look for.

        Returns:
            `True` if the Edit button is visible.
        """
        return self.is_visible_within(self._row(title), locators.ROW_EDIT_BUTTON)

    def has_delete_button(self, title: str) -> bool:
        """Check whether the row matching `title` renders a visible Delete button.

        Args:
            title: Task title to look for.

        Returns:
            `True` if the Delete button is visible.
        """
        return self.is_visible_within(self._row(title), locators.ROW_DELETE_BUTTON)

    @allure.step("Verify task '{title}' authorized actions: edit={can_edit}, delete={can_delete}")
    def verify_authorized_actions(self, title: str, *, can_edit: bool, can_delete: bool) -> None:
        """Assert the row matching `title` shows or hides its Edit/Delete buttons as expected.

        Args:
            title: Task title to look for.
            can_edit: Whether the Edit button is expected to be visible.
            can_delete: Whether the Delete button is expected to be visible.
        """
        edit_visible = self.has_edit_button(title)
        assert (
            edit_visible == can_edit
        ), f"expected task '{title}' Edit button visible={can_edit}, got visible={edit_visible}"
        delete_visible = self.has_delete_button(title)
        assert (
            delete_visible == can_delete
        ), f"expected task '{title}' Delete button visible={can_delete}, got visible={delete_visible}"
