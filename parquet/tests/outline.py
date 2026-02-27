import os

from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *


@TestOutline
def import_export(
    self, snapshot_name, import_file, snapshot_id=None, limit=None, settings=None
):
    """Import parquet file into a clickhouse table and export it back."""

    if check_clickhouse_version(">=26.1")(self):
        settings = [("max_memory_usage", 20000000000)]

    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/{table_name}.parquet"
    file_import = f"import_{getuid()}"
    file_export = f"export_{getuid()}"

    if limit is None:
        limit = 100

    if snapshot_id is None:
        if check_clickhouse_version(">=24.1")(self):
            snapshot_id = f"{self.context.snapshot_id}_above_24"
        else:
            snapshot_id = self.context.snapshot_id

    with Given("I save file structure"):
        import_column_structure = node.query(
            f"DESCRIBE TABLE file('{import_file}', Parquet) FORMAT TabSeparated",
            settings=settings,
        )

    with And("I try to import the binary Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE {table_name}
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet) LIMIT {limit} FORMAT TabSeparated
            """,
            file_output="output" + getuid(),
            use_file=True,
            settings=settings,
        )

    with And("I read the contents of the created table"):
        node.query(
            f"SELECT * FROM {table_name} FORMAT TabSeparated",
            file_output=file_import,
            use_file=True,
            settings=settings,
        )

    with Check("import"):
        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        import_column_structure.output.strip(),
                        name=(
                            snapshot_name + "_22_4"
                            if check_clickhouse_version("<=22.4")(self)
                            else snapshot_name
                        ),
                        id=snapshot_id,
                        mode=snapshot.CHECK,
                    )
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} LIMIT {limit} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet",
                use_file=True,
                file_output="output" + getuid(),
            )

        with And("I check the exported Parquet file's contents"):
            node.query(
                f"SELECT * FROM file('{path_to_export}', Parquet) FORMAT TabSeparated",
                file_output=file_export,
                use_file=True,
                settings=settings,
            )

        with Then("output must match the import"):
            node.command(f"diff {file_import} {file_export}", exitcode=0)

        with And("I check that table structure matches ..."):
            if "datetime" in import_column_structure.output.lower():
                skip("datetime column structure is different in Parquet and ClickHouse")

            export_columns_structure = node.query(
                f"DESCRIBE TABLE file('{path_to_export}') FORMAT TabSeparated",
                settings=settings,
            )
            assert (
                import_column_structure.output.strip()
                == export_columns_structure.output.strip()
            ), error()
