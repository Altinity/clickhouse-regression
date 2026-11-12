#!/usr/bin/env python3
"""Select regression suites for one Altinity/ClickHouse pull request.

Resolves the PR head build, asks a Cursor agent to follow the
regression-test-selection skill, and writes the plan the workflow runs.
The agent matches files and looks up suites through the tools in this
script. It does not start the suite jobs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

SERVER_REPO = "Altinity/ClickHouse"
S3_BASE = "https://altinity-build-artifacts.s3.amazonaws.com"
HISTORY_BUCKET = "altinity-build-artifacts"
PLAN_NAME = "selection-plan.json"
SKILL_PATH = Path(".claude/skills/regression-test-selection/SKILL.md")
TAXONOMY_PATH = Path(".claude/skills/regression-test-selection/taxonomy.yaml")
MAPPING_PATH = Path(".claude/skills/regression-test-selection/mapping.yaml")

# reusable-suite.yml assigns regression_args inside single quotes, then
# expands it unquoted. Double quotes must stay so paths with spaces survive.
# These characters break that assignment or start another shell command.
UNSAFE_ARGS = re.compile(r"['\n;`&$\\<>]")

# A job with no --only and no --skip runs the whole suite. These suites are
# already split into numbered jobs in run-regression.yml. Each entry is the
# filter for that part, in order.
WHOLE_SUITE_PARTS = {
    "aggregate_functions": [
        '--only "/aggregate functions/part 1/*"',
        '--only "/aggregate functions/part 2/*"',
        '--only "/aggregate functions/part 3/*"',
    ],
    "clickhouse_keeper": [
        '--only "/clickhouse keeper/part 1/*"',
        '--only "/clickhouse keeper/part 2/*"',
    ],
    "rbac": [
        '--only "/rbac/part 1/*"',
        '--only "/rbac/part 2/*"',
        '--only "/rbac/part 3/*"',
    ],
    "iceberg": [
        '--only "/iceberg/iceberg engine/rest catalog/*" "/iceberg/s3 table function/*" "/iceberg/icebergS3 table function/*" "/iceberg/iceberg cache/*"',
        '--only "/iceberg/iceberg engine/glue catalog/*" "/iceberg/iceberg table engine/*" "/iceberg/export partition/*"',
    ],
}

# The tiered storage suite creates one feature from the flag. --only of
# "/tiered storage/with minio/*" does not start MinIO. These are the jobs
# run-regression.yml uses for each feature.
TIERED_STORAGE_JOBS = [
    ("with minio", "tiered_storage_minio", "/minio", "--with-minio"),
    (
        "with s3amazon",
        "tiered_storage_aws",
        "/aws",
        "--with-s3amazon --aws-s3-access-key {{AWS_ACCESS_KEY}} --aws-s3-key-id {{AWS_KEY_ID}} --aws-s3-uri https://s3.{{AWS_REGION}}.amazonaws.com/{{AWS_BUCKET}}/data/",
    ),
    ("with s3hetzner", "tiered_storage_hetzner", "/hetzner", "--with-s3hetzner"),
    (
        "with s3gcs",
        "tiered_storage_gcs",
        "/gcs",
        "--with-s3gcs --gcs-uri {{GCS_URI}} --gcs-key-id {{GCS_KEY_ID}} --gcs-key-secret {{GCS_KEY_SECRET}}",
    ),
    ("with cas", "tiered_storage_cas", "/cas", "--with-cas"),
]

# Whole-suite --cas / --cas-s3-cache reruns. mapping.yaml marks the feature
# ci: manual. Automatic selection must not start them.
CAS_FULL_SUITES = {
    "aggregate_functions",
    "alter",
    "atomic_insert",
    "engines",
    "lightweight_delete",
    "selects",
}

WHOLE_SUITE_CAS_GLOBS = {
    "aggregate_functions": {
        "/aggregate functions/part 1/*",
        "/aggregate functions/part 2/*",
        "/aggregate functions/part 3/*",
    },
    "lightweight_delete": {
        "/lightweight delete/disk space/*",
        "/lightweight delete/hard restart/*",
        "/lightweight delete/alter after delete/*",
        "/lightweight delete/concurrent alter and delete/*",
        "/lightweight delete/concurrent delete/*",
        "/lightweight delete/basic checks/*",
        "/lightweight delete/performance/*",
        "/lightweight delete/ontime tests/*",
    },
    "alter": {
        "/alter/replace partition/*",
        "/alter/attach partition/*",
        "/alter/attach partition/part 1/*",
        "/alter/attach partition/part 2/*",
        "/alter/attach partition/part 3/*",
        "/alter/move partition/*",
    },
}

# alter without --cas, split the way run-regression.yml does.
ALTER_SPLITS = [
    ("/alter/replace partition", "alter_replace_partition", "", "/replace_partition", 180),
    ("/alter/attach partition/part 1", "alter_attach_partition", "1", "/attach_partition", 360),
    ("/alter/attach partition/part 2", "alter_attach_partition", "2", "/attach_partition", 360),
    ("/alter/attach partition/part 3", "alter_attach_partition", "3", "/attach_partition", 360),
    ("/alter/move partition", "alter_move_partition", "", "/move_partition", 180),
]
LIGHTWEIGHT_DELETE_CAS_PARTS = [
    '--only "/lightweight delete/disk space/*"',
    '--only "/lightweight delete/hard restart/*"',
    '--skip "/lightweight delete/disk space/*" "/lightweight delete/hard restart/*" "/lightweight delete/alter after delete/*" "/lightweight delete/concurrent alter and delete/*" "/lightweight delete/concurrent delete/*" "/lightweight delete/basic checks/*" "/lightweight delete/performance/*" "/lightweight delete/ontime tests/*"',
    '--only "/lightweight delete/alter after delete/*" "/lightweight delete/concurrent alter and delete/*" "/lightweight delete/concurrent delete/*" "/lightweight delete/basic checks/*" "/lightweight delete/performance/*" "/lightweight delete/ontime tests/*"',
]


class SelectionError(Exception):
    """The plan cannot be run. The message says what to do next."""


def parse_pr(value: str) -> tuple[str, int]:
    text = value.strip()
    match = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", text)
    if match:
        return f"{match.group(1)}/{match.group(2)}", int(match.group(3))
    if re.fullmatch(r"\d+", text):
        return SERVER_REPO, int(text)
    raise SelectionError(
        f"Could not read a pull request from {value!r}. "
        "Pass a PR number, or a github.com/<owner>/<repo>/pull/<number> URL."
    )


def issue_urls(title: str, body: str, repo: str) -> list[str]:
    text = f"{title}\n{body}"
    found: list[str] = []
    seen: set[str] = set()

    def add(url: str) -> None:
        if url not in seen:
            seen.add(url)
            found.append(url)

    for url in re.findall(r"https://github\.com/[\w.-]+/[\w.-]+/issues/\d+", text):
        add(url)
    for number in re.findall(r"(?<![\w/])#(\d+)\b", text):
        add(f"https://github.com/{repo}/issues/{number}")
    return found


def gh_json(args: list[str]) -> dict:
    try:
        output = subprocess.check_output(["gh", *args], text=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise SelectionError(
            "gh could not read the pull request. "
            "The token in this job needs access to the server repository. "
            f"{detail}"
        ) from exc
    return json.loads(output)


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "clickhouse-regression"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise SelectionError(f"No build report at {url}.") from exc
        raise SelectionError(
            f"Could not read the build report at {url}. HTTP {exc.code}."
        ) from exc
    except urllib.error.URLError as exc:
        raise SelectionError(f"Could not reach {url}. {exc.reason}") from exc


def release_deb(urls: list[str]) -> str:
    """The clickhouse-common-static deb from a Build (amd_release) or Build (arm_release) report."""
    debs = [
        url
        for url in urls
        if "clickhouse-common-static_" in url and str(url).endswith(".deb")
    ]
    if len(debs) != 1:
        raise SelectionError(
            f"The release build report has {len(debs)} clickhouse-common-static debs. Expected one."
        )
    return debs[0]


def version_from_deb(url: str) -> str:
    name = url.rstrip("/").split("/")[-1]
    parts = name.split("_")
    if len(parts) < 3 or not parts[1]:
        raise SelectionError(f"Cannot read a version from the package name {name}.")
    return parts[1]


def release_package(pr_number: int, sha: str, arch: str) -> str:
    name = "amd" if arch == "x86" else "arm"
    job = f"Build ({name}_release)"
    report_url = (
        f"{S3_BASE}/PRs/{pr_number}/{sha}/"
        f"build_{name}_release/artifact_report_build_{name}_release.json"
    )
    try:
        report = fetch_json(report_url)
    except SelectionError as exc:
        if "No build report" in str(exc):
            raise SelectionError(
                f"No build report for {job} at {report_url}. "
                "That release build is not published for this commit yet. "
                "Re-run this workflow after it finishes."
            ) from exc
        raise
    try:
        return release_deb(report.get("build_urls") or [])
    except SelectionError as exc:
        raise SelectionError(f"{job}: {exc}") from exc


def source_matches(source: str, path: str) -> bool:
    if source.endswith("/"):
        return path.startswith(source)
    return path == source or path.startswith(source + "/")


def load_features(path: Path) -> list[dict]:
    document = yaml.safe_load(path.read_text())
    features: list[dict] = []
    for parent in document["features"]:
        features.append(
            {
                "id": parent["id"],
                "parent": None,
                "sources": parent.get("sources") or [],
            }
        )
        for child in parent.get("children") or []:
            features.append(
                {
                    "id": child["id"],
                    "parent": parent["id"],
                    "sources": child.get("sources") or [],
                }
            )
    return features


def match_files(features: list[dict], files: list[str]) -> list[dict]:
    """Longest sources prefix across the taxonomy. Equal lengths all win."""
    matched = []
    for path in files:
        best = -1
        winners: list[dict] = []
        seen: set[str] = set()
        for feature in features:
            length = 0
            winning_source = ""
            for source in feature["sources"]:
                if source_matches(source, path) and len(source) > length:
                    length = len(source)
                    winning_source = source
            if length == 0 or length < best:
                continue
            if length > best:
                best = length
                winners = []
                seen = set()
            if feature["id"] in seen:
                continue
            seen.add(feature["id"])
            winners.append(
                {
                    "id": feature["id"],
                    "parent": feature["parent"],
                    "source": winning_source,
                    "length": length,
                }
            )
        matched.append({"file": path, "matches": winners})
    return matched


def load_suites(path: Path) -> list[dict]:
    document = yaml.safe_load(path.read_text())
    return document["suites"]


def lookup_features(suites: list[dict], ids: list[str]) -> dict:
    wanted = set(ids)
    found = []
    hit_ids: set[str] = set()
    for suite in suites:
        suite_path = suite.get("path")
        if not suite_path or suite_path == ".":
            continue
        hits = []
        for feature in suite.get("features") or []:
            if feature.get("id") not in wanted:
                continue
            hit_ids.add(feature["id"])
            hits.append(
                {
                    "id": feature["id"],
                    "description": feature.get("description") or "",
                    "scenarios": feature.get("scenarios") or [],
                    "ci": feature.get("ci"),
                }
            )
        if not hits:
            continue
        found.append(
            {
                "path": suite_path,
                "ci": suite.get("ci"),
                "description": suite.get("description") or "",
                "notes": suite.get("notes") or [],
                "hits": hits,
            }
        )
    return {"suites": found, "ids_with_no_suite": sorted(wanted - hit_ids)}


def suite_of(root: Path, file_path: Path) -> str | None:
    current = file_path.parent
    while True:
        if (current / "regression.py").is_file() and current != root:
            return str(current.relative_to(root))
        if current == root:
            return None
        current = current.parent


def search_issue(root: Path, url: str) -> list[dict]:
    """Quoted TestFlows paths whose expected-failure reason cites this issue URL."""
    skip_parts = {"requirements", "docs", ".git", ".claude", "helpers"}
    hits = []
    for path in root.rglob("*.py"):
        if any(part in skip_parts for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if url not in text:
            continue
        names = re.findall(
            rf"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*[\"']{re.escape(url)}[\"']",
            text,
            flags=re.M,
        )
        keys = list(re.finditer(r'["\'](/.+?)["\']\s*:', text))
        paths: list[str] = []
        for index, key in enumerate(keys):
            end = keys[index + 1].start() if index + 1 < len(keys) else len(text)
            body = text[key.end() : end]
            if url in body or any(name in body for name in names):
                paths.append(key.group(1))
        suite = suite_of(root, path)
        if suite is None and not paths:
            continue
        hits.append(
            {
                "file": str(path.relative_to(root)),
                "suite": suite,
                "paths": paths,
            }
        )
    return hits


def normalize_args(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        parts = []
        for item in value:
            text = str(item)
            if re.search(r"\s", text):
                parts.append('"' + text.replace('"', "") + '"')
            else:
                parts.append(text)
        return " ".join(parts)
    return str(value)


def validate_jobs(suites: list[dict], jobs: list) -> list[dict]:
    if not isinstance(jobs, list):
        raise SelectionError("The plan's jobs value is not a list.")
    allowed = {}
    manual = set()
    for suite in suites:
        suite_path = suite.get("path")
        if not suite_path or suite_path == ".":
            continue
        allowed[suite_path] = suite
        if suite.get("ci") in ("manual", True):
            manual.add(suite_path)

    accepted = []
    seen = set()
    for index, job in enumerate(jobs):
        if not isinstance(job, dict):
            raise SelectionError(f"Job {index} is not an object.")
        suite_name = str(job.get("suite_name") or "")
        if suite_name in manual:
            print(f"Leaving out {suite_name}: automatic selection must not run it.", file=sys.stderr)
            continue
        if suite_name not in allowed:
            raise SelectionError(
                f"The plan names suite {suite_name!r}, which is not a directory in mapping.yaml. "
                "The agent has to choose a suite the lookup tool returned."
            )
        if suite_name in seen:
            raise SelectionError(
                f"The plan lists {suite_name} more than once. "
                "Put every --only path for that suite on one job."
            )
        seen.add(suite_name)
        args = canonicalize_args(normalize_args(job.get("regression_args")))
        if UNSAFE_ARGS.search(args):
            raise SelectionError(
                f"regression_args for {suite_name} contains a character the runner cannot pass through. "
                f"Got: {args!r}"
            )
        storage = str(job.get("storage_path") or "")
        if storage and not re.fullmatch(r"[A-Za-z0-9_./-]+", storage):
            raise SelectionError(f"storage_path for {suite_name} is not a plain path: {storage!r}")
        part = str(job.get("part") or "")
        if part and not re.fullmatch(r"\d+", part):
            raise SelectionError(f"part for {suite_name} must be empty or a number. Got {part!r}.")
        built = normalize_s3_storage(
            {
                "suite_name": suite_name,
                "job_name": suite_name.replace("/", "_"),
                "part": part,
                "regression_args": args,
                "storage_path": storage,
                "timeout_minutes": 480 if suite_name == "s3" else 300,
            }
        )
        for tiered in split_tiered_storage(built):
            if is_full_cas_rerun(tiered):
                print(
                    f"Leaving out {tiered['suite_name']} with {tiered['regression_args']}: "
                    "a whole-suite --cas rerun is manual or scheduled.",
                    file=sys.stderr,
                )
                continue
            for piece in split_alter(tiered):
                accepted.extend(split_whole_suite(piece))
    return accepted


def is_full_cas_rerun(job: dict) -> bool:
    """A whole-suite --cas or --cas-s3-cache job, including the part splits of that whole suite."""
    suite = job["suite_name"]
    if suite not in CAS_FULL_SUITES:
        return False
    args = job["regression_args"]
    if "--cas-s3-cache" not in args and re.search(r"(^|\s)--cas(\s|$)", args) is None:
        return False
    paths = _only_paths(args)
    if not paths:
        return True
    return all(path in WHOLE_SUITE_CAS_GLOBS.get(suite, ()) for path in paths)


def _only_paths(args: str) -> list[str]:
    return re.findall(r'"(/[^"]+)"', args)


def _covered_by(path: str, pattern: str) -> bool:
    if not pattern.endswith("/*"):
        return False
    return path.startswith(pattern[:-1])


def canonicalize_args(args: str) -> str:
    """Drop an --only path already covered by a wildcard in the same argument list."""

    def replace(match: re.Match) -> str:
        paths = re.findall(r'"(/[^"]+)"', match.group(0))
        kept = [
            path
            for path in paths
            if not any(_covered_by(path, other) for other in paths if other != path)
        ]
        return "--only " + " ".join(f'"{path}"' for path in kept)

    return re.sub(r'--only(\s+"[^"]*")+', replace, args).strip()


def normalize_s3_storage(job: dict) -> dict:
    """Omitting --storage runs MinIO. Write that flag so it matches an explicit MinIO job."""
    if job.get("suite_name") != "s3":
        return job
    args = job.get("regression_args") or ""
    updated = {**job, "timeout_minutes": 480}
    if "--storage" not in args:
        updated["regression_args"] = f"--storage minio {args}".strip()
        updated["storage_path"] = job.get("storage_path") or "/minio"
    return updated


def _path_in_split(requested: str, split_prefix: str) -> bool:
    req = requested.rstrip("*").rstrip("/")
    part = split_prefix.rstrip("/")
    return part == req or part.startswith(req + "/") or req.startswith(part + "/")


def split_alter(job: dict) -> list[dict]:
    """Split alter the way run-regression.yml does, unless this is one narrow path."""
    if job["suite_name"] != "alter" or is_full_cas_rerun(job):
        return [job]
    requested = _only_paths(job["regression_args"])
    flags = re.sub(r'--only(\s+"[^"]*")+', "", job["regression_args"]).strip()
    chosen = []
    for prefix, job_name, part, storage, timeout in ALTER_SPLITS:
        if requested and not any(_path_in_split(path, prefix) for path in requested):
            continue
        if not requested:
            only = f'--only "{prefix}/*"'
        else:
            covered = [path for path in requested if _path_in_split(path, prefix)]
            broad = any(
                prefix.startswith(path.rstrip("*").rstrip("/"))
                or prefix == path.rstrip("*").rstrip("/")
                for path in covered
            )
            only = f'--only "{prefix}/*"' if broad else "--only " + " ".join(f'"{path}"' for path in covered)
        chosen.append(
            {
                **job,
                "job_name": job_name,
                "part": part,
                "storage_path": storage or job["storage_path"],
                "regression_args": f"{flags} {only}".strip(),
                "timeout_minutes": timeout,
            }
        )
    return chosen or [job]


def split_tiered_storage(job: dict) -> list[dict]:
    """Replace --only of a tiered-storage backend with the flag that starts it."""
    if job["suite_name"] != "tiered_storage" or "--with-" in job["regression_args"]:
        return [job]
    args = job["regression_args"]
    if "--only" not in args:
        return [job]
    matched = [spec for spec in TIERED_STORAGE_JOBS if spec[0] in args]
    if not matched:
        return [job]
    return [
        {
            **job,
            "job_name": job_name,
            "storage_path": storage,
            "regression_args": flags,
        }
        for _needle, job_name, storage, flags in matched
    ]


def split_whole_suite(job: dict) -> list[dict]:
    """Turn one whole-suite job into the numbered parts CI already uses."""
    args = job["regression_args"]
    if job["part"] or "--only" in args or "--skip" in args:
        return [job]
    parts = WHOLE_SUITE_PARTS.get(job["suite_name"])
    if job["suite_name"] == "lightweight_delete" and args.strip() in ("--cas", "--cas-s3-cache"):
        parts = LIGHTWEIGHT_DELETE_CAS_PARTS
    if not parts:
        return [job]
    prefix = args.strip()
    split = []
    for index, only in enumerate(parts, start=1):
        split.append(
            {
                **job,
                "part": str(index),
                "regression_args": f"{prefix} {only}".strip(),
            }
        )
    return split


def extract_json(text: str) -> dict:
    stripped = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", stripped, flags=re.S)
    if fenced:
        stripped = fenced.group(1)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start < 0 or end < start:
        raise SelectionError(
            "The agent did not return a JSON object. "
            "The last lines of its reply are:\n"
            + text[-2000:]
        )
    try:
        return json.loads(stripped[start : end + 1])
    except json.JSONDecodeError as exc:
        raise SelectionError(
            f"The agent's reply is not valid JSON ({exc}). "
            "The last lines of its reply are:\n"
            + text[-2000:]
        ) from exc


def build_prompt(pr: dict, skill: str) -> str:
    files = "\n".join(pr["files"]) or "(no files)"
    issues = "\n".join(pr["issues"]) or "(none)"
    fips = "yes" if "fips" in pr["version"].lower() else "no"
    return f"""You select Altinity regression tests for one pull request.

Follow the skill below. The workflow prints your plan and then starts the suite jobs. You do not start them. You do not run regression.py. You do not edit files.

Use the tools. Call match_files once with every changed file. Call lookup_features with every winning feature id and, when a winner has a parent, that parent id too. Call search_issue once for each issue URL listed below. A feature with no scenarios in the lookup result is a flag: put that flag in regression_args and do not invent --only paths for it. If the lookup lists a suite for an id, that suite runs. Do not drop it because the change looks small, targeted, or unrelated. A feature entry with ci: manual is not an automatic run. Do not emit a whole-suite --cas or --cas-s3-cache job for aggregate_functions, alter, atomic_insert, engines, lightweight_delete, or selects. Leave out a suite whose ci is manual. Leave out a path the notes call not started. Leave out a FIPS-only path unless this package is a FIPS build. A docs-only, changelog-only, or comment-only change selects nothing.

When several scenarios belong to one suite, return one job. regression_args is one string. Quote every TestFlows path with double quotes. Example: --only "/parquet/file/*" "/parquet/url/*"
When the lookup names --cas or --cas-s3-cache, put that flag in the same string, before --only.

Your final message is only this JSON object, with no markdown fence:

{{
  "report_markdown": "the skill report",
  "jobs": [
    {{
      "suite_name": "directory from mapping.yaml",
      "regression_args": "",
      "storage_path": "",
      "part": ""
    }}
  ]
}}

Pull request: {pr["url"]}
Version: {pr["version"]}
FIPS package: {fips}
x86 package: {pr["packages"]["x86"]}
arm64 package: {pr["packages"]["arm64"]}

Title: {pr["title"]}

Body:
{pr["body"]}

Issue URLs:
{issues}

Changed files:
{files}

Skill:

{skill}
"""


def run_agent(prompt: str, root: Path, features: list[dict], suites: list[dict]) -> dict:
    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        raise SelectionError(
            "CURSOR_API_KEY is not set. Add your Cursor user API key as the "
            "CURSOR_API_KEY secret on this repository, then re-run the workflow."
        )
    try:
        from cursor_sdk import (
            Agent,
            AgentOptions,
            CustomTool,
            LocalAgentOptions,
        )
    except ImportError as exc:
        raise SelectionError(
            "cursor-sdk is not installed. The workflow installs it before this script."
        ) from exc

    def match_tool(arguments, _context):
        files = arguments.get("files") or []
        if isinstance(files, str):
            files = [files]
        return match_files(features, [str(item) for item in files])

    def lookup_tool(arguments, _context):
        ids = arguments.get("ids") or []
        if isinstance(ids, str):
            ids = [ids]
        return lookup_features(suites, [str(item) for item in ids])

    def issue_tool(arguments, _context):
        url = str(arguments.get("url") or "")
        if not url:
            return {"error": "url is required"}
        return search_issue(root, url)

    file_schema = {
        "type": "object",
        "properties": {"files": {"type": "array", "items": {"type": "string"}}},
        "required": ["files"],
    }
    id_schema = {
        "type": "object",
        "properties": {"ids": {"type": "array", "items": {"type": "string"}}},
        "required": ["ids"],
    }
    url_schema = {
        "type": "object",
        "properties": {"url": {"type": "string"}},
        "required": ["url"],
    }
    result = Agent.prompt(
        prompt,
        AgentOptions(
            api_key=api_key,
            model="composer-2.5",
            local=LocalAgentOptions(
                cwd=root,
                setting_sources=[],
                auto_review=True,
                custom_tools={
                    "match_files": CustomTool(
                        description=(
                            "Match changed file paths to taxonomy features. "
                            "The longest sources prefix wins. Equal lengths all win. "
                            "A winner's parent is the parent to report with that child."
                        ),
                        input_schema=file_schema,
                        execute=match_tool,
                    ),
                    "lookup_features": CustomTool(
                        description=(
                            "Return the regression suites whose features list these taxonomy ids. "
                            "An empty scenarios list means the description names a flag. "
                            "ci manual means the suite must not run."
                        ),
                        input_schema=id_schema,
                        execute=lookup_tool,
                    ),
                    "search_issue": CustomTool(
                        description=(
                            "Find TestFlows paths in this repository whose expected-failure "
                            "reason cites the exact issue URL."
                        ),
                        input_schema=url_schema,
                        execute=issue_tool,
                    ),
                },
            ),
        ),
    )
    print(f"Agent {result.agent_id} finished with status {result.status}.", file=sys.stderr)
    if result.status != "finished":
        detail = result.error_message or result.result or result.status
        raise SelectionError(f"The agent run ended with status {result.status}. {detail}")
    return extract_json(result.result or "")


def write_github_output(name: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        print(f"{name}={value}")
        return
    delimiter = f"EOF_{os.urandom(8).hex()}"
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")


def write_summary(markdown: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        print(markdown)
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(markdown)
        if not markdown.endswith("\n"):
            handle.write("\n")


def load_pr(repo: str, number: int) -> dict:
    viewed = gh_json(
        [
            "pr",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            "title,body,headRefOid,url,files",
        ]
    )
    sha = viewed["headRefOid"]
    title = viewed.get("title") or ""
    body = (viewed.get("body") or "")[:30000]
    packages = {
        "x86": release_package(number, sha, "x86"),
        "arm64": release_package(number, sha, "arm64"),
    }
    version = version_from_deb(packages["x86"])
    arm_version = version_from_deb(packages["arm64"])
    if version != arm_version:
        raise SelectionError(
            f"The amd_release package is {version} and the arm_release package is {arm_version}. "
            "They have to be the same build."
        )
    return {
        "repo": repo,
        "number": number,
        "url": viewed.get("url") or f"https://github.com/{repo}/pull/{number}",
        "title": title,
        "body": body,
        "sha": sha,
        "version": version,
        "files": [item["path"] for item in viewed.get("files") or [] if item.get("path")],
        "issues": issue_urls(title, body, repo),
        "packages": packages,
    }


def job_key(job: dict) -> tuple:
    """Identity of what the suite will run. Report path and timeout are not part of it."""
    return (
        job.get("suite_name"),
        str(job.get("part") or ""),
        canonicalize_args(job.get("regression_args") or ""),
    )


def normalize_remembered(job: dict) -> list[dict]:
    """Reapply the current splitters so an old plan cannot rerun a stale command."""
    cleaned = {key: value for key, value in job.items() if key != "carried_forward"}
    normalized = []
    for tiered in split_tiered_storage(cleaned):
        if is_full_cas_rerun(tiered):
            continue
        for piece in split_alter(tiered):
            normalized.extend(split_whole_suite(piece))
    return normalized


def union_jobs(previous: list[dict], current: list[dict]) -> list[dict]:
    """Keep every earlier job for this PR, then add jobs from this commit."""
    remembered = []
    for job in previous:
        remembered.extend(normalize_remembered(job))
    merged: dict[tuple, dict] = {}
    order: list[tuple] = []
    for job in current:
        job = normalize_s3_storage(
            {key: value for key, value in job.items() if key != "carried_forward"}
        )
        job["regression_args"] = canonicalize_args(job.get("regression_args") or "")
        key = job_key(job)
        if key not in merged:
            order.append(key)
        merged[key] = job
    for job in remembered:
        job = normalize_s3_storage(
            {key: value for key, value in job.items() if key != "carried_forward"}
        )
        job["regression_args"] = canonicalize_args(job.get("regression_args") or "")
        key = job_key(job)
        if key in merged:
            continue
        order.append(key)
        merged[key] = {**job, "carried_forward": True}
    return [merged[key] for key in order]


def history_key(pr_number: int) -> str:
    return f"PRs/{pr_number}/regression-selection.json"


def s3_client():
    if not (os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")):
        return None
    import boto3

    return boto3.client("s3", region_name=os.getenv("AWS_DEFAULT_REGION") or None)


def load_previous_jobs(pr_number: int) -> list[dict]:
    key = history_key(pr_number)
    client = s3_client()
    if client is None:
        print(
            f"::warning::No AWS credentials. Selection history at s3://{HISTORY_BUCKET}/{key} was not read.",
            file=sys.stderr,
        )
        return []
    try:
        body = client.get_object(Bucket=HISTORY_BUCKET, Key=key)["Body"].read()
    except Exception as exc:
        response = getattr(exc, "response", None)
        code = response.get("Error", {}).get("Code", "") if isinstance(response, dict) else ""
        if code in ("NoSuchKey", "404"):
            return []
        print(f"Could not read s3://{HISTORY_BUCKET}/{key}. {exc}", file=sys.stderr)
        return []
    jobs = [
        job
        for job in json.loads(body).get("jobs") or []
        if isinstance(job, dict) and job.get("suite_name")
    ]
    if jobs:
        print(f"Carrying forward jobs from s3://{HISTORY_BUCKET}/{key}.", file=sys.stderr)
    return jobs


def save_history(pr_number: int, document: dict) -> None:
    key = history_key(pr_number)
    client = s3_client()
    if client is None:
        print(
            f"::warning::Selection history was not saved. "
            f"Set AWS_ACCESS_KEY_ID to write s3://{HISTORY_BUCKET}/{key}",
            file=sys.stderr,
        )
        return
    try:
        client.put_object(
            Bucket=HISTORY_BUCKET,
            Key=key,
            Body=json.dumps(document, indent=2).encode(),
            ContentType="application/json",
        )
    except Exception as exc:
        print(
            f"::warning::Could not save selection history to s3://{HISTORY_BUCKET}/{key}. {exc}",
            file=sys.stderr,
        )
        return
    print(f"Saved selection history to s3://{HISTORY_BUCKET}/{key}", file=sys.stderr)


def save_history(pr_number: int, document: dict) -> None:
    key = history_key(pr_number)
    client = s3_client()
    if client is None:
        print(
            f"::warning::Selection history was not saved. "
            f"Set AWS_ACCESS_KEY_ID to write s3://{HISTORY_BUCKET}/{key}",
            file=sys.stderr,
        )
        return
    try:
        client.put_object(
            Bucket=HISTORY_BUCKET,
            Key=key,
            Body=json.dumps(document, indent=2).encode(),
            ContentType="application/json",
        )
    except Exception as exc:
        print(
            f"::warning::Could not save selection history to s3://{HISTORY_BUCKET}/{key}. {exc}",
            file=sys.stderr,
        )
        return
    print(f"Saved selection history to s3://{HISTORY_BUCKET}/{key}", file=sys.stderr)


def select(pr: dict, root: Path) -> dict:
    features = load_features(root / TAXONOMY_PATH)
    suites = load_suites(root / MAPPING_PATH)
    skill = (root / SKILL_PATH).read_text()
    plan = run_agent(build_prompt(pr, skill), root, features, suites)
    report = plan.get("report_markdown")
    if not isinstance(report, str) or not report.strip():
        raise SelectionError("The plan has no report_markdown.")
    jobs = validate_jobs(suites, plan.get("jobs"))
    jobs = union_jobs(load_previous_jobs(pr["number"]), jobs)
    return {"report_markdown": report, "jobs": jobs}


def emit(pr: dict, plan: dict, root: Path) -> None:
    document = {
        "pr": pr["number"],
        "repo": pr["repo"],
        "url": pr["url"],
        "sha": pr["sha"],
        "version": pr["version"],
        "packages": pr["packages"],
        "report_markdown": plan["report_markdown"],
        "jobs": plan["jobs"],
    }
    (root / PLAN_NAME).write_text(json.dumps(document, indent=2) + "\n")
    run_jobs = [
        {key: value for key, value in job.items() if key != "carried_forward"}
        for job in plan["jobs"]
    ]
    write_github_output("jobs", json.dumps(run_jobs))
    write_github_output("job_count", str(len(plan["jobs"])))
    write_github_output("version", pr["version"])
    write_github_output("package_x86", pr["packages"]["x86"])
    write_github_output("package_arm64", pr["packages"]["arm64"])
    write_github_output("pr_number", str(pr["number"]))
    write_github_output("sha", pr["sha"])

    job_lines = "\n".join(
        (
            f"- `{job['suite_name']}` {job['regression_args']}"
            + (" (kept from an earlier commit)" if job.get("carried_forward") else "")
        ).rstrip()
        for job in plan["jobs"]
    ) or "- Nothing to run."
    write_summary(
        "\n".join(
            [
                f"## PR {pr['number']}",
                f"- {pr['url']}",
                f"- `{pr['sha']}`",
                f"- version `{pr['version']}`",
                f"- x86 package `{pr['packages']['x86']}`",
                f"- arm64 package `{pr['packages']['arm64']}`",
                "",
                plan["report_markdown"],
                "",
                "## Jobs on x86 and arm64",
                job_lines,
                "",
            ]
        )
    )
    save_history(pr["number"], document)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", help="Pull request number or URL")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    if not args.pr:
        raise SelectionError("Pass --pr.")
    repo, number = parse_pr(args.pr)
    pr = load_pr(repo, number)
    plan = select(pr, root)
    emit(pr, plan, root)


if __name__ == "__main__":
    try:
        main()
    except SelectionError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        sys.exit(1)
