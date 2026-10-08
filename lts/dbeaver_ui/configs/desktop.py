"""Drive the X desktop inside the DBeaver container.

The test steps run this with `docker exec`; every command prints JSON.

  desktop.py elements              showing accessible elements, with boxes and states
  desktop.py click X Y             left click at screen coordinates
  desktop.py key KEYS...           xdotool key names, for example ctrl+Return
  desktop.py type TEXT             type text with the keyboard
  desktop.py paste TEXT            put TEXT on the clipboard and press ctrl+v
  desktop.py clipboard             print the clipboard
  desktop.py screenshot PATH       save a PNG of the screen
  desktop.py windows               names of the top-level windows
  desktop.py maximize              fill the screen with the active window
"""
import json
import os
import subprocess
import sys

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

os.environ.setdefault("DISPLAY", ":99")

STATES = {
    "enabled": Atspi.StateType.ENABLED,
    "focused": Atspi.StateType.FOCUSED,
    "selected": Atspi.StateType.SELECTED,
    "checked": Atspi.StateType.CHECKED,
    "expanded": Atspi.StateType.EXPANDED,
    "editable": Atspi.StateType.EDITABLE,
    "multi-line": Atspi.StateType.MULTI_LINE,
}


def elements():
    """Return every showing element of every application, depth first.

    Applications themselves have no SHOWING state, so depth 0 is not filtered.
    """
    found = []

    def walk(node, depth, window):
        try:
            states = node.get_state_set()
            if depth > 0 and not states.contains(Atspi.StateType.SHOWING):
                return
            role = node.get_role_name()
            name = (node.get_name() or "").strip()
            if role in ("frame", "dialog", "window"):
                window = name
            extents = node.get_extents(Atspi.CoordType.SCREEN)
            if depth > 0 and extents.width > 0 and extents.height > 0:
                text = ""
                if role in ("text", "password text", "label"):
                    try:
                        text = Atspi.Text.get_text(node, 0, -1)
                    except Exception:
                        text = ""
                found.append({
                    "role": role,
                    "name": name,
                    "text": text,
                    "window": window,
                    "box": [extents.x, extents.y, extents.width, extents.height],
                    "states": [k for k, v in STATES.items() if states.contains(v)],
                })
            for i in range(node.get_child_count()):
                walk(node.get_child_at_index(i), depth + 1, window)
        except Exception:
            pass

    desktop = Atspi.get_desktop(0)
    for i in range(desktop.get_child_count()):
        walk(desktop.get_child_at_index(i), 0, "")
    return found


def xdotool(*args):
    subprocess.run(["xdotool", *args], check=True)


def main():
    command, *args = sys.argv[1:]
    result = {"ok": True}
    if command == "elements":
        result = elements()
    elif command == "windows":
        result = [e["name"] for e in elements() if e["role"] in ("frame", "dialog")]
    elif command == "maximize":
        # Through the window manager, so the title bar counts: resizing the
        # window to the screen size pushes its bottom edge off the screen.
        subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-b", "add,maximized_vert,maximized_horz"], check=True)
    elif command == "click":
        xdotool("mousemove", args[0], args[1], "click", "1")
    elif command == "key":
        xdotool("key", "--delay", "50", *args)
    elif command == "type":
        xdotool("type", "--delay", "30", args[0])
    elif command == "paste":
        subprocess.run(["xclip", "-selection", "clipboard"], input=args[0].encode(), check=True)
        xdotool("key", "ctrl+v")
    elif command == "clipboard":
        out = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True)
        result = out.stdout.decode(errors="replace")
    elif command == "screenshot":
        subprocess.run(["scrot", "-o", args[0]], check=True)
    else:
        sys.exit(f"unknown command {command}")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
