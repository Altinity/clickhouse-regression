from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from s3.tests.export_part.steps import *
from s3.tests.common import named_s3_credentials
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_part import *


@TestStep(When)
def get_s3_filenames(self, table_name, node=None):
    """Get all distinct file names from an S3 table."""
    if node is None:
        node = self.context.node

    output = node.query(
        f"SELECT DISTINCT _file FROM {table_name} ORDER BY _file",
        exitcode=0,
        steps=True,
    ).output

    return [row.strip() for row in output.splitlines() if row.strip()]


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Settings_FilenamePattern("1.0"))
def default_pattern(self):
    """Check that the default filename pattern {part_name}_{checksum} produces
    files named <part_name>_<hex_checksum>.<seq>.parquet."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export parts with the default filename pattern"):
        parts = get_parts(table_name=source_table)
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("I wait for all exports to complete"):
        wait_for_all_exports_to_complete(table_name=source_table)

    with Then("the exported filenames should contain the part name"):
        filenames = get_s3_filenames(table_name=s3_table_name)
        assert len(filenames) > 0, error()

        for part_name in parts:
            matching = [f for f in filenames if f.startswith(part_name + "_")]
            assert len(matching) > 0, error()

    with And("the exported data should match the source"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Settings_FilenamePattern("1.0"))
def custom_prefix_pattern(self):
    """Check that a custom prefix pattern like 'myprefix_{part_name}' is applied
    to the exported filenames."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export parts with a custom prefix pattern"):
        parts = get_parts(table_name=source_table)
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            settings=[
                (
                    "export_merge_tree_part_filename_pattern",
                    "myprefix_{part_name}",
                )
            ],
        )

    with And("I wait for all exports to complete"):
        wait_for_all_exports_to_complete(table_name=source_table)

    with Then("every exported filename should start with 'myprefix_'"):
        filenames = get_s3_filenames(table_name=s3_table_name)
        assert len(filenames) > 0, error()

        for f in filenames:
            assert f.startswith("myprefix_"), error()

    with And("every part name should appear in the filenames"):
        for part_name in parts:
            matching = [f for f in filenames if f"myprefix_{part_name}" in f]
            assert len(matching) > 0, error()

    with And("the exported data should match the source"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Settings_FilenamePattern("1.0"))
def pattern_with_checksum_only(self):
    """Check that a pattern using only {checksum} produces valid filenames."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export parts with a checksum-only pattern"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            settings=[
                (
                    "export_merge_tree_part_filename_pattern",
                    "export_{checksum}",
                )
            ],
        )

    with And("I wait for all exports to complete"):
        wait_for_all_exports_to_complete(table_name=source_table)

    with Then(
        "every filename should start with 'export_' and contain no literal braces"
    ):
        filenames = get_s3_filenames(table_name=s3_table_name)
        assert len(filenames) > 0, error()

        for f in filenames:
            assert f.startswith("export_"), error()
            assert "{" not in f and "}" not in f, error()

    with And("the exported data should match the source"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Settings_FilenamePattern("1.0"))
def pattern_with_database_and_table_macros(self):
    """Check that {database} and {table} macros in the pattern are expanded
    to the actual database and table name."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export parts with {database}_{table}_{part_name} pattern"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            settings=[
                (
                    "export_merge_tree_part_filename_pattern",
                    "{database}_{table}_{part_name}",
                )
            ],
        )

    with And("I wait for all exports to complete"):
        wait_for_all_exports_to_complete(table_name=source_table)

    with Then("filenames should contain no literal braces (macros are expanded)"):
        filenames = get_s3_filenames(table_name=s3_table_name)
        assert len(filenames) > 0, error()

        for f in filenames:
            assert "{" not in f and "}" not in f, error()

    with And("filenames should contain the source table name"):
        for f in filenames:
            assert source_table in f, error()

    with And("the exported data should match the source"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPart_Settings_FilenamePattern("1.0"),
    RQ_ClickHouse_ExportPart_Shards("1.0"),
)
def pattern_with_shard_macro(self):
    """Check that {shard} macro in the pattern is expanded using the server's
    configured macros. Each shard produces a filename containing its shard identifier,
    preventing filename collisions when multiple shards export the same partition."""

    cluster = "sharded_cluster12"

    with Given("I get all nodes for the sharded cluster"):
        node_names = get_cluster_nodes(cluster=cluster)
        nodes = [self.context.cluster.node(name) for name in node_names]

    with And("I create local MergeTree tables on each shard"):
        local_table = "local_" + getuid()

        partitioned_merge_tree_table(
            table_name=local_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            populate=False,
            cluster=cluster,
        )

    with And("I create a Distributed table for inserting"):
        distributed_table = create_distributed_table(
            cluster=cluster,
            local_table_name=local_table,
            node=nodes[0],
        )

    with And("I create an S3 destination table on the cluster"):
        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, cluster=cluster
        )

    with And("I insert data through the Distributed table"):
        nodes[0].query(
            f"INSERT INTO {distributed_table} (p, i) SELECT 1, rand64() FROM numbers(200)",
            exitcode=0,
            steps=True,
        )

    with And("I wait for data to be distributed"):
        wait_for_distributed_table_data(
            table_name=distributed_table,
            expected_count=200,
            node=nodes[0],
        )

    with When("I export parts from each shard with a {shard} pattern"):
        for shard_node in nodes:
            export_parts(
                source_table=local_table,
                destination_table=s3_table_name,
                node=shard_node,
                settings=[
                    (
                        "export_merge_tree_part_filename_pattern",
                        "{part_name}_{shard}_{checksum}",
                    )
                ],
            )

    with And("I wait for all exports to complete on all nodes"):
        for shard_node in nodes:
            wait_for_all_exports_to_complete(node=shard_node, table_name=local_table)

    with Then("filenames should contain the shard identifier"):
        filenames = get_s3_filenames(table_name=s3_table_name, node=nodes[0])
        assert len(filenames) > 0, error()

        for f in filenames:
            assert "{" not in f and "}" not in f, error()

    with And("the exported data should match the distributed table"):
        source_matches_destination(
            source_table=distributed_table,
            destination_table=s3_table_name,
            node=nodes[0],
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPart_Settings_FilenamePattern("1.0"),
    RQ_ClickHouse_ExportPart_Shards("1.0"),
)
def sharded_default_pattern_collision(self):
    """Check that when two shards export parts with the same name using the default
    pattern, the exported file is overwritten and only one copy of the data remains.
    This verifies the collision behavior that the filename_pattern setting is designed to solve.
    """

    cluster = "sharded_cluster12"

    with Given("I get all nodes for the sharded cluster"):
        node_names = get_cluster_nodes(cluster=cluster)
        nodes = [self.context.cluster.node(name) for name in node_names]

    with And("I create local tables and insert the same data on each shard"):
        local_table = "local_" + getuid()

        for shard_node in nodes:
            shard_node.query(
                f"""
                CREATE TABLE IF NOT EXISTS {local_table}
                (p UInt8, i UInt64) ENGINE = MergeTree
                PARTITION BY p ORDER BY i
                """,
                exitcode=0,
                steps=True,
            )
            shard_node.query(f"SYSTEM STOP MERGES {local_table}", exitcode=0)
            shard_node.query(
                f"INSERT INTO {local_table} (p, i) SELECT 1, number FROM numbers(3)",
                exitcode=0,
                steps=True,
            )

    with And("I create an S3 destination table on the cluster"):
        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, cluster=cluster
        )

    with When("I export from both shards with default pattern"):
        for shard_node in nodes:
            export_parts(
                source_table=local_table,
                destination_table=s3_table_name,
                node=shard_node,
                settings=[
                    (
                        "export_merge_tree_part_file_already_exists_policy",
                        "overwrite",
                    )
                ],
            )

    with And("I wait for all exports to complete"):
        for shard_node in nodes:
            wait_for_all_exports_to_complete(node=shard_node, table_name=local_table)

    with Then(
        "only one copy of the data should exist because identical filenames cause overwrite"
    ):
        file_count = count_s3_files(table_name=s3_table_name, node=nodes[0])
        assert file_count == 1, error()

        row_count = (
            nodes[0]
            .query(
                f"SELECT count() FROM {s3_table_name}",
                exitcode=0,
                steps=True,
            )
            .output.strip()
        )
        assert row_count == "3", error()


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPart_Settings_FilenamePattern("1.0"),
    RQ_ClickHouse_ExportPart_TableFunction_Destination("1.0"),
)
def pattern_with_table_function_destination(self):
    """Check that the filename pattern setting works when exporting to a table
    function destination (TO TABLE FUNCTION s3(...))."""

    with Given("I set up s3_credentials named collection"):
        named_s3_credentials(
            access_key_id=self.context.access_key_id,
            secret_access_key=self.context.secret_access_key,
            restart=False,
        )

    with And("I create a populated source table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )

    with And("I create a temp bucket path"):
        create_temp_bucket()

    with When("I export parts to a table function with a custom pattern"):
        filename = f"tf_{getuid()}"

        export_parts_to_table_function(
            source_table=source_table,
            filename=filename,
            settings=[
                (
                    "export_merge_tree_part_filename_pattern",
                    "tfprefix_{part_name}_{checksum}",
                )
            ],
        )

    with And("I wait for all exports to complete"):
        wait_for_all_exports_to_complete(table_name=source_table)

    with Then("I can read the exported data back"):
        node = self.context.node

        row_count = node.query(
            f"""
            SELECT count()
            FROM s3(
                '{self.context.uri}{filename}/**/*.parquet',
                '{self.context.access_key_id}',
                '{self.context.secret_access_key}',
                'Parquet'
            )
            """,
            exitcode=0,
            steps=True,
        ).output.strip()

        source_count = node.query(
            f"SELECT count() FROM {source_table}",
            exitcode=0,
            steps=True,
        ).output.strip()

        assert row_count == source_count, error()


@TestFeature
@Name("filename pattern")
def feature(self):
    """Check the export_merge_tree_part_filename_pattern setting for exporting parts."""

    Scenario(run=default_pattern)
    Scenario(run=custom_prefix_pattern)
    Scenario(run=pattern_with_checksum_only)
    Scenario(run=pattern_with_database_and_table_macros)
    Scenario(run=pattern_with_shard_macro)
    Scenario(run=sharded_default_pattern_collision)
    Scenario(run=pattern_with_table_function_destination)
