"""Find, click and read DBeaver's widgets through the accessibility bus.

Elements are found by their accessible role and name, as AT-SPI reports them,
never by fixed coordinates: a click goes to the centre of the element's
current box. ``configs/desktop.py`` runs in the container and does the work.
"""

import json
import os
import time

from testflows.core import *

from lts.steps.docker import screenshots_dir
from lts.dbeaver_ui.steps.environment import SUITE, docker_exec

screenshot_number = [0]


def desktop(*args, timeout=120):
    """Run one ``desktop.py`` command in the container and return its JSON result."""
    return json.loads(docker_exec("python3", "/desktop.py", *args, timeout=timeout))


def elements():
    """Return the showing elements, without the duplicates that SWT reports
    for some widgets (same role, name and box)."""
    seen = set()
    unique = []
    for element in desktop("elements"):
        key = (element["role"], element["name"], tuple(element["box"]))
        if key not in seen:
            seen.add(key)
            unique.append(element)
    return unique


def find(role=None, name=None, window=None, name_prefix=None, among=None):
    """Return the showing elements that match every given condition."""
    matches = []
    for element in among if among is not None else elements():
        if role is not None and element["role"] != role:
            continue
        if name is not None and element["name"] != name:
            continue
        if name_prefix is not None and not element["name"].startswith(name_prefix):
            continue
        if window is not None and element["window"] != window:
            continue
        matches.append(element)
    return matches


def describe(role=None, name=None, window=None, name_prefix=None):
    parts = [role or "element"]
    if name is not None:
        parts.append(repr(name))
    if name_prefix is not None:
        parts.append(f"starting with {name_prefix!r}")
    if window is not None:
        parts.append(f"in window {window!r}")
    return " ".join(parts)


@TestStep(When)
def wait_for(self, role=None, name=None, window=None, name_prefix=None, timeout=60):
    """Wait until an element matching the conditions shows, and return it."""
    deadline = time.time() + timeout
    while True:
        matches = find(role=role, name=name, window=window, name_prefix=name_prefix)
        if matches:
            return matches[0]
        if time.time() > deadline:
            fail(f"{describe(role, name, window, name_prefix)} did not show within {timeout}s; "
                 f"open windows: {desktop('windows')}")
        time.sleep(1)


@TestStep(When)
def wait_for_window(self, name=None, name_prefix=None, timeout=60):
    """Wait until a top-level window shows, and return it."""
    return wait_for(role="frame", name=name, name_prefix=name_prefix, timeout=timeout)


@TestStep(When)
def wait_until_gone(self, role=None, name=None, window=None, timeout=60):
    """Wait until no element matching the conditions shows."""
    deadline = time.time() + timeout
    while find(role=role, name=name, window=window):
        if time.time() > deadline:
            fail(f"{describe(role, name, window)} still showing after {timeout}s")
        time.sleep(1)


def centre(element):
    x, y, width, height = element["box"]
    return x + width // 2, y + height // 2


def click(element):
    """Click the centre of an element."""
    x, y = centre(element)
    note(f"click {element['role']} {element['name']!r} at {x},{y}")
    desktop("click", str(x), str(y))


@TestStep(When)
def click_element(self, role, name, window=None, timeout=60):
    """Wait for an element and click it."""
    element = wait_for(role=role, name=name, window=window, timeout=timeout)
    click(element=element)
    return element


def press(*keys):
    """Press keys, for example ``press("ctrl+a", "ctrl+c")``."""
    note(f"press {' '.join(keys)}")
    desktop("key", *keys)


def type_text(text):
    """Type ``text`` with the keyboard."""
    desktop("type", text)


def paste(text):
    """Paste ``text`` from the clipboard. Typing SQL into DBeaver's editor goes
    through autocomplete, which changes it; pasting does not."""
    desktop("paste", text)


def clipboard():
    """Return the clipboard's contents."""
    return desktop("clipboard")


def field_for_label(label, window=None):
    """Return the text field on the same row as ``label`` and right of it.

    DBeaver's input fields have no accessible name; their label is a separate
    element to the left.
    """
    current = elements()
    labels = find(role="label", name=label, window=window, among=current)
    if not labels:
        fail(f"no label {label!r} in window {window!r}")
    lx, ly, lw, lh = labels[0]["box"]
    label_middle = ly + lh / 2
    fields = []
    for element in current:
        if element["role"] not in ("text", "password text"):
            continue
        if window is not None and element["window"] != window:
            continue
        x, y, width, height = element["box"]
        if x >= lx + lw and y <= label_middle <= y + height:
            fields.append(element)
    if not fields:
        fail(f"no input field right of label {label!r}")
    return min(fields, key=lambda element: element["box"][0])


@TestStep(When)
def fill_field(self, label, value, window=None):
    """Click the field labelled ``label``, replace its text with ``value``, and
    check that the field shows it."""
    click(element=field_for_label(label, window=window))
    press("ctrl+a")
    type_text(value)
    shown = field_for_label(label, window=window)["text"]
    if shown != value:
        fail(f"field {label!r} shows {shown!r} after typing {value!r}")


@TestStep(Then)
def screenshot(self, name):
    """Save a numbered screenshot of the whole screen to
    ``lts/_instances/dbeaver_ui/screenshots/`` and attach its path."""
    screenshots_dir(SUITE)
    screenshot_number[0] += 1
    filename = f"{screenshot_number[0]:02d}_{name}.png"
    desktop("screenshot", f"/results/screenshots/{filename}")
    path = os.path.join(screenshots_dir(SUITE), filename)
    metric(name=name, value=path, units="screenshot")
    return path
