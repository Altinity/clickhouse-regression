# Claude Code conventions for this repository

Only about investigating CI failures. Ignore if you are doing something else.

## Invoke the skill, do not just read it

For an investigation that ends in a verdict, **invoke the matching skill with the
`Skill` tool**. Opening a `SKILL.md` to look up a host or a query, then proceeding
by hand, skips the procedure it defines - that has happened, and the answer was
right but not comparable to any other investigation.

For a quick look at a single log, just answer. The skills are for investigations,
not for every question about CI.

| What you are looking at | Skill |
|---|---|
| A pull request's CI, before approving it | `pr-ci-failure-triage` |
| A failure whose name starts with `/` (`/benchmark/minio/queries`) - a TestFlows regression scenario | `regression-test-database-investigation` |
| Any other single failure - `03340_projections_formatting`, `test_x/test.py::test_y`, or a job-level name with no test (`Server died`, `Timeout`) | `upstream-test-investigation` |
| A release branch across its last N MasterCI runs | `release-branch-monitor` |
| One fact out of a job: a previous attempt's log, a huge artifact, runner CPU, a bisect | `ci-job-forensics` |
| Writing the issue afterwards | `github-issue-template` |

The name shape decides it because it decides the table: `/...` is in
`gh-data.clickhouse_regression_results`, everything else in `gh-data.checks`. If a
failure fits neither, say so rather than forcing it into one.

When a skill names another skill, that means **invoke** it, not reimplement it.

Two files are read by path, not invoked (relative to the repository root):
`.claude/skills/_shared/failure-categories.md` (the five categories every verdict
uses) and `.claude/skills/_shared/ci-urls.md` (every CI report and artifact URL).

Investigating needs the CI database password. Ask the user for it; never assume one.
