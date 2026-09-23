"""What ClickHouse writes is a valid Iceberg table (plan §3.7, invariants D)."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.native_create_drop import *
from iceberg.tests.iceberg_engine.native_create.steps import *

COLUMNS = ["id Int64", "name Nullable(String)", "d Date"]


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Metadata_InitialFile("1.0"))
def initial_file(self):
    """D1 on both paths: one file under metadata/, pointed at by the catalog,
    spec-valid and empty."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )

    for path in (ENGINE_LESS, EXPLICIT_ENGINE):
        with Check(path, flags=TE):
            namespace = f"ns_{getuid()}"  # own namespace per table: a CREATE into an existing namespace costs ~33 s (findings.md #3)
            table_name = f"t_{getuid()}"
            args = dict(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                database_name=database_name,
            )
            with By("snapshot state"):
                before = snapshot_state(**args)
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                path=path,
                columns=COLUMNS,
                partition_by="toRelativeDayNum(d)",
                order_by="id",
            )
            with By("snapshot state"):
                after = snapshot_state(**args)
            assert_table_created(before=before, after=after)

            with By("read registered metadata"):
                metadata, location = read_registered_metadata(
                    catalog=catalog, namespace=namespace, table_name=table_name
                )
            table = catalog.load_table(f"{namespace}.{table_name}")

            with By("format-version is 1 or 2 and PyIceberg agrees"):
                assert metadata["format-version"] in (1, 2), error(
                    metadata["format-version"]
                )
                assert (
                    table.metadata.format_version == metadata["format-version"]
                ), error()

            with By("one schema with the declared fields"):
                assert len(metadata["schemas"]) == 1, error(len(metadata["schemas"]))
                fields = metadata["schemas"][0]["fields"]
                assert [(f["name"], f["type"], f["required"]) for f in fields] == [
                    ("id", "long", True),
                    ("name", "string", False),
                    ("d", "date", True),
                ], error(fields)
                assert metadata["last-column-id"] == 3, error(
                    metadata["last-column-id"]
                )

            with By("one partition spec and one sort order"):
                assert len(metadata["partition-specs"]) == 1, error()
                assert [
                    f["transform"] for f in metadata["partition-specs"][0]["fields"]
                ] == ["day"], error()
                assert len(metadata["sort-orders"]) == 1, error()
                assert [
                    f["source-id"] for f in metadata["sort-orders"][0]["fields"]
                ] == [1], error()

            with By("no snapshots, no current snapshot, empty logs"):
                assert metadata.get("snapshots", []) == [], error(
                    metadata.get("snapshots")
                )
                assert metadata.get("current-snapshot-id") in (None, -1), error(
                    metadata.get("current-snapshot-id")
                )
                assert metadata.get("metadata-log", []) == [], error(
                    metadata.get("metadata-log")
                )
                assert metadata.get("snapshot-log", []) == [], error(
                    metadata.get("snapshot-log")
                )
                assert table.current_snapshot() is None, error()

            with By("location field matches the catalog"):
                assert metadata["location"] == after.table_location, error()


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_Metadata_Compression("1.0"))
@Examples("path", [(ENGINE_LESS,), (EXPLICIT_ENGINE,)])
def gzip_metadata(self, path):
    """D3: with iceberg_metadata_compression_method = 'gzip' the initial file
    is gzip-compressed and named with the suffix; the table then works.
    On a REST catalog the engine-less file is written by the server, so the
    setting cannot apply there and the table must simply work."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    ch_name = clickhouse_table_name(database_name, namespace, table_name)
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with When("CREATE TABLE with gzip metadata"):
        before = snapshot_state(**args)
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=path,
            columns=COLUMNS,
            settings=[("iceberg_metadata_compression_method", "gzip")],
        )

    with Then("the registered file is what the setting asked for"):
        after = snapshot_state(**args)
        assert_table_created(before=before, after=after)
        key = s3.key_from_uri(after.metadata_location)
        raw = s3.get_object_bytes(key)
        client_written = path == EXPLICIT_ENGINE or self.context.catalog == "glue"
        if client_written:
            assert key.endswith(".gzip.metadata.json"), error(key)
            assert raw[:2] == s3.GZIP_MAGIC, error(raw[:2])
        else:
            note(f"server-written metadata: {key}, gzip={raw[:2] == s3.GZIP_MAGIC}")

    with And("INSERT and SELECT work"):
        insert_into_native_iceberg_table(
            table_name=ch_name, values_sql="(1, 'a', '2024-01-01')"
        )
        check_column_value(table_name=ch_name, expected="1\ta\t2024-01-01")
        check_state_invariants(**args, expected=PRESENT)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Metadata_FirstCommit("1.0"))
def first_commit_has_no_parent(self):
    """D2: the first INSERT's snapshot has no parent, metadata-log points at
    the initial file, and the second INSERT chains to the first snapshot."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    ch_name = clickhouse_table_name(database_name, namespace, table_name)

    with Given("a fresh table"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
        )
        _, initial_location = read_registered_metadata(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When("first INSERT"):
        insert_into_native_iceberg_table(
            table_name=ch_name, values_sql="(1, 'a', '2024-01-01')"
        )

    with Then("one snapshot, no parent, metadata-log[0] is the initial file"):
        metadata, location = read_registered_metadata(
            catalog=catalog, namespace=namespace, table_name=table_name
        )
        assert location != initial_location, error("metadata-location did not advance")
        assert len(metadata["snapshots"]) == 1, error(metadata["snapshots"])
        first = metadata["snapshots"][0]
        assert "parent-snapshot-id" not in first, error(first)
        assert metadata["current-snapshot-id"] == first["snapshot-id"], error()
        assert (
            metadata["metadata-log"][0]["metadata-file"].rsplit("/", 1)[-1]
            == initial_location.rsplit("/", 1)[-1]
        ), error(f"{metadata['metadata-log']} vs {initial_location}")
        table = catalog.load_table(f"{namespace}.{table_name}")
        assert table.current_snapshot().parent_snapshot_id is None, error()

    with When("second INSERT"):
        insert_into_native_iceberg_table(
            table_name=ch_name, values_sql="(2, 'b', '2024-01-02')"
        )

    with Then("the second snapshot's parent is the first"):
        metadata, _ = read_registered_metadata(
            catalog=catalog, namespace=namespace, table_name=table_name
        )
        by_id = {s["snapshot-id"]: s for s in metadata["snapshots"]}
        current = by_id[metadata["current-snapshot-id"]]
        assert current.get("parent-snapshot-id") == first["snapshot-id"], error(current)
        rows = (
            catalog.load_table(f"{namespace}.{table_name}")
            .scan()
            .to_arrow()
            .to_pylist()
        )
        assert sorted(r["id"] for r in rows) == [1, 2], error(rows)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Metadata_ExternalReader("1.0"))
def pyiceberg_reads_clickhouse_rows(self):
    """C4 / D: on both paths an external reader through the catalog sees the
    schema, spec, sort order, location and the rows ClickHouse wrote."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )

    for path in (ENGINE_LESS, EXPLICIT_ENGINE):
        with Check(path, flags=TE):
            namespace = f"ns_{getuid()}"  # own namespace per table: a CREATE into an existing namespace costs ~33 s (findings.md #3)
            table_name = f"t_{getuid()}"
            ch_name = clickhouse_table_name(database_name, namespace, table_name)
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                path=path,
                columns=COLUMNS,
                partition_by="icebergBucket(4, id)",
                order_by="d",
            )
            insert_into_native_iceberg_table(
                table_name=ch_name,
                values_sql="(1, 'a', '2024-01-01'), (2, NULL, '2024-01-02')",
            )

            table = catalog.load_table(f"{namespace}.{table_name}")
            assert pyiceberg_schema_shape(table) == [
                ("id", "long", True),
                ("name", "string", False),
                ("d", "date", True),
            ], error()
            assert pyiceberg_spec_shape(table) == [(1, "bucket[4]")], error(
                str(table.spec())
            )
            assert pyiceberg_sort_shape(table) == [(3, "identity")], error(
                str(table.sort_order())
            )
            assert table.metadata.location == expected_table_location(
                namespace, table_name
            ), error(table.metadata.location)
            rows = sorted(table.scan().to_arrow().to_pylist(), key=lambda r: r["id"])
            assert [(r["id"], r["name"]) for r in rows] == [(1, "a"), (2, None)], error(
                rows
            )


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Metadata_ExternalReader("1.0"))
def spark_interop(self):
    """Spark reads ClickHouse rows and ClickHouse reads Spark rows through
    the Apache REST fixture."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    skip(
        "Spark interop deferred: needs the rest:8181 database wrapper from deletion_vectors/steps/common.py"
    )


@TestFeature
@Name("metadata")
def feature(self, minio_root_user, minio_root_password):
    """Written metadata validity."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
