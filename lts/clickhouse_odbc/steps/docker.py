"""Reusable steps for building and running the ODBC Docker test environment."""

import os
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
    """Verify that the test log shows no failures."""
    test_log = os.path.join(packages_dir, "test.log")
    if not os.path.exists(test_log):
        fail(f"test.log not found at {test_log}")

    with open(test_log) as f:
        log_content = f.read()

    if "tests failed" in log_content and "0 tests failed" not in log_content:
        fail(f"Tests failed. See {test_log}:\n{log_content[-2000:]}")

    note(f"Tests passed. Log: {test_log}")
