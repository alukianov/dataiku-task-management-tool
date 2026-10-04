"""Component Object for the Edit Task modal."""

import allure

from src.ui.components.base_modal_component import BaseModalComponent
from src.ui.locators import task_list_locators as locators


class EditTaskModalComponent(BaseModalComponent):
    """Fills/submits (or closes/discards) the Edit Task modal.

    Assumes the modal is already open - see `TaskTableComponent.begin_edit`, which clicks the
    specific row's Edit button to open it.
    """

    def __init__(self, driver):
        super().__init__(driver, locators.EDIT_MODAL_TITLE_INPUT, locators.EDIT_MODAL_CLOSE_BUTTON)

    @allure.step("Fill Edit Task modal title as '{new_title}'")
    def fill_title(self, new_title: str) -> None:
        """Replace the modal's title field with `new_title`. Does not save.

        Args:
            new_title: New title to type into the title field.
        """
        self.wait_open()
        self.type_text(locators.EDIT_MODAL_TITLE_INPUT, new_title)

    @allure.step("Rename tag #{index} to '{new_name}'")
    def rename_tag(self, index: int, new_name: str) -> None:
        """Replace the name of the `index`-th rendered tag input. Does not save.

        Args:
            index: Zero-based index of the rendered tag input to rename.
            new_name: New tag name to type into that input.
        """
        tag_input = self.driver.find_elements(*locators.EDIT_MODAL_TAG_INPUTS)[index]
        tag_input.clear()
        tag_input.send_keys(new_name)

    def tag_input_count(self) -> int:
        """Return how many rename-in-place tag inputs are currently rendered."""
        return len(self.driver.find_elements(*locators.EDIT_MODAL_TAG_INPUTS))

    def tag_section_button_count(self) -> int:
        """Return how many buttons exist inside the Tags section."""
        tags_section = self.driver.find_element(*locators.EDIT_MODAL_TAGS_SECTION)
        return self.count_tag_within(tags_section, "button")

    @allure.step("Set Edit Task modal Done checkbox to {value}")
    def set_done(self, value: bool) -> None:
        """Check/uncheck the modal's Done checkbox so it matches `value`. Does not save.

        Args:
            value: Desired checkbox state.
        """
        checkbox = self.wait_visible(locators.EDIT_MODAL_DONE_CHECKBOX)
        if checkbox.is_selected() != value:
            checkbox.click()

    @allure.step("Save Edit Task modal")
    def save(self) -> None:
        """Click "Save changes" and wait for the modal to close."""
        self.click(locators.EDIT_MODAL_SUBMIT_BUTTON)
        self.wait_closed()

    @allure.step("Save task title as '{new_title}'")
    def save_title(self, new_title: str) -> None:
        """Replace the modal's title field with `new_title` and save.

        Args:
            new_title: New title to save.
        """
        self.fill_title(new_title)
        self.save()
