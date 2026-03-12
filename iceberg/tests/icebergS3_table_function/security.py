from testflows.core import *
from testflows.asserts import error


@TestFeature
@Name("file_scheme_escape_reads_local_file")
def file_scheme_escape_reads_local_file(self, minio_root_user, minio_root_password):
    """
    Basis test: copy a pre-created Iceberg table under user_files and read it
    using icebergLocal(), without any path traversal.
    """
    node = self.context.node

    base_path = "/var/lib/clickhouse/user_files/iceberg_local_basic"
    metadata_dir = f"{base_path}/metadata"
    data_dir = f"{base_path}/data"

    with Given("I copy the pre-created Iceberg table under user_files"):
        # Clean and recreate base directory
        node.command(f"rm -rf {base_path}", exitcode=0)
        node.command(f"mkdir -p {metadata_dir} {data_dir}", exitcode=0)

        # In the container, we mount the test table here:
        # ../tests/icebergS3_table_function/iceberg_table/ : /mnt/iceberg_table/
        node.command(
            "cp -r /mnt/iceberg_table/data/* " f"{data_dir}/",
            exitcode=0,
        )

    with And("I copy local-path Iceberg metadata fixtures generated with fastavro"):
        node.command(
            "cp -r /mnt/iceberg_table/local_metadata/* " f"{metadata_dir}/",
            exitcode=0,
        )
        # Keep Iceberg-style metadata filename so metadata discovery can find it.
        node.command(
            f"cp {metadata_dir}/metadata_local.json {metadata_dir}/00002-local.metadata.json",
            exitcode=0,
        )

    with When("I read the table using icebergLocal() and Parquet format"):
        query = f"""
SELECT *
FROM icebergLocal(
    '{base_path}',
    'Parquet',
    SETTINGS iceberg_metadata_table_uuid = 'fbb0a4ea-488e-4387-9cdc-23888ec32fae'
)
FORMAT TSV
"""
        # For now we just expect the query to succeed (no INCORRECT_DATA).
        result = node.query(query, steps=False, no_checks=True)

    with Then("I see that icebergLocal() returned some rows from the table"):
        # We only check that the output is non-empty and contains at
        # least one of the known names from the pre-created table.
        output = result.output.strip()
        assert output, error("icebergLocal returned no data")
        assert "Alice" in output or "Bob" in output or "Charlie" in output, error(
            f"unexpected icebergLocal output:\n{output}"
        )

    with Finally("I clean up the copied Iceberg table under user_files"):
        node.command(f"rm -rf {base_path}", exitcode=0)
