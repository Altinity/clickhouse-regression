"""Reusable steps for building and running the ODBC Docker test environment."""

import os
import re
import subprocess

from testflows.core import *


@TestStep(Given)
def build_odbc_runner_image(self, configs_dir, clickhouse_image):
    """Build the Docker image for the clickhouse-odbc test runner."""
    build_cmd = [
        "docker",
        "build",
        "--build-arg",
        f"CLICKHOUSE_IMAGE={clickhouse_image}",
        "-t",
        "clickhouse-odbc-runner",
        ".",
    ]
    note(f"Running: {' '.join(build_cmd)}")
    result = subprocess.run(build_cmd, cwd=configs_dir)
    if result.returncode != 0:
        fail(f"docker build failed with exit code {result.returncode}")


@TestStep(When)
def run_odbc_tests_in_container(self, configs_dir, packages_dir, odbc_release):
    """Run clickhouse-odbc tests inside the Docker container."""
    # Clear any stale logs from a previous run so verify_test_results
    # doesn't accidentally read old data when the container fails early.
    for stale in ("test.log", "test_detailed.log"):
        path = os.path.join(packages_dir, stale)
        if os.path.exists(path):
            os.remove(path)

    run_cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{packages_dir}:/clickhouse",
        "-e",
        f"RELEASE={odbc_release}",
        "clickhouse-odbc-runner",
    ]
    note(f"Running: {' '.join(run_cmd)}")
    result = subprocess.run(run_cmd, cwd=configs_dir)
    if result.returncode != 0:
        fail(f"docker run failed with exit code {result.returncode}")


@TestStep(Then)
def verify_test_results(self, packages_dir):
    """Verify that the test log shows no failures.

    Parses ctest summary lines such as
    ``100% tests passed, 0 tests failed out of N`` to determine pass/fail.
    """
    test_log = os.path.join(packages_dir, "test.log")
    if not os.path.exists(test_log):
        fail(f"test.log not found at {test_log}")

    with open(test_log) as f:
        log_content = f.read()

    summary = re.search(
        r"(\d+)% tests passed,\s+(\d+) tests failed out of\s+(\d+)",
        log_content,
    )
    if summary is None:
        fail(
            f"Could not find ctest summary line in {test_log}. "
            f"Tail of log:\n{log_content[-2000:]}"
        )

    failed = int(summary.group(2))
    total = int(summary.group(3))
    if failed > 0:
        fail(
            f"{failed}/{total} ODBC tests failed. See {test_log}:\n"
            f"{log_content[-2000:]}"
        )

    note(f"All {total} ODBC tests passed. Log: {test_log}")
