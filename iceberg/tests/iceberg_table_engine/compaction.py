from testflows.core import *

from helpers.common import getuid

import iceberg.tests.steps.iceberg_writes as iceberg_writes


@TestScenario
def compaction_smoke(self, minio_root_user, minio_root_password):
    """OPTIMIZE compacts position deletes on an ENGINE=Iceberg table.

    Mirrors upstream ``test_storage_iceberg_with_spark/test_optimize.py`` without Spark.
    """
    ch_table_name = f"iceberg_compaction_{getuid()}"

    with Given("merge-on-read Iceberg table with Iceberg engine"):
        iceberg_writes.setup_iceberg_engine_mor_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            ch_table_name=ch_table_name,
        )

    with When("insert initial data"):
        iceberg_writes.insert_into_iceberg_engine_table(
            table_name=ch_table_name,
            insert_query=(
                f"INSERT INTO {ch_table_name} (id, data) "
                "SELECT number, char(number + ascii('a')) FROM numbers(10, 90)"
            ),
        )

    with And("delete some rows"):
        iceberg_writes.delete_from_iceberg_engine_table(
            table_name=ch_table_name,
            condition="id < 20",
        )

    with And("insert more rows"):
        iceberg_writes.insert_into_iceberg_engine_table(
            table_name=ch_table_name,
            insert_query=(
                f"INSERT INTO {ch_table_name} (id, data) "
                "SELECT number, char(number + ascii('a')) FROM numbers(100, 10)"
            ),
        )

    with Then("row count is unchanged after delete + insert"):
        iceberg_writes.assert_table_count(
            table_name=ch_table_name,
            expected_count=90,
        )

    with When("compact the table"):
        iceberg_writes.optimize_iceberg_engine_table(table_name=ch_table_name)

    with Then("data is unchanged after compaction"):
        iceberg_writes.assert_table_count(
            table_name=ch_table_name,
            expected_count=90,
        )
        iceberg_writes.assert_table_ids(
            table_name=ch_table_name,
            expected_ids=range(20, 110),
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=compaction_smoke)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
