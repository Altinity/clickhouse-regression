"""Steps for what a user does in DBeaver: start it, create a connection, run SQL
in the SQL editor, read the result grid and browse the navigator."""

import time

from testflows.core import *

from lts.dbeaver_ui.steps.environment import clickhouse_query
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
    select_node(wait_for(role="table cell", name=connection))
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


def results_panel():
    """Return the results panel: the tab list below the SQL editor, in the
    main window, that is lowest on the screen."""
    panels = [e for e in find(role="page tab list")
              if 480 < e["box"][0] < 1490 and e["box"][1] > 300 and e["box"][2] > 500]
    if not panels:
        fail("no results panel is showing below the SQL editor")
    return max(panels, key=lambda e: e["box"][1])


def copy_grid():
    """Copy the result grid with Ctrl+A, Ctrl+C and return the clipboard. A
    click in the upper part of the results panel lands in the grid."""
    x, y = results_panel()["box"][:2]
    desktop("click", str(x + 100), str(y + 110))
    press("ctrl+a", "ctrl+c")
    time.sleep(0.5)
    return clipboard()


# The grid copied for the previous query. A query's result is ready when the
# grid's copy differs from it, so two queries in a row must not return the
# same rows.
last_grid = [None]
query_number = [0]


@TestStep(When)
def run_query(self, sql, timeout=120):
    """Replace the SQL editor's text with ``sql``, run it with Ctrl+Enter, and
    return the result grid as a list of rows of strings.

    The query is tagged with ``SETTINGS log_comment``, so the server's
    ``system.query_log`` shows when DBeaver sent it and when it finished. The
    rows are then copied from the grid with Ctrl+A, Ctrl+C, because the grid is
    drawn by DBeaver and its cells are not accessible.
    """
    query_number[0] += 1
    marker = f"lts-dbeaver-ui-{query_number[0]}"
    click(element=editor())
    press("ctrl+a")
    paste(f"{sql} SETTINGS log_comment = '{marker}'")
    press("ctrl+Return")

    deadline = time.time() + timeout
    while True:
        finished = clickhouse_query(
            "SYSTEM FLUSH LOGS; SELECT type FROM system.query_log "
            f"WHERE log_comment = '{marker}' AND type != 'QueryStart' FORMAT TSV")
        if finished:
            break
        errors = [e for e in elements() if e["name"].startswith("SQL Error")
                  or e["text"].startswith("SQL Error")]
        if errors:
            fail(f"DBeaver reports an error for {sql!r}: {errors[0]['name'] or errors[0]['text']}")
        if time.time() > deadline:
            screenshot(name="query_timeout")
            fail(f"the server did not finish {sql!r} from DBeaver within {timeout}s")
        time.sleep(1)
    if finished != "QueryFinish":
        fail(f"the server reports {finished} for {sql!r}")

    while True:
        text = copy_grid()
        if text != last_grid[0] and not text.endswith(f"'{marker}'"):
            break
        if time.time() > deadline:
            screenshot(name="grid_timeout")
            fail(f"the result grid still shows the previous result {text!r}")
        time.sleep(1)
    last_grid[0] = text
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


def select_node(node, attempts=5):
    """Click a navigator node on its name until it is selected.

    A tree cell spans the whole width of the navigator, and a click on the
    empty space right of the name does not select the row. A refresh (F5)
    that is still running rebuilds the tree and drops the selection, so the
    node is found again and clicked again until the selection sticks.
    """
    name = node["name"]
    for attempt in range(1, attempts + 1):
        x, y, width, height = node["box"]
        desktop("click", str(x + min(20, width // 2)), str(y + height // 2))
        for _ in range(6):
            time.sleep(0.5)
            matches = find(role="table cell", name=name)
            if any("selected" in e["states"] for e in matches):
                return
        note(f"navigator node {name!r} at {node['box']} not selected after click {attempt}")
        node = wait_for(role="table cell", name=name)
    screenshot(name="node_not_selected")
    fail(f"clicking navigator node {name!r} {attempts} times did not select it")


@TestStep(When)
def expand_node(self, name, timeout=60):
    """Select a navigator node and expand it with the Right key."""
    node = wait_for(role="table cell", name=name, timeout=timeout)
    select_node(node)
    press("Right")
    return node


@TestStep(When)
def refresh_node(self, name):
    """Select a navigator node and refresh it with F5."""
    select_node(wait_for(role="table cell", name=name))
    press("F5")
