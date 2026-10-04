"""Component Object for the Add Task modal."""

import allure

from src.ui.components.base_modal_component import BaseModalComponent
from src.ui.locators import task_list_locators as locators


class AddTaskModalComponent(BaseModalComponent):
    """Opens the Add Task modal, fills title/tags, and submits (or closes/discards) it."""

    def __init__(self, driver):
        super().__init__(driver, locators.ADD_MODAL_TITLE_INPUT, locators.ADD_MODAL_CLOSE_BUTTON)

    @allure.step("Open the Add Task modal")
    def open(self) -> None:
        """Click "+ Add Task" and wait for the modal to render."""
        self.click(locators.ADD_TASK_BUTTON)
        self.wait_open()

    @allure.step("Fill Add Task modal: title='{title}', tags={tags}")
    def fill(self, title: str, tags: list[str] | None = None) -> None:
        """Fill the title and tags fields. The modal must already be open.

        Args:
            title: Title to type into the title field.
            tags: Tag names to type into the tags field, space-separated.
        """
        # Always types a real tag, even when `tags` is empty - works around TM-18
        # (docs/known-defects-and-improvements.md): an untouched Tags field silently aborts task creation.
        self.type_text(locators.ADD_MODAL_TITLE_INPUT, title, clear=False)
        self.type_text(locators.ADD_MODAL_TAGS_INPUT, " ".join(tags) if tags else "untagged", clear=False)

    @allure.step("Submit Add Task modal")
    def submit(self) -> None:
        """Click "Add task" and wait for the modal to close."""
        self.click(locators.ADD_MODAL_SUBMIT_BUTTON)
        self.wait_closed()

    @allure.step("Add task '{title}'")
    def add(self, title: str, tags: list[str] | None = None) -> None:
        """Open, fill, and submit the Add Task modal in one call.

        Args:
            title: Title of the task to create.
            tags: Tag names to assign to the task.
        """
        self.open()
        self.fill(title, tags)
        self.submit()

    @allure.step("Add task '{title}' with the Tags field left untouched (reproduces TM-18)")
    def add_with_untouched_tags(self, title: str) -> None:
        """Open the modal, fill only the title, and submit, leaving Tags untouched.

        Args:
            title: Title of the task to create.
        """
        self.open()
        self.type_text(locators.ADD_MODAL_TITLE_INPUT, title, clear=False)
        self.submit()

    def title_label_text(self) -> str:
        """Return the modal's header text."""
        return self.wait_visible(locators.ADD_MODAL_TITLE_LABEL).text

    def field_values(self) -> tuple[str, str]:
        """Return the current field values.

        Returns:
            Tuple of (title, tags) input values.
        """
        return self.get_value(locators.ADD_MODAL_TITLE_INPUT), self.get_value(locators.ADD_MODAL_TAGS_INPUT)
