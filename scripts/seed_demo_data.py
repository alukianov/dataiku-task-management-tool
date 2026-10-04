"""One-off seed script: populates the shared instance with demo tasks/tags for visual inspection.

Run manually:

    .venv\\Scripts\\python.exe scripts\\seed_demo_data.py
"""

import truststore

from src.api.auth import basic_auth
from src.api.client import TaskManagementAPIClient
from src.api.resources.tasks import TaskUpdate
from src.config.settings import settings

# Use the OS trust store (not a verify=False bypass); must run before any HTTPS call below.
truststore.inject_into_ssl()

# 10 distinct tags, reused across a handful of demo tasks (titles <= 20 chars per the spec limit).
TASKS = [
    {"title": "Fix login bug", "tags": ["bug"]},
    {"title": "Write API docs", "tags": ["docs"]},
    {"title": "Redesign UI", "tags": ["frontend"]},
    {"title": "Refactor backend", "tags": ["backend"]},
    {"title": "Security audit", "tags": ["security"]},
    {"title": "Plan new feature", "tags": ["feature"]},
    {"title": "Fix billing issue", "tags": ["billing"]},
    {"title": "User onboarding", "tags": ["onboarding"]},
    {"title": "Build report", "tags": ["reporting"]},
    {"title": "Hotfix prod issue", "tags": ["urgent"]},
    {"title": "Update dependencies", "tags": ["backend", "security"]},
    {"title": "Polish onboarding", "tags": ["onboarding", "frontend"]},
]

# Titles marked done after creation, to also show that state rendered in the UI.
DONE_TITLES = {"Fix login bug", "Hotfix prod issue"}


def main() -> None:
    """Create the demo tasks/tags and mark a couple of them done."""
    client = TaskManagementAPIClient()
    qa_user = settings.user("qa")
    auth = basic_auth(qa_user.username, qa_user.password)

    created = []
    for spec in TASKS:
        response = client.tasks.create_task(spec["title"], tags=spec["tags"], auth=auth)
        print(f"PUT / -> {response.status_code} {spec['title']} {spec['tags']}")
        if response.ok:
            created.append(response.json())

    for task in created:
        if task.get("title") in DONE_TITLES:
            task_id = task["id"]
            response = client.tasks.update_task(task_id, TaskUpdate(done=True), auth=auth)
            print(f"PATCH /{task_id} -> {response.status_code} done=True")

    tags_response = client.tags.list_tags()
    print(f"\nGET /tags -> {tags_response.status_code}")
    print(tags_response.json())


if __name__ == "__main__":
    main()
