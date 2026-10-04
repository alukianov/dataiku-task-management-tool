"""Smoke test validating the web app loads and renders the task table."""

import allure
import pytest


@allure.feature("Platform Health")
@pytest.mark.ui
@pytest.mark.smoke
def test_web_app_loads(task_list_page):
    """Verifies that the web app loads and renders the task table."""
    page = task_list_page.load()
    page.verify_loaded()


@allure.feature("Platform Health")
@pytest.mark.ui
@pytest.mark.negative
@pytest.mark.xfail(
    reason='TM-31 (docs/known-defects-and-improvements.md): the page <title> spells "ToDo" with '
    'inconsistent casing between its two occurrences ("ToDo or not ToDO"). Remove xfail once the '
    "defect is fixed.",
    strict=True,
)
def test_page_title_is_spelled_consistently(driver, task_list_page):
    """Verifies that the page title spells "ToDo" the same way both times it appears."""
    task_list_page.load()
    assert driver.title == "ToDo or not ToDo", f"expected page title 'ToDo or not ToDo', got {driver.title!r}"
