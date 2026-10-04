"""Shared Allure evidence helpers: HTTP request/response logging and test-failure diagnostics."""

import json

import allure
from selenium.common.exceptions import WebDriverException

_REDACTED = "***redacted***"


def _pretty_body(raw) -> str:
    """Pretty-print a JSON body if possible, otherwise return it as plain text.

    Args:
        raw: Request or response body, as `bytes`, `str`, or `None`.

    Returns:
        The formatted body text.
    """
    if not raw:
        return "<empty>"
    text = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
    try:
        return json.dumps(json.loads(text), indent=2)
    except json.JSONDecodeError:
        return text


def _safe_headers(headers) -> str:
    """Render headers as text, masking the Authorization value.

    Args:
        headers: Mapping of header name to value.

    Returns:
        The formatted header text.
    """
    lines = [
        f"{key}: {_REDACTED if key.lower() == 'authorization' else value}" for key, value in headers.items()
    ]
    return "\n".join(lines) or "<none>"


def log_http_call(response) -> None:
    """Attach one request/response pair to the Allure report as a named step.

    Args:
        response: `requests.Response` to log.
    """
    request = response.request
    try:
        with allure.step(f"{request.method} {request.url} -> {response.status_code}"):
            allure.attach(
                _safe_headers(request.headers),
                name="Request headers",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                _pretty_body(request.body), name="Request body", attachment_type=allure.attachment_type.JSON
            )
            allure.attach(
                _safe_headers(response.headers),
                name="Response headers",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                _pretty_body(response.text), name="Response body", attachment_type=allure.attachment_type.JSON
            )
    except KeyError:
        pass


def log_failure(item, excinfo) -> None:
    """Attach the failure's exception/assertion message, and UI diagnostics if the test used `driver`.

    Args:
        item: Pytest test item that failed.
        excinfo: Captured exception info for the failure.
    """
    allure.attach(str(excinfo.value), name="Failure reason", attachment_type=allure.attachment_type.TEXT)
    driver = item.funcargs.get("driver")
    if driver is None:
        return
    allure.attach(
        driver.get_screenshot_as_png(),
        name="Screenshot on failure",
        attachment_type=allure.attachment_type.PNG,
    )
    allure.attach(
        driver.page_source,
        name="Page source on failure",
        attachment_type=allure.attachment_type.HTML,
    )
    _attach_console_log(driver)


def _attach_console_log(driver) -> None:
    """Attach browser console log entries, if the driver supports it.

    Args:
        driver: Selenium WebDriver to read the console log from.
    """
    try:
        entries = driver.get_log("browser")
    except WebDriverException:
        return
    if not entries:
        return
    text = "\n".join(f"[{entry['level']}] {entry['message']}" for entry in entries)
    allure.attach(text, name="Browser console log", attachment_type=allure.attachment_type.TEXT)
