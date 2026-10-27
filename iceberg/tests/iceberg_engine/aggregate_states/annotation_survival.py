"""Whether `clickhouse.type` annotations survive the catalog and commits by
other engines (review comment on Altinity/ClickHouse#2680).

The Iceberg spec does not define the key, and Java Iceberg and PyIceberg
rebuild schema JSON from their own models, so a catalog server or an external
writer may drop it. Each concern is its own scenario so that one failing does
not hide the others. Commits by other engines start from a table ClickHouse
wrote at a path and registered in the catalog, so they do not depend on the
annotation surviving CREATE through the catalog."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from pyiceberg.types import LongType

from iceberg.requirements.aggregate_states import *
from iceberg.tests.iceberg_engine.aggregate_states.steps import *
from iceberg.tests.iceberg_engine.native_create.steps import (
    ENGINE_LESS,
    EXPLICIT_ENGINE,
    catalog_and_database,
    clickhouse_table_name,
    create_table,
    read_registered_metadata,
)

EXPECTED_ANNOTATIONS = {"k": None, "u": U_TYPE, "s": S_TYPE}


@TestStep(Given)
def registered_clickhouse_table(self, catalog):
    """A table ClickHouse wrote at a path with one batch of states, registered
    in the catalog at its latest metadata file. ice-rest-catalog refuses to
    register metadata without a snapshot, so the table is never empty.

    Returns ``(namespace, table_name, pyiceberg_table)``."""
    namespace = f"ns_{getuid()}"
    table_name = iceberg_s3_table()
    insert_states(table_name=table_name)
    key = latest_metadata_key(table_prefix(table_name))
    with By("check the annotations ClickHouse wrote"):
        metadata = s3.read_json_object(key)
        assert_annotations(metadata=metadata, expected=EXPECTED_ANNOTATIONS, where=key)
    table = registered_in_catalog(
        catalog=catalog, namespace=namespace, table_name=table_name, metadata_key=key
    )
    return namespace, table_name, table


@TestCheck
def check_annotations_written_on_create_through_catalog(self, path):
    """CREATE TABLE in a DataLakeCatalog database: the metadata file the
    catalog registers carries the annotations."""
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=self.context.minio_root_user,
            minio_root_password=self.context.minio_root_password,
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"

    with When("CREATE TABLE with aggregate columns"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=path,
            columns=[COLUMNS],
            settings=STATE_SETTINGS,
        )

    with Then("the registered metadata carries the annotations"):
        metadata, location = read_registered_metadata(
            catalog=catalog, namespace=namespace, table_name=table_name
        )
        assert_annotations(
            metadata=metadata, expected=EXPECTED_ANNOTATIONS, where=location
        )


@TestCheck
def check_clickhouse_type_after_create_through_catalog(self, path):
    """CREATE TABLE in a DataLakeCatalog database: reading the table back
    through the catalog reports the aggregate types."""
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=self.context.minio_root_user,
            minio_root_password=self.context.minio_root_password,
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"

    with When("CREATE TABLE with aggregate columns"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=path,
            columns=[COLUMNS],
            settings=STATE_SETTINGS,
        )

    with Then("DESCRIBE through the catalog reports the aggregate types"):
        columns = describe(
            clickhouse_table_name(database_name, namespace, table_name),
            settings=STATE_SETTINGS,
        )
        assert columns == [("k", "Int32"), ("u", U_TYPE), ("s", S_TYPE)], error(columns)


@TestSketch(Scenario)
@Flags(TE)
@Requirements(RQ_Iceberg_AggregateStates_Interop_CreateThroughCatalog("1.0"))
def annotations_written_on_create_through_catalog(self):
    """Engine-less and explicit-engine CREATE through the catalog register
    metadata that carries the annotations."""
    check_annotations_written_on_create_through_catalog(
        path=either(ENGINE_LESS, EXPLICIT_ENGINE)
    )


@TestSketch(Scenario)
@Flags(TE)
@Requirements(RQ_Iceberg_AggregateStates_Interop_CreateThroughCatalog("1.0"))
def clickhouse_type_after_create_through_catalog(self):
    """After engine-less and explicit-engine CREATE through the catalog,
    ClickHouse reports the aggregate types."""
    check_clickhouse_type_after_create_through_catalog(
        path=either(ENGINE_LESS, EXPLICIT_ENGINE)
    )


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Interop_ExternalCommit("1.0"))
def annotations_survive_external_append(self):
    """PyIceberg appends to an annotated table through the catalog: the
    metadata file the commit registers still carries the annotations."""
    with Given("catalog"):
        catalog, _ = catalog_and_database(
            minio_root_user=self.context.minio_root_user,
            minio_root_password=self.context.minio_root_password,
        )

    with And("a ClickHouse-written table with states, registered in the catalog"):
        namespace, table_name, table = registered_clickhouse_table(catalog=catalog)
        _, before = read_registered_metadata(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When("PyIceberg appends states"):
        pyiceberg_append_states(table=table, rows=external_rows(start=200, count=100))

    with Then("the append registered a new metadata file"):
        metadata, after = read_registered_metadata(
            catalog=catalog, namespace=namespace, table_name=table_name
        )
        assert after != before, error(
            f"metadata-location did not advance from {before}"
        )

    with And("its current schema still carries the annotations"):
        assert_annotations(
            metadata=metadata, expected=EXPECTED_ANNOTATIONS, where=after
        )


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Interop_ExternalCommit("1.0"))
def clickhouse_merges_after_external_append(self):
    """ClickHouse wrote one batch of states and PyIceberg appended another:
    reading through the catalog, ClickHouse reports the aggregate types and
    merges both batches to the result over all original rows."""
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=self.context.minio_root_user,
            minio_root_password=self.context.minio_root_password,
        )

    with And("a ClickHouse-written table with states, registered in the catalog"):
        namespace, table_name, table = registered_clickhouse_table(catalog=catalog)
        name = clickhouse_table_name(database_name, namespace, table_name)

    with When("PyIceberg appends states for the next rows"):
        pyiceberg_append_states(table=table, rows=external_rows(start=200, count=100))

    with Then("DESCRIBE through the catalog reports the aggregate types"):
        columns = describe(name, settings=STATE_SETTINGS)
        assert columns == [("k", "Int32"), ("u", U_TYPE), ("s", S_TYPE)], error(columns)

    with And("both batches merge to the result over all rows"):
        assert_merge_matches(source=name, expected=expected_result(start=0, count=300))


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Interop_ExternalSchemaEvolution("1.0"))
def annotations_survive_external_schema_evolution(self):
    """PyIceberg adds a column: the fields carried into the new current
    schema keep their annotations."""
    with Given("catalog"):
        catalog, _ = catalog_and_database(
            minio_root_user=self.context.minio_root_user,
            minio_root_password=self.context.minio_root_password,
        )

    with And("a ClickHouse-written table with states, registered in the catalog"):
        namespace, table_name, table = registered_clickhouse_table(catalog=catalog)
        before, _ = read_registered_metadata(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When("PyIceberg adds a column"):
        with table.update_schema() as update:
            update.add_column("extra", LongType())

    with Then("there is a new current schema with the added column"):
        metadata, location = read_registered_metadata(
            catalog=catalog, namespace=namespace, table_name=table_name
        )
        assert metadata["current-schema-id"] != before["current-schema-id"], error(
            "current-schema-id did not change"
        )
        assert "extra" in fields_by_name(metadata), error(fields_by_name(metadata))

    with And("the carried-over fields keep their annotations"):
        assert_annotations(
            metadata=metadata,
            expected={**EXPECTED_ANNOTATIONS, "extra": None},
            where=location,
        )


@TestFeature
@Name("annotation survival")
def feature(self):
    """Annotations through the catalog and commits by other engines."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
