from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import Column, create_table
from helpers.datatypes import Int32, Date, Nullable

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_SchemaRefresh,
)

from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_s3_destination,
)
from iceberg.tests.export_partition.steps.export_operations import (
    insert_into_iceberg_destination,
)
from iceberg.tests.export_partition.schema_evolution import (
    alter_iceberg_destination,
)

from iceberg.tests.hybrid.core.common import (
    ALL_ROWS,
    COLUMNS,
    COLUMNS_SQL,
    LEFT_PREDICATE,
    RIGHT_PREDICATE,
    PREFER_LOCALHOST,
    cluster_all_tf,
    create_mergetree_segment,
    settings_clause,
    values_sql,
)


COLUMNS_WITH_SCORE = [
    Column(name="id", datatype=Int32()),
    Column(name="value", datatype=Int32()),
    Column(name="date_col", datatype=Date()),
    Column(name="score", datatype=Nullable(Int32())),
]


def fingerprint_with_score(from_expr):
    return (
        "SELECT count(), coalesce(sum(id), 0), coalesce(sum(value), 0), "
        "coalesce(sum(assumeNotNull(score)), 0), "
        "groupBitXor(cityHash64(id, value, toString(date_col), "
        "ifNull(toString(score), ''))) "
        f"FROM {from_expr}"
    )


@TestScenario
@Name("add column then create or replace hybrid")
def add_column_then_create_or_replace(self, minio_root_user, minio_root_password):
    """ADD COLUMN on segments, CREATE OR REPLACE Hybrid, fingerprint still matches."""
    node = self.context.node
    self.context.catalog = "no"

    with Given("cluster(MT) + IcebergS3 Hybrid with base schema"):
        left = create_mergetree_segment(
            cluster="all",
            seed_all_nodes=False,
            rows=ALL_ROWS,
        )
        iceberg = create_iceberg_s3_destination(
            columns=COLUMNS_SQL,
            partition_by="",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        insert_into_iceberg_destination(
            destination=iceberg,
            values=values_sql(ALL_ROWS),
        )
        hybrid = f"hybrid_{getuid()}"
        left_tf = cluster_all_tf(left)
        create_table(
            name=hybrid,
            engine=(
                f"Hybrid({left_tf}, {LEFT_PREDICATE}, {iceberg}, {RIGHT_PREDICATE})"
            ),
            columns=COLUMNS,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    with When("ADD COLUMN score Nullable(Int32) on left MergeTree on all shards"):
        node.query(
            f"ALTER TABLE {left} ON CLUSTER all ADD COLUMN score Nullable(Int32)"
        )

    with And("ADD COLUMN score Nullable(Int32) on Iceberg destination"):
        alter_iceberg_destination(
            destination=iceberg,
            alter_clause="ADD COLUMN score Nullable(Int32)",
        )

    with And("CREATE OR REPLACE Hybrid with expanded schema"):
        cols = ", ".join(c.full_definition() for c in COLUMNS_WITH_SCORE)
        node.query(
            f"CREATE OR REPLACE TABLE {hybrid} ({cols}) "
            f"ENGINE = Hybrid({left_tf}, {LEFT_PREDICATE}, {iceberg}, {RIGHT_PREDICATE})",
            settings=[("allow_experimental_hybrid_table", 1)],
            exitcode=0,
        )

    clause = settings_clause(PREFER_LOCALHOST)
    ref = (
        f"(SELECT id, value, date_col, score FROM {left_tf} WHERE {LEFT_PREDICATE} "
        f"UNION ALL "
        f"SELECT id, value, date_col, score FROM {iceberg} WHERE {RIGHT_PREDICATE})"
    )

    with Then("fingerprint including score matches reference"):
        h = node.query(
            fingerprint_with_score(hybrid) + f" {clause}"
        ).output.strip()
        r = node.query(fingerprint_with_score(ref) + f" {clause}").output.strip()
        assert h == r, error()

    with And("count still spans both watermarks"):
        h = node.query(f"SELECT count() FROM {hybrid} {clause}").output.strip()
        assert h == "4", error()


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_SchemaRefresh("1.0"),
)
@Name("schema refresh")
def feature(self, minio_root_user, minio_root_password):
    """Hybrid header refresh via CREATE OR REPLACE after ADD COLUMN."""
    self.context.catalog = "no"
    Scenario(test=add_column_then_create_or_replace)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
