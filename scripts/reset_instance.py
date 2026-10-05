"""Wipe all data on the target instance via GET /reset, once, before the API and UI suites start.

Used by the regression workflow; run manually only against an isolated or authorized instance:

    .venv\\Scripts\\python.exe -m scripts.reset_instance --environment test
"""

import argparse
import sys

import truststore

from src.api.client import TaskManagementAPIClient
from src.config.settings import load_settings

# Use the OS trust store (not a verify=False bypass); must run before any HTTPS call below.
truststore.inject_into_ssl()


def main() -> int:
    """Reset the selected environment and return a process exit code.

    Returns:
        0 if the reset succeeded, 1 otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", default=None, help="Environment name from config.ini")
    args = parser.parse_args()

    active_settings = load_settings(environment=args.environment or None)
    client = TaskManagementAPIClient(active_settings.base_url, timeout=active_settings.request_timeout)
    response = client.system.reset()
    print(f"[{active_settings.environment.name}] GET /reset -> {response.status_code}")
    return 0 if response.ok else 1


if __name__ == "__main__":
    sys.exit(main())
