"""Centralized endpoint path definitions for the task management REST API."""

TASKS = "/"
TASK = "/{task_id}"
TAGS = "/tags"
TAG = "/tags/{tag_id}"
USERS = "/users"
AUTHENTICATE = "/authenticate"
RESET = "/reset"


def build_path(template: str, **kwargs) -> str:
    """Fill a `{placeholder}` path template's values.

    Args:
        template: Path template containing `{placeholder}` segments.
        **kwargs: Values to substitute into the template's placeholders.

    Returns:
        The template with placeholders replaced by their values.
    """
    return template.format(**kwargs)
