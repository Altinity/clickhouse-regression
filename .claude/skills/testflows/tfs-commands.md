# tfs command catalog

Installed CLI: TestFlows `tfs` (this repo: v2.0.x). Handbook: https://testflows.com/handbook

Most log commands read **stdin** by default. Pipe the log:

```bash
cat test.log | tfs <command>
tfs <command> test.log
```

`--no-colors` is useful when capturing output for analysis.

```bash
tfs --no-colors show fails test.log
```

---

## Retrieve last log

```bash
tfs log test.log          # copy last temporary log → test.log
tfs log -                 # print to stdout
```

Use this after a terminal run that did **not** pass `-l` / `--log`.

---

## Run a test program

```bash
tfs run regression.py -- --only "/suite/test/*" -l test.log
tfs run --pid run.pid --stdout run.out --stderr run.err regression.py -- -o classic
tfs run --exitcode run.exitcode regression.py
tfs run -q --stdout run.out --stderr run.err regression.py -- -o classic
```

`--` separates `tfs run` options from the test program arguments. If `--stdout` or `--stderr` is set, `--no-colors` is applied to the program unless you pass `--no-colors off`.

In this repo, suites are usually run directly:

```bash
cd alter && python3 regression.py --local --clickhouse <url> --only "/alter/.../*" -l test.log
```

---

## Show test data (`tfs show`)

| Command | Purpose |
| --- | --- |
| `tfs show fails` | Failed tests (`-n` / `--new` = new fails only) |
| `tfs show passing` | Passing tests |
| `tfs show results` | All results |
| `tfs show result [name]` | Result of one test |
| `tfs show totals` | Counts |
| `tfs show unstable` | Unstable tests |
| `tfs show tests [name]` | Tests in the log |
| `tfs show messages [name]` | Messages (`-f nice\|raw`) |
| `tfs show procedure [name]` | Procedure (Given/When/Then) |
| `tfs show details [name]` | Details |
| `tfs show description [name]` | Description |
| `tfs show arguments [name]` | Arguments |
| `tfs show attributes [name]` | Attributes |
| `tfs show requirements [name]` | Linked requirements |
| `tfs show tags [name]` | Tags |
| `tfs show metrics [name]` | Metrics |
| `tfs show examples [name]` | Examples |
| `tfs show specifications [name]` | Specifications |
| `tfs show coverage` | Coverage |
| `tfs show version` | Framework version used in the log |

Commands that take `[name]` also accept `--log` / `--output`:

```bash
cat test.log | tfs show messages "/path/to/test"
cat test.log | tfs show messages -f raw "/path/to/test"
cat test.log | tfs show procedure "/path/to/test"
cat test.log | tfs show fails -n
```

Test names with regex-special characters (`* ( ) . [ ]`) must be escaped when passed as `name`.

README equivalent: `tfs show messages` (not `tfs show test messages`).

---

## Transform logs (`tfs transform`)

Readable views of the compressed log:

| Command | Output |
| --- | --- |
| `tfs transform nice` | Default stdout-style (timestamps, steps, results) |
| `tfs transform pnice` | Parallel nice |
| `tfs transform brisk` | Brisk |
| `tfs transform plain` | Plain |
| `tfs transform short` | Procedures + results |
| `tfs transform slick` | Names with result icons |
| `tfs transform classic` | Classic |
| `tfs transform manual` | Manual |
| `tfs transform dots` | One dot per test |
| `tfs transform raw` | Raw JSON messages |
| `tfs transform compact` | Compact JSON (results; `--with-steps` / `--without-steps`) |
| `tfs transform compress` | LZMA compress |
| `tfs transform decompress` | LZMA decompress |

Fail-focused transforms (use these for analysis):

| Command | Output |
| --- | --- |
| `tfs transform fails` | Fail summary (`-n` new; `--nice` `--pnice` `--brisk`) |
| `tfs transform new-fails` | New fails |
| `tfs transform nice-fails` | Nice fail summary |
| `tfs transform nice-new-fails` | Nice **new** fails (CI artifact) |
| `tfs transform brisk-fails` | Brisk fails |
| `tfs transform brisk-new-fails` | Brisk new fails |
| `tfs transform plain-fails` | Plain fails |
| `tfs transform plain-new-fails` | Plain new fails |
| `tfs transform pnice-fails` | Parallel nice fails |
| `tfs transform pnice-new-fails` | Parallel nice new fails |

```bash
cat test.log | tfs transform nice
cat test.log | tfs transform nice-fails
cat test.log | tfs transform nice-new-fails
cat test.log | tfs transform fails --new --nice
cat test.log | tfs transform decompress | rg '"message_keyword":"EXCEPTION"'
```

Decompress without `tfs`:

```bash
xzcat test.log
```

---

## Reports (`tfs report`)

```bash
cat test.log | tfs report results
cat test.log | tfs report results --format json
cat test.log | tfs report results | tfs document convert > report.html
cat test.log | tfs report results -a "$ARTIFACTS_URL" --copyright "Altinity Inc." --logo ./altinity.png | tfs document convert > report.html

cat test.log | tfs report coverage requirements.py | tfs document convert > coverage.html
cat test.log | tfs report coverage --show unsatisfied untested

cat test.log | tfs report specification | tfs document convert > specification.html
cat test.log | tfs report traceability | tfs document convert > traceability.html
cat test.log | tfs report metrics                    # openmetrics (default) or --format csv
```

Compare runs:

```bash
tfs report compare results --log 'run-*/test.log'
tfs report compare metrics --log 'run-*/test.log' --name test-time
```

`--format md` (default) or `json` on results. Coverage `--show`: `satisfied`, `unsatisfied`, `untested`.

---

## Documents (`tfs document`)

```bash
# Markdown → HTML (used after tfs report *)
cat report.md | tfs document convert > report.html
tfs document convert -f html -s custom.css report.md report.html

# Table of contents
tfs document toc README.md
tfs document toc --update README.md          # rewrite file with updated TOC
tfs document toc --heading "Contents"

# New SRS stub
tfs document new requirements > srs.md
```

Handbook also describes executable `.tfd` docs via `testflows.texts` (`pip3 install testflows.texts`):

```bash
tfs document run -i my_document.tfd -o my_document.md
tfs document run -i test.tfd -o -
tfs document run -- --help
tfs document run -i test.tfd -o test.md -- --output classic
```

`.tfd` files are Markdown with `python:testflows` code blocks. Outside those blocks, text is an f-string: escape `{` / `}` as `{{` / `}}`. No raw `"""` in the document body.

---

## Requirements (`tfs requirements`)

```bash
tfs requirements generate -h
cat srs.md | tfs requirements generate > requirements.py
```

Do not edit generated `requirements.py` by hand; regenerate from the Markdown SRS.

---

## Other commands

```bash
tfs snapshots rewrite ...
tfs database create ...
tfs ssl new
tfs ssl show
```

Rarely needed for failure analysis.

---

## Test program options (not `tfs`, passed to `regression.py`)

| Option | Meaning |
| --- | --- |
| `-l` / `--log FILE` | Save TestFlows log |
| `--only PATTERN ...` | Run matching tests (end with `/*`) |
| `--skip PATTERN ...` | Skip matching tests |
| `--only-tags ...` | Filter by tags |
| `--show-skipped` | Include skipped tests in output |
| `--debug` | Full framework tracebacks |
| `-o` / `--output FORMAT` | stdout format (`nice`, `classic`, `nice-new-fails`, `raw`, ...) |
| `--name` | Rename top-level test |
| `--strict-names` | Reject restricted characters in test names |

```bash
python3 regression.py --help
```

---

## CI mapping (this repo)

From `.github/create_and_upload_logs.sh`:

```bash
tfs --no-colors transform nice-new-fails raw.log nice-new-fails.log.txt
tfs --no-colors transform fails raw.log fails.log.txt
tfs --no-colors report results -a "$JOB_REPORT_INDEX" raw.log - | tfs --no-colors document convert > report.html
```

Server logs uploaded separately: `*/_instances/*.log` (see [instances.md](instances.md)).
