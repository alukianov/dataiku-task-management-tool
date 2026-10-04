"""Environment and user configuration for the test framework."""

import configparser
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# settings.py lives at <repo_root>/src/config/settings.py, so climb 2 levels (config/, src/) to root.
_REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = _REPO_ROOT / "config.ini"


@dataclass(frozen=True)
class EnvironmentConfig:
    """A target environment: a name and its base URL."""

    name: str
    base_url: str


@dataclass(frozen=True)
class UserConfig:
    """A named test user: username and password."""

    username: str
    password: str


@dataclass(frozen=True)
class Settings:
    """Resolved configuration for a test run: active environment, available users, run knobs."""

    environment: EnvironmentConfig
    users: dict[str, UserConfig]
    default_username: str
    headless: bool
    request_timeout: int

    @property
    def base_url(self) -> str:
        """Return the base URL of the active environment."""
        return self.environment.base_url

    def user(self, username: str | None = None) -> UserConfig:
        """Look up a configured test user.

        Args:
            username: Username to look up. Defaults to the configured default user.

        Returns:
            The matching `UserConfig`.
        """
        key = username or self.default_username
        try:
            found = self.users[key]
        except KeyError as exc:
            available = ", ".join(sorted(self.users)) or "none configured"
            raise ValueError(f"Unknown username {key!r}; available: {available}") from exc
        if not found.password:
            raise ValueError(
                f"No password configured for user {key!r}; set {key.upper()}_PASSWORD in "
                ".env (see .env.example) rather than leaving it blank."
            )
        return found


def _environment_config(parser: configparser.ConfigParser, environment: str) -> EnvironmentConfig:
    """Build the `EnvironmentConfig` for the given environment.

    Args:
        parser: Parsed config.ini.
        environment: Name of the environment to resolve.

    Returns:
        The resolved `EnvironmentConfig`.
    """
    section_name = f"environment.{environment}"
    if section_name not in parser:
        available = ", ".join(
            s.removeprefix("environment.")
            for s in parser.sections()
            if s.startswith("environment.") and ".user." not in s
        )
        raise ValueError(f"Unknown environment {environment!r}; available: {available or 'none configured'}")
    return EnvironmentConfig(name=environment, base_url=parser[section_name]["base_url"].rstrip("/"))


def _user_configs(parser: configparser.ConfigParser, environment: str) -> dict[str, UserConfig]:
    """Build the configured users for the given environment.

    Args:
        parser: Parsed config.ini.
        environment: Name of the environment to resolve users for.

    Returns:
        Mapping of username to `UserConfig`.
    """
    prefix = f"environment.{environment}.user."
    users = {}
    for section_name in parser.sections():
        if not section_name.startswith(prefix):
            continue
        username = section_name.removeprefix(prefix)
        password = os.getenv(f"{username.upper()}_PASSWORD", "")
        users[username] = UserConfig(username=username, password=password)
    return users


def load_settings(environment: str | None = None, username: str | None = None) -> Settings:
    """Build Settings for the given environment and default username.

    Args:
        environment: Environment name. Falls back to the ENVIRONMENT env var, then config.ini.
        username: Default username. Falls back to the TEST_USER env var, then config.ini.

    Returns:
        The resolved `Settings`.
    """
    parser = configparser.ConfigParser()
    parser.read(CONFIG_PATH)

    environment = environment or os.getenv("ENVIRONMENT") or parser.get("default", "environment")
    username = username or os.getenv("TEST_USER") or parser.get("default", "user")

    return Settings(
        environment=_environment_config(parser, environment),
        users=_user_configs(parser, environment),
        default_username=username,
        headless=os.getenv("HEADLESS", "true").lower() == "true",
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
    )


settings = load_settings()
