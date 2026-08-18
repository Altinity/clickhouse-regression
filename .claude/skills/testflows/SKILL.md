---
name: testflows
description: Retrieve and analyze TestFlows logs with tfs, then inspect ClickHouse _instances server error logs. Use when analyzing TestFlows test failures, reading test.log/raw.log, running tfs show/transform/report/document, debugging a local regression.py run, or looking at clickhouse-server.err.log under _instances.
---

# TestFlows Failure Analysis

Source of truth for the framework: [TestFlows Handbook](https://testflows.com/handbook).

This skill is for Cursor models analyzing **why a TestFlows test failed**. There are two independent log sources:

| Source | What it is | How to get it |
| --- | --- | --- |
| TestFlows log (`test.log` / `raw.log`) | What the **test program** did (steps, asserts, exceptions) | `tfs log` or `--log` / CI artifacts |
| `_instances/` | What **ClickHouse** did (server errors, crashes, stack traces) | suite-local folder; **not** TestFlows |

Read [tfs-commands.md](tfs-commands.md) for the full `tfs` catalog. Read [instances.md](instances.md) for `_instances` layout and ClickHouse error logs.

---

## 1. Get the TestFlows log

Logs are LZMA-compressed JSON. Pass the file to `tfs`; do not decompress first unless you need raw JSON.

### Local run that already used `--log` / `-l`

```bash
python3 regression.py --local --clickhouse <url> --only "/alter/.../*" -l test.log
```

Use that `test.log` file (usually in the suite directory: `alter/test.log`, `cas/test.log`).

### Local run in a terminal **without** `--log`

TestFlows still writes a temporary log. Copy the latest one:

```bash
tfs log test.log
```

The log appears in `test.log` in the current directory.

### CI artifacts

CI names the same log `raw.log` and also publishes derived files:

| File | Use |
| --- | --- |
| `raw.log` | Full TestFlows log (may still be xz-compressed) |
| `nice-new-fails.log.txt` | Human-readable **new** fails (start here) |
| `fails.log.txt` | All fails including known/xfailed |
| `report.html` | Results report |

If `raw.log` is xz-compressed and `tfs` cannot read it:

```bash
xzcat raw.log > test.log
```

---

## 2. Find what failed

Parent tests Fail when a child Fails. The **leaf** (deepest path) is the actual failure.

```bash
cat test.log | tfs show fails
cat test.log | tfs show fails -n          # new fails only (not XFail)
cat test.log | tfs transform nice-fails
cat test.log | tfs transform nice-new-fails
cat test.log | tfs show totals
cat test.log | tfs show results
```

Results: `OK`, `Fail`, `Error`, `Null`, `Skip`, plus crossed `XOK` / `XFail` / `XError` / `XNull` (treated as passing).

---

## 3. Get messages for one failing test

Copy the full test path from `tfs show fails`. Regex-special characters in the name (`*`, `(`, `)`, `.`, `[`, `]`) must be escaped.

```bash
cat test.log | tfs show messages "/alter/table/attach partition/..."
cat test.log | tfs show messages --format raw "/path/to/test"
cat test.log | tfs show procedure "/path/to/test"
cat test.log | tfs show result "/path/to/test"
cat test.log | tfs show details "/path/to/test"
```

`--format nice` (default) is readable. `--format raw` is JSON messages.

If `tfs show messages` is empty or the name does not match, list tests then retry:

```bash
cat test.log | tfs show tests | rg -i "attach partition"
```

---

## 4. Then read ClickHouse logs (`_instances`)

The TestFlows log is not the ClickHouse server log. After you know the failing test, inspect `_instances` on **every node**. Start with `clickhouse-server.err.log`. See [instances.md](instances.md).

Typical correlation:

1. Timestamp of the Fail in `tfs show messages`
2. Same window in `_instances/clickhouseN/logs/clickhouse-server.err.log`
3. Query id / table name from the test step in the server log
4. Stack trace / `LOGICAL_ERROR` / sanitizer / signal in `.err.log` or `stderr.log`
5. Cores under `_instances/clickhouseN/database/cores/`

---

## 5. Failure analysis output

Lead with the leaf test and the ClickHouse error (if any). Then:

- **Leaf test path** and result (`Fail` vs `Error`)
- **Assert / exception** from `tfs show messages` (last `Then` / traceback)
- **ClickHouse error** from `.err.log` (code, exception name, query)
- **Node** (`clickhouse1` vs `clickhouse2` vs `clickhouse3`)
- **Known xfail?** (parent `xfails` dict in `regression.py`, or `XFail` in the log)
- **Crash?** (`<Fatal>`, sanitizer, `Aborted`, core file) vs expected SQL error vs test bug

Do not treat ancestor Fails as separate bugs.

---

## Filtering tests when re-running

Patterns are unix-like paths. End with `/*` or nested steps are skipped (except `Given` / `Finally`, which are mandatory).

```bash
python3 regression.py --only "/alter/table/attach partition/feature/*" -l test.log
python3 regression.py --only "attach partition/*"          # relative → anchored at top test
python3 regression.py --only "/alter/:/*" --show-skipped
```

Wildcards: `*` any chars, `?` one char, `:` one path level, `[seq]` / `[!seq]`. Literal `*` in a name: `[*]`.

Handbook: [Filtering Tests By Name](https://testflows.com/handbook/#Filtering-Tests-By-Name).

---

## Saving a log on the next run

```bash
python3 regression.py -l test.log
python3 regression.py --log test.log
```

Without `-l`, recover afterwards with `tfs log test.log`.
