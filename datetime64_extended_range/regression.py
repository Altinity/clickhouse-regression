#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.common import experimental_analyzer
from helpers.argparser import argparser, CaptureClusterArgs
from datetime64_extended_range.requirements import *
from datetime64_extended_range.common import *
from datetime64_extended_range.requirements import RQ_SRS_010_DateTime64_ExtendedRange

# cross-outs
# https://github.com/ClickHouse/ClickHouse/issues/16581#issuecomment-804360350: 128 and 256-bit types are not supported for now
# https://github.com/ClickHouse/ClickHouse/issues/17079#issuecomment-783396589 : leap seconds unsupported
# https://github.com/ClickHouse/ClickHouse/issues/22824 : dateDiff not working woth dt64
# https://github.com/ClickHouse/ClickHouse/issues/22852 : formatDateTime wrong value
# https://github.com/ClickHouse/ClickHouse/issues/22854 : timeSlot(), toMonday() wrong when out of normal
# https://github.com/ClickHouse/ClickHouse/issues/16260 : timeSlots(), dateDiff() not working with DT64
# https://github.com/ClickHouse/ClickHouse/issues/22927#issuecomment-816574952 : toRelative...Num() wrong when out of normal range
# https://github.com/ClickHouse/ClickHouse/issues/22928 : toStartOf...() wrong when out of normal range
# https://github.com/ClickHouse/ClickHouse/issues/22929 : toUnixTimestamp() exception when out of normal
# https://github.com/ClickHouse/ClickHouse/issues/22930 : toWeek()
# https://github.com/ClickHouse/ClickHouse/issues/22948 : toYearWeek()
# https://github.com/ClickHouse/ClickHouse/issues/22959 : toUnixTimestamp64*() wrong fractal seconds treatment
# https://github.com/ClickHouse/ClickHouse/issues/34831 : DateTime64 to Arrow format mistreats negative timestamps

# For `reference times` test it is unclear how to evaluate correctness - majority of test cases are correct, and ONLY
# Juba and Monrovia timezones are damaged - probably, due to wrong DST shifts lookup tables

xfails = {
    "type conversion/to int 8 16 32 64 128 256/:": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/16581#issuecomment-804360350",
        )
    ],
    "type conversion/to uint 8 16 32 64 256/:": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/16581#issuecomment-804360350",
        )
    ],
    "non existent time/leap seconds/:": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/17079#issuecomment-783396589",
        )
    ],
    "date time funcs/format date time/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22852")
    ],
    "date time funcs/time slot/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22854")
    ],
    "date time funcs/to monday/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22854")
    ],
    "date time funcs/time slots/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/16260")
    ],
    "date time funcs/to relative :/:": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/22927#issuecomment-816574952",
        )
    ],
    "date time funcs/to start of :/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22928")
    ],
    "date time funcs/to unix timestamp/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22929")
    ],
    "date time funcs/to week/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22930")
    ],
    "date time funcs/to year week/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22948")
    ],
    "type conversion/to unix timestamp64 */:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22959")
    ],
    "type conversion/from unix timestamp64 */:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22959")
    ],
    "reference times/:": [(Fail, "check procedure unclear")],
    "generic/transform/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/32387")
    ],
    "format conversion/arrow format/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/34831")
    ],
    "type conversion/to datetime/:": [(Fail, "needs to be investigated")],
    "/datetime64 extended range/date time funcs/date diff/*1927-01-01*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/pull/42308",
            check_clickhouse_version("<22.9"),
        )
    ],
    "/datetime64 extended range/date time funcs/date diff/*1927-12-31*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/pull/42308",
            check_clickhouse_version("<22.9"),
        )
    ],
    "/datetime64 extended range/date time funcs/date diff/*2236-01-01*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/pull/42308",
            check_clickhouse_version("<22.9"),
        )
    ],
    "/datetime64 extended range/date time funcs/date diff/*2236-12-31*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/pull/42308",
            check_clickhouse_version("<22.9"),
        )
    ],
    "/datetime64 extended range/date time funcs/date diff/*2236-02-29*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/pull/42308",
            check_clickhouse_version("<22.9"),
        )
    ],
}

ffails = {
    "type conversion/to date32/:": (
        XFail,
        "toDate32 not implemented before 21.10",
        (lambda test: check_clickhouse_version("<21.10")(test)),
    )
}


@TestModule
@Name("datetime64 extended range")
@ArgumentParser(argparser)
@Specifications(QA_SRS010_ClickHouse_DateTime64_Extended_Range)
@Requirements(
    RQ_SRS_010_DateTime64_ExtendedRange("1.0"),
)
@XFails(xfails)
@FFails(ffails)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=False,
    with_analyzer=False,
):
    """ClickHouse DateTime64 Extended Range regression module."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
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

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    with Pool(2) as pool:
        try:
            Scenario(
                run=load("datetime64_extended_range.tests.generic", "generic"),
                parallel=True,
                executor=pool,
            )
            Scenario(
                run=load(
                    "datetime64_extended_range.tests.non_existent_time", "feature"
                ),
                parallel=True,
                executor=pool,
            )
            Scenario(
                run=load(
                    "datetime64_extended_range.tests.reference_times",
                    "reference_times",
                ),
                parallel=True,
                executor=pool,
            )
            Scenario(
                run=load(
                    "datetime64_extended_range.tests.date_time_functions",
                    "date_time_funcs",
                ),
                parallel=True,
                executor=pool,
            )
            Scenario(
                run=load(
                    "datetime64_extended_range.tests.type_conversion",
                    "type_conversion",
                ),
                parallel=True,
                executor=pool,
            )
            Scenario(
                run=load(
                    "datetime64_extended_range.tests.format_conversion",
                    "format_conversion",
                ),
                parallel=True,
                executor=pool,
            )
        finally:
            join()


if main():
    regression()
