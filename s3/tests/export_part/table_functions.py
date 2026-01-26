from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_part import *
from s3.tests.common import named_s3_credentials
from alter.stress.tests.tc_netem import *


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_TableFunction_ExplicitSchema("1.0"))
def explicit_schema(self):
    """Test exporting parts to a table function with explicit schema (structure parameter)."""

    with Given("I create a populated source table"):
        source_table = f"source_{getuid()}"
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        create_temp_bucket()

    with And("I get the source table structure"):
        source_columns = get_column_info(table_name=source_table)
        structure_str = ", ".join(
            [f"{col['name']} {col['type']}" for col in source_columns]
        )

    with When("I export parts to a table function with explicit structure"):
        filename = f"export_{getuid()}"
        export_parts_to_table_function(
            source_table=source_table,
            filename=filename,
            structure=structure_str,
        )

    with And("I wait for exports to complete"):
        wait_for_all_exports_to_complete(table_name=source_table)

    with Then("I verify exported data matches source by reading from table function"):
        table_function = f"s3(s3_credentials, url='{self.context.uri}{filename}/**.parquet', format='Parquet')"
        source_data = select_all_ordered(table_name=source_table)
        dest_data = select_all_ordered(table_name=table_function, identifier="*")
        assert source_data == dest_data, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_TableFunction_SchemaInheritance("1.0"))
def schema_inheritance(self):
    """Test exporting parts to a table function with schema inheritance (no structure parameter)."""

    with Given("I create a populated source table"):
        source_table = f"source_{getuid()}"
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        create_temp_bucket()

    with When(
        "I export parts to a table function without explicit structure (schema inheritance)"
    ):
        filename = f"export_{getuid()}"
        export_parts_to_table_function(
            source_table=source_table,
            filename=filename,
        )

    with And("I wait for exports to complete"):
        wait_for_all_exports_to_complete(table_name=source_table)

    with Then("I verify exported data matches source by reading from table function"):
        table_function = f"s3(s3_credentials, url='{self.context.uri}{filename}/**.parquet', format='Parquet')"
        source_data = select_all_ordered(table_name=source_table)
        dest_data = select_all_ordered(table_name=table_function, identifier="*")
        assert source_data == dest_data, error()

    with And("I verify the table function has the correct column names"):
        source_column_names = [
            col["name"] for col in get_column_info(table_name=source_table)
        ]
        dest_result = self.context.node.query(
            f"DESCRIBE TABLE {table_function} FORMAT TabSeparated",
            exitcode=0,
            steps=True,
        )
        dest_column_names = [
            line.split("\t")[0] for line in dest_result.output.strip().splitlines()
        ]
        assert source_column_names == dest_column_names, error(
            "Column names should match"
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Restrictions_SimultaneousExport("1.0"))
def same_part_simultaneous_export_error(self):
    """Test that the same part cannot be exported simultaneously to different locations."""

    with Given("I create a populated source table"):
        source_table = f"source_{getuid()}"
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        create_temp_bucket()

    with And("I get a single part to export"):
        parts = get_parts(table_name=source_table)
        assert len(parts) > 0, error("No parts found in source table")
        part_to_export = parts[0]

    with And("I slow the network to make export take longer"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with When(
        "I try to export the same part to two different table functions simultaneously"
    ):
        filename1 = f"export1_{getuid()}"
        filename2 = f"export2_{getuid()}"

        result1 = export_parts_to_table_function(
            source_table=source_table,
            filename=filename1,
            parts=[part_to_export],
            exitcode=0,
        )
        result2 = export_parts_to_table_function(
            source_table=source_table,
            filename=filename2,
            parts=[part_to_export],
            exitcode=1,
        )

    with Then("I verify the first export succeeded"):
        assert result1[0].exitcode == 0, error("First export should have succeeded")
        wait_for_all_exports_to_complete(table_name=source_table)
        table_function1 = f"s3(s3_credentials, url='{self.context.uri}{filename1}/**.parquet', format='Parquet')"
        count1 = get_row_count(node=self.context.node, table_name=table_function1)
        assert count1 > 0, error("First export should have data")

    with And("I verify the second export failed"):
        assert result2[0].exitcode != 0, error("Second export should have failed")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_TableFunction_Destination("1.0"))
def multiple_parts(self):
    """Test exporting multiple parts to a table function."""

    with Given("I create a source table with multiple parts"):
        source_table = f"source_{getuid()}"
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            number_of_partitions=3,
            number_of_parts=2,
        )
        create_temp_bucket()

    with When("I export all parts to a table function"):
        filename = f"export_{getuid()}"
        export_parts_to_table_function(
            source_table=source_table,
            filename=filename,
        )

    with And("I wait for exports to complete"):
        wait_for_all_exports_to_complete(table_name=source_table)

    with Then("I verify exported data matches source"):
        table_function = f"s3(s3_credentials, url='{self.context.uri}{filename}/**.parquet', format='Parquet')"
        source_data = select_all_ordered(table_name=source_table)
        dest_data = select_all_ordered(table_name=table_function, identifier="*")
        assert source_data == dest_data, error()

    with And("I verify row counts match"):
        source_count = get_row_count(node=self.context.node, table_name=source_table)
        dest_count = get_row_count(node=self.context.node, table_name=table_function)
        assert source_count == dest_count, error()


@TestFeature
@Name("table functions")
def feature(self):
    """Check export part functionality with table functions as destinations."""

    with Given("I set up s3_credentials named collection"):
        named_s3_credentials(
            access_key_id=self.context.access_key_id,
            secret_access_key=self.context.secret_access_key,
            restart=False,
        )

    Scenario(run=explicit_schema)
    Scenario(run=schema_inheritance)
    Scenario(run=same_part_simultaneous_export_error)
    Scenario(run=multiple_parts)
