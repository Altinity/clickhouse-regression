---
name: regression-test-selection
description: >-
  Select Altinity regression tests for a ClickHouse pull request from a fixed
  feature taxonomy. Use when the user gives a PR, diff, or change and asks
  which regression suites, taxonomy leaves, or TestFlows tests to run.
---

# Regression test selection

Choose taxonomy leaves for a change, then name the regression tests those leaves map to. Report the selection. Do not start CI.

Read [taxonomy.md](taxonomy.md) and [mapping.md](mapping.md) before choosing. The taxonomy file is the only legal set of leaf ids. The mapping file is the only source of test paths.

## Get the change

Use whatever the user handed you.

- A pasted diff or file list is the change. Do not fetch anything else.
- A pull request number or URL: load the title, body, and changed-file list with `gh`. The server repository is `Altinity/ClickHouse`. This repository is `Altinity/clickhouse-regression`. Read the diff for files whose path does not already name the feature.

## Choose leaves

Pick the most specific leaf the change actually implements or breaks.

- Use an id from taxonomy.md. Do not invent one, and do not rename one.
- A parent id includes every child. Use the parent when the change is the feature as a whole. Use the child when the change is that child.
- When a child fits, do not also emit its parent.
- A docs-only, changelog-only, or comment-only change selects nothing.
- `runtime.common` means the broad profile. That profile has no suite list yet. Say so. Do not expand it into every suite.
- MinIO, AWS, GCS, Hetzner, and Azure are run targets of the same tests. Select `storage.gcs` or `storage.azure` only when the change is specific to that backend.
- `--with-analyzer` and `--use-keeper` are run flags. Do not treat either as a leaf.
- `storage.cas` and `storage.cas.cache` are the `--cas` and `--cas-s3-cache` runs in mapping.md. Copy the flag and any `--only` or `--skip` with the path. Do not add soak, Jepsen, or alter stress.

## Map leaves to tests

For each chosen leaf, copy the test paths from mapping.md.

- Recommend only paths the mapping marks as run by the suite.
- If the mapping says a path exists but the suite does not run it, put that path under "Not part of the default run".
- If the leaf has no regression coverage, say so. Do not borrow a neighboring suite.
- Union the paths when several leaves are chosen. List each path once, with every leaf that selected it.

## Report

Use this shape:

```markdown
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
