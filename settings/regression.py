#!/usr/bin/env python3
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import (
    argparser,
    CaptureClusterArgs,
)

from helpers.common import check_clickhouse_version, check_if_head, check_with_any_sanitizer

xfails = {
    # Profiler settings have different defaults in sanitizer builds (profilers disabled)
    "/settings/default values/query_profiler_cpu_time_period_ns": [
        (
            Fail,
            "Profilers are disabled in sanitizer builds",
            check_with_any_sanitizer,
        )
    ],
    "/settings/default values/query_profiler_real_time_period_ns": [
        (
            Fail,
            "Profilers are disabled in sanitizer builds",
            check_with_any_sanitizer,
        )
    ],
    "/settings/default values/parallel_replicas_mark_segment_size": [
        (
            Fail,
            "https://altinity.slack.com/archives/C07TTAQ7GN5/p1750239551029079",
            lambda test: check_clickhouse_version(">=24.8")(test)
            and check_clickhouse_version("<24.9")(test),
        )
    ],
    "/settings/default values/query_plan_merge_filters": [
        (
            Fail,
            "altinity 1, upstream 0",
            lambda test: check_clickhouse_version(">=24.8")(test)
            and check_clickhouse_version("<24.9")(test),
        )
    ],
    "/settings/default values/input_format_parquet_filter_push_down": [
        (
            Fail,
            "Altinity 0, upstream 1",
            lambda test: check_clickhouse_version(">=24.3")(test)
            and check_clickhouse_version("<24.4")(test),
        )
    ],
    "/settings/default values/compile_expressions": [
        (
            Fail,
            "Altinity 0, upstream 1",
            lambda test: check_clickhouse_version(">=23.3")(test)
            and check_clickhouse_version("<23.4")(test),
        )
    ],
    "/settings/default values/max_alter_threads": [
        (
            Fail,
            "Need to investigate",
        )
    ],
    "/settings/default values/max_final_threads": [
        (
            Fail,
            "Need to investigate",
        )
    ],
    "/settings/default values/max_parsing_threads": [
        (
            Fail,
            "Need to investigate",
        )
    ],
    "/settings/default values/max_threads": [
        (
            Fail,
            "Need to investigate",
        )
    ],
    "/settings/default values/enable_job_stack_trace": [
        (
            Fail,
            "Need to investigate",
        )
    ],
    "/settings/default values/*": [
        (
            Fail,
            "A lot of changes on head, do not need to track before release.",
            check_if_head,
        )
    ],
    "/settings/default values/allow_experimental_database_glue_catalog": [
        (
            Fail,
            "1 by default from 25.6",
            check_clickhouse_version("<25.6"),
        )
    ],
    "/settings/default values/allow_experimental_database_iceberg": [
        (
            Fail,
            "1 by default from 25.6",
            check_clickhouse_version("<25.6"),
        )
    ],
    "/settings/default values/allow_experimental_database_unity_catalog": [
        (
            Fail,
            "1 by default from 25.6",
            check_clickhouse_version("<25.6"),
        )
    ],
}

ffails = {
    "/settings/default values": (
        Skip,
        "Skip before 23.3",
        check_clickhouse_version("<23.3"),
    )
}


@TestModule
@Name("settings")
@FFails(ffails)
@XFails(xfails)
@ArgumentParser(argparser)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
    minio_args=None,
):
    """Run tests for Swarm clusters."""
    nodes = {
        "clickhouse": ("clickhouse1",),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    self.context.node = self.context.cluster.node("clickhouse1")

    Feature(test=load("settings.tests.default_values", "feature"))()


if main():
    regression()
