"""clickhouse-jdbc sub-suite feature loaded by the LTS orchestrator."""

import os
import subprocess

from testflows.core import *

from lts.clickhouse_jdbc.requirements.requirements import (
    SRS_105_ClickHouse_JDBC_Driver_clickhouse_jdbc_LTS_Testing,
    RQ_SRS_105_ClickHouseJDBC_UpstreamTests,
    RQ_SRS_105_ClickHouseJDBC_Compatibility_LTS,
)
from lts.steps.docker import pull_image, suite_results_dir
from lts.steps.upstream import run_upstream_tests


@TestFeature
@Name("clickhouse-jdbc")
@Specifications(SRS_105_ClickHouse_JDBC_Driver_clickhouse_jdbc_LTS_Testing)
@Requirements(
    RQ_SRS_105_ClickHouseJDBC_UpstreamTests("1.0"),
    RQ_SRS_105_ClickHouseJDBC_Compatibility_LTS("1.0"),
)
def feature(self, release="v0.9.9", maven_args="", timeout=7200):
    """Run the clickhouse-jdbc module tests of clickhouse-java at tag ``release``
    and report each upstream test.

    The tests start ClickHouse from the image themselves through the host
    Docker socket, so the runner uses the host network, and its work
    directory is mounted at the same path on the host and in the container.
    ``maven_args`` is appended to ``mvn verify``, for example
    ``-Dtest=ClickHouseConnectionTest -Dit.test=ClickHouseConnectionTest``.
    """
    clickhouse_image = self.context.clickhouse_image
    work_dir = os.path.join(suite_results_dir("clickhouse_jdbc"), "work")

    with Given("the ClickHouse image is pulled"):
        pull_image(image=clickhouse_image)

    docker_api_version = subprocess.run(
        ["docker", "version", "--format", "{{.Server.APIVersion}}"],
        capture_output=True,
        text=True,
    ).stdout.strip()
    note(f"host Docker API version: {docker_api_version}")

    run_upstream_tests(
        suite="clickhouse_jdbc",
        configs_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs"),
        env={
            "RELEASE": release,
            "CLICKHOUSE_IMAGE": clickhouse_image,
            "WORK_DIR": work_dir,
            "JDBC_MAVEN_ARGS": maven_args,
            "TESTCONTAINERS_HOST_OVERRIDE": "localhost",
            "DOCKER_API_VERSION": docker_api_version,
        },
        mounts={
            work_dir: work_dir,
            "/var/run/docker.sock": "/var/run/docker.sock",
            "lts-maven-cache": "/root/.m2",
        },
        docker_args=["--network", "host"],
        timeout=timeout,
        xml_glob="reports/*.xml",
        strip_prefix="com.clickhouse.",
        # v0.9.9 on 26.3: 320 tests (89 unit, 231 integration), none skipped.
        # --jdbc-maven-args usually selects a subset, so the guards are relaxed.
        min_tests=1 if maven_args else 300,
        max_skipped=None if maven_args else 5,
    )
