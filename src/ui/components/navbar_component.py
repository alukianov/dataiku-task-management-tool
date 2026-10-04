"""Component Object for the navbar's sign-in/out form (reusable across any page that renders it)."""

import time

import allure

from src.ui.locators import task_list_locators as locators
from src.ui.pages.base_page import BaseComponent


class NavbarComponent(BaseComponent):
    """The navbar's sign-in/out form and its auth-related warning banners."""

    def wait_until_rendered(self, timeout: int = 20) -> None:
        """Wait for the sign-in inputs to render.

        Args:
            timeout: Maximum seconds to wait.
        """
        # Longer than DEFAULT_TIMEOUT - these inputs stay hidden until initial async setup completes.
        self.wait_visible(locators.USERNAME_INPUT, timeout=timeout)

    @allure.step("Sign in as '{username}'")
    def sign_in(self, username: str, password: str) -> None:
        """Fill the sign-in form and submit it, clearing any previous input first.

        Args:
            username: Username to sign in with.
            password: Password to sign in with.
        """
        self.type_text(locators.USERNAME_INPUT, username)
        self.type_text(locators.PASSWORD_INPUT, password)
        self.click(locators.SIGN_IN_BUTTON)
        # Without this, callers that act on post-auth controls can hit ElementNotInteractableException
        # while the DOM is mid-reflow from the auth AJAX call.
        self._wait_for_sign_in_response()

    def _wait_for_sign_in_response(self, timeout: int = 5) -> None:
        """Wait for the navbar to settle after a sign-in attempt, success or warning banner.

        Args:
            timeout: Maximum seconds to wait.
        """

        def _settled(_driver) -> bool:
            return self.is_visible(locators.SIGN_OUT_BUTTON) or self.is_visible(locators.WARNING_ALERTS)

        self.wait_until(_settled, timeout)

    @allure.step("Sign out")
    def sign_out(self) -> None:
        """Click the navbar sign-out button."""
        self.click(locators.SIGN_OUT_BUTTON)

    def is_authenticated(self, timeout: int = BaseComponent.DEFAULT_TIMEOUT) -> bool:
        """Wait for the navbar to switch to the signed-in ("Sign out") state.

        Args:
            timeout: Maximum seconds to wait.

        Returns:
            `True` if the navbar switched to the signed-in state.
        """
        return self.is_visible(locators.SIGN_OUT_BUTTON, timeout)

    def brand_text(self) -> str:
        """Return the navbar brand link's text."""
        return self.get_text(locators.NAVBAR_BRAND)

    def displayed_username(self) -> str:
        """Return the username shown in the "Sign out (<username>)" button.

        Returns:
            The displayed username, or `""` if signed out.
        """
        return self.get_text(locators.NAVBAR_USERNAME_DISPLAY)

    @allure.step("Verify authenticated state is {expected} (username='{username}')")
    def verify_authenticated(
        self,
        expected: bool = True,
        username: str | None = None,
        timeout: int = BaseComponent.DEFAULT_TIMEOUT,
    ) -> None:
        """Assert the navbar's signed-in state matches `expected`.

        Args:
            expected: Expected signed-in state.
            username: If given, also assert this username is shown.
            timeout: Maximum seconds to wait.
        """
        actual = self.is_authenticated(timeout)
        assert actual is expected, f"expected authenticated={expected}, got authenticated={actual}"
        if username is not None:
            displayed = self.displayed_username()
            assert displayed == username, f"expected displayed username {username!r}, got {displayed!r}"

    def credential_inputs_are_empty(self) -> bool:
        """Check whether both the username and password inputs are currently empty.

        Returns:
            `True` if both inputs are empty.
        """
        return self.get_value(locators.USERNAME_INPUT) == "" and self.get_value(locators.PASSWORD_INPUT) == ""

    def warning_alert_count(self, timeout: int = 5) -> int:
        """Count the currently visible `.alert-warning` banners.

        Args:
            timeout: Maximum seconds to wait for at least one banner to appear.

        Returns:
            The number of visible warning banners, polled until the count stabilizes.
        """

        # The clone-on-failed-login handler can insert several banners in quick succession, so an
        # immediate read can under-count a still-in-progress DOM update.
        def _visible_count(_driver) -> int:
            return sum(
                1 for alert in self.driver.find_elements(*locators.WARNING_ALERTS) if alert.is_displayed()
            )

        if not self.wait_until(lambda driver: _visible_count(driver) >= 1, timeout):
            return 0

        count = _visible_count(self.driver)
        stable_until = time.monotonic() + 1.0
        while time.monotonic() < stable_until:
            time.sleep(0.2)
            current = _visible_count(self.driver)
            if current != count:
                count = current
                stable_until = time.monotonic() + 1.0
        return count

    def warning_alert_message(self) -> str:
        """Return the first visible warning banner's message text.

        Returns:
            The message text, or `""` if no banner is visible.
        """
        # Every warning banner is a clone of the same template; only the first clone's text gets set.
        elements = self.driver.find_elements(*locators.WARNING_ALERT_TEXT)
        return elements[0].text if elements else ""

    def warning_alert_status(self) -> str:
        """Return the first visible warning banner's HTTP status text.

        Returns:
            The status text, or `""` if no banner is visible.
        """
        elements = self.driver.find_elements(*locators.WARNING_ALERT_STATUS)
        return elements[0].text if elements else ""

    @allure.step("Verify warning banner shows '{expected_message}' ({expected_status})")
    def verify_warning(self, expected_message: str, expected_status: str = "401") -> None:
        """Assert a warning banner is visible with the given message and status.

        Args:
            expected_message: Expected banner message text.
            expected_status: Expected banner HTTP status text.
        """
        assert self.warning_alert_count() >= 1, "expected at least one warning banner to be visible"
        actual_message = self.warning_alert_message()
        assert (
            actual_message == expected_message
        ), f"expected warning banner message {expected_message!r}, got {actual_message!r}"
        actual_status = self.warning_alert_status()
        assert (
            actual_status == expected_status
        ), f"expected warning banner status {expected_status!r}, got {actual_status!r}"
