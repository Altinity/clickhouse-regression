"""Run a tool's own upstream test suite in a runner container and report each test."""

import glob
import os
import shutil

from testflows.core import *

from lts.steps.docker import (
    build_runner_image,
    run_runner_container,
    suite_results_dir,
    tail,
)
from lts.steps.junit import report_junit_results


def run_upstream_tests(
    suite,
    configs_dir,
    env,
    build_args=None,
    mounts=None,
    docker_args=None,
    timeout=None,
    xml_glob="junit.xml",
    strip_prefix="",
    min_tests=1,
    max_skipped=None,
    ok_exit_codes=(0,),
):
    """Build ``configs_dir`` into a runner image, run it, and report its JUnit XML
    as features and scenarios nested under the current test.

    The runner writes JUnit XML under ``/results``, which is mounted from
    ``lts/_instances/<suite>``; ``xml_glob`` is relative to that directory.
    The build and test output go to ``lts/_instances/<suite>/logs``.
    ``mounts`` maps host paths (created if missing) or named volumes to
    container paths. The runner exits with the test tool's exit code, and the
    suite fails if it is not in ``ok_exit_codes``, because an internal error
    or a crash can leave partial JUnit XML in which every test passed.
    """
    results_dir = suite_results_dir(suite)
    for entry in os.listdir(results_dir):
        path = os.path.join(results_dir, entry)
        if entry == "logs":
            continue
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            os.remove(path)
    for host_path in mounts or {}:
        if os.path.isabs(host_path) and not os.path.exists(host_path):
            os.makedirs(host_path)
    logs_dir = os.path.join(results_dir, "logs")
    image = f"lts-{suite}-runner"

    with Given("runner image is built"):
        build_runner_image(
            context_dir=configs_dir,
            tag=image,
            build_args=build_args,
            log_path=os.path.join(logs_dir, "build.log"),
        )

    with When("upstream tests run in the runner container"):
        exitcode = run_runner_container(
            image=image,
            name=f"lts-{suite}-{os.getpid()}",
            log_path=os.path.join(logs_dir, "test.log"),
            env=env,
            mounts={results_dir: "/results", **(mounts or {})},
            docker_args=docker_args,
            timeout=timeout,
        )

    xml_glob = os.path.join(results_dir, xml_glob)
    if not glob.glob(xml_glob):
        fail(
            f"the runner wrote no JUnit XML ({xml_glob}), so the tests did not run. "
            f"Tail of {os.path.join(logs_dir, 'test.log')}:\n"
            + tail(os.path.join(logs_dir, "test.log"))
        )

    report_junit_results(
        xml_glob=xml_glob,
        strip_prefix=strip_prefix,
        min_tests=min_tests,
        max_skipped=max_skipped,
    )

    if exitcode not in ok_exit_codes:
        fail(
            f"the runner exited with code {exitcode}, expected one of {list(ok_exit_codes)}. "
            f"Tail of {os.path.join(logs_dir, 'test.log')}:\n"
            + tail(os.path.join(logs_dir, "test.log"))
        )
