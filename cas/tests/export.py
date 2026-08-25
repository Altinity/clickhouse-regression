"""EXPORT PARTITION against a CAS source.

ClickHouse refuses this path: it would clone parts file-by-file with no
CAS transaction and corrupt the clone. Assert that fail-closed rejection.
"""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid


CAS_EXPORT_REJECTION = "not supported on a CAS disk yet"


@TestScenario
@Name("EXPORT PARTITION from a CAS disk is rejected")
def export_partition_from_cas_disk_is_rejected(self):
    """``ALTER TABLE ... EXPORT PARTITION`` against a source on ``cas_policy``
    is refused with ``SUPPORT_IS_DISABLED``.
    """
    node = self.context.node
    uid = getuid()
    source_table = f"mt_cas_export_{uid}"
    dest_table = f"iceberg_cas_export_{uid}"
    user = self.context.minio_root_user
    password = self.context.minio_root_password
    dest_url = f"http://minio:9000/warehouse/data/{dest_table}/"

    try:
        with Given("a MergeTree source on the CAS storage policy"):
            node.query(
                f"""
                CREATE TABLE {source_table}
                (
                    id Int64,
                    year Int32
                )
                ENGINE = MergeTree
                PARTITION BY year
                ORDER BY id
                SETTINGS storage_policy = 'cas_policy'
                """
            )
            node.query(
                f"INSERT INTO {source_table} VALUES (1, 2020), (2, 2020), (3, 2020)"
            )

        with And("an IcebergS3 destination"):
            node.query(
                f"""
                CREATE TABLE {dest_table}
                (
                    id Int64,
                    year Int32
                )
                ENGINE = IcebergS3('{dest_url}', '{user}', '{password}')
                PARTITION BY year
                """,
                settings=[("allow_experimental_insert_into_iceberg", 1)],
            )

        with When("I export the 2020 partition to Iceberg"):
            result = node.query(
                f"ALTER TABLE {source_table} "
                f"EXPORT PARTITION ID '2020' TO TABLE {dest_table}",
                settings=[("allow_experimental_insert_into_iceberg", 1)],
                ignore_exception=True,
            )

        with Then("the ALTER is rejected as SUPPORT_IS_DISABLED"):
            assert result.exitcode != 0, error(
                "expected CAS export to be rejected, "
                f"got exitcode={result.exitcode}: {result.output}"
            )
            assert CAS_EXPORT_REJECTION in result.output, error(result.output)
            assert (
                "Code: 344" in result.output or "SUPPORT_IS_DISABLED" in result.output
            ), error(result.output)
    finally:
        with Finally("drop source and destination"):
            node.query(f"DROP TABLE IF EXISTS {source_table} SYNC")
            node.query(f"DROP TABLE IF EXISTS {dest_table} SYNC")


@TestFeature
@Name("export")
def feature(self):
    """EXPORT PARTITION behaviour for tables stored on a CAS disk."""
    Scenario(run=export_partition_from_cas_disk_is_rejected)
