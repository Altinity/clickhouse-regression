#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from window_functions.requirements import (
    SRS019_ClickHouse_Window_Functions,
    RQ_SRS_019_ClickHouse_WindowFunctions,
)
from helpers.common import check_clickhouse_version, experimental_analyzer


xfails = {
    "tests/:/frame clause/range frame/between expr following and expr following without order by error": [
        (Fail, "invalid error message")
    ],
    "tests/:/frame clause/range frame/between expr following and expr preceding without order by error": [
        (Fail, "invalid error message")
    ],
    "tests/:/frame clause/range frame/between expr following and current row without order by error": [
        (Fail, "invalid error message")
    ],
    "tests/:/frame clause/range frame/between expr following and current row zero special case": [
        (Fail, "known bug")
    ],
    "tests/:/frame clause/range frame/between expr following and expr preceding with order by zero special case": [
        (Fail, "known bug")
    ],
    "tests/:/funcs/lag/anyOrNull with column value as offset": [
        (Fail, "column values are not supported as offset")
    ],
    "tests/:/funcs/lead/subquery as offset": [
        (Fail, "subquery is not supported as offset")
    ],
    "tests/:/frame clause/range frame/between current row and unbounded following modifying named window": [
        (Fail, "range with named window is not supported")
    ],
    "tests/:/frame clause/range overflow/negative overflow with Int16": [
        (Fail, "exception on conversion")
    ],
    "tests/:/frame clause/range overflow/positive overflow with Int16": [
        (Fail, "exception on conversion")
    ],
    "tests/:/misc/subquery expr preceding": [
        (Fail, "subquery is not supported as offset")
    ],
    "tests/:/frame clause/range errors/error negative preceding offset": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22442")
    ],
    "tests/:/frame clause/range errors/error negative following offset": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22442")
    ],
    "tests/:/misc/window functions in select expression": [
        (Fail, "not supported, https://github.com/ClickHouse/ClickHouse/issues/19857")
    ],
    "tests/:/misc/window functions in subquery": [
        (Fail, "not supported, https://github.com/ClickHouse/ClickHouse/issues/19857")
    ],
    "tests/:/misc/in view": [
        (Fail, "bug, https://github.com/ClickHouse/ClickHouse/issues/26001")
    ],
    "tests/:/frame clause/range frame/order by decimal": [
        (
            Fail,
            "Exception: The RANGE OFFSET frame for 'DB::ColumnDecimal<DB::Decimal<long> >' ORDER BY column is not implemented",
        )
    ],
    "tests/:/frame clause/range frame/with nulls": [
        (
            Fail,
            "DB::Exception: The RANGE OFFSET frame for 'DB::ColumnNullable' ORDER BY column is not implemented",
        )
    ],
    "tests/:/aggregate funcs/aggregate funcs over rows frame/"
    + name.clean("func='mannWhitneyUTest(salary, 1)'"): [(Fail, "need to investigate")],
    "tests/:/aggregate funcs/aggregate funcs over rows frame/"
    + name.clean("func='rankCorr(salary, 0.5)'"): [(Fail, "need to investigate")],
    "tests/distributed/misc/query with order by and one window": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/23902")
    ],
    "tests/distributed/over clause/empty named window": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/23902")
    ],
    "tests/distributed/over clause/empty": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/23902")
    ],
    "tests/distributed/over clause/adhoc window": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/23902")
    ],
    "tests/distributed/frame clause/range datetime/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/23902")
    ],
    "tests/distributed/frame clause/range frame/between expr preceding and expr following with partition by same column twice": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/23902")
    ],
    "tests/:/funcs/leadInFrame/explicit default value": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/25057")
    ],
    "tests/:/funcs/leadInFrame/with nulls": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/25057")
    ],
    "tests/:/funcs/leadInFrame/default offset": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/23902")
    ],
    "tests/:/funcs/lagInFrame/explicit default value": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/25057")
    ],
    "tests/:/funcs/lagInFrame/with nulls": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/25057")
    ],
    "tests/:/funcs/lagInFrame/default offset": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/23902")
    ],
    "tests/:/time decayed funcs/exponentialTimeDecayed:/check decay length with INTERVAL": [
        (Fail, "not supported and should return an error")
    ],
    "tests/:/non-negative derivative func/check intervals/valid/:": [
        (Fail, "bug, LOGICAL_ERROR that needs to be investigated")
    ],
    "tests/:/non-negative derivative func/valid metric types/:": [
        (Fail, "bug, LOGICAL_ERROR that needs to be investigated")
    ],
    "tests/:/non-negative derivative func/valid timestamp types/:": [
        (Fail, "bug, LOGICAL_ERROR that needs to be investigated")
    ],
    "tests/:/non-negative derivative func/check one row per partition": [
        (Fail, "bug, LOGICAL_ERROR that needs to be investigated")
    ],
    "tests/:/non-negative derivative func/check over windows/:": [
        (Fail, "bug, LOGICAL_ERROR that needs to be investigated")
    ],
    "tests/:/funcs/last value/partition by window/using last_value": [
        (
            Fail,
            "23.2 fail https://github.com/ClickHouse/ClickHouse/issues/49461",
            check_clickhouse_version(">=23.2"),
        )
    ],
    "tests/:/funcs/last value/partition by window/using anyLast:": [
        (
            Fail,
            "23.2 fail https://github.com/ClickHouse/ClickHouse/issues/49461",
            check_clickhouse_version(">=23.2"),
        )
    ],
    "/window functions/tests/:/time decayed funcs/exponentialTimeDecayed:/:/:": [
        (Fail, "not working correctly on 22.3", check_clickhouse_version("<22.8"))
    ],
    "/window functions/tests/:/aggregate funcs/avgWeighted/decimal value and weight/*": [
        (
            Fail,
            "can not use the aggregate function avgWeighted with arguments of type Decimal from 23.11",
            check_clickhouse_version(">=23.11"),
        )
    ],
    "/window functions/tests/:/aggregate funcs/avgWeighted/decimal weight/*": [
        (
            Fail,
            "can not use the aggregate function avgWeighted with arguments of type Decimal from 23.11",
            check_clickhouse_version(">=23.11"),
        )
    ],
    "/window functions/tests/distributed/misc/subquery multiple window functions/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/58714",
            check_clickhouse_version(">=23.11"),
        )
    ],
    "/window functions/tests/non distributed/misc/subquery multiple window functions with bigger table/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/58714",
            check_clickhouse_version(">=23.11"),
        )
    ],
    "/window functions/tests/*/errors/error named window defined twice/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/63539",
        )
    ],
    "/window functions/tests/distributed/over clause/invalid window name/*": [
        (Fail, "was fixed in 24.5", check_clickhouse_version("<24.5"))
    ],
    "/window functions/tests/distributed/errors/error using non window function/*": [
        (Fail, "was fixed in 24.5", check_clickhouse_version("<24.5")),
    ],
    "/window functions/tests/non distributed/over clause/invalid window name/*": [
        (Fail, "was fixed in 24.5", check_clickhouse_version("<24.5")),
    ],
    "/window functions/tests/non distributed/errors/error using non window function/*": [
        (Fail, "was fixed in 24.5", check_clickhouse_version("<24.5")),
    ],
}

xflags = {}

ffails = {
    "tests/:/datatypes/low cardinality": (
        Skip,
        "Server crashes on 21.9 and 21.10",
        (
            lambda test: check_clickhouse_version(">=21.9")(test)
            and check_clickhouse_version("<21.11")(test)
        ),
    ),
    "tests/:/aggregate funcs/avgWeighted/:": (
        Skip,
        "Server crashes on 21.9",
        (
            lambda test: check_clickhouse_version(">=21.9")(test)
            and check_clickhouse_version("<21.10")(test)
        ),
    ),
    "tests/:/time decayed funcs": (
        Skip,
        "Not implemented before 21.11",
        check_clickhouse_version("<21.11"),
    ),
    "tests/:/non-negative derivative func": (
        Skip,
        "Not implemented before 22.6",
        check_clickhouse_version("<22.6"),
    ),
}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("window functions")
@Specifications(SRS019_ClickHouse_Window_Functions)
@Requirements(RQ_SRS_019_ClickHouse_WindowFunctions("1.0"))
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """Window functions regression."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

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

    Feature(run=load("window_functions.tests.feature", "feature"), flags=TE)


if main():
    regression()
