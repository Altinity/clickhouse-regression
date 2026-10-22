---
name: regression-test-selection
description: >-
  Select Altinity regression tests for a ClickHouse pull request from a fixed
  feature taxonomy. Use when the user gives a PR, diff, or change and asks
  which regression suites, parent or child features, or TestFlows tests to run.
---

# Regression test selection

Choose parent and child features for a change, then name the regression tests those features map to. Report the selection. Do not start CI.

Read [taxonomy.yaml](taxonomy.yaml) before choosing a feature. Read [mapping.md](mapping.md) before naming tests.

## Get the change

Use whatever the user handed you.

- A pasted diff or file list is the change. Do not fetch anything else.
- A pull request number or URL: load the title, body, and changed-file list with `gh`. The server repository is `Altinity/ClickHouse`. This repository is `Altinity/clickhouse-regression`. Read the diff for files whose path does not already name the feature.

## Choose features

Name the parent, then the child when one matches. Match each changed file to the longest `sources` prefix in taxonomy.yaml. The longest prefix wins across the whole file, so `src/Processors/Formats/` is `formats`, not `query`.

If a child wins, report that child and its parent. If only the parent matches, report the parent. There is no level below a child. Do not invent one.

- When several features list the same file, select every one of them. A diff that names a single registered layout or source, such as `sparse_hashed` or `postgresql`, selects that feature only.
- A docs-only, changelog-only, or comment-only change selects nothing.
- A change under a suite directory in this repository selects the feature whose mapping lists that path.
- A match that stops at the parent has no child. Look up that parent id in mapping.md. If no directory lists it, record the gap. Do not run every suite.
- MinIO, AWS, GCS, Hetzner, and Azure are run targets of the same tests. Select `storage.gcs` or `storage.azure` only when the change is specific to that backend.
- `--with-analyzer` and `--use-keeper` are run flags. Do not treat either as a feature.
- `storage.cas` and `storage.disk.cache` are the `--cas` and `--cas-s3-cache` runs in mapping.md. Copy the flag and any `--only` or `--skip` with the path. Do not add soak, Jepsen, or alter stress.

## Map features to tests

mapping.md is organized by test directory. A directory lists the child features it covers, and every id there is a child from taxonomy.yaml. Find every directory that lists a chosen feature and run that directory. When the feature names a file or a flag under the directory, run that file with that flag. Do not run a neighboring directory that does not list the feature. A path marked "not started" or "not in the default CI split" goes in the report under "Not part of the default run".

## Report

Use this shape:

```markdown
## Parent
- `name` — the files that put the change here

## Children
- `child.id` — why, with the files that decided it

## Tests
- `path` — feature ids

## Not part of the default run
- `path` — the suite does not start it

## Considered and left out
- `feature.id` — why it lost

## Gaps
- Features with no regression coverage
```

Omit an empty section. The "Considered and left out" section is required whenever you chose among nearby features. Name the features you almost picked.
