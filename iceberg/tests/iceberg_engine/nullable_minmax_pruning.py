"""File min/max pruning on a nullable Iceberg column.

Three unpartitioned data files, one append each:

* low is ``'aaa'`` plus a null
* high is ``'zzz'`` plus a null
* hit is ``'sg2o27m'`` and has no null

Manifest min/max is the non-null range. ``null_value_counts`` counts the
nulls separately. ClickHouse prunes a file when that range misses the
predicate and a SQL NULL in the file cannot make the predicate true.
``IS NULL``, ``assumeNotNull``, and ``IN`` / ``NOT IN`` with
``transform_null_in`` still read a file that contains NULL.
"""

import pyarrow as pa
from pyiceberg.partitioning import PartitionSpec
from pyiceberg.schema import Schema, NestedField
from pyiceberg.table.sorting import SortOrder
from pyiceberg.types import StringType
from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.common as common
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.metrics as metrics


PROBE = "sg2o27m"

# (predicate, extra settings, rows, IcebergMinMaxIndexPrunedFiles)
CASES = [
    (f"partner_id = '{PROBE}'", [], 1, 2),
    ("partner_id = 'aaa'", [], 1, 2),
    ("partner_id = 'zzz'", [], 1, 2),
    (f"NOT partner_id = '{PROBE}'", [], 2, 1),
    (f"partner_id <=> '{PROBE}'", [], 1, 2),
    ("partner_id IS NULL", [], 2, 1),
    (f"partner_id = '{PROBE}' OR partner_id IS NULL", [], 3, 0),
    ("assumeNotNull(partner_id) = ''", [], 2, 1),
    # A file with a null stays. The hit file has no null and is not 'aaa'.
    ("assumeNotNull(partner_id) = 'aaa'", [], 1, 1),
    # IN / NOT IN keep a file that contains NULL.
    # NOT IN with transform_null_in matches the NULL rows.
    # IN with NULL in the list does not: the storage filter drops those rows,
    # while the same expression in the SELECT list matches them.
    (f"partner_id IN ('{PROBE}')", [], 1, 0),
    (f"partner_id IN ('{PROBE}', NULL)", [], 1, 0),
    (f"partner_id IN ('{PROBE}', NULL)", [("transform_null_in", 1)], 1, 0),
    ("partner_id NOT IN ('zzz')", [], 2, 0),
    ("partner_id NOT IN ('zzz')", [("transform_null_in", 1)], 4, 0),
    ("NOT (partner_id <=> 'zzz')", [], 4, 0),
    (f"NOT (partner_id <=> '{PROBE}')", [], 4, 1),
]


def _count_and_pruned(
    node, database_name, namespace, table_name, where, extra_settings
):
    log_comment = f"nullable_minmax_{getuid()}"
    common.drop_all_caches(node=node)
    result = node.query(
        "SELECT count() FROM "
        f"{database_name}.\\`{namespace}.{table_name}\\` WHERE {where}",
        settings=[
            ("log_comment", log_comment),
            ("use_iceberg_metadata_files_cache", "0"),
            ("input_format_parquet_filter_push_down", "0"),
            ("input_format_parquet_bloom_filter_push_down", "0"),
            ("input_format_parquet_page_filter_push_down", "0"),
            ("use_cache_for_count_from_files", "0"),
            ("optimize_move_to_prewhere", "0"),
            *extra_settings,
        ],
    )
    pruned = metrics.get_IcebergMinMaxIndexPrunedFiles(log_comment=log_comment)
    return int(result.output.strip()), int(pruned.output.strip())


@TestScenario
def files(self, minio_root_user, minio_root_password, node=None):
    """Prune nullable Iceberg files from manifest min/max."""
    if node is None:
        node = self.context.node

    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"database_{getuid()}"

    with Given("I have a catalog and an unpartitioned nullable string column"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            # Cluster teardown deletes the MinIO volume, so skip the aws CLI cleanup.
            clean_up_minio_bucket=False,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
        schema = Schema(
            NestedField(
                field_id=1,
                name="partner_id",
                field_type=StringType(),
                required=False,
            )
        )
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
        )

    with And("three data files, so compaction cannot merge the bounds"):
        arrow_schema = pa.schema([("partner_id", pa.string())])
        for rows in (
            [{"partner_id": "aaa"}, {"partner_id": None}],
            [{"partner_id": "zzz"}, {"partner_id": None}],
            [{"partner_id": PROBE}],
        ):
            table.append(pa.Table.from_pylist(rows, schema=arrow_schema))

    with And("a DataLakeCatalog database over that catalog"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with Then("each predicate returns the matching rows and prunes the rest"):
        for where, extra_settings, expected_rows, expected_pruned in CASES:
            label = where
            if extra_settings:
                settings = ", ".join(
                    f"{name} = {value}" for name, value in extra_settings
                )
                label = f"{where} SETTINGS {settings}"
            with By(label):
                rows, pruned = _count_and_pruned(
                    node,
                    database_name,
                    namespace,
                    table_name,
                    where,
                    extra_settings,
                )
                assert rows == expected_rows, error()
                assert pruned == expected_pruned, error()


@TestFeature
@Name("nullable minmax pruning")
def feature(self, minio_root_user, minio_root_password):
    """Nullable Iceberg file min/max pruning."""
    Scenario(test=files)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
