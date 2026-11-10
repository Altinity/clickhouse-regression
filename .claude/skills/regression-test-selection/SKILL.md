---
name: regression-test-selection
description: >-
  Select Altinity regression tests for a ClickHouse pull request from a fixed
  feature taxonomy. Use when the user gives a PR, diff, or change and asks
  which regression suites, parent or child features, or TestFlows tests to run.
---

# Regression test selection

Report which regression tests to run for a change. Do not start CI.

Read [taxonomy.yaml](taxonomy.yaml) before you choose a feature. Read [mapping.yaml](mapping.yaml) before you name a test.

## Get the change

Use the change the user handed you.

- A pasted diff or file list is the change. Do not fetch anything else. Read issue numbers from that text only when it includes them.
- A pull request number or URL: load the title, body, and changed-file list with `gh`. The server repository is `Altinity/ClickHouse`. This repository is `Altinity/clickhouse-regression`. Read the diff when a file path does not already name the feature.

Collect every issue the title or body names. Keep the owner and repository from a full `github.com/<owner>/<repo>/issues/<number>` URL. A bare `#<number>` on an `Altinity/ClickHouse` pull request is issue `<number>` in `Altinity/ClickHouse`.

## Select scenarios that cite the issue (if an issue is present)

Search this repository for the exact URL `https://github.com/<owner>/<repo>/issues/<number>`. Do not search for the bare number.

In a suite `regression.py`, open the expected-failure lists named `xfails` and `ffails`. Each entry starts with a quoted TestFlows path. The reason follows in parentheses. When that reason contains the issue URL, select the quoted path. The suite is the directory that contains that `regression.py`.

Also select a test file when its scenario or feature text cites the issue.

Skip a mention in `requirements/` or `docs/`. Skip a "see also" comment in a helper.

Include these scenarios even when the feature match missed them. In Tests, name the issue. When `regression.py` expects that path to fail, say so.

## Choose features

Name the parent feature, then the child feature when one matches. Match each changed file to the longest `sources` prefix in taxonomy.yaml. The longest prefix wins across the whole file.

When a child wins, report that child and its parent. When only the parent matches, report the parent and stop. There is no level below a child. Do not invent one.

- When several features list the same file, select every one of them.
- A docs-only, changelog-only, or comment-only change selects nothing.
- A match that stops at the parent has no child. Look up that parent id in mapping.yaml. When no suite lists it, record the gap.
- MinIO, AWS, GCS, Hetzner, and Azure are run targets of the same tests. Select `storage.gcs` or `storage.azure` only when the change is specific to that backend.
- `--with-analyzer` and `--use-keeper` are run flags. Do not treat either flag as a feature.

## Map features to tests

If mapping.yaml lists a chosen id on a suite, run that suite. Do not drop it because the pull request looks small, targeted, or unrelated.

Run the `scenarios` under that id. When the entry has no `scenarios`, run the suite with the flag in its description. `storage.cas` is `--cas`. `storage.cas.cache` is `--cas-s3-cache`. Do not add soak, Jepsen, or alter stress.

The mapping already names the only skips. Do not run a suite marked `ci: manual`. Do not run a feature entry marked `ci: manual`. A whole-suite `--cas` or `--cas-s3-cache` rerun is marked that way. Matching `storage.cas` or `storage.cas.cache` does not start that rerun. Put a path the notes call not started under "Not part of the default run". Put a FIPS-only entry there too, unless the package under test is a FIPS build.

Leave out a suite that does not list the id.

## Report

Use this shape:

```markdown
## Taxonomy
- `feature.id` — why it won, with the files that decided it

## Tests
- `path` — the feature id, or the issue number this scenario cites

## Not part of the default run
- `path` — the suite does not start it

## Considered and left out
- `feature.id` — why it lost

## Gaps
- Features with no regression coverage. Leave a feature off this list when a scenario that cites the PR's issue covers the change.
```

Omit an empty section. "Considered and left out" is a feature the prefix match rejected. It is not a suite you chose not to run. Name the features you almost picked.
