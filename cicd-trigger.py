#!/usr/bin/env python3
"""Manual GitHub Actions workflow trigger script.

This script allows triggering GitHub Actions workflows for running ClickHouse regression tests
on either x86 or ARM architectures. It supports various test suites and configuration options.

Example:
    Run example test suite on x86:
        python3 cicd-trigger.py --suite example

    Run example test suite on ARM:
        python3 cicd-trigger.py --suite example --arch arm

    Run with debug output:
        python3 cicd-trigger.py --suite example --debug

    List currently running workflows:
        python3 cicd-trigger.py --list-running
"""
import os
import sys
import time
import requests
import datetime
from argparse import ArgumentParser, RawTextHelpFormatter

# GitHub repository configuration
REPO_OWNER = "altinity"
REPO_NAME = "clickhouse-regression"
PROGRESS = "\u2591"

# Default values and choices
DEFAULTS = {
    "package": "docker://altinity/clickhouse-server:24.3.12.76.altinitystable",
    "version": "24.3.12.76.altinitystable",
    "flags": "none",
    "suite": "all",
    "output_format": "classic",
    "artifacts": "public",
    "branch": "main",
    "arch": "x86",
}

# Available choices for arguments
CHOICES = {
    "architectures": ["x86", "arm"],
    "flags": [
        "--use-keeper --with-analyzer",
        "--use-keeper",
        "none",
        "--as-binary",
        "--as-binary --use-keeper",
        "--thread-fuzzer",
        "--thread-fuzzer --use-keeper",
        "--thread-fuzzer --as-binary",
        "--thread-fuzzer --as-binary --use-keeper",
        "--with-analyzer",
        "--with-analyzer --use-keeper",
        "--with-analyzer --as-binary",
        "--with-analyzer --as-binary --use-keeper",
        "--thread-fuzzer --with-analyzer",
        "--thread-fuzzer --with-analyzer --use-keeper",
        "--thread-fuzzer --with-analyzer --as-binary",
        "--thread-fuzzer --with-analyzer --as-binary --use-keeper",
    ],
    "output_formats": [
        "nice-new-fails",
        "brisk-new-fails",
        "plain-new-fails",
        "pnice-new-fails",
        "new-fails",
        "classic",
        "nice",
        "fails",
        "slick",
        "brisk",
        "quiet",
        "short",
        "manual",
        "dots",
        "progress",
        "raw",
    ],
    "artifact_locations": ["internal", "public"],
    "suites": [
        "all",
        "all_aws",
        "all_gcs",
        "aes_encryption",
        "aggregate_functions",
        "atomic_insert",
        "alter_all",
        "alter_replace_partition",
        "alter_attach_partition",
        "alter_move_partition",
        "attach",
        "base_58",
        "benchmark_all",
        "benchmark_aws",
        "benchmark_gcs",
        "benchmark_minio",
        "clickhouse_keeper",
        "clickhouse_keeper_failover",
        "data_types",
        "datetime64_extended_range",
        "disk_level_encryption",
        "dns",
        "engines",
        "example",
        "extended_precision_data_types",
        "functions",
        "iceberg",
        "jwt_authentication",
        "kafka",
        "kerberos",
        "key_value",
        "ldap",
        "lightweight_delete",
        "memory",
        "parquet_all",
        "parquet",
        "parquet_minio",
        "parquet_s3",
        "part_moves_between_shards",
        "rbac",
        "s3_all",
        "s3_aws",
        "s3_azure",
        "s3_gcs",
        "s3_minio",
        "selects",
        "session_timezone",
        "ssl_server",
        "tiered_storage_all",
        "tiered_storage_aws",
        "tiered_storage_gcs",
        "tiered_storage_local",
        "tiered_storage_minio",
        "window_functions",
    ],
}


class Action:
    """Simple action wrapper for logging and error handling."""

    debug = False

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print(f"{timestamp()} \u270d  {self.name}")

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_value is not None:
            print(f"{timestamp()} \u274c Error", BaseException)
            if self.debug:
                raise
            sys.exit(1)
        else:
            print(f"{timestamp()} \u2705 OK")


def timestamp():
    """Return formatted timestamp string."""
    dt = datetime.datetime.now(datetime.timezone.utc)
    return dt.astimezone().strftime("%b %d,%Y %H:%M:%S.%f %Z")


def create_parser():
    """Create and configure argument parser."""
    parser = ArgumentParser(
        "cicd-trigger.py",
        description=__doc__,
        formatter_class=RawTextHelpFormatter,
    )

    # Add arguments with their choices and defaults
    parser.add_argument(
        "--arch",
        choices=CHOICES["architectures"],
        default=DEFAULTS["arch"],
        help=f"Choose architecture to run tests on, default: '{DEFAULTS['arch']}'",
    )
    parser.add_argument(
        "--branch",
        default=DEFAULTS["branch"],
        help=f"Choose which branch to run the tests on, default: '{DEFAULTS['branch']}'",
    )
    parser.add_argument(
        "--package",
        default=DEFAULTS["package"],
        help=(
            "Package specifier to use for tests. Either 'docker://' or 'https://'. "
            f"default: {DEFAULTS['package']}. "
            "Example: 'https://.../clickhouse-common-static_23.3.1.64_amd64.deb', "
            "or 'docker://altinity/clickhouse-server:23.8.8'"
        ),
    )
    parser.add_argument(
        "--version",
        default=DEFAULTS["version"],
        help=f"Expected version of clickhouse to use for tests, default: {DEFAULTS['version']}",
    )
    parser.add_argument(
        "--flags",
        choices=CHOICES["flags"],
        default=DEFAULTS["flags"],
        help="Test flags to use",
    )
    parser.add_argument(
        "-s",
        "--suite",
        choices=CHOICES["suites"],
        default=DEFAULTS["suite"],
        help=f"Choose specific suite to run, default: '{DEFAULTS['suite']}'",
    )
    parser.add_argument(
        "-o",
        "--output-format",
        choices=CHOICES["output_formats"],
        default=DEFAULTS["output_format"],
        help=f"Choose test program's output format, default: '{DEFAULTS['output_format']}'",
    )
    parser.add_argument(
        "--artifacts",
        choices=CHOICES["artifact_locations"],
        default=DEFAULTS["artifacts"],
        help=f"Specify artifact location, default: '{DEFAULTS['artifacts']}'",
    )
    parser.add_argument(
        "--ref",
        help="Commit SHA to checkout. Default: current branch.",
        default="",
    )
    parser.add_argument(
        "--extra-args",
        help="Extra test program arguments. Default: none.",
        default="",
    )
    parser.add_argument(
        "--custom-run-name",
        help="Custom run name (optional)",
        default="",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("GITHUB_TOKEN"),
        help="GitHub personal access token with workflow scope, default: $GITHUB_TOKEN env variable.",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for the workflow to finish, default: False",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode, default: False",
    )
    parser.add_argument(
        "--list-running",
        action="store_true",
        help="List all currently running workflows and exit",
    )

    return parser


def get_workflow_id(headers, arch):
    """Get workflow ID for the specified architecture."""
    response = requests.get(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows",
        headers=headers,
    )
    response.raise_for_status()
    workflows = response.json()["workflows"]

    workflow_path = (
        ".github/workflows/run-regression.yml"
        if arch == "x86"
        else ".github/workflows/run-arm-regression.yml"
    )
    try:
        workflow = next(w for w in workflows if w["path"] == workflow_path)
        print(f"   found workflow: {workflow['name']} ({workflow_path})")
        return workflow["id"]
    except StopIteration:
        print(f"Error: Could not find workflow at path '{workflow_path}'")
        print("Available workflows:")
        for w in workflows:
            print(f"  - {w['path']} ({w['name']})")
        sys.exit(1)


def prepare_inputs(args):
    """Prepare workflow inputs from command line arguments."""
    inputs = {}
    if args.package:
        assert args.package.startswith("docker://") or args.package.startswith(
            "https://"
        ), "package name should start with docker:// or https://"
        inputs["package"] = args.package
    if args.version:
        inputs["version"] = args.version
    if args.flags and args.flags != "none":
        inputs["flags"] = args.flags
    if args.suite:
        inputs["suite"] = args.suite
    if args.output_format:
        inputs["output_format"] = args.output_format
    if args.artifacts:
        inputs["artifacts"] = args.artifacts
    if args.ref:
        inputs["ref"] = args.ref
    if args.extra_args:
        inputs["extra_args"] = args.extra_args
    if args.custom_run_name:
        inputs["custom_run_name"] = args.custom_run_name

    return inputs


def wait_for_workflow(headers, branch):
    """Wait for workflow to complete and check its status."""
    i = 1
    sys.stdout.write(f"{timestamp()}    {PROGRESS}")
    sys.stdout.flush()

    try:
        while True:
            response = requests.get(
                f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs",
                headers=headers,
                params={"branch": branch, "status": "in_progress"},
            )
            response.raise_for_status()
            runs = response.json()["workflow_runs"]

            if not runs:
                break

            if i > 1 and i % 40 == 0:
                sys.stdout.write(f"\n{timestamp()}    ")
            sys.stdout.write(PROGRESS)
            sys.stdout.flush()
            time.sleep(1)
            i += 1
    finally:
        sys.stdout.write("\n")

    # Check final status
    response = requests.get(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs",
        headers=headers,
        params={"branch": branch, "status": "completed"},
    )
    response.raise_for_status()
    runs = response.json()["workflow_runs"]
    if runs and runs[0]["conclusion"] != "success":
        print(f"Error: Workflow completed with status: {runs[0]['conclusion']}")
        sys.exit(1)


def list_running_workflows(headers):
    """List all currently running workflows."""
    response = requests.get(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs",
        headers=headers,
        params={"status": "in_progress"},
    )
    response.raise_for_status()
    runs = response.json()["workflow_runs"]

    if not runs:
        print("No workflows are currently running.")
        return

    print("\nCurrently running workflows:")
    print("-" * 80)
    for run in runs:
        print(f"Workflow: {run['name']}")
        print(f"  ID: {run['id']}")
        print(f"  Branch: {run['head_branch']}")
        print(f"  Started: {run['created_at']}")
        print(f"  URL: {run['html_url']}")
        print("-" * 80)


def trigger():
    """Main function to trigger GitHub Actions workflow."""
    args = create_parser().parse_args()

    if args.debug:
        Action.debug = True

    if not args.token:
        print(
            "Error: GitHub token is required. Set GITHUB_TOKEN environment variable or use --token option."
        )
        sys.exit(1)

    headers = {
        "Authorization": f"token {args.token}",
        "Accept": "application/vnd.github.v3+json",
    }

    with Action("Authenticate with GitHub"):
        response = requests.get("https://api.github.com/user", headers=headers)
        response.raise_for_status()
        user = response.json()
        print(f"   authenticated as {user['login']}")

    if args.list_running:
        with Action("Listing running workflows"):
            list_running_workflows(headers)
        return

    with Action("Get workflow ID"):
        workflow_id = get_workflow_id(headers, args.arch)

    with Action("Trigger workflow"):
        inputs = prepare_inputs(args)

        if args.debug:
            print("\nDebug information:")
            print(f"  Workflow ID: {workflow_id}")
            print(f"  Branch: {args.branch}")
            print("  Inputs:")
            for k, v in inputs.items():
                print(f"    {k}: {v}")

        try:
            payload = {"ref": args.branch, "inputs": inputs}
            if args.debug:
                print("\n  Request payload:")
                print(f"    {payload}")

            response = requests.post(
                f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{workflow_id}/dispatches",
                headers=headers,
                json=payload,
            )

            if args.debug:
                print("\n  Response:")
                print(f"    Status code: {response.status_code}")
                print(f"    Response text: {response.text}")

            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"\nError triggering workflow: {e}")
            if e.response.status_code == 404:
                print(
                    "This might be because the workflow file doesn't exist or you don't have permission to access it."
                )
            elif e.response.status_code == 422:
                print(
                    "This might be because the inputs are invalid. Check the workflow file for valid input options."
                )
            print(f"Response: {e.response.text}")
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print(f"Error type: {type(e)}")
            if hasattr(e, "response"):
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            sys.exit(1)

        log_path = (
            "altinity-internal-test-reports"
            if args.artifacts == "internal"
            else "altinity-test-reports"
        )
        print(
            f"   Workflow triggered on branch {args.branch} for {args.arch} architecture\n"
            f"   \u2728 https://github.com/{REPO_OWNER}/{REPO_NAME}/actions \u2728"
        )
        print("\n".join(f"   {k}: {v}" for k, v in inputs.items()))
        print(
            f"   Job logs will be located in https://{log_path}.s3.amazonaws.com/index.html#clickhouse/{inputs['version']}/testflows/ after the run is complete"
        )

    if args.wait:
        with Action("Wait for workflow to finish"):
            wait_for_workflow(headers, args.branch)


if __name__ == "__main__":
    trigger()
