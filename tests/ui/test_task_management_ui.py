"""UI task management tests: add/edit/mark-done/delete flows via the Add/Edit modals and row buttons."""

import allure
import pytest


@allure.feature("Tasks")
@pytest.mark.ui
def test_add_task_appears_in_list(task_list_page, settings, unique_name):
    """Verifies that adding a task via the modal renders it in the table for the signed-in owner."""
    user = settings.user()
    title = unique_name()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.verify_authenticated()

    page.add_task(title, tags=["ui"])
    page.verify_task_visible(title)
    page.verify_in_progress(title)

    page.delete_task(title)


@allure.feature("Tasks")
@pytest.mark.ui
def test_edit_task_title_updates_row(task_list_page, settings, unique_name):
    """Verifies that editing a task's title via the modal updates the rendered row in place."""
    user = settings.user()
    title = unique_name()
    new_title = unique_name()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.add_task(title)
    page.verify_task_visible(title)

    page.edit_task_title(title, new_title)
    page.verify_task_visible(new_title)

    page.delete_task(new_title)


@allure.feature("Tasks")
@pytest.mark.ui
def test_mark_done_then_mark_in_progress_toggles_label(task_list_page, settings, unique_name):
    """Verifies that Mark Done flips the row's label to Done, and Mark In Progress flips it back."""
    user = settings.user()
    title = unique_name()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.add_task(title)
    page.verify_in_progress(title)

    page.mark_done(title)
    page.verify_done(title)

    page.mark_in_progress(title)
    page.verify_in_progress(title)

    page.delete_task(title)


@allure.feature("Tasks")
@pytest.mark.ui
def test_delete_task_removes_row(task_list_page, settings, unique_name):
    """Verifies that deleting a task via the row button removes it from the table."""
    user = settings.user()
    title = unique_name()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.add_task(title)
    page.verify_task_visible(title)

    page.delete_task(title)
    assert not page.has_task(
        title, timeout=2
    ), f"expected task '{title}' to be removed from the table after delete"


@allure.feature("Tasks")
@pytest.mark.ui
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-18 (docs/known-defects-and-improvements.md): the Add Task view model's `tags` field defaults "
    'to a plain array, and addTask() unconditionally calls `.split(" ")` on it - if the Tags input '
    "is never touched, the array is never converted to a string, `.split()` throws, and the task is "
    "silently never created even though tags are optional per the spec. Remove xfail once fixed.",
    strict=True,
)
def test_add_task_with_untouched_tags_field_is_still_created(task_list_page, settings, unique_name):
    """Verifies that submitting Add Task with Tags left untouched still creates the task."""
    user = settings.user()
    title = unique_name()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)

    page.add_modal.add_with_untouched_tags(title)

    assert page.has_task(title), f"expected task '{title}' to be created even with the Tags field untouched"
    page.delete_task(title)


@allure.feature("Tasks")
@pytest.mark.ui
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-23 (docs/known-defects-and-improvements.md): the Add and Edit modals share the exact same "
    'hardcoded header text "Update a task" - the Add modal was never given its own title. Remove '
    "xfail once the defect is fixed.",
    strict=True,
)
def test_add_task_modal_has_its_own_title(task_list_page, settings):
    """Verifies that the Add Task modal is titled distinctly from the Edit Task modal."""
    user = settings.user()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)

    page.add_modal.open()
    actual_title = page.add_modal.title_label_text().strip()
    assert actual_title.lower() != "update a task", (
        f"Add modal header should be its own text, not the Edit modal's 'Update a task' - got: "
        f"{actual_title!r}"
    )


@allure.feature("Tasks")
@pytest.mark.ui
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-24 (docs/known-defects-and-improvements.md): AddTaskViewModel.title/.tags are never reset "
    "after a successful submit, so reopening the Add modal shows the previous task's title/tags "
    "still populated. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_add_task_modal_inputs_are_cleared_after_submit(task_list_page, settings, unique_name):
    """Verifies that reopening Add Task after a successful create shows a blank form."""
    user = settings.user()
    title = unique_name()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.add_task(title, tags=["tm24"])

    page.add_modal.open()
    try:
        actual_fields = page.add_modal.field_values()
        assert actual_fields == ("", ""), f"expected a blank Add modal (title, tags), got {actual_fields}"
    finally:
        page.add_modal.close()
        page.delete_task(title)


@allure.feature("Tasks")
@pytest.mark.ui
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-25 (docs/known-defects-and-improvements.md): the Edit modal only renders one input per "
    "existing tag (rename-in-place) - there is no control to add a brand-new tag or remove an "
    "existing one. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_edit_modal_supports_adding_and_removing_tags(task_list_page, settings, unique_name):
    """Verifies that the Edit modal offers a way to add/remove tags, not just rename existing ones."""
    user = settings.user()
    title = unique_name()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.add_task(title, tags=["original"])

    page.task_table.begin_edit(title)
    try:
        actual_tag_inputs = page.edit_modal.tag_input_count()
        assert (
            actual_tag_inputs == 1
        ), f"expected exactly one tag input (rename-in-place), got {actual_tag_inputs}"

        # Today the Tags section only renders rename-in-place inputs - a real add/remove-tag
        # affordance would add at least one button inside that section.
        assert page.edit_modal.tag_section_button_count() > 0, "expected an add/remove-tag control"
    finally:
        page.edit_modal.close()
        page.delete_task(title)


@allure.feature("Tasks")
@pytest.mark.ui
def test_edit_modal_done_checkbox_toggles_task_status(task_list_page, settings, unique_name):
    """Verifies that toggling Done via the Edit modal's checkbox updates the row's status."""
    user = settings.user()
    title = unique_name()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.add_task(title)
    page.verify_in_progress(title)

    page.task_table.begin_edit(title)
    page.edit_modal.set_done(True)
    page.edit_modal.save()
    page.task_table.wait_until_done(title, True)

    page.task_table.begin_edit(title)
    page.edit_modal.set_done(False)
    page.edit_modal.save()
    page.task_table.wait_until_done(title, False)

    page.delete_task(title)


@allure.feature("Tasks")
@pytest.mark.ui
@pytest.mark.negative
def test_add_task_close_button_discards_task(task_list_page, settings, unique_name):
    """Verifies that clicking Close on the Add modal does not create the task."""
    user = settings.user()
    title = unique_name()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)

    page.add_modal.open()
    page.add_modal.fill(title)
    page.add_modal.close()

    assert not page.has_task(
        title, timeout=3
    ), f"expected task '{title}' to be discarded after closing the Add modal"


@allure.feature("Tasks")
@pytest.mark.ui
@pytest.mark.negative
def test_edit_modal_close_button_discards_title_change(task_list_page, settings, unique_name):
    """Verifies that clicking Close on the Edit modal after changing the title leaves it unchanged."""
    user = settings.user()
    title = unique_name()
    new_title = unique_name()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.add_task(title)

    page.task_table.begin_edit(title)
    page.edit_modal.fill_title(new_title)
    page.edit_modal.close()

    assert page.has_task(title), f"expected original task '{title}' to still be present after closing Edit"
    assert not page.has_task(
        new_title, timeout=3
    ), f"expected discarded title '{new_title}' to never appear after closing Edit without saving"

    page.delete_task(title)


@allure.feature("Tasks")
@pytest.mark.ui
@pytest.mark.negative
def test_edit_modal_close_button_discards_done_change(task_list_page, settings, unique_name):
    """Verifies that clicking Close on the Edit modal after toggling Done leaves the status unchanged."""
    user = settings.user()
    title = unique_name()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.add_task(title)
    page.verify_in_progress(title)

    page.task_table.begin_edit(title)
    page.edit_modal.set_done(True)
    page.edit_modal.close()

    page.verify_in_progress(title)

    page.delete_task(title)


@allure.feature("Tasks")
@pytest.mark.ui
@pytest.mark.negative
@pytest.mark.xfail(
    reason="TM-32 (docs/known-defects-and-improvements.md): EditTaskViewModel.tags() holds the exact same "
    "tag objects as the row's own view model (not a copy), so renaming a tag in the Edit modal "
    "mutates the row's displayed tag immediately - before Save is even clicked - and Close does not "
    "revert it, even though no PATCH is ever sent. Remove xfail once the defect is fixed.",
    strict=True,
)
def test_edit_modal_close_button_discards_tag_rename(task_list_page, settings, unique_name):
    """Verifies that clicking Close on the Edit modal after renaming a tag leaves the tags unchanged."""
    user = settings.user()
    title = unique_name()
    page = task_list_page.load()
    page.sign_in(user.username, user.password)
    page.add_task(title, tags=["original"])
    original_tags = page.task_table.tags(title)

    page.task_table.begin_edit(title)
    page.edit_modal.rename_tag(0, "mutated")
    page.edit_modal.close()

    page.verify_tags(title, original_tags)

    page.delete_task(title)
