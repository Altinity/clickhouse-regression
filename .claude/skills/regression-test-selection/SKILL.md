---
name: regression-test-selection
description: >-
  Select Altinity regression tests for a ClickHouse pull request from a fixed
  feature taxonomy. Use when the user gives a PR, diff, or change and asks
  which regression suites, taxonomy leaves, or TestFlows tests to run.
---

# Regression test selection

Choose taxonomy leaves for a change, then name the regression tests those leaves map to. Report the selection. Do not start CI.

Read [taxonomy.yaml](taxonomy.yaml) before choosing a feature. Read [mapping.md](mapping.md) before naming tests.

## Get the change

Use whatever the user handed you.

- A pasted diff or file list is the change. Do not fetch anything else.
- A pull request number or URL: load the title, body, and changed-file list with `gh`. The server repository is `Altinity/ClickHouse`. This repository is `Altinity/clickhouse-regression`. Read the diff for files whose path does not already name the feature.

## Choose leaves

Name the big feature first, then a medium feature when taxonomy.yaml has one. Match each changed file to the longest `sources` prefix in that file. The longest prefix wins across the whole file, so `src/Processors/Formats/` is `formats`, not `query`.

If the winning entry is a medium feature, report its parent big feature too. If the winning entry is a big feature with no medium child for that path, stop there and say the section is not expanded. Do not invent a medium feature.

- When several leaves list the same file, select every one of them. A diff that names a single registered layout or source, such as `sparse_hashed` or `postgresql`, selects that leaf only.
- A docs-only, changelog-only, or comment-only change selects nothing.
- A change under a suite directory in this repository selects the leaf whose mapping lists that path.
- `runtime.common` means the broad profile. That profile has no suite list yet. Say so. Do not expand it into every suite.
- MinIO, AWS, GCS, Hetzner, and Azure are run targets of the same tests. Select `storage.gcs` or `storage.azure` only when the change is specific to that backend.
- `--with-analyzer` and `--use-keeper` are run flags. Do not treat either as a leaf.
- `storage.cas` and `storage.disk.cache` are the `--cas` and `--cas-s3-cache` runs in mapping.md. Copy the flag and any `--only` or `--skip` with the path. Do not add soak, Jepsen, or alter stress.

## Map leaves to tests

mapping.md is organized by test directory. A directory lists the leaves it covers. Find every directory that lists a chosen leaf and run that directory. When the leaf names a file or a flag under the directory, run that file with that flag. Do not run a neighboring directory that does not list the leaf.

## Report

Use this shape:

```markdown
## Big feature
- `name` — the files that put the change here

## Leaves
- `leaf.id` — why, with the files that decided it

## Tests
- `path` — leaf ids

## Not part of the default run
- `path` — the suite does not start it

## Considered and left out
- `leaf.id` — why it lost

## Gaps
- Leaves with no regression coverage, or `runtime.common` with no broad profile
```

Omit an empty section. The "Considered and left out" section is required whenever you chose among nearby leaves. Name the leaves you almost picked.
