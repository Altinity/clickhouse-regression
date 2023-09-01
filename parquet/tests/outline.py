import os

from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *


@TestOutline
def import_export(self, snapshot_name, import_file, snapshot_id=None):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/{table_name}.parquet"
    file_import = f"import_{getuid()}"
    file_export = f"export_{getuid()}"

    if snapshot_id is None:
        snapshot_id = self.context.snapshot_id

    with Given("I save file structure"):
        import_column_structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

    with And("I try to import the binary Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE {table_name}
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet) LIMIT 100
            """,
            file_output="output" + getuid(),
            use_file=True,
        )

    with And("I read the contents of the created table"):
        node.query(
            f"SELECT * FROM {table_name}",
            file_output=file_import,
            use_file=True,
        )

    with Check("import"):
        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        import_column_structure.output.strip(),
                        name=snapshot_name,
                        id=snapshot_id,
                    )
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} LIMIT 100 INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet",
                use_file=True,
                file_output="output" + getuid(),
            )

        with And("I check the exported Parquet file's contents"):
            node.query(
                f"SELECT * FROM file('{path_to_export}', Parquet)",
                file_output=file_export,
                use_file=True,
            )

        with Then("output must match the import"):
            node.command(f"diff {file_import} {file_export}", exitcode=0)

        with And("I check that table structure matches ..."):
            export_columns_structure = node.query(
                f"DESCRIBE TABLE file('{path_to_export}')"
            )
            assert (
                import_column_structure.output.strip()
                == export_columns_structure.output.strip()
            ), error()
