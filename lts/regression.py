#!/usr/bin/env python3
"""LTS regression: run clickhouse-odbc tests against ClickHouse (e.g. LTS builds)."""
import os
import subprocess

from testflows.core import *

append_path(sys.path, "..")

from helpers.argparser import argparser, CaptureClusterArgs


def lts_argparser(parser):
    """Extended argument parser for LTS/ODBC suite."""
    argparser(parser)
    parser.add_argument(
        "--odbc-release",
        type=str,
        dest="odbc_release",
        help="clickhouse-odbc driver version (git tag), default: v1.2.1.20220905",
        default="v1.2.1.20220905",
    )


@TestModule
@Name("lts")
@ArgumentParser(lts_argparser)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    odbc_release="v1.2.1.20220905",
    stress=None,
    with_analyzer=False,
):
    """Run clickhouse-odbc tests in a Docker container against the given ClickHouse image."""
    suite_dir = os.path.dirname(os.path.abspath(__file__))
    odbc_dir = os.path.join(suite_dir, "odbc")
    packages_dir = os.path.join(odbc_dir, "PACKAGES")
    os.makedirs(packages_dir, exist_ok=True)

    clickhouse_path = cluster_args.get("clickhouse_path", "/usr/bin/clickhouse")
    if clickhouse_path and str(clickhouse_path).startswith("docker://"):
        clickhouse_image = str(clickhouse_path).removeprefix("docker://")
    else:
        clickhouse_image = "altinityinfra/clickhouse-server:0-25.8.16.10001.altinitytest"

    with Scenario("build ODBC runner image"):
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
        result = subprocess.run(build_cmd, cwd=odbc_dir)
        if result.returncode != 0:
            fail(f"docker build failed with exit code {result.returncode}")

    with Scenario("run clickhouse-odbc tests"):
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
        result = subprocess.run(run_cmd, cwd=odbc_dir)
        if result.returncode != 0:
            fail(f"docker run failed with exit code {result.returncode}")

    with Scenario("verify test results"):
        test_log = os.path.join(packages_dir, "test.log")
        if not os.path.exists(test_log):
            fail(f"test.log not found at {test_log}")

        with open(test_log) as f:
            log_content = f.read()

        if "tests failed" in log_content and "0 tests failed" not in log_content:
            fail(f"Tests failed. See {test_log}:\n{log_content[-2000:]}")

        note(f"Tests passed. Log: {test_log}")


if main():
    regression()
