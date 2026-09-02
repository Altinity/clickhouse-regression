# Shared reference: CI report, log and artifact URLs

Single source for every CI URL pattern. Read this instead of keeping copies -
these patterns drift (the MasterCI report layout has changed before), and copies
drift apart silently.

Not a skill (no `SKILL.md`). Read by `pr-ci-failure-triage`,
`upstream-test-investigation`, `upstream-ci-database-queries`, `ci-job-forensics`,
`release-branch-monitor`.

---

## The one distinction that matters: PR run vs REF run

Everything below forks on this. Get it wrong and every URL 404s.

| | PR run | Branch / REF run (MasterCI, `pull_request_number = 0`) |
|---|---|---|
| Path segment | `PRs/<PR>/<SHA>/` | `REFs/<BRANCH>/<SHA>//` (**double slash**) |
| JSON browser key | `PR=<PR>` + `name_0=PR` | `REF=<BRANCH>` + `name_0=MasterCI` |
| Job log file | `job.log` (plain) | `job.log.zst` (**zstd-compressed**) |

---

## CI report

```
PR:  https://s3.amazonaws.com/altinity-build-artifacts/PRs/<PR>/<SHA>/<RUN_ID>/ci_run_report.html
REF: https://s3.amazonaws.com/altinity-build-artifacts/REFs/<BRANCH>/<SHA>/<RUN_ID>/ci_run_report.html
```

## JSON log browser

```
PR:  https://altinity-build-artifacts.s3.amazonaws.com/json.html?PR=<PR>&sha=<SHA>&name_0=PR&name_1=<URL_ENCODED_JOB_NAME>
REF: https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=<BRANCH>&sha=<SHA>&name_0=MasterCI&name_1=<URL_ENCODED_JOB_NAME>
```

Worked examples of `name_1` encoding:

```
Integration tests:  Integration%20tests%20%28<build_type>%29
Stateless tests:    Stateless+tests+%28<build_type>%29&name_2=Tests
```

## Direct artifact file

```
PR:  https://altinity-build-artifacts.s3.amazonaws.com/PRs/<PR>/<SHA>/<job_artifact_dir>/<log_file>
REF: https://altinity-build-artifacts.s3.amazonaws.com/REFs/<BRANCH>/<SHA>//<job_artifact_dir>/<log_file>
```

### `<job_artifact_dir>` naming

| Job type | Pattern | Example |
|----------|---------|---------|
| Integration tests | `integration_tests_<build>_<N>_<M>` | `integration_tests_amd_binary_1_5` |
| Stateless tests | `stateless_tests_<build>_<modes>_parallel` | `stateless_tests_amd_binary_old_analyzer_s3_storage_databasereplicated_parallel` |
| AST fuzzer | `ast_fuzzer_<build>` | `ast_fuzzer_amd_msan` |
| Stress test | `stress_test_<build>` | `stress_test_amd_tsan` |

### Common `<log_file>` names

`job.log` / `job.log.zst`, `clickhouse-server.log(.zst)`, `clickhouse-server.err.log`,
`run.log`, `application_errors.txt`, `fatal.log`, `stderr.log`,
`integration_run_parallel_N.log`

## Listing what a job produced

```bash
# PR
curl -s "https://altinity-build-artifacts.s3.amazonaws.com/?list-type=2&prefix=PRs/<PR>/<SHA>/&delimiter=/" \
  | grep -oE '<Prefix>[^<]+</Prefix>' | sed 's/<[^>]*>//g'

# REF
curl -s "https://altinity-build-artifacts.s3.amazonaws.com/?list-type=2&prefix=REFs/<BRANCH>/<SHA>/&delimiter=/" \
  | grep -oE '<Prefix>[^<]+</Prefix>' | sed 's/<[^>]*>//g'
```

## Reading a large log without downloading it

```bash
curl -s -r 0-300000  "<URL>"        > head.log   # startup banner, CPU features, config
curl -s -r -2000000  "<URL>"        > tail.log   # the crash and its stack trace
curl -s "<URL>.zst" | zstd -dc | head -c 300000  # compressed (REF) artifacts
```

---

## Two gotchas

**Artifacts are overwritten on rerun.** What you download belongs to the *latest*
attempt, even when you are investigating an earlier one. Facts read from them - the
CPU model, the server logs - may describe a different run. Cross-check the timestamp
inside the artifact against the attempt's start time, or read that attempt's log
from the GitHub API instead:

```bash
gh api repos/Altinity/ClickHouse/actions/jobs/<JOB_ID>/logs
```

**GitHub job logs are immutable; S3 artifacts are not.** When the question is about
one specific attempt, prefer the GitHub job log. See `ci-job-forensics` section 1.
