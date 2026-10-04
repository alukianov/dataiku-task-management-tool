"""Smoke tests validating basic connectivity to the REST API."""

import allure
import pytest


@allure.feature("Platform Health")
@pytest.mark.api
@pytest.mark.smoke
def test_root_endpoint_is_reachable(api_client, verify_response):
    """Verifies that the tasks list endpoint responds with 200 and a JSON list of tasks."""
    response = api_client.tasks.list_tasks()
    verify_response(response, 200)


@allure.feature("Platform Health")
@pytest.mark.api
@pytest.mark.smoke
def test_tags_endpoint_is_reachable(api_client, verify_response):
    """Verifies that the tags list endpoint responds with 200."""
    response = api_client.tags.list_tags()
    verify_response(response, 200)
