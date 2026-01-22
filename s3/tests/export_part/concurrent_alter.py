from testflows.core import *
import s3.tests.export_part.steps as steps
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_part import *
from helpers.alter import column, ttl, update, delete, table
from alter.stress.tests.tc_netem import *
from helpers.common import getuid
from s3.tests.export_part import alter_wrappers


class AlterExample:
    """Wrapper class to control how example names appear in coverage reports."""

    def __init__(self, alter_function, kwargs, name):
        self.alter_function = alter_function
        self.kwargs = kwargs
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def get_alter_functions():
    return [
        AlterExample(
            alter_wrappers.alter_table_add_column,
            {},
            "add column",
        ),
        AlterExample(
            alter_wrappers.alter_table_drop_column,
            {},
            "drop column",
        ),
        AlterExample(
            alter_wrappers.alter_table_modify_column,
            {"column_name": "i"},
            "modify column",
        ),
        AlterExample(
            alter_wrappers.alter_table_rename_column,
            {"column_name_old": "Path"},
            "rename column",
        ),
        AlterExample(
            column.alter_table_comment_column,
            {"column_name": "p", "comment": "test column comment"},
            "comment column",
        ),
        AlterExample(
            alter_wrappers.alter_table_add_constraint,
            {},
            "add constraint",
        ),
        AlterExample(
            alter_wrappers.alter_table_drop_constraint,
            {},
            "drop constraint",
        ),
        AlterExample(
            alter_wrappers.alter_table_drop_partition,
            {},
            "drop partition",
        ),
        AlterExample(
            ttl.alter_table_modify_ttl,
            {
                "ttl_expression": "if(Time < toDateTime('2006-02-07'), Time + INTERVAL 100 YEAR, toDateTime('2106-02-07'))"
            },
            "modify ttl",
        ),
        AlterExample(
            alter_wrappers.alter_table_detach_partition,
            {},
            "detach partition",
        ),
        AlterExample(
            alter_wrappers.alter_table_attach_partition,
            {},
            "attach partition",
        ),
        AlterExample(
            alter_wrappers.alter_table_attach_partition_from,
            {},
            "attach partition from",
        ),
        AlterExample(
            alter_wrappers.alter_table_move_partition_to_table,
            {},
            "move partition to table",
        ),
        AlterExample(
            alter_wrappers.alter_table_move_partition,
            {},
            "move partition",
        ),
        AlterExample(
            alter_wrappers.alter_table_clear_column_in_partition,
            {"column_name": "i"},
            "clear column in partition",
        ),
        AlterExample(
            alter_wrappers.alter_table_clear_index_in_partition,
            {},
            "clear index in partition",
        ),
        AlterExample(
            alter_wrappers.alter_table_freeze_partition,
            {},
            "freeze partition",
        ),
        AlterExample(
            alter_wrappers.alter_table_freeze_partition_with_name,
            {},
            "freeze partition with name",
        ),
        AlterExample(
            alter_wrappers.alter_table_unfreeze_partition_with_name,
            {},
            "unfreeze partition with name",
        ),
        AlterExample(
            alter_wrappers.alter_table_replace_partition,
            {},
            "replace partition",
        ),
        AlterExample(
            update.alter_table_update_column,
            {"column_name": "i", "expression": "0", "condition": "1 = 1"},
            "update column",
        ),
        AlterExample(
            delete.alter_table_delete_rows,
            {"condition": "p = 1"},
            "delete rows",
        ),
        AlterExample(
            table.alter_table_modify_comment,
            {"comment": "test table comment"},
            "modify table comment",
        ),
        AlterExample(
            alter_wrappers.alter_table_fetch_partition,
            {"cleanup": True},
            "fetch partition",
        ),
        AlterExample(
            create_partitions_with_random_uint64,
            {"number_of_partitions": 5, "number_of_parts": 1},
            "create partitions",
        ),
        AlterExample(
            alter_wrappers.drop_table,
            {"recreate": True},
            "drop table",
        ),
    ]


@TestStep(Given)
def create_source_table(
    self, alter_function, number_of_parts=2, number_of_partitions=5
):
    """Create a source table in preparation for the given alter function."""
    source_table = f"source_{getuid()}"

    if alter_function == alter_wrappers.alter_table_fetch_partition:
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            number_of_parts=number_of_parts,
            number_of_partitions=number_of_partitions,
            columns=steps.default_columns(simple=False),
            stop_merges=True,
            query_settings="storage_policy = 'tiered_storage'",
        )
    else:
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            number_of_parts=number_of_parts,
            number_of_partitions=number_of_partitions,
            columns=steps.default_columns(simple=False),
            stop_merges=True,
            query_settings="storage_policy = 'tiered_storage'",
        )

    return source_table


@TestOutline(Scenario)
@Examples(
    "example",
    [(example,) for example in get_alter_functions()],
)
@Requirements(RQ_ClickHouse_ExportPart_Concurrency_ConcurrentAlters("1.0"))
def before_export(self, example):
    """Test altering the source table before exporting parts."""

    with Given("I create a populated source table"):
        source_table = create_source_table(alter_function=example.alter_function)

    with And("I start merges"):
        steps.start_merges(table_name=source_table)

    with When(f"I {example.alter_function.__name__} on the source table"):
        example.alter_function(table_name=source_table, **example.kwargs)

    with And("I populate the source table with new parts"):
        steps.insert_into_table(
            table_name=source_table,
        )

    with And("I create an empty S3 table"):
        s3_table_name = steps.create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=steps.get_column_info(table_name=source_table),
        )

    with And("I export parts to the S3 table"):
        steps.export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            settings=[
                ("export_merge_tree_part_throw_on_pending_mutations", False),
                ("export_merge_tree_part_throw_on_pending_patch_parts", False),
            ],
        )

    with Then("Check source matches destination"):
        steps.part_log_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )
        steps.source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestOutline(Scenario)
@Examples(
    "example",
    [(example,) for example in get_alter_functions()],
)
@Requirements(
    RQ_ClickHouse_ExportPart_Concurrency_ConcurrentAlters("1.0"),
    RQ_ClickHouse_ExportPart_SchemaChangeIsolation("1.0"),
)
def after_export(self, example):
    """Test altering the source table after exporting parts."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = create_source_table(alter_function=example.alter_function)
        s3_table_name = steps.create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=steps.default_columns(simple=False),
        )

    with When("I export parts to the S3 table"):
        steps.export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            settings=[
                ("export_merge_tree_part_throw_on_pending_mutations", False),
                ("export_merge_tree_part_throw_on_pending_patch_parts", False),
            ],
        )

    with And("I read data on the S3 table"):
        steps.wait_for_all_exports_to_complete(table_name=source_table)
        initial_destination_data = select_all_ordered(table_name=s3_table_name)

    with And("I start merges"):
        steps.start_merges(table_name=source_table)

    with And(f"I {example.alter_function.__name__} on the source table"):
        example.alter_function(table_name=source_table, **example.kwargs)

    with Then("Check destination is not affected by the alter"):
        steps.part_log_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )
        final_destination_data = select_all_ordered(table_name=s3_table_name)
        assert initial_destination_data == final_destination_data, error()


@TestOutline(Scenario)
@Examples(
    "example",
    [(example,) for example in get_alter_functions()],
)
@Requirements(RQ_ClickHouse_ExportPart_Concurrency_ConcurrentAlters("1.0"))
def during_export(self, example):
    """Test altering the source table during exporting parts."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = create_source_table(alter_function=example.alter_function)
        s3_table_name = steps.create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=steps.default_columns(simple=False),
        )

    with And("I read data on the source table"):
        initial_source_data = select_all_ordered(table_name=source_table)

    with And("I slow the network"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with When("I export parts to the S3 table"):
        steps.export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            settings=[
                ("export_merge_tree_part_throw_on_pending_mutations", False),
                ("export_merge_tree_part_throw_on_pending_patch_parts", False),
            ],
        )

    with And("I start merges"):
        steps.start_merges(table_name=source_table)

    with And(f"I {example.alter_function.__name__} on the source table"):
        example.alter_function(table_name=source_table, **example.kwargs)

    with Then("Check source matches destination"):
        steps.part_log_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )
        destination_data = select_all_ordered(table_name=s3_table_name)
        assert initial_source_data == destination_data, error()


@TestOutline(Scenario)
@Examples(
    "example",
    [(example,) for example in get_alter_functions()],
)
@Requirements(
    RQ_ClickHouse_ExportPart_Concurrency_ConcurrentAlters("1.0"),
    RQ_ClickHouse_ExportPart_NetworkResilience_DestinationInterruption("1.0"),
)
def during_minio_interruption(self, example):
    """Test altering the source table during MinIO interruption."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = create_source_table(alter_function=example.alter_function)
        s3_table_name = steps.create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=steps.default_columns(simple=False),
        )

    with And("I get initial source data"):
        initial_source_data = select_all_ordered(table_name=source_table)

    with And("I stop MinIO"):
        steps.kill_minio()

    with When("I export parts to the S3 table"):
        steps.export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            settings=[
                ("export_merge_tree_part_throw_on_pending_mutations", False),
                ("export_merge_tree_part_throw_on_pending_patch_parts", False),
            ],
        )

    with And("I start merges"):
        steps.start_merges(table_name=source_table)

    with And(f"I {example.alter_function.__name__} on the source table"):
        if example.alter_function != alter_wrappers.drop_table:
            example.alter_function(table_name=source_table, **example.kwargs)

    with And("I start MinIO"):
        steps.start_minio()

    with Then("Check source matches destination"):
        steps.part_log_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )
        destination_data = select_all_ordered(table_name=s3_table_name)
        assert initial_source_data == destination_data, error()


@TestOutline(Scenario)
@Examples(
    "example",
    [(example,) for example in get_alter_functions()],
)
@Requirements(RQ_ClickHouse_ExportPart_Concurrency("1.0"))
def stress(self, example):
    """Test a high volume of alters in parallel with exports."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = create_source_table(
            alter_function=example.alter_function,
            number_of_parts=10,
            number_of_partitions=10,
        )
        s3_table_name = steps.create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=steps.default_columns(simple=False),
        )

    with And("I start merges"):
        steps.start_merges(table_name=source_table)

    with And("I slow the network"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.5)

    with When(
        f"I export parts to the S3 table in parallel with {example.alter_function.__name__}"
    ):
        with Pool(10) as executor:
            for _ in range(100):
                Step(test=steps.export_parts, parallel=True, executor=executor)(
                    source_table=source_table,
                    destination_table=s3_table_name,
                    parts=[steps.get_random_part(table_name=source_table)],
                    exitcode=1,
                    settings=[
                        ("export_merge_tree_part_throw_on_pending_mutations", False),
                        ("export_merge_tree_part_throw_on_pending_patch_parts", False),
                    ],
                )
                Step(test=example.alter_function, parallel=True, executor=executor)(
                    table_name=source_table, **example.kwargs
                )
                time.sleep(0.3)
            join()

    with Then("Check successfully exported parts are present in destination"):
        steps.part_log_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestFeature
@Name("concurrent alter")
def feature(self):
    """Check concurrent actions on the source table during exporting parts to S3 storage."""

    with Given("I set up MinIO storage configuration"):
        steps.minio_storage_configuration(restart=True)

    Scenario(run=before_export)
    Scenario(run=during_export)
    Scenario(run=after_export)
    Scenario(run=during_minio_interruption)
    Scenario(run=stress)
