"""Fixtures shared by the UI test suite: browser x resolution matrix (chrome/safari, fullhd/4k)."""

import logging
import platform

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.safari.options import Options as SafariOptions

from src.config.browsers import RESOLUTIONS, resolve_browsers, resolve_resolutions
from src.ui.pages.task_list_page import TaskListPage

logger = logging.getLogger(__name__)


def pytest_generate_tests(metafunc):
    """Parametrize any test using the `driver` fixture over the browser x resolution matrix.

    Args:
        metafunc: Pytest metafunc for the test being collected.
    """
    if "browser_resolution" not in metafunc.fixturenames:
        return
    browsers = resolve_browsers(metafunc.config.getoption("--browser"))
    resolutions = resolve_resolutions(metafunc.config.getoption("--resolution"))
    combos = [(browser, resolution) for browser in browsers for resolution in resolutions]
    metafunc.parametrize("browser_resolution", combos, ids=[f"{b}-{r}" for b, r in combos], indirect=True)


@pytest.fixture(name="browser_resolution")
def _browser_resolution(request):
    """Resolve the (browser, resolution) combo for this test instance.

    Returns:
        Tuple of (browser, resolution).
    """
    browser, resolution = request.param
    if browser == "safari" and platform.system() != "Darwin":
        pytest.skip("Safari automation requires macOS (safaridriver) - skipping on this platform.")
    return browser, resolution


@pytest.fixture(name="driver", scope="function")
def _driver(browser_resolution, settings):
    """Build a WebDriver for the parametrized browser, sized to the parametrized resolution.

    Returns:
        The `WebDriver` instance, quit automatically after the test.
    """
    # Scope is explicitly function - a reused browser would leak one test's signed-in/cookie state
    # (session auth lives entirely in a cookie) into the next.
    browser, resolution_name = browser_resolution
    width, height = RESOLUTIONS[resolution_name]
    logger.debug("starting %s driver at %s (%dx%d)", browser, resolution_name, width, height)

    if browser == "chrome":
        options = ChromeOptions()
        if settings.headless:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={width},{height}")
        drv = webdriver.Chrome(options=options)
    else:
        # Safari has no headless mode and ignores --window-size; resize after launch instead.
        drv = webdriver.Safari(options=SafariOptions())
        drv.set_window_size(width, height)

    yield drv
    logger.debug("quitting %s driver", browser)
    drv.quit()


@pytest.fixture(name="task_list_page")
def _task_list_page(driver, settings):
    """Build a TaskListPage bound to the active environment's base URL.

    Returns:
        The `TaskListPage`.
    """
    return TaskListPage(driver, settings.base_url)


@pytest.fixture
def signed_in_page(task_list_page, settings):
    """Build a loaded TaskListPage, already signed in as the default configured test user.

    Returns:
        The signed-in `TaskListPage`.
    """
    user = settings.user()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    return page
