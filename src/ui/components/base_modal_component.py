"""Shared base for Bootstrap modal Component Objects (Add/Edit task modals)."""

import allure

from src.ui.pages.base_page import BaseComponent


class BaseModalComponent(BaseComponent):
    """A modal's Close (`data-dismiss="modal"`) button - the one thing every modal has in common."""

    def __init__(self, driver, title_input_locator: tuple[str, str], close_button_locator: tuple[str, str]):
        """Bind the modal's title input and close button locators.

        Args:
            driver: Selenium WebDriver to bind this component to.
            title_input_locator: Locator for the modal's title input, used to detect open/closed.
            close_button_locator: Locator for the modal's Close button.
        """
        super().__init__(driver)
        self._title_input_locator = title_input_locator
        self._close_button_locator = close_button_locator

    def wait_open(self, timeout: int = BaseComponent.DEFAULT_TIMEOUT) -> None:
        """Wait for the modal to finish opening.

        Args:
            timeout: Maximum seconds to wait.
        """
        self.wait_visible(self._title_input_locator, timeout)

    def wait_closed(self, timeout: int = BaseComponent.DEFAULT_TIMEOUT) -> None:
        """Wait for the modal to finish closing.

        Args:
            timeout: Maximum seconds to wait.
        """
        self.wait_invisible(self._title_input_locator, timeout)

    @allure.step("Close modal (discard changes)")
    def close(self) -> None:
        """Click Close and wait for the modal to disappear. Discards the form; no request is sent."""
        self.click(self._close_button_locator)
        self.wait_closed()
