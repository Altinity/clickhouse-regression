from testflows.core import *

from helpers.common import getuid

import iceberg.tests.steps.common as common
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.iceberg_writes as iceberg_writes


@TestScenario
def read_position_deletes(self, minio_root_user, minio_root_password):
    """DataLakeCatalog reads rows after ClickHouse writes position deletes.

    Catalog ``ALTER DELETE`` fails with ``Metadata is not initialized`` (mutate
    path does not lazy-init metadata). Position deletes are written via
    ``ENGINE=Iceberg``, the REST catalog pointer is re-registered to the new
    metadata, then DataLakeCatalog reads the result.
    """
    database_name = f"iceberg_database_{getuid()}"
    namespace = f"iceberg_{getuid()}"
    table_name = f"table_{getuid()}"
    ch_table_name = f"iceberg_engine_{getuid()}"
    catalog_table_name = iceberg_writes.catalog_table_sql_name(
        database_name, namespace, table_name
    )
    merge_tree_table_name = f"merge_tree_table_{getuid()}"

    with Given("merge-on-read Iceberg table with Iceberg engine"):
        iceberg_table, _, namespace, table_name = (
            iceberg_writes.setup_iceberg_engine_mor_table(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                namespace=namespace,
                table_name=table_name,
                ch_table_name=ch_table_name,
            )
        )
        catalog = iceberg_table.catalog

    with When("insert rows via ENGINE=Iceberg"):
        iceberg_writes.insert_into_iceberg_engine_table(
            table_name=ch_table_name,
            insert_query=(
                f"INSERT INTO {ch_table_name} (id, data) "
                "SELECT number, toString(number) FROM numbers(1, 5)"
            ),
        )

    with And("write position deletes via ENGINE=Iceberg"):
        iceberg_writes.delete_from_iceberg_engine_table(
            table_name=ch_table_name,
            condition="id <= 2",
        )

    with And("point REST catalog at metadata written by ENGINE=Iceberg"):
        iceberg_writes.sync_catalog_to_latest_metadata(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create MergeTree oracle table"):
        self.context.node.query(
            f"""
            CREATE TABLE {merge_tree_table_name} (
                id Nullable(Int64),
                data Nullable(String)
            )
            ENGINE = MergeTree
            ORDER BY tuple()
            """
        )
        self.context.node.query(
            f"INSERT INTO {merge_tree_table_name} "
            "SELECT number, toString(number) FROM numbers(1, 5)"
        )
        self.context.node.query(
            f"ALTER TABLE {merge_tree_table_name} DELETE WHERE id <= 2"
        )

    with Then("DataLakeCatalog matches MergeTree oracle after position deletes"):
        common.compare_data_in_two_tables(
            table_name1=merge_tree_table_name,
            table_name2=catalog_table_name,
            select_columns="id, data",
            order_by="id",
        )


@TestFeature
@Name("position delete reads")
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=read_position_deletes)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
