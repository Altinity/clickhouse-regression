from testflows.core import *
from testflows.asserts import error


@TestFeature
@Name("file_scheme_escape_reads_local_file")
def icebergLocal(self, minio_root_user, minio_root_password):
    """
    Test icebergLocal() table function with path traversal.
    """
    node = self.context.node

    base_path = "/var/lib/clickhouse/user_files/iceberg_local_basic"
    metadata_dir = f"{base_path}/metadata"
    data_dir = f"{base_path}/data"

    with Given("copy the pre-created Iceberg table under user_files"):
        # Clean and recreate base directory
        node.command(f"rm -rf {base_path}", exitcode=0)
        node.command(f"mkdir -p {metadata_dir} {data_dir}", exitcode=0)

        # In the container, we mount the test table here:
        # ../tests/icebergS3_table_function/iceberg_table/ : /mnt/iceberg_table/
        node.command(
            "cp -r /mnt/iceberg_table/data/* " f"{data_dir}/",
            exitcode=0,
        )

    with And("copy local-path Iceberg metadata fixtures generated with fastavro"):
        node.command(
            "cp -r /mnt/iceberg_table/local_metadata/* " f"{metadata_dir}/",
            exitcode=0,
        )
        # Keep Iceberg-style metadata filename so metadata discovery can find it.
        node.command(
            f"cp {metadata_dir}/metadata_local.json {metadata_dir}/00002-local.metadata.json",
            exitcode=0,
        )

    with And("create user that only has access to use IcebergLocal()"):
        node.query(
            f"CREATE USER IF NOT EXISTS iceberg_local_user_only_read",
        )

    with And("grant select on icebergLocal() to the user"):
        node.query(
            f"GRANT READ ON FILE TO iceberg_local_user_only_read",
        )
        node.query(
            f"GRANT CREATE TEMPORARY TABLE ON *.* TO iceberg_local_user_only_read",
        )

    with When("read the table using icebergLocal() and Parquet format"):
        settings = []
        settings.append(("user", "iceberg_local_user_only_read"))
        query = f"""
                SELECT *
                FROM icebergLocal(
                    '{base_path}',
                    'Parquet',
                    SETTINGS iceberg_metadata_table_uuid = 'fbb0a4ea-488e-4387-9cdc-23888ec32fae'
                )
                FORMAT TSV
                """
        result = node.query(query, settings=settings)

    with Then("check that icebergLocal() returned some rows from the table"):
        # We only check that the output is non-empty and contains at
        # least one of the known names from the pre-created table.
        output = result.output.strip()
        assert output, error("icebergLocal returned no data")
        assert "Alice" in output and "Bob" in output and "Charlie" in output, error(
            f"unexpected icebergLocal output:\n{output}"
        )

    with When(
        "try to read a file outside user_files using iceberg metadata chain with user that only has access to use IcebergLocal()"
    ):
        settings = []
        settings.append(("user", "iceberg_local_user_only_read"))
        node.command(
            f"cp {metadata_dir}/metadata_outside.json {metadata_dir}/00003-outside.metadata.json",
            exitcode=0,
        )
        outside_query = f"""
            SELECT *
            FROM icebergLocal(
                '{base_path}',
                'RawBLOB',
                SETTINGS iceberg_metadata_table_uuid = 'outside-read-uuid'
            )
            FORMAT TSV
            """
        outside_result = node.query(outside_query, settings=settings)

    with Then("check that traversal reaches file outside user_files"):
        outside_output = outside_result.output.strip()
        note(f"outside_output: {outside_output}")

    with Finally("I clean up the copied Iceberg table under user_files"):
        node.command(f"rm -rf {base_path}", exitcode=0)
