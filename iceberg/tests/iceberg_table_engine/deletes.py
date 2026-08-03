from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import iceberg.tests.steps.iceberg_writes as iceberg_writes


@TestScenario
def position_delete_smoke(self, minio_root_user, minio_root_password):
    """ClickHouse writes position deletes to an ENGINE=Iceberg table."""
    ch_table_name = f"iceberg_delete_{getuid()}"

    with Given("merge-on-read Iceberg table with Iceberg engine"):
        iceberg_writes.setup_iceberg_engine_mor_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            ch_table_name=ch_table_name,
        )

    with When("insert rows"):
        iceberg_writes.insert_into_iceberg_engine_table(
            table_name=ch_table_name,
            insert_query=(
                f"INSERT INTO {ch_table_name} (id, data) "
                "SELECT number, toString(number) FROM numbers(1, 5)"
            ),
        )

    with And("delete two rows via ALTER DELETE"):
        iceberg_writes.delete_from_iceberg_engine_table(
            table_name=ch_table_name,
            condition="id <= 2",
        )

    with Then("deleted rows are not visible"):
        iceberg_writes.assert_table_count(
            table_name=ch_table_name,
            expected_count=3,
        )
        iceberg_writes.assert_table_ids(
            table_name=ch_table_name,
            expected_ids=[3, 4, 5],
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=position_delete_smoke)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
