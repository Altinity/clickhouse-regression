# DBeaver UI suite — agent instructions

This suite runs [DBeaver] Community Edition itself and drives its user
interface, as the manual DBeaver check did: start DBeaver, create a connection
to a local ClickHouse server, create a dataset from the SQL editor, query it and
find it in the navigator, with a screenshot of each step. It follows the shared
conventions in [../AGENTS.md](../AGENTS.md).

The driver-level suite in [../dbeaver/](../dbeaver/AGENTS.md) replays DBeaver's
SQL through its JDBC driver without running DBeaver. Keep the two separate.

## How it works

One container, built from the ClickHouse image under test, runs the server,
Xvfb (1920x1080), openbox and DBeaver. The tests on the host run
`configs/desktop.py` in it with `docker exec` for every action.

DBeaver reports its windows and widgets through AT-SPI, the Linux accessibility
interface, with role, name and screen position. The tests find a widget by role
and name, for example `push button "Test Connection ..."` in the window
`Connect to a database`, and click the centre of its current box.

| File | Role |
|---|---|
| `configs/Dockerfile` | ClickHouse image + Xvfb, openbox, xdotool, wmctrl, xclip, AT-SPI + DBeaver CE |
| `configs/start.sh` | Starts ClickHouse via `/entrypoint.sh`, the display, D-Bus and the AT-SPI bus |
| `configs/desktop.py` | In the container: list elements, click, keys, type, paste, clipboard, screenshot |
| `steps/environment.py` | Builds the image, runs the container, saves logs, starts DBeaver |
| `steps/desktop.py` | Find and wait for elements, input fields by label, screenshots |
| `steps/dbeaver.py` | DBeaver actions: first run, new connection, test connection, run SQL, navigator |
| `tests/session.py` | The scenarios, in order, sharing one DBeaver session |
| `requirements/requirements.md` | SRS-107; regenerate `requirements.py` from it |

Run it:

```bash
python3 lts/regression.py --clickhouse docker://<image> --only "/lts/dbeaver-ui/*" --log test.log
```

`--dbeaver-version <tag>` selects the DBeaver CE release (default `26.2.1`),
shared with the driver-level suite.

## Rules

- **Find widgets by role and name, never by fixed coordinates.** The only
  computed click is into the result grid, relative to the results panel found
  through its Refresh button.
- **What AT-SPI does not show, and what to do instead:**
  - The driver gallery of the New Database Connection wizard is drawn by
    DBeaver. Type the driver name, wait for the filter, press Tab (selects the
    first match), press Next, then check `Driver name:` on the next page.
  - The result grid is drawn by DBeaver. Copy it with Ctrl+A, Ctrl+C and
    compare the clipboard with exact rows.
  - Input fields have no name. Find the text field right of its label
    (`field_for_label`).
  - Toolbar icons have no names. Use the menu or keyboard shortcuts.
- **Paste SQL, don't type it.** Typing goes through autocomplete, which
  rewrites the SQL.
- **Assert exact values.** Check the dataset on the server with
  `clickhouse-client` too, and compare each query's grid with every row.
- **Push buttons never report `enabled`.** Don't wait for that state.
- **Keep the window maximized through wmctrl.** Resizing it to the screen size
  with xdotool pushes the bottom (results toolbar and status line) off the
  screen, and widgets off the screen are not reported. `main_window` fails when
  the window does not fit.
- **Wait for DBeaver's own progress.** A click on Download while the dialog
  still shows `Resolve dependencies: ...` does nothing; `test_connection`
  waits for it.

## Known behavior

- A new workspace shows the Product Configuration wizard first; the suite
  presses Apply.
- DBeaver downloads the ClickHouse JDBC driver from Maven Central on the first
  Test Connection. It needs internet access and can take minutes on a slow
  connection; `test_connection` allows 10 minutes.

## Before you finish

1. Run the suite against the default image. All scenarios pass, and
   `lts/_instances/dbeaver_ui/screenshots/` has a screenshot of each step.
2. Show that a new or changed check can fail. Run against an image whose
   `users.d` profile sets a silent `<limit>5</limit>`, or `<readonly>1</readonly>`
   (see [../DEBUGGING.md](../DEBUGGING.md#proving-that-a-check-can-fail)).
3. Regenerate `requirements.py` if you changed `requirements.md`.
4. Update this file if a rule or known behavior changed.

## Evidence

`lts/_instances/dbeaver_ui/`: `screenshots/NN_<step>.png`, and in `logs/`:
`build.log`, `clickhouse-server.log`, `dbeaver.log` (DBeaver's output, including
the Maven URLs of the driver download), `dbeaver-debug.log` and `container.log`.

[DBeaver]: https://github.com/dbeaver/dbeaver
