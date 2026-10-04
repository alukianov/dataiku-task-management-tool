"""Tags resource tests: `GET /tags` and `GET /tags/<tag_id>`."""

import allure
import pytest

NONEXISTENT_TAG_ID = 999999999  # well-formed integer id that will never exist on this instance


def _tag_id_from_url(url: str) -> str:
    """Extract the numeric tag id from a tag URL.

    Args:
        url: Tag URL, e.g. ".../tags/5".

    Returns:
        The numeric tag id, e.g. "5".
    """
    return url.rstrip("/").split("/")[-1]


@allure.feature("Tags")
@pytest.mark.api
def test_list_tags_includes_newly_created_tag(create_task, qa_auth, api_client, unique_name, verify_response):
    """Verifies that the tags list includes a tag auto-created via a task, keyed by tag name."""
    tag_name = unique_name()
    create_task(unique_name(), tags=[tag_name], auth=qa_auth)

    response = api_client.tags.list_tags()
    verify_response(response, 200)
    assert tag_name in response.json(), f"expected tag {tag_name!r} to be present in {response.json()}"


@allure.feature("Tags")
@pytest.mark.api
def test_get_tag_by_id_returns_tag_detail(create_task, qa_auth, api_client, unique_name, verify_response):
    """Verifies that fetching a tag by id, parsed from the tags list, returns its detail."""
    tag_name = unique_name()
    task_title = unique_name()
    create_task(task_title, tags=[tag_name], auth=qa_auth)

    tags = api_client.tags.list_tags().json()
    tag_id = _tag_id_from_url(tags[tag_name])

    response = api_client.tags.get_tag(tag_id)
    verify_response(response, 200, expected_body={"tag": tag_name})
    assert (
        task_title in response.json()["tasks"]
    ), f"expected task {task_title!r} to be listed under tag {tag_name!r}, got {response.json()['tasks']}"


@allure.feature("Tags")
@pytest.mark.api
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-15 (docs/known-defects-and-improvements.md): the 404 body is an empty {} with no 'message' "
    "key - every error response must explain what went wrong. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_get_nonexistent_tag_returns_404(api_client, verify_response):
    """Verifies that fetching a well-formed but never-created id returns 404 with an explanatory message."""
    response = api_client.tags.get_tag(NONEXISTENT_TAG_ID)
    # Ideal-behavior placeholder - the real body is currently an empty {} (TM-15), no message yet.
    verify_response(response, 404, expected_message="Tag not found")


@allure.feature("Tags")
@pytest.mark.api
def test_tag_is_deduplicated_across_tasks(create_task, qa_auth, api_client, unique_name):
    """Verifies that two tasks created with the same tag name share a single tag entry."""
    tag_name = unique_name()
    title_one = unique_name()
    title_two = unique_name()

    create_task(title_one, tags=[tag_name], auth=qa_auth)
    create_task(title_two, tags=[tag_name], auth=qa_auth)

    tags = api_client.tags.list_tags().json()
    tag_id = _tag_id_from_url(tags[tag_name])

    detail = api_client.tags.get_tag(tag_id).json()
    assert (
        title_one in detail["tasks"]
    ), f"expected deduplicated tag to list task {title_one!r}, got {detail['tasks']}"
    assert (
        title_two in detail["tasks"]
    ), f"expected deduplicated tag to list task {title_two!r}, got {detail['tasks']}"


@allure.feature("Tags")
@pytest.mark.api
@pytest.mark.boundary
@pytest.mark.parametrize("length", [19, 20])
def test_tag_name_within_limit_is_accepted(create_task, qa_auth, unique_name, verify_response, length):
    """Verifies that tag names at or under the documented 20-char limit are accepted unmodified."""
    tag_name = unique_name(length)
    response = create_task(unique_name(), tags=[tag_name], auth=qa_auth)
    verify_response(response, 200)
    actual_tags = [t["name"] for t in response.json()["tags"]]
    assert actual_tags == [tag_name], f"expected tags {[tag_name]}, got {actual_tags}"


@allure.feature("Tags")
@pytest.mark.api
@pytest.mark.boundary
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-07 (docs/known-defects-and-improvements.md): a 21-char tag name crashes the request with 500 "
    "instead of being rejected with a clean 400. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_tag_name_exceeding_limit_is_rejected(create_task, qa_auth, unique_name, verify_response):
    """Verifies that a tag name over the documented 20-char limit is rejected, not crashing the request."""
    response = create_task(unique_name(), tags=[unique_name(21)], auth=qa_auth)
    # Ideal-behavior placeholder - the request currently crashes with 500 instead (TM-07).
    verify_response(response, 400, expected_message="Tag name must be at most 20 characters")
