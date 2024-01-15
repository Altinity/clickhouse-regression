#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser
from helpers.common import check_clickhouse_version
from object_storage_vfs.tests.steps import enable_vfs
from data_types.requirements import SRS018_ClickHouse_Map_Data_Type

xfails = {
    "map/table map with key integer/Int:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21032")
    ],
    "map/table map with value integer/Int:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21032")
    ],
    "map/table map with key integer/UInt256": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21031")
    ],
    "map/table map with value integer/UInt256": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21031")
    ],
    "map/select map with key integer/Int64": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21030")
    ],
    "map/select map with value integer/Int64": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21030")
    ],
    "map/cast tuple of two arrays to map/string -> int": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21029")
    ],
    "map/mapcontains/null key in map": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21028")
    ],
    "map/mapcontains/null key not in map": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21028")
    ],
    "map/mapkeys/null key not in map": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21028")
    ],
    "map/mapkeys/null key in map": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21028")
    ],
    "map/mapcontains/select nullable key": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21026")
    ],
    "map/mapkeys/select keys from column": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21026")
    ],
    "map/table map select key with value string/LowCardinality:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21406")
    ],
    "map/table map select key with key string/FixedString": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21406")
    ],
    "map/table map select key with key string/Nullable": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21406")
    ],
    "map/table map select key with key string/Nullable(NULL)": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21026")
    ],
    "map/table map select key with key string/LowCardinality:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21406")
    ],
    "map/table map select key with key integer/Int:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21032")
    ],
    "map/table map select key with key integer/UInt256": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21031")
    ],
    "map/table map select key with key integer/toNullable": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21406")
    ],
    "map/table map select key with key integer/toNullable(NULL)": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/21026")
    ],
    "map/select map with key integer/Int128": [
        (Fail, "large Int128 as key not supported")
    ],
    "map/select map with key integer/Int256": [
        (Fail, "large Int256 as key not supported")
    ],
    "map/select map with key integer/UInt256": [
        (Fail, "large UInt256 as key not supported")
    ],
    "map/select map with key integer/toNullable": [
        (Fail, "Nullable type as key not supported")
    ],
    "map/select map with key integer/toNullable(NULL)": [
        (Fail, "Nullable type as key not supported")
    ],
    "map/select map with key string/Nullable": [
        (Fail, "Nullable type as key not supported")
    ],
    "map/select map with key string/Nullable(NULL)": [
        (Fail, "Nullable type as key not supported")
    ],
    "map/table map queries/select map with nullable value": [
        (Fail, "Nullable value not supported")
    ],
    "map/table map with key integer/toNullable": [
        (Fail, "Nullable type as key not supported")
    ],
    "map/table map with key integer/toNullable(NULL)": [
        (Fail, "Nullable type as key not supported")
    ],
    "map/table map with key string/Nullable": [
        (Fail, "Nullable type as key not supported")
    ],
    "map/table map with key string/Nullable(NULL)": [
        (Fail, "Nullable type as key not supported")
    ],
    "map/table map with key string/LowCardinality(String)": [
        (Fail, "LowCardinality(String) as key not supported")
    ],
    "map/table map with key string/LowCardinality(String) cast from String": [
        (Fail, "LowCardinality(String) as key not supported")
    ],
    "map/table map with key string/LowCardinality(String) for key and value": [
        (Fail, "LowCardinality(String) as key not supported")
    ],
    "map/table map with key string/LowCardinality(FixedString)": [
        (Fail, "LowCardinality(FixedString) as key not supported")
    ],
    "map/table map with value string/LowCardinality(String) for key and value": [
        (Fail, "LowCardinality(String) as key not supported")
    ],
    # JSON related
    "map/table map with duplicated keys/Map(Int64, String))": [
        (Fail, "new bug due to JSON changes")
    ],
    "map/table map with key integer/UInt64": [(Fail, "new bug due to JSON changes")],
    "map/table map with value integer/UInt64": [(Fail, "new bug due to JSON changes")],
    "map/:/:": [(Fail, "debug")],
}

xflags = {}

ffails = {
    "/clickhouse/data types/map/table map unsupported types/nullable map": (
        XFail,
        "type supported in 21.12",
        (lambda test: check_clickhouse_version(">=21.12")(test)),
    ),
    "/clickhouse/data types/map/table map unsupported types/map with nothing type for key and value": (
        XFail,
        "type supported in 21.12",
        (lambda test: check_clickhouse_version(">=21.12")(test)),
    ),
    "/clickhouse/data types/map/table map invalid key/integer when key is string": (
        XFail,
        "type supported in 21.12",
        (lambda test: check_clickhouse_version(">=21.12")(test)),
    ),
}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("data types")
@Specifications(SRS018_ClickHouse_Map_Data_Type)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress=None,
    allow_vfs=False,
):
    """Map type regression."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
    
    if allow_vfs:
        with Given("I enable allow_object_storage_vfs"):
            enable_vfs()

    Feature(run=load("data_types.tests.map", "feature"))


if main():
    regression()
