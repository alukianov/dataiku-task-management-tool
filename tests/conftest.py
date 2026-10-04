"""Root pytest configuration: CLI options, SSL trust store setup, and shared API/UI fixtures."""

import logging
import os
import pathlib
import uuid

import allure
import pytest
import truststore

from src.api.auth import basic_auth, token_auth
from src.api.client import TaskManagementAPIClient
from src.config.browsers import (
    DEFAULT_BROWSERS,
    DEFAULT_RESOLUTIONS,
    RESOLUTIONS,
    SUPPORTED_BROWSERS,
    resolve_browsers,
    resolve_resolutions,
)
from src.config.settings import UserConfig, load_settings
from src.reporting.allure_logging import log_failure

logger = logging.getLogger(__name__)

# Use the OS trust store (not a verify=False bypass) so requests work unmodified on machines behind a
# TLS-inspecting corporate proxy, without weakening certificate validation.
truststore.inject_into_ssl()


def pytest_addoption(parser):
    """Register the --environment/--user/--browser/--resolution CLI options.

    Args:
        parser: Pytest argument parser.
    """
    parser.addoption(
        "--environment",
        action="store",
        default=None,
        help="Environment name from config.ini (overrides ENVIRONMENT env var / config.ini default).",
    )
    parser.addoption(
        "--user",
        action="store",
        default=None,
        help="Default test username from config.ini (overrides TEST_USER env var / config.ini default).",
    )
    parser.addoption(
        "--browser",
        action="append",
        choices=list(SUPPORTED_BROWSERS),
        default=None,
        help=f"Browser(s) for UI tests; repeatable. Default: {', '.join(DEFAULT_BROWSERS)}.",
    )
    parser.addoption(
        "--resolution",
        action="append",
        choices=list(RESOLUTIONS),
        default=None,
        help=f"Named resolution(s) for UI tests; repeatable. Default: {', '.join(DEFAULT_RESOLUTIONS)}.",
    )


def pytest_configure(config):
    """Validate --environment/--user early so bad CLI input fails cleanly.

    Args:
        config: Pytest config object.
    """
    try:
        resolved = load_settings(
            environment=config.getoption("--environment"),
            username=config.getoption("--user"),
        )
        resolved.user()
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach failure evidence to Allure on any test failure.

    Args:
        item: Pytest test item being reported on.
        call: Pytest call info for the current test phase.
    """
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed and call.excinfo is not None:
        log_failure(item, call.excinfo)


@pytest.fixture(scope="session", name="settings")
def _settings(pytestconfig):
    """Build the resolved Settings for the whole test session.

    Returns:
        The resolved `Settings`.
    """
    return load_settings(
        environment=pytestconfig.getoption("--environment"),
        username=pytestconfig.getoption("--user"),
    )


@pytest.fixture(name="api_client")
def _api_client(settings):
    """Build a fresh, unauthenticated API client bound to the active environment.

    Returns:
        The `TaskManagementAPIClient`.
    """
    return TaskManagementAPIClient(base_url=settings.base_url, timeout=settings.request_timeout)


@pytest.fixture(name="create_task")
def _create_task(api_client):
    """Build a factory that creates a task and cleans it up again during teardown.

    Returns:
        A callable `(title, tags=None, auth=None) -> Response` that creates a task.
    """
    created_task_ids = []

    def _create(title, tags=None, auth=None):
        response = api_client.tasks.create_task(title, tags=tags, auth=auth)
        # Retry once on a transient 5xx from the dev server - keeps setup steps resilient to that
        # noise; never use this fixture where the create call itself is what's under test.
        if response.status_code >= 500:
            response = api_client.tasks.create_task(title, tags=tags, auth=auth)
        if response.status_code == 200:
            created_task_ids.append((response.json()["id"], auth))
            logger.debug("created task %r (id=%s)", title, response.json()["id"])
        return response

    yield _create

    # The shared instance is never reset between runs, so tests must clean up after themselves.
    # Best-effort: some tests delete the task themselves as part of the scenario, and a repeat
    # DELETE is fine.
    for task_id, auth in created_task_ids:
        logger.debug("cleaning up task id=%s", task_id)
        api_client.tasks.delete_task(task_id, auth=auth)


@pytest.fixture
def qa_auth(settings):
    """Build Basic auth credentials for the default configured test user.

    Returns:
        The `HTTPBasicAuth` credentials.
    """
    user = settings.user()
    return basic_auth(user.username, user.password)


@pytest.fixture(name="unique_name")
def _unique_name():
    """Build a factory for fresh, unique title/tag names.

    Returns:
        A callable `(length=12) -> str` that generates a unique name, at most 20 chars.
    """

    def _make(length: int = 12) -> str:
        return uuid.uuid4().hex[:length]

    return _make


@pytest.fixture
def verify_response():
    """Build a factory that asserts a response's status and optionally its body.

    Returns:
        A callable `(response, expected_status, *, expected_body=None, expected_message=None)` that
        performs the assertions.
    """

    @allure.step("Verify response ({expected_status})")
    def _verify(
        response,
        expected_status: int | tuple[int, ...],
        *,
        expected_body: dict | None = None,
        expected_message: str | None = None,
    ) -> None:
        if isinstance(expected_status, int):
            assert (
                response.status_code == expected_status
            ), f"expected status {expected_status}, got {response.status_code} (body: {response.text})"
        else:
            assert response.status_code in expected_status, (
                f"expected status in {expected_status}, got {response.status_code} "
                f"(body: {response.text})"
            )
        if expected_message is not None:
            actual_message = response.json().get("message")
            assert (
                actual_message == expected_message
            ), f"expected response message {expected_message!r}, got {actual_message!r}"
        elif expected_body is not None:
            actual_body = response.json()
            assert (
                expected_body.items() <= actual_body.items()
            ), f"expected response body to include {expected_body}, got {actual_body}"

    return _verify


@pytest.fixture
def other_users_task(make_user_auth, create_task, unique_name):
    """Build a factory that creates a task owned by a brand-new 'other' user.

    Returns:
        A callable `() -> (created_task, title)` that creates the task.
    """

    def _make():
        other_auth = make_user_auth()
        title = unique_name()
        created = create_task(title, auth=other_auth).json()
        return created, title

    return _make


def _authenticate(api_client, username, password):
    """Authenticate and return token auth for the resulting token.

    Args:
        api_client: API client to authenticate with.
        username: Username to authenticate with.
        password: Password to authenticate with.

    Returns:
        The resulting token auth.
    """
    response = api_client.auth.authenticate(username, password)
    assert response.status_code == 200, f"/authenticate failed: {response.status_code} {response.text}"
    return token_auth(response.json()["token"])


@pytest.fixture
def qa_token_auth(api_client, settings):
    """Build token auth for the default configured test user.

    Returns:
        The resulting token auth.
    """
    user = settings.user()
    return _authenticate(api_client, user.username, user.password)


@pytest.fixture(name="make_user")
def _make_user(api_client):
    """Build a factory that registers a brand-new, randomly-named user for this test scenario only.

    Returns:
        A callable `() -> UserConfig` that registers the user.
    """

    def _make() -> UserConfig:
        username = f"qa_scenario_{uuid.uuid4().hex[:10]}"
        password = uuid.uuid4().hex
        api_client.users.create_user(username, password)
        logger.debug("registered scenario user %r", username)
        return UserConfig(username=username, password=password)

    return _make


@pytest.fixture(name="make_user_auth")
def _make_user_auth(make_user):
    """Build a factory that registers a brand-new user and returns ready-to-use Basic auth for it.

    Returns:
        A callable `() -> HTTPBasicAuth` that registers the user and returns its auth.
    """

    def _auth():
        user = make_user()
        return basic_auth(user.username, user.password)

    return _auth


@pytest.fixture
def make_user_token_auth(make_user, api_client):
    """Factory: register a brand-new user and return token-based auth (post-/authenticate) for it."""

    def _auth():
        user = make_user()
        return _authenticate(api_client, user.username, user.password)

    return _auth


def pytest_sessionstart(session):
    """Optionally wipe the instance via /reset, then write the Allure environment.properties file.

    With pytest-xdist, this hook runs in the controller AND every worker process; skip workers (they
    have a `workerinput` attribute, the controller does not) so both the reset and the file write
    happen exactly once, in the controller, before any worker is spawned and starts running tests
    (xdist only spins up workers once the controller's own session startup has fully completed).
    """
    if hasattr(session.config, "workerinput"):
        return

    active_settings = load_settings(
        environment=session.config.getoption("--environment"),
        username=session.config.getoption("--user"),
    )

    # Opt-in only, default off (unset/"false") - this instance is shared in general (TM-11), so a
    # blanket reset must never be the default for anyone who clones this repo. Enable locally via
    # RESET_BEFORE_RUN=true in .env only when you know you're the sole user of the target instance.
    if os.getenv("RESET_BEFORE_RUN", "false").lower() in ("1", "true", "yes"):
        client = TaskManagementAPIClient(active_settings.base_url, timeout=active_settings.request_timeout)
        response = client.system.reset()
        print(f"\n[RESET_BEFORE_RUN] GET /reset -> {response.status_code}")

    browsers = resolve_browsers(session.config.getoption("--browser"))
    resolutions = resolve_resolutions(session.config.getoption("--resolution"))
    results_dir = pathlib.Path("reports/allure-results")
    results_dir.mkdir(parents=True, exist_ok=True)
    env_file = results_dir / "environment.properties"
    env_file.write_text(
        f"ENVIRONMENT={active_settings.environment.name}\n"
        f"BASE_URL={active_settings.base_url}\n"
        f"TEST_USER={active_settings.default_username}\n"
        f"BROWSERS={','.join(browsers)}\n"
        f"RESOLUTIONS={','.join(resolutions)}\n"
        f"HEADLESS={active_settings.headless}\n",
        encoding="utf-8",
    )
