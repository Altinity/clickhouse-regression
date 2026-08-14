"""Feature-scope sanity: ClickHouse reads Iceberg v3 deletion vectors and
never writes them, regardless of which writer operation produced them."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.steps.spark as spark
import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects
import iceberg.tests.deletion_vectors.steps.puffin as puffin
import iceberg.tests.deletion_vectors.steps.manifest as manifest


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Read("1.0"))
def read_deletion_vectors(self):
    """Rows deleted through a deletion vector are excluded exactly."""
    rows = 100
    deleted = [i for i in range(rows) if i % 10 == 0]

    with Given("a v3 merge-on-read table where Spark deleted every 10th row"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )

    with Then("the visible row set matches the writer-committed state"):
        common.assert_visible_ids(table=table, ids=common.expected_ids(rows, deleted))

    with And("count() agrees"):
        assert common.count_rows(table=table) == rows - len(deleted), error()


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ReadOnly("1.0"))
def read_only(self):
    """No ClickHouse read operation modifies Puffin files or any other
    table object."""
    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors()

    with And("the full object inventory of the table is recorded"):
        inventory_before = s3_objects.object_inventory(table.prefix)

    with When("ClickHouse reads the table in several ways"):
        common.read_result(table=table, order_by="id")
        common.count_rows(table=table)
        common.read_result(table=table, where_clause="id > 50", columns="id")
        common.read_result(table=table, cluster=True, order_by="id")
        engine_table = common.engine_table(table=table)
        self.context.node.query(f"SELECT count() FROM {engine_table}")

    with And("caches are dropped and the table is read again"):
        common.drop_puffin_cache()
        common.read_result(table=table, order_by="id")

    with Then("no object under the table location changed"):
        inventory_after = s3_objects.object_inventory(table.prefix)
        assert inventory_after == inventory_before, error(
            "table objects changed during read-only operations: "
            f"added={set(inventory_after) - set(inventory_before)}, "
            f"removed={set(inventory_before) - set(inventory_after)}"
        )


MUTATIONS = {
    "delete mutation": {
        "statement": "ALTER TABLE {table} DELETE WHERE id < 10",
        # rows the mutation claims to remove/change; zero matches after an
        # honestly applied mutation
        "verify_where": "id < 10",
    },
    "update mutation": {
        "statement": "ALTER TABLE {table} UPDATE data = 'mutated' WHERE id < 10",
        "verify_where": "id < 10 AND data != 'mutated'",
    },
}


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_MutationsRejected("1.0"))
def mutation_rejected(self, name, statement, verify_where):
    """One ClickHouse mutation on a v3 table with deletion vectors is
    rejected with an explicit error — never a silent no-op. A mutation that
    writes v2 position delete files onto a v3 table reports success while
    every compliant reader (including ClickHouse itself) must ignore those
    deletes and keep returning the rows."""
    node = self.context.node
    rows = 100
    deleted = [i for i in range(rows) if i % 10 == 0]

    with Given("an Iceberg engine table over a v3 table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )
        engine_table = common.engine_table(table=table)

    with When(f"ClickHouse runs the {name}"):
        result = node.query(
            statement.format(table=engine_table),
            settings=[("mutations_sync", "2")],
            no_checks=True,
        )

    if result.exitcode != 0:
        with Then("the mutation is rejected with an explicit error"):
            assert "Exception" in result.output, error(result.output[:2000])

        with And("the table is unchanged after the rejection"):
            common.assert_visible_ids(
                table=table, ids=common.expected_ids(rows, deleted)
            )
    else:
        with Then(
            "a mutation that reported success must be applied — the rows "
            "must not stay visible to later SELECT queries"
        ):
            remaining = node.query(
                f"SELECT count() FROM {engine_table} WHERE {verify_where}"
            )
            assert int(remaining.output.strip()) == 0, error(
                f"the {name} reported success but {remaining.output.strip()} "
                f"matching rows are still visible: the mutation is a silent "
                f"no-op on a format version 3 table"
            )

        with And("the writer engine sees the same state"):
            spark_rows = spark.select_rows(
                namespace=table.namespace,
                table_name=table.table_name,
                columns="id",
                where=verify_where.replace("!=", "<>"),
            )
            assert spark_rows == [], error(
                f"the {name} reported success but a compliant reader still "
                f"returns {len(spark_rows)} matching rows"
            )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_MutationsRejected("1.0"))
def mutations_rejected(self):
    """ClickHouse mutations on a v3 table with deletion vectors are
    rejected explicitly, never silently ignored."""
    for name, mutation in MUTATIONS.items():
        Scenario(test=mutation_rejected, name=name)(
            name=name,
            statement=mutation["statement"],
            verify_where=mutation["verify_where"],
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Read("1.0"))
def puffin_metadata_structure(self):
    """The writer-produced deletion-vector metadata chain carries every
    kind of information the reader depends on — checked structurally (field
    presence and types), not by value: the Puffin file framing, the footer
    blob descriptors, and the deletion-vector manifest entry."""
    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors()

    with When("the Puffin file and its manifest entry are fetched"):
        dv_entries = manifest.find_dv_entries(table.namespace, table.table_name)
        assert dv_entries, error("no live deletion-vector manifest entry")
        data_file = dv_entries[0]["entry"]["data_file"]
        puffin_bytes = s3_objects.get_object_bytes(
            s3_objects.key_from_uri(data_file["file_path"])
        )

    with Then("the Puffin file is framed by the format magic"):
        assert puffin_bytes[:4] == puffin.PUFFIN_MAGIC, error(
            f"leading magic {puffin_bytes[:4]!r}"
        )
        assert puffin_bytes[-4:] == puffin.PUFFIN_MAGIC, error(
            f"trailing magic {puffin_bytes[-4:]!r}"
        )

    with And("every footer blob descriptor carries the required fields"):
        footer = puffin.parse_puffin_footer(puffin_bytes)
        assert isinstance(footer.get("blobs"), list) and footer["blobs"], error(
            f"footer has no blobs list: {footer}"
        )
        for index, blob in enumerate(footer["blobs"]):
            for field, kinds in {
                "type": str,
                "fields": list,
                "snapshot-id": int,
                "sequence-number": int,
                "offset": int,
                "length": int,
                "properties": dict,
            }.items():
                assert isinstance(blob.get(field), kinds), error(
                    f"blob {index}: field {field!r} missing or not "
                    f"{kinds.__name__}: {blob}"
                )
            assert blob["type"] == "deletion-vector-v1", error(
                f"blob {index}: type {blob['type']!r}"
            )
            assert blob["offset"] >= 4 and blob["length"] > 0, error(
                f"blob {index}: implausible location "
                f"({blob['offset']}, {blob['length']})"
            )
            properties = blob["properties"]
            referenced = properties.get("referenced-data-file")
            assert isinstance(referenced, str) and referenced, error(
                f"blob {index}: missing referenced-data-file: {properties}"
            )
            cardinality = properties.get("cardinality")
            assert isinstance(cardinality, str) and cardinality.isdigit(), error(
                f"blob {index}: cardinality is not an unsigned integer "
                f"string: {properties}"
            )

    with And("the deletion-vector manifest entry carries the required fields"):
        assert data_file["content"] == 1, error(
            f"content = {data_file['content']}, expected 1 (deletes)"
        )
        assert str(data_file["file_format"]).upper() == "PUFFIN", error(
            f"file_format = {data_file['file_format']!r}"
        )
        assert str(data_file["file_path"]).endswith(".puffin"), error(
            f"file_path = {data_file['file_path']!r}"
        )
        referenced = data_file.get("referenced_data_file")
        assert isinstance(referenced, str) and referenced, error(
            f"referenced_data_file = {referenced!r}"
        )
        for field in ("content_offset", "content_size_in_bytes", "record_count"):
            assert (
                isinstance(data_file.get(field), int) and data_file[field] > 0
            ), error(f"{field} = {data_file.get(field)!r}, expected a positive integer")
        assert data_file["content_offset"] + data_file["content_size_in_bytes"] <= len(
            puffin_bytes
        ), error("manifest-declared blob location exceeds the Puffin file size")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Read("1.0"))
def crafted_writer_conformance(self):
    """The suite's crafted Puffin writer stays field-for-field identical to
    a compliant writer (Spark) for the same vector. This guards the
    corruption harness itself: a crafted file must differ from a real one
    only in the defect a test injects, never in a default the harness got
    wrong (the way snapshot-id/sequence-number once defaulted to 1 instead
    of the spec-mandated -1)."""
    rows = 100
    positions = [i for i in range(rows) if i % 10 == 0]

    with Given("a Spark-written Puffin file and its footer blob descriptor"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )
        dv_entries = manifest.find_dv_entries(table.namespace, table.table_name)
        data_file = dv_entries[0]["entry"]["data_file"]
        spark_bytes = s3_objects.get_object_bytes(
            s3_objects.key_from_uri(data_file["file_path"])
        )
        spark_blob = puffin.parse_puffin_footer(spark_bytes)["blobs"][0]

    with When("the crafted writer builds a Puffin file for the same vector"):
        payload = puffin.build_dv_payload(positions=positions)
        _, crafted_blobs = puffin.build_puffin(
            [
                {
                    "payload": payload,
                    "properties": {
                        "referenced-data-file": spark_blob["properties"][
                            "referenced-data-file"
                        ],
                        "cardinality": spark_blob["properties"]["cardinality"],
                    },
                }
            ]
        )
        crafted_blob = crafted_blobs[0]

    with Then("both writers emit the same set of footer fields"):
        assert set(crafted_blob) == set(spark_blob), error(
            f"crafted writer drifted from the compliant writer: "
            f"crafted-only fields {sorted(set(crafted_blob) - set(spark_blob))}, "
            f"Spark-only fields {sorted(set(spark_blob) - set(crafted_blob))}"
        )

    with And(
        "every field except the layout-dependent offset and length is "
        "value-identical"
    ):
        for field in ("type", "fields", "snapshot-id", "sequence-number", "properties"):
            assert crafted_blob[field] == spark_blob[field], error(
                f"crafted writer drifted from the compliant writer on "
                f"{field!r}: crafted {crafted_blob[field]!r}, "
                f"Spark {spark_blob[field]!r}"
            )

    with And("both blob payloads carry the deletion-vector envelope"):
        spark_payload = spark_bytes[
            spark_blob["offset"] : spark_blob["offset"] + spark_blob["length"]
        ]
        for producer, blob_payload in (("Spark", spark_payload), ("crafted", payload)):
            assert blob_payload[4:8] == puffin.DV_MAGIC, error(
                f"{producer} payload does not start with the 4-byte length "
                f"and deletion-vector magic: {blob_payload[:8]!r}"
            )


WRITER_OPERATIONS = {
    "delete": ["DELETE FROM {table} WHERE id % 7 = 0"],
    "update": ["UPDATE {table} SET data = 'updated' WHERE id BETWEEN 20 AND 40"],
    "merge": [
        "MERGE INTO {table} t "
        "USING (SELECT id * 3 AS id, concat('m-', CAST(id AS STRING)) AS data "
        "FROM range(40)) s "
        "ON t.id = s.id "
        "WHEN MATCHED AND s.id % 2 = 0 THEN UPDATE SET t.data = s.data "
        "WHEN MATCHED AND s.id % 2 = 1 THEN DELETE "
        "WHEN NOT MATCHED THEN INSERT (id, data) VALUES (s.id, s.data)"
    ],
    "combined operations": [
        "DELETE FROM {table} WHERE id % 11 = 0",
        "UPDATE {table} SET data = 'u' WHERE id % 5 = 0 AND id % 11 != 0",
        "MERGE INTO {table} t "
        "USING (SELECT id + 90 AS id, 'merged' AS data FROM range(20)) s "
        "ON t.id = s.id "
        "WHEN MATCHED THEN DELETE "
        "WHEN NOT MATCHED THEN INSERT (id, data) VALUES (s.id, s.data)",
    ],
}


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_WriterOperations("1.0"))
def writer_operation(self, operation, statements):
    """ClickHouse returns exactly the writer engine's own result for one
    vector-producing writer operation."""
    with Given("a v3 merge-on-read table with 100 rows and no deletes yet"):
        table = common.table_with_deletion_vectors(
            rows=100, delete_condition=None, verify_puffin=False
        )

    with When(f"Spark commits the {operation}"):
        spark.execute(
            namespace=table.namespace,
            table_name=table.table_name,
            statements=statements,
        )

    with And("the operation produced at least one deletion vector"):
        s3_objects.assert_puffin_exists(
            namespace=table.namespace, table_name=table.table_name
        )

    with Then("ClickHouse rows equal the writer engine's own rows"):
        spark_rows = spark.select_rows(
            namespace=table.namespace,
            table_name=table.table_name,
            columns="id, data",
            order_by="id",
        )
        result = common.read_result(table=table, columns="id, data", order_by="id")
        clickhouse_rows = [
            line.split("\t") for line in result.output.splitlines() if line.strip()
        ]
        assert clickhouse_rows == spark_rows, error(
            f"ClickHouse returned {len(clickhouse_rows)} rows, "
            f"Spark returned {len(spark_rows)}"
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_WriterOperations("1.0"))
def writer_operations(self):
    """ClickHouse matches the writer's own result whether the deletion
    vector came from DELETE, UPDATE, MERGE, or a combination."""
    for operation, statements in WRITER_OPERATIONS.items():
        Scenario(test=writer_operation, name=operation)(
            operation=operation, statements=statements
        )


@TestFeature
@Name("sanity")
def feature(self, minio_root_user, minio_root_password):
    """Basic deletion-vector read support."""
    Scenario(run=read_deletion_vectors)
    Scenario(run=read_only)
    Suite(run=mutations_rejected)
    Scenario(run=puffin_metadata_structure)
    Scenario(run=crafted_writer_conformance)
    Suite(run=writer_operations)
