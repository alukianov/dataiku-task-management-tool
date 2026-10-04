"""Locators for TaskListPage (web/index.html)."""

from selenium.webdriver.common.by import By


def xpath(expression: str) -> tuple[str, str]:
    """Wrap an XPath expression as a `By.XPATH` locator tuple.

    Args:
        expression: XPath expression.

    Returns:
        The `(By.XPATH, expression)` locator tuple.
    """
    return (By.XPATH, expression)


ADD_MODAL = "//*[@id='add']"
EDIT_MODAL = "//*[@id='edit']"

TASK_TABLE = xpath("//table")
TASK_ROWS = xpath("//table/tbody/tr")

# Navbar / authentication
NAVBAR_BRAND = xpath("//a[contains(@class,'navbar-brand')]")
USERNAME_INPUT = (By.NAME, "username")
PASSWORD_INPUT = (By.NAME, "password")
SIGN_IN_BUTTON = xpath("//button[@data-bind='click: authenticate']")
SIGN_OUT_BUTTON = xpath("//button[@data-bind='click: logout']")
NAVBAR_USERNAME_DISPLAY = xpath("//button[@data-bind='click: logout']//span[@data-bind='text: username']")

# Add-task modal
ADD_TASK_BUTTON = (By.ID, "btn-add")
ADD_MODAL_TITLE_LABEL = xpath(f"{ADD_MODAL}//h4[@class='modal-title']")
ADD_MODAL_TITLE_INPUT = xpath(f"{ADD_MODAL}//input[@data-bind='value: title']")
ADD_MODAL_TAGS_INPUT = xpath(f"{ADD_MODAL}//input[@data-bind='value: tags']")
ADD_MODAL_SUBMIT_BUTTON = xpath(f"{ADD_MODAL}//button[@data-bind='click:addTask']")
ADD_MODAL_CLOSE_BUTTON = xpath(f"{ADD_MODAL}//button[@data-dismiss='modal']")

# Edit-task modal
EDIT_MODAL_TITLE_LABEL = xpath(f"{EDIT_MODAL}//h4[@class='modal-title']")
EDIT_MODAL_TITLE_INPUT = xpath(f"{EDIT_MODAL}//input[@data-bind='value: title']")
EDIT_MODAL_DONE_CHECKBOX = xpath(f"{EDIT_MODAL}//input[@data-bind='checked: done']")
EDIT_MODAL_TAG_INPUTS = (By.ID, "inputTags")
EDIT_MODAL_TAGS_SECTION = xpath(
    f"{EDIT_MODAL}//span[contains(@class,'input-group-addon') and normalize-space(text())='Tags']"
    "/parent::div"
)
EDIT_MODAL_SUBMIT_BUTTON = xpath(f"{EDIT_MODAL}//button[@data-bind='click:editTask']")
EDIT_MODAL_CLOSE_BUTTON = xpath(f"{EDIT_MODAL}//button[@data-dismiss='modal']")

# Error/warning banners
WARNING_ALERTS = xpath("//div[contains(@class,'alert-warning')]")
WARNING_ALERT_TEXT = xpath("//div[contains(@class,'alert-warning')]//span[contains(@class,'error-text')]")
WARNING_ALERT_STATUS = xpath("//div[contains(@class,'alert-warning')]//span[contains(@class,'error-status')]")
DANGER_ALERTS = xpath("//div[contains(@class,'alert-danger')]")

# Per-row controls, queried relative to the row WebElement from row_by_title()
ROW_OWNER = xpath(".//b[@data-bind='text: username']")
ROW_EDIT_BUTTON = xpath(".//button[contains(@class,'glyphicon-pencil')]")
ROW_DELETE_BUTTON = xpath(".//button[contains(@class,'glyphicon-trash')]")
ROW_MARK_DONE_BUTTON = xpath(".//button[contains(@class,'glyphicon-ok')]")
ROW_MARK_IN_PROGRESS_BUTTON = xpath(".//button[contains(@class,'glyphicon-list-alt')]")
ROW_DONE_LABEL = xpath(".//span[contains(@class,'label-success')]")
ROW_TAGS = xpath(".//span[contains(@class,'task-tag')]")


def row_by_title(title: str):
    """Build a document-level locator for the task row whose title cell matches `title` exactly.

    Args:
        title: Task title to match.

    Returns:
        The `By.XPATH` locator tuple for that row.
    """
    return xpath(f"//tr[.//b[normalize-space(text())='{title}']]")
