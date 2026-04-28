#!/usr/bin/env python3
"""Cross-reference failures across multiple CI run reports for a release branch.

Usage:
    cross_reference.py <branch> <run_id1>:<sha1>:<report_url1> ...

Each positional after <branch> describes one run. The report_url is the full
ci_run_report.html URL.

Output: a markdown report grouping failures by:
  - CONSISTENT: failed in every run
  - FLAKY (>=2/N): failed in at least 2 runs
  - ISOLATED: failed in only 1 run

Strategy: jobs are matched by job_name; specific tests by (job_name, test_name)
for Checks sections; regression entries by (arch, job_name, test_name).
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent


def parse(url: str) -> dict:
    out = subprocess.check_output(
        [sys.executable, str(HERE / "parse_report.py"), url], text=True
    )
    return json.loads(out)


def fmt_run_label(run: dict) -> str:
    return f"#{run['idx']} ({run['run_id']}, {run['sha'][:7]})"


def crosstable(rows_per_run: list[set], total: int) -> dict:
    """Return {key: count} aggregating presence across runs."""
    counts = defaultdict(int)
    for s in rows_per_run:
        for k in s:
            counts[k] += 1
    return counts


def render(branch: str, runs: list[dict], data: list[dict]) -> str:
    n = len(runs)
    lines = []
    lines.append(f"# MasterCI failure monitor — branch `{branch}`")
    lines.append("")
    lines.append("## Runs analyzed")
    lines.append("")
    lines.append("| # | Run ID | Commit | Conclusion |")
    lines.append("|---|--------|--------|------------|")
    for r in runs:
        lines.append(
            f"| {r['idx']} | [{r['run_id']}](https://github.com/Altinity/ClickHouse/actions/runs/{r['run_id']}) | `{r['sha'][:7]}` | {r.get('conclusion','?')} |"
        )
    lines.append("")

    # ---- Jobs failing across runs (Checks Errors + Checks New Fails)
    job_runs = [set() for _ in range(n)]
    for i, d in enumerate(data):
        for row in d["checks_errors"] + d["checks_new_fails"]:
            if row["job_name"]:
                job_runs[i].add(row["job_name"])
    job_counts = crosstable(job_runs, n)

    def classify(c: int) -> str:
        if c == n:
            return "CONSISTENT"
        if c >= 2:
            return "FLAKY"
        return "ISOLATED"

    lines.append(f"## Failing jobs across runs (Checks Errors + Checks New Fails)")
    lines.append("")
    header = "| Job | " + " | ".join(f"#{r['idx']}" for r in runs) + " | Verdict |"
    sep = "|---|" + "|".join(["---"] * n) + "|---|"
    lines.append(header)
    lines.append(sep)
    for job, c in sorted(job_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        marks = ["X" if job in job_runs[i] else "-" for i in range(n)]
        verdict = classify(c)
        if verdict == "CONSISTENT":
            v = f"**CONSISTENT ({c}/{n})**"
        elif verdict == "FLAKY":
            v = f"FLAKY ({c}/{n})"
        else:
            v = f"isolated ({c}/{n})"
        lines.append(f"| {job} | " + " | ".join(marks) + f" | {v} |")
    lines.append("")

    # ---- Specific tests across runs
    test_runs = [set() for _ in range(n)]
    for i, d in enumerate(data):
        for row in d["checks_errors"] + d["checks_new_fails"]:
            if row.get("test_name"):
                test_runs[i].add((row["job_name"], row["test_name"]))
    test_counts = crosstable(test_runs, n)
    repeating_tests = {k: c for k, c in test_counts.items() if c >= 2}
    lines.append(f"## Specific tests failing in >=2 runs (Checks)")
    lines.append("")
    if not repeating_tests:
        lines.append("_No specific test name repeated across runs._")
        lines.append(
            "(When the same job fails with different tests each run, it usually "
            "means the job/shard is unstable rather than one test regressing.)"
        )
    else:
        lines.append("| Job | Test | " + " | ".join(f"#{r['idx']}" for r in runs) + " | Verdict |")
        lines.append("|---|---|" + "|".join(["---"] * n) + "|---|")
        for (job, test), c in sorted(repeating_tests.items(), key=lambda kv: (-kv[1], kv[0])):
            marks = ["X" if (job, test) in test_runs[i] else "-" for i in range(n)]
            verdict = classify(c)
            v = (
                f"**CONSISTENT ({c}/{n})**" if verdict == "CONSISTENT"
                else (f"FLAKY ({c}/{n})" if verdict == "FLAKY" else f"isolated ({c}/{n})")
            )
            lines.append(f"| {job} | `{test}` | " + " | ".join(marks) + f" | {v} |")
    lines.append("")

    # ---- Regression New Fails
    reg_runs = [set() for _ in range(n)]
    for i, d in enumerate(data):
        for row in d["regression_new_fails"]:
            reg_runs[i].add((row["arch"], row["job_name"], row["test_name"]))
    reg_counts = crosstable(reg_runs, n)

    lines.append("## Regression New Fails across runs")
    lines.append("")
    if not reg_counts:
        lines.append("_No regression failures in any of the analyzed runs._")
    else:
        lines.append("| Arch | Job | Test | " + " | ".join(f"#{r['idx']}" for r in runs) + " | Verdict |")
        lines.append("|---|---|---|" + "|".join(["---"] * n) + "|---|")
        for (arch, job, test), c in sorted(reg_counts.items(), key=lambda kv: (-kv[1], kv[0])):
            marks = ["X" if (arch, job, test) in reg_runs[i] else "-" for i in range(n)]
            verdict = classify(c)
            v = (
                f"**CONSISTENT ({c}/{n})**" if verdict == "CONSISTENT"
                else (f"FLAKY ({c}/{n})" if verdict == "FLAKY" else f"isolated ({c}/{n})")
            )
            lines.append(f"| {arch} | {job} | `{test}` | " + " | ".join(marks) + f" | {v} |")
    lines.append("")

    # ---- Docker Images CVEs (high/critical)
    lines.append("## Docker Images CVEs (high/critical)")
    lines.append("")
    any_cve = False
    lines.append("| # | Section title | High/Critical CVEs |")
    lines.append("|---|---|---|")
    for i, d in enumerate(data):
        run_lbl = f"#{runs[i]['idx']}"
        title = d.get("cve_section_title") or "(section not found)"
        cves = d.get("cve_high_critical", [])
        if cves:
            any_cve = True
            cve_summary = "; ".join(
                f"{c['severity']} {c['identifier']} ({c['image'].split(':')[-1]})"
                for c in cves
            )
        else:
            cve_summary = "_none_"
        lines.append(f"| {run_lbl} | {title} | {cve_summary} |")
    if any_cve:
        lines.append("")
        lines.append("**Action:** investigate any High/Critical CVE before release.")
    lines.append("")

    # ---- CI Jobs Status sanity check
    # Goal: confirm that every job marked error/failure in "CI Jobs Status"
    # is already represented in the Checks Errors / Checks New Fails / Regression
    # sections. Anything that isn't is flagged as "uncovered".
    lines.append("## CI Jobs Status — sanity check")
    lines.append("")
    lines.append(
        "Confirms that every job marked `error`/`failure` in the `CI Jobs Status` "
        "table also appears in `Checks Errors`, `Checks New Fails`, or as a "
        "regression failure. Any uncovered job is reported below."
    )
    lines.append("")
    any_uncovered = False
    # Build, for each run, the set of "covered" job names
    for i, d in enumerate(data):
        covered = set()
        for row in d["checks_errors"] + d["checks_new_fails"]:
            if row["job_name"]:
                covered.add(row["job_name"])
        # Regression jobs in CI Jobs Status are usually named like
        # "Regression aarch64 swarms" / "Regression release swarms".
        # Map regression failures (job_name="Swarms", arch=...) to those forms
        # so they count as covered.
        for row in d["regression_new_fails"]:
            jn = (row.get("job_name") or "").lower()
            arch = (row.get("arch") or "").lower()
            covered.add(f"Regression {'aarch64' if arch == 'aarch64' else 'release'} {jn}")
            covered.add(f"Regression aarch64 {jn}")
            covered.add(f"Regression release {jn}")

        uncovered = []
        for job in d.get("ci_jobs_failed", []):
            name = job["job_name"]
            # The "MasterCI" rollup job is always failure when anything else fails — ignore.
            if name == "MasterCI":
                continue
            if name in covered:
                continue
            # Heuristic: regression jobs reported in CI Jobs Status under names like
            # "Regression aarch64 swarms" should match the covered regression entries.
            if name.lower().startswith("regression ") and any(
                name.lower() == c.lower() for c in covered
            ):
                continue
            uncovered.append(job)

        if uncovered:
            any_uncovered = True
            lines.append(f"### Run #{runs[i]['idx']} — uncovered failing jobs")
            lines.append("")
            lines.append("| Job | Status | Message |")
            lines.append("|---|---|---|")
            for j in uncovered:
                msg = j["message"] or ""
                if len(msg) > 180:
                    msg = msg[:177] + "..."
                lines.append(f"| {j['job_name']} | {j['job_status']} | {msg} |")
            lines.append("")

    if not any_uncovered:
        lines.append("_All failing jobs are accounted for in the sections above._")
        lines.append("")

    # ---- Executive summary
    consistent_jobs = [j for j, c in job_counts.items() if c == n]
    flaky_jobs = [j for j, c in job_counts.items() if 2 <= c < n]
    consistent_reg = [k for k, c in reg_counts.items() if c == n]
    flaky_reg = [k for k, c in reg_counts.items() if 2 <= c < n]
    any_high_cve = any(d.get("cve_high_critical") for d in data)

    lines.append("## Executive summary")
    lines.append("")
    lines.append(f"### Consistent failures (failed in all {n}/{n} runs) — action needed before release")
    if consistent_jobs:
        for j in consistent_jobs:
            lines.append(f"- Job: **{j}**")
    if consistent_reg:
        for arch, job, test in consistent_reg:
            lines.append(f"- Regression: **{job}** [{arch}] `{test}`")
    if any_high_cve:
        for i, d in enumerate(data):
            for c in d.get("cve_high_critical", []):
                lines.append(
                    f"- CVE [{c['severity']}] `{c['identifier']}` in `{c['image']}` (run #{runs[i]['idx']})"
                )
    if not consistent_jobs and not consistent_reg and not any_high_cve:
        lines.append("- _None._")
    lines.append("")

    lines.append(f"### Flaky failures (failed in 2/{n} runs) — monitor on next run")
    if flaky_jobs:
        for j in flaky_jobs:
            lines.append(f"- Job: {j}")
    if flaky_reg:
        for arch, job, test in flaky_reg:
            lines.append(f"- Regression: {job} [{arch}] `{test}`")
    if not flaky_jobs and not flaky_reg:
        lines.append("- _None._")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 3:
        print(
            "usage: cross_reference.py <branch> <idx>:<run_id>:<sha>:<report_url> ...",
            file=sys.stderr,
        )
        sys.exit(2)
    branch = sys.argv[1]
    runs = []
    data = []
    for arg in sys.argv[2:]:
        idx, run_id, sha, url = arg.split(":", 3)
        runs.append({"idx": idx, "run_id": run_id, "sha": sha, "url": url, "conclusion": ""})
        data.append(parse(url))
    print(render(branch, runs, data))


if __name__ == "__main__":
    main()
