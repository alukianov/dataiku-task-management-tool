"""Supported browsers and named screen resolutions for UI test parametrization."""

import os

RESOLUTIONS: dict[str, tuple[int, int]] = {
    "fullhd": (1920, 1080),
    "4k": (3840, 2160),
}

# The two most popular desktop browsers; Safari only runs on macOS (see tests/ui/conftest.py).
SUPPORTED_BROWSERS = ("chrome", "safari")

# Fast default for a plain `pytest` run; the rest of the matrix is opt-in via --browser/--resolution.
DEFAULT_BROWSERS = ("chrome",)
DEFAULT_RESOLUTIONS = ("fullhd",)


def resolve_browsers(cli_value: list[str] | None) -> list[str]:
    """Resolve the browser(s) to test.

    Args:
        cli_value: Browser names from the --browser CLI flag.

    Returns:
        List of browser names, falling back to the BROWSER env var, then the default browsers.
    """
    if cli_value:
        return cli_value
    env_value = os.getenv("BROWSER")
    if env_value:
        return [b.strip() for b in env_value.split(",") if b.strip()]
    return list(DEFAULT_BROWSERS)


def resolve_resolutions(cli_value: list[str] | None) -> list[str]:
    """Resolve the resolution(s) to test.

    Args:
        cli_value: Resolution names from the --resolution CLI flag.

    Returns:
        List of resolution names, falling back to the RESOLUTION env var, then the default resolutions.
    """
    if cli_value:
        return cli_value
    env_value = os.getenv("RESOLUTION")
    if env_value:
        return [r.strip() for r in env_value.split(",") if r.strip()]
    return list(DEFAULT_RESOLUTIONS)
