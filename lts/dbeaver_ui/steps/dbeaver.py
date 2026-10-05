"""Steps for what a user does in DBeaver: start it, create a connection, run SQL
in the SQL editor, read the result grid and browse the navigator."""

import re
import time

from testflows.core import *

from lts.dbeaver_ui.steps.desktop import (
    click,
    click_element,
    clipboard,
    desktop,
    elements,
    field_for_label,
    fill_field,
    find,
    paste,
    press,
    screenshot,
    type_text,
    wait_for,
    wait_for_window,
    wait_until_gone,
)

WIZARD = "Connect to a database"
FETCHED = re.compile(r"\d+ row\(s\) fetched")


@TestStep(Given)
def main_window(self, dbeaver_version, timeout=240):
    """Wait for DBeaver's main window, accepting the first-run Product
    Configuration wizard if it shows, and maximize the window."""
    title = f"DBeaver {dbeaver_version}"
    deadline = time.time() + timeout
    while True:
        current = elements()
        if find(role="frame", name="Product Configuration", among=current):
            note("accepting the first-run Product Configuration wizard")
            click_element(role="push button", name="Apply", window="Product Configuration")
            wait_until_gone(role="frame", name="Product Configuration")
            continue
        if find(role="frame", name=title, among=current):
            break
        if time.time() > deadline:
            fail(f"no {title!r} window within {timeout}s; open windows: {desktop('windows')}")
        time.sleep(2)
    desktop("maximize")
    # Widgets below the screen's edge do not show, so the whole window must fit.
    for _ in range(10):
        x, y, width, height = find(role="frame", name=title)[0]["box"]
        if x >= 0 and y >= 0 and x + width <= 1920 and y + height <= 1080:
            return title
        time.sleep(1)
    fail(f"the main window {x},{y} {width}x{height} does not fit the 1920x1080 screen")


@TestStep(When)
def new_connection(self, driver="ClickHouse", host="localhost", port="8123", user="default"):
    """Create a connection through Database > New Database Connection, and leave
    the wizard open on the connection settings page."""
    with By("opening Database > New Database Connection"):
        click_element(role="menu", name="Database")
        click_element(role="menu item", name="New Database Connection")
        wait_for_window(name=WIZARD)
        screenshot(name="new_connection_wizard")

    with And(f"selecting the {driver} driver"):
        # The search box has the focus. Tab moves it to the driver gallery,
        # which selects the first match; the gallery is not accessible, so the
        # page that follows shows which driver was picked.
        type_text(driver)
        # The gallery filters a moment after typing stops; a Tab before
        # that selects nothing.
        time.sleep(2)
        press("Tab")
        screenshot(name="driver_selected")
        click_element(role="push button", name="Next >", window=WIZARD)
        wait_for(role="label", name="Driver name:", window=WIZARD, timeout=30)
        picked = field_driver_name()
        if picked != driver:
            fail(f"the wizard picked the {picked!r} driver, not {driver!r}")

    with And("filling in the connection settings"):
        for label, value in (("Host:", host), ("Port:", port)):
            shown = field_for_label(label, window=WIZARD)["text"]
            if shown != value:
                fill_field(label=label, value=value, window=WIZARD)
        fill_field(label="Username:", value=user, window=WIZARD)
        screenshot(name="connection_settings")


def field_driver_name():
    """Return the driver name the wizard shows next to ``Driver name:``."""
    current = elements()
    label = find(role="label", name="Driver name:", window=WIZARD, among=current)[0]
    lx, ly, lw, lh = label["box"]
    names = [e for e in current if e["role"] == "label" and e["window"] == WIZARD
             and e["box"][1] == ly and e["box"][0] > lx]
    if not names:
        fail("no driver name next to 'Driver name:'")
    return min(names, key=lambda e: e["box"][0])["name"]


@TestStep(When)
def test_connection(self, timeout=600):
    """Press Test Connection, download the driver if DBeaver asks to, and
    return what the Connection test dialog shows as
    ``(status, server, driver)``."""
    click_element(role="push button", name="Test Connection ...", window=WIZARD)
    deadline = time.time() + timeout
    clicked_download = None
    while True:
        current = elements()
        download = find(role="push button", name="Download", window="Driver settings", among=current)
        # The dialog first resolves the driver's Maven dependencies, and a
        # click on Download before that finishes does nothing. A label shows
        # what it is doing: "Resolve dependencies: ..." and then
        # "Download N/M - <url>".
        busy = [e for e in current if e["window"] == "Driver settings" and e["role"] == "label"
                and e["name"].startswith(("Resolve dependencies", "Download "))]
        resolving = any(e["name"].startswith("Resolve dependencies") for e in busy)
        if download and not resolving and (
                clicked_download is None or (not busy and time.time() - clicked_download > 15)):
            if clicked_download is None:
                screenshot(name="driver_download")
            note("DBeaver asks to download the driver files")
            click(element=download[0])
            clicked_download = time.time()
        elif find(role="frame", name="Connection test", among=current):
            break
        elif find(role="frame", name_prefix="Error", among=current) or \
                find(role="frame", name="Connection error", among=current):
            screenshot(name="connection_error")
            fail(f"connection test failed: {[e['name'] for e in current if e['role'] == 'label' and e['name']]}")
        if time.time() > deadline:
            screenshot(name="connection_test_timeout")
            fail(f"no Connection test result within {timeout}s; open windows: {desktop('windows')}")
        time.sleep(2)

    status = wait_for(role="label", name_prefix="Connect", window="Connection test")["name"]
    server = field_for_label("Server:", window="Connection test")["text"]
    driver = field_for_label("Driver:", window="Connection test")["text"]
    screenshot(name="connection_test")
    click_element(role="push button", name="OK", window="Connection test")
    wait_until_gone(role="frame", name="Connection test")
    return status, server, driver


@TestStep(When)
def finish_wizard(self, name="localhost"):
    """Press Finish and wait for the connection to show in the navigator."""
    click_element(role="push button", name="Finish", window=WIZARD)
    wait_until_gone(role="frame", name=WIZARD)
    return wait_for(role="table cell", name=name)


@TestStep(When)
def open_sql_editor(self, connection="localhost"):
    """Select the connection in the navigator and open a SQL editor for it
    with Ctrl+]."""
    click_element(role="table cell", name=connection)
    press("ctrl+bracketright")
    wait_for(role="page tab", name_prefix=f"<{connection}> Script")


def editor():
    """Return the SQL editor's text area: the editable multi-line text in the
    main window that is highest on the screen."""
    texts = [e for e in elements() if e["role"] == "text"
             and "editable" in e["states"] and "multi-line" in e["states"]
             and e["name"] == "" and e["box"][0] > 480]
    if not texts:
        fail("no SQL editor text area is showing")
    return min(texts, key=lambda e: e["box"][1])


def fetched_status():
    """Return the result panel's ``N row(s) fetched ...`` status line, or None."""
    for element in find(role="label"):
        if FETCHED.match(element["name"]):
            return element["name"]
    return None


@TestStep(When)
def run_query(self, sql, timeout=120):
    """Replace the SQL editor's text with ``sql``, run it with Ctrl+Enter, and
    return the result grid as a list of rows of strings.

    The rows are copied from the grid with Ctrl+A, Ctrl+C: the grid is drawn by
    DBeaver and its cells are not accessible.
    """
    before = fetched_status()
    click(element=editor())
    press("ctrl+a")
    paste(sql)
    press("ctrl+Return")

    deadline = time.time() + timeout
    while True:
        status = fetched_status()
        if status is not None and status != before:
            break
        errors = [e for e in elements() if e["name"].startswith("SQL Error")
                  or e["text"].startswith("SQL Error")]
        if errors:
            fail(f"DBeaver reports an error for {sql!r}: {errors[0]['name'] or errors[0]['text']}")
        if time.time() > deadline:
            fail(f"no result for {sql!r} within {timeout}s")
        time.sleep(1)
    note(status)

    # The results panel is the tab list below the editor that holds the
    # Refresh button. A click in its upper part lands in the grid.
    refresh = wait_for(role="push button", name="Refresh")
    rx, ry = refresh["box"][0], refresh["box"][1]
    panels = [e for e in find(role="page tab list")
              if e["box"][0] <= rx and e["box"][1] < ry < e["box"][1] + e["box"][3]]
    if not panels:
        fail("no result panel holds the Refresh button")
    panel = max(panels, key=lambda e: e["box"][1])
    x, y = panel["box"][0], panel["box"][1]
    desktop("click", str(x + 100), str(y + 110))
    press("ctrl+a", "ctrl+c")
    time.sleep(0.5)
    text = clipboard()
    if text == sql:
        fail("copying the result grid did not change the clipboard")
    return [line.split("\t") for line in text.split("\n")]


@TestStep(When)
def run_script(self, sql, timeout=300):
    """Replace the SQL editor's text with ``sql`` and run it as a script with
    Alt+X, then wait for DBeaver's script statistics."""
    click(element=editor())
    press("ctrl+a")
    paste(sql)
    press("alt+x")
    deadline = time.time() + timeout
    while True:
        current = elements()
        errors = [e for e in current if e["name"].startswith("SQL Error")
                  or e["text"].startswith("SQL Error")]
        if errors:
            fail(f"DBeaver reports an error: {errors[0]['name'] or errors[0]['text']}")
        if find(role="page tab", name="Statistics 1", among=current):
            return
        if time.time() > deadline:
            fail(f"the script did not finish within {timeout}s")
        time.sleep(1)


@TestStep(When)
def expand_node(self, name, timeout=60):
    """Select a navigator node and expand it with the Right key."""
    node = wait_for(role="table cell", name=name, timeout=timeout)
    click(element=node)
    press("Right")
    return node


@TestStep(When)
def refresh_node(self, name):
    """Select a navigator node and refresh it with F5."""
    click_element(role="table cell", name=name)
    press("F5")
