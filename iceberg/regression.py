#!/usr/bin/env python3
import sys
import warnings
from testflows.core import *

append_path(sys.path, "..")

from iceberg.requirements.requirements import *
from helpers.cluster import create_cluster
from helpers.argparser import (
    argparser_minio,
    CaptureClusterArgs,
    CaptureMinioArgs,
)
from helpers.common import (
    check_clickhouse_version,
    check_if_not_antalya_build,
    check_is_altinity_build,
    experimental_analyzer,
    check_if_antalya_build,
)


xfails = {
    "/iceberg/icebergS3 table function/recreate table/scan and display data with pyiceberg, expect empty table": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/rest catalog/icebergS3 table function/recreate table/*": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
    "/iceberg/icebergS3 table function/glue catalog/icebergS3 table function/recreate table/*": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
    "/iceberg/icebergS3 table function/rest catalog/icebergS3 table function/recreate table and insert new data/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/glue catalog/icebergS3 table function/recreate table and insert new data/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/rest catalog/icebergS3 table function/recreate table and insert new data multiple times/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/glue catalog/icebergS3 table function/recreate table and insert new data multiple times/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/*": [
        (Fail, "Need to investigate", check_clickhouse_version("<=24")),
    ],
    "/iceberg/iceberg engine/* catalog/swarm/*": [
        (Fail, "Only works with antalya build", check_if_not_antalya_build),
    ],
    "/iceberg/iceberg cache/rest catalog/iceberg table engine/*": [
        (Fail, "Need to investigate"),
    ],
    "/iceberg/iceberg cache/glue catalog/iceberg table engine/*": [
        (Fail, "Need to investigate"),
    ],
    "/iceberg/iceberg engine/* catalog/predicate push down/issue with decimal column": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/80200")
    ],
    "/iceberg/iceberg engine/* catalog/predicate push down/issue with float column": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/80200")
    ],
    "/iceberg/iceberg engine/* catalog/feature/multiple tables": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/75187",
            check_clickhouse_version("<25.3"),
        ),
    ],
    "/iceberg/iceberg engine/glue catalog/schema evolution/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/81272",
            check_clickhouse_version("<25.7"),
        )
    ],
    "/iceberg/iceberg engine/glue catalog/nested datatypes/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/81301",
            check_clickhouse_version("<25.5"),
        )
    ],
    "/iceberg/iceberg engine/glue catalog/feature/sanity/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/82601",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_clickhouse_version("<25.4")(test),
        )
    ],
    "/iceberg/iceberg engine/: catalog/feature/alter:/*": [
        (
            Fail,
            "https://github.com/clickhouse/clickhouse/issues/86024",
            check_clickhouse_version(">=25.8"),
        )
    ],
    "/iceberg/iceberg table engine/feature/alter:/*": [
        (
            Fail,
            "https://github.com/clickhouse/clickhouse/issues/86024",
            check_clickhouse_version(">=25.8"),
        )
    ],
    "/iceberg/iceberg table engine/feature/alter comment columns": [
        (
            Fail,
            "Need to investigate",
            check_clickhouse_version(">=25.6"),
        )
    ],
    "/iceberg/iceberg engine/rest catalog/feature/show databases queries/*": [
        (
            Fail,
            "https://github.com/Altinity/clickhouse-regression/issues/86",
            lambda test: check_clickhouse_version(">=25.8")(test)
            and check_if_antalya_build(),
        )
    ],
    "/iceberg/iceberg table engine/write min max pruning/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/91363",
            lambda test: (
                check_if_not_antalya_build() and check_clickhouse_version("<26.1")(test)
            )
            or (
                check_if_antalya_build() and check_clickhouse_version("<=25.8.9")(test)
            ),
        )
    ],
    "/iceberg/iceberg engine/glue catalog/feature/show data lake catalogs in system tables/*": [
        (
            Fail,
            "https://github.com/clickhouse/clickhouse/issues/91363",
            check_clickhouse_version(">=25.8"),
        )
    ],
    "/iceberg/iceberg cache/rest catalog/iceberg database engine/cache": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/1277",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_if_antalya_build(),
        )
    ],
    "/iceberg/iceberg cache/rest catalog/icebergS3 table function/cache": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/1277",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_if_antalya_build(),
        )
    ],
        "/iceberg/iceberg cache/glue catalog/iceberg database engine/cache": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/1277",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_if_antalya_build(),
        )
    ],
        "/iceberg/iceberg cache/glue catalog/icebergS3 table function/cache": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/1277",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_if_antalya_build(),
        )
    ],
    "/iceberg/iceberg engine/: catalog/iceberg partition pruning/check iceberg partition pruning with integer type": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/93416",
            check_clickhouse_version(">=26.1")
        )
    ],
    "/iceberg/iceberg engine/: catalog/iceberg partition pruning/check partition pruning with complex where clause": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/93416",
            check_clickhouse_version(">=26.1")
        )
    ],
    "/iceberg/iceberg engine/: catalog/iceberg partition pruning/partition pruning with date type": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/93416",
            check_clickhouse_version(">=26.1")
        )
    ],
}

ffails = {
    "/iceberg/iceberg engine": (
        Skip,
        "Iceberg engine was introduced in 24.12",
        check_clickhouse_version("<24.12"),
    ),
    "/iceberg/iceberg cache": (
        Skip,
        "Iceberg engine was introduced in 24.12",
        check_clickhouse_version("<24.12"),
    ),
    "/iceberg/icebergS3 table function": (
        Skip,
        "Iceberg engine was introduced in 23.2",
        check_clickhouse_version("<=23.2"),
    ),
    "/iceberg/s3 table function": (
        Skip,
        "Support for codec 'zstd' not built",
        check_clickhouse_version("<23.8"),
    ),
    "/iceberg/iceberg table engine": (
        Skip,
        "Iceberg table engine was introduced in 23.2",
        check_clickhouse_version("<24.2"),
    ),
    "/iceberg/iceberg cache/*": (
        Skip,
        "Metadata caching was introduced in antalya build from 24.12",
        check_if_not_antalya_build,
    ),
    "/iceberg/iceberg engine/: catalog/feature/show data lake catalogs in system tables": (
        Skip,
        "show_data_lake_catalogs_in_system_tables setting is not supported before 25.3 and on 25.4",
        lambda test: check_clickhouse_version("<25.3")(test)
        or check_clickhouse_version("==25.4")(test),
    ),
    "/iceberg/icebergS3 table function/: catalog/several iceberg tables in one dir": (
        Skip,
        "setting used for test introduced in 25.8",
        check_clickhouse_version("<25.8"),
    ),
    "/iceberg/iceberg engine/: catalog/iceberg iterator race condition/iceberg iterator race condition": (
        Skip,
        "https://github.com/ClickHouse/ClickHouse/issues/92120",
        lambda test: check_clickhouse_version("<=25.8.12")(test) or check_if_not_antalya_build(test),
    ),
    "/iceberg/iceberg engine/: catalog/namespace filtering": (
        Skip,
        "namespace filtering is supported only in antalya build from >= 25.8",
        lambda test: check_clickhouse_version("<=25.8.15")(test) or check_if_not_antalya_build(),
    ),
    "/iceberg/iceberg engine/: catalog/dot separated column names/*": (
        Skip,
        "dot-separated column names broken before 25.7 and in 25.11-26.1 (https://github.com/ClickHouse/ClickHouse/issues/94196)",
        lambda test: check_clickhouse_version("<25.7")(test)
        or (
            check_clickhouse_version(">=25.11")(test)
            and check_clickhouse_version("<26.2")(test)
        ),
    ),
    # "/iceberg/iceberg engine/: catalog/feature/alter:/*": (
    #     Skip,
    #     "https://github.com/clickhouse/clickhouse/issues/86024",
    #     check_clickhouse_version(">=25.8"),
    # ),
    # "/iceberg/iceberg table engine/feature/alter:/*": (
    #     Skip,
    #     "https://github.com/clickhouse/clickhouse/issues/86024",
    #     check_clickhouse_version(">=25.8"),
    # ),

}


@TestModule
@Name("iceberg")
@FFails(ffails)
@XFails(xfails)
@ArgumentParser(argparser_minio)
@Specifications(Apache_Iceberg_Table)
@CaptureClusterArgs
@CaptureMinioArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
    minio_args=None,
):
    """Run tests for Iceberg tables."""
    warnings.filterwarnings("ignore", message="Delete operation did not match any records")

    nodes = {
        "clickhouse": (
            "clickhouse1",
            "clickhouse2",
            "clickhouse3",
        ),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    minio_root_user = minio_args["minio_root_user"].value
    minio_root_password = minio_args["minio_root_password"].value

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
            environ={
                "MINIO_ROOT_USER": minio_root_user,
                "MINIO_ROOT_PASSWORD": minio_root_password,
            },
        )
        self.context.cluster = cluster

    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node2 = self.context.cluster.node("clickhouse2")
    self.context.node3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node, self.context.node2, self.context.node3]

    with And("enable or disable experimental analyzer if needed"):
        for node in self.context.nodes:
            experimental_analyzer(node=node, with_analyzer=with_analyzer)

    Feature(
        test=load("iceberg.tests.iceberg_engine.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.iceberg_table_engine.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.s3_table_function.s3_table_function", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.icebergS3_table_function.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.cache.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    # Feature(
    #     test=load("iceberg.tests.catalogs.feature", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)


if main():
    regression()
