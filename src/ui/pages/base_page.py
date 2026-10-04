"""Shared base classes for Page Objects and Component Objects.

A Page Object owns a URL and loads it (`BasePage`); a Component Object is a reusable widget within a
page that never navigates on its own (`BaseComponent`). Both share the same low-level Selenium helpers
via `DriverBound`.
"""

import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class DriverBound:
    """Common Selenium helpers shared by every Page Object and Component Object."""

    DEFAULT_TIMEOUT = 10

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def wait(self, timeout: int = DEFAULT_TIMEOUT) -> WebDriverWait:
        """Build a WebDriverWait bound to this object's driver.

        Args:
            timeout: Maximum seconds to wait.

        Returns:
            The `WebDriverWait` instance.
        """
        return WebDriverWait(self.driver, timeout)

    def click(self, locator: tuple[str, str]) -> None:
        """Find the element at `locator` and click it.

        Args:
            locator: Selenium locator tuple identifying the element.
        """
        logger.debug("click %s", locator)
        self.driver.find_element(*locator).click()

    def type_text(self, locator: tuple[str, str], text: str, *, clear: bool = True) -> None:
        """Find the element at `locator`, optionally clear it, and type `text` into it.

        Args:
            locator: Selenium locator tuple identifying the element.
            text: Text to type.
            clear: Whether to clear the element's current value first.
        """
        logger.debug("type_text %s (%d chars, clear=%s)", locator, len(text), clear)
        # Value is never logged - type_text() is also how sign_in() enters the password.
        element = self.driver.find_element(*locator)
        if clear:
            element.clear()
        element.send_keys(text)

    def get_value(self, locator: tuple[str, str]) -> str:
        """Find the element at `locator` and return its current `value` attribute.

        Args:
            locator: Selenium locator tuple identifying the element.

        Returns:
            The element's `value` attribute, or `""` if unset.
        """
        logger.debug("get_value %s", locator)
        return self.driver.find_element(*locator).get_attribute("value") or ""

    def get_text(self, locator: tuple[str, str]) -> str:
        """Return the text of the first element matching `locator`.

        Args:
            locator: Selenium locator tuple identifying the element.

        Returns:
            The element's text, or `""` if none is present.
        """
        logger.debug("get_text %s", locator)
        elements = self.driver.find_elements(*locator)
        return elements[0].text if elements else ""

    def wait_visible(self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        """Wait for the element at `locator` to become visible.

        Args:
            locator: Selenium locator tuple identifying the element.
            timeout: Maximum seconds to wait.

        Returns:
            The located `WebElement`.
        """
        logger.debug("wait_visible %s (timeout=%ds)", locator, timeout)
        return self.wait(timeout).until(EC.visibility_of_element_located(locator))

    def wait_present(self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        """Wait for the element at `locator` to exist in the DOM, whether or not it is visible.

        Args:
            locator: Selenium locator tuple identifying the element.
            timeout: Maximum seconds to wait.

        Returns:
            The located `WebElement`.
        """
        logger.debug("wait_present %s (timeout=%ds)", locator, timeout)
        return self.wait(timeout).until(EC.presence_of_element_located(locator))

    def wait_invisible(self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT) -> None:
        """Wait for the element at `locator` to become invisible or absent from the DOM.

        Args:
            locator: Selenium locator tuple identifying the element.
            timeout: Maximum seconds to wait.
        """
        logger.debug("wait_invisible %s (timeout=%ds)", locator, timeout)
        self.wait(timeout).until(EC.invisibility_of_element_located(locator))

    def wait_until(self, condition, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Wait for `condition` to succeed, without raising on timeout.

        Args:
            condition: Callable accepted by `WebDriverWait.until()`.
            timeout: Maximum seconds to wait.

        Returns:
            `True` if the condition succeeded, `False` if it timed out.
        """
        try:
            self.wait(timeout).until(condition)
            logger.debug("wait_until %s -> True", condition)
            return True
        except TimeoutException:
            logger.debug("wait_until %s -> False (timed out after %ds)", condition, timeout)
            return False

    def is_present(self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Wait for `locator` to exist in the DOM, without raising on timeout.

        Args:
            locator: Selenium locator tuple identifying the element.
            timeout: Maximum seconds to wait.

        Returns:
            `True` if an element was found, `False` if it timed out.
        """
        logger.debug("is_present %s (timeout=%ds)", locator, timeout)
        return self.wait_until(EC.presence_of_element_located(locator), timeout)

    def is_visible(self, locator: tuple[str, str], timeout: int | None = None) -> bool:
        """Check whether `locator` currently matches a visible element.

        Args:
            locator: Selenium locator tuple identifying the element.
            timeout: If given, poll up to this many seconds instead of checking once immediately.

        Returns:
            `True` if a visible element was found, `False` otherwise.
        """
        logger.debug("is_visible %s (timeout=%s)", locator, timeout)
        if timeout is None:
            elements = self.driver.find_elements(*locator)
            return len(elements) > 0 and elements[0].is_displayed()
        return self.wait_until(EC.visibility_of_element_located(locator), timeout)

    @staticmethod
    def is_visible_within(parent: WebElement, locator: tuple[str, str]) -> bool:
        """Check whether `locator` matches at least one visible element inside `parent`.

        Args:
            parent: Element to search within.
            locator: Selenium locator tuple identifying the element.

        Returns:
            `True` if a visible matching element was found, `False` otherwise.
        """
        logger.debug("is_visible_within <%s> %s", parent.tag_name, locator)
        elements = parent.find_elements(*locator)
        return len(elements) > 0 and elements[0].is_displayed()

    @staticmethod
    def get_text_within(parent: WebElement, locator: tuple[str, str]) -> str:
        """Return the text of the first element matching `locator` inside `parent`.

        Args:
            parent: Element to search within.
            locator: Selenium locator tuple identifying the element.

        Returns:
            The element's text, or `""` if none is present.
        """
        logger.debug("get_text_within <%s> %s", parent.tag_name, locator)
        elements = parent.find_elements(*locator)
        return elements[0].text if elements else ""

    @staticmethod
    def count_within(parent: WebElement, locator: tuple[str, str]) -> int:
        """Count elements matching `locator` inside `parent`.

        Args:
            parent: Element to search within.
            locator: Selenium locator tuple identifying the elements.

        Returns:
            The number of matching elements.
        """
        logger.debug("count_within <%s> %s", parent.tag_name, locator)
        return len(parent.find_elements(*locator))

    @staticmethod
    def count_tag_within(parent: WebElement, tag_name: str) -> int:
        """Count elements of a given tag name inside `parent`.

        Args:
            parent: Element to search within.
            tag_name: HTML tag name to count, e.g. "button".

        Returns:
            The number of matching elements.
        """
        logger.debug("count_tag_within <%s> %s", parent.tag_name, tag_name)
        return len(parent.find_elements(By.TAG_NAME, tag_name))


class BasePage(DriverBound):
    """Common helpers shared by every top-level Page Object (one per URL)."""

    def __init__(self, driver: WebDriver, base_url: str):
        super().__init__(driver)
        self.base_url = base_url

    def open(self, url: str) -> None:
        """Navigate the driver to the given URL.

        Args:
            url: URL to navigate to.
        """
        logger.debug("open %s", url)
        self.driver.get(url)


class BaseComponent(DriverBound):
    """Common helpers shared by every Component Object - a reusable widget scoped within a page."""
