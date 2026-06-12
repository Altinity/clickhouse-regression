import uuid
from testflows.core import *
from testflows.asserts import error
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_part import *
from alter.stress.tests.tc_netem import *
from s3.tests.export_part import alter_wrappers
from helpers.alter import delete, update


class MutationExample:
    """Wrapper class to control how example names appear in coverage reports."""

    def __init__(self, mutation_function, kwargs, name):
        self.mutation_function = mutation_function
        self.kwargs = kwargs
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Concurrency("1.0"))
def insert_parts(self):
    """Check that exports work correctly with concurrent inserts of source data."""

    with Given("I create an empty source and S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            populate=False,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When(
        "I insert data and export it in parallel",
        description="""
        5 partitions with 1 part each are inserted.
        The export is queued in parallel and usually behaves by exporting
        a snapshot of the source data, often getting just the first partition
        which means the export happens right after the first INSERT query completes.
    """,
    ):
        Step(test=create_partitions_with_random_uint64, parallel=True)(
            table_name=source_table,
            number_of_partitions=5,
            number_of_parts=1,
        )
        Step(test=export_parts, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
        )
        join()

    with Then("Destination data should be a subset of source data"):
        wait_for_all_exports_to_complete()
        source_data = select_all_ordered(table_name=source_table)
        destination_data = select_all_ordered(table_name=s3_table_name)
        assert set(source_data) >= set(destination_data), error()

    with And("Inserts should have completed successfully"):
        assert len(source_data) == 15, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Concurrency("1.0"))
def multiple_sources_same_destination(self, num_tables):
    """Check concurrent exports from different sources to the same S3 table."""

    with Given(f"I create {num_tables} populated source tables and an empty S3 table"):
        source_tables, destination_tables = concurrent_export_tables(
            num_tables=num_tables
        )

    with And("I read data from all tables"):
        source_data = []
        destination_data = []
        for i in range(num_tables):
            data = select_all_ordered(table_name=source_tables[i])
            source_data.extend(data)
            data = select_all_ordered(table_name=destination_tables[i])
            destination_data.extend(data)

    with Then("All data should be present in the S3 table"):
        assert set(source_data) == set(destination_data), error()

    with And("Exports should have run concurrently"):
        verify_export_concurrency(source_tables=source_tables)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Concurrency_NonBlocking("1.0"))
def select_parts(self):
    """Test selecting from the source table before, during, and after exports."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(simple=False),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=False),
        )

    with And("I select data from the source table before exporting parts"):
        before_export_data = select_all_ordered(table_name=source_table)

    with When("I slow the network"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with And("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("I select data from the source table during exporting parts"):
        during_export_data = select_all_ordered(table_name=source_table)

    with And("I select data from the source and destination after exporting parts"):
        wait_for_all_exports_to_complete()
        after_export_data = select_all_ordered(table_name=source_table)
        destination_data = select_all_ordered(table_name=s3_table_name)

    with Then("Check data is consistent before, during, and after exports"):
        assert before_export_data == during_export_data, error()
        assert during_export_data == after_export_data, error()
        assert before_export_data == after_export_data, error()
        assert before_export_data == destination_data, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Concurrency_NonBlocking("1.0"))
def optimize_parts(self):
    """Test merging parts from the source table before, during, and after exporting parts."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            number_of_parts=2,
            columns=default_columns(simple=False),
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=False),
        )

    with And("I optimize partition 1 before export"):
        alter_wrappers.optimize_partition(
            table_name=source_table,
            partition="1",
        )

    with And("I read source parts before export"):
        source_parts_before_export = get_parts_per_partition(table_name=source_table)

    with When("I slow the network to make export take longer"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with And("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("I optimize partition 2 during export"):
        alter_wrappers.optimize_partition(
            table_name=source_table,
            partition="2",
        )

    with And("I optimize partition 3 after export"):
        wait_for_all_exports_to_complete()
        alter_wrappers.optimize_partition(
            table_name=source_table,
            partition="3",
        )

    with Then("I verify destination partition structure is correct"):
        destination_parts_after_export = get_s3_parts_per_partition(
            table_name=s3_table_name
        )
        assert destination_parts_after_export == source_parts_before_export, error()

    with And("Source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("Final partition structure is correct"):
        source_parts_after_export = get_parts_per_partition(table_name=source_table)
        assert source_parts_after_export == {
            "1": 1,
            "2": 1,
            "3": 1,
            "4": 2,
            "5": 2,
        }, error()
        assert destination_parts_after_export == {
            "1": 1,
            "2": 2,
            "3": 2,
            "4": 2,
            "5": 2,
        }, error()


@TestStep(When)
def get_active_export_part_names(self, source_table, node=None):
    """Return part names with an in-flight row in ``system.exports``."""
    if node is None:
        node = self.context.node

    output = node.query(
        f"SELECT part_name FROM system.exports "
        f"WHERE source_table = '{source_table}' "
        f"ORDER BY part_name",
        exitcode=0,
        steps=True,
    ).output
    return [line.strip() for line in output.splitlines() if line.strip()]


@TestStep(Then)
def assert_parts_active_on_disk(self, table_name, part_names, node=None):
    """Each named part must still be an active row in ``system.parts``."""
    if node is None:
        node = self.context.node

    for part_name in part_names:
        active_count = node.query(
            f"SELECT count() FROM system.parts "
            f"WHERE table = '{table_name}' "
            f"AND active = 1 AND name = '{part_name}'",
            exitcode=0,
            steps=True,
        ).output.strip()
        assert int(active_count) == 1, error(
            f"part '{part_name}' is not active on disk during export"
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Concurrency_NonBlocking("1.0"))
def merge_during_export_retains_parts_on_disk(self):
    """Merges may run during export without blocking, while exporting parts
    stay active on disk until the background read finishes.
    """
    node = self.context.node
    export_partition = "4"
    merge_partition = "5"

    with Given("I create a populated source table with merges enabled"):
        source_table = f"source_{getuid()}"
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            number_of_parts=2,
            columns=default_columns(simple=False),
            stop_merges=False,
            number_of_values=10000,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=False),
        )

    with And("partition 5 starts with two parts eligible to merge"):
        parts_before_merge = get_parts_per_partition(table_name=source_table, node=node)
        assert parts_before_merge.get(merge_partition) == 2, error(
            f"expected two parts in partition {merge_partition}, "
            f"got {parts_before_merge!r}"
        )

    with And(
        f"I pick one part from partition {export_partition} to export "
        f"while partition {merge_partition} will merge"
    ):
        part_to_export = node.query(
            f"SELECT name FROM system.parts "
            f"WHERE table = '{source_table}' AND active = 1 "
            f"AND partition = '{export_partition}' "
            f"ORDER BY name LIMIT 1",
            exitcode=0,
            steps=True,
        ).output.strip()
        assert part_to_export, error(
            f"no active part found in partition {export_partition}"
        )

    with And("I slow the network so the export stays in flight longer"):
        network_packet_rate_limit(node=node, rate_mbit=0.05)

    with When(f"I queue export for part '{part_to_export}' only"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=node,
            parts=[part_to_export],
        )

    with And("wait until the export is active in system.exports"):
        for attempt in retries(timeout=30, delay=0.2):
            with attempt:
                assert (
                    get_num_active_exports(node=node, table_name=source_table) > 0
                ), error()

    with And("the exporting part remains active on disk before the merge"):
        exporting_parts = get_active_export_part_names(
            source_table=source_table, node=node
        )
        assert exporting_parts == [part_to_export], error(
            f"expected only {part_to_export!r} in system.exports, got {exporting_parts!r}"
        )
        assert_parts_active_on_disk(
            table_name=source_table,
            part_names=[part_to_export],
            node=node,
        )

    with And(f"I merge partition {merge_partition} while the export is still active"):
        alter_wrappers.optimize_partition(
            table_name=source_table,
            partition=merge_partition,
            node=node,
        )

    with Then("the merge completed without waiting for the export to finish"):
        parts_after_merge = get_parts_per_partition(table_name=source_table, node=node)
        assert parts_after_merge.get(merge_partition) == 1, error(
            f"partition {merge_partition} should have merged to one part, "
            f"got {parts_after_merge!r}"
        )
        assert (
            get_num_active_exports(node=node, table_name=source_table) > 0
        ), error("export finished before merge-during-export could be observed")

    with And("the exporting part is still active on disk after the merge"):
        exporting_parts = get_active_export_part_names(
            source_table=source_table, node=node
        )
        assert exporting_parts == [part_to_export], error(
            f"export of {part_to_export!r} disappeared before part retention check"
        )
        assert_parts_active_on_disk(
            table_name=source_table,
            part_names=[part_to_export],
            node=node,
        )

    with And("I restore network speed and wait for the export to complete"):
        network_packet_rate_limit_replace(node=node, rate_mbit=20)
        wait_for_all_exports_to_complete(node=node, table_name=source_table)

    with And("I export the remaining parts"):
        remaining_parts = [
            part
            for part in get_parts(table_name=source_table, node=node)
            if part != part_to_export
        ]
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=node,
            parts=remaining_parts,
        )

    with And("source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
            node=node,
        )


@TestStep(When)
def select_and_collect(self, table_name, select_action, results_list, node=None):
    """Wrapper to collect select results."""
    if node is None:
        node = self.context.node
    result = select_action(table_name=table_name, node=node)
    results_list.append(result)
    return result


@TestOutline(Scenario)
@Examples(
    "select_action",
    [
        (select_all_ordered,),
        (select_hash,),
    ],
)
@Requirements(RQ_ClickHouse_ExportPart_Concurrency_NonBlocking("1.0"))
def stress_select(self, select_action):
    """Test a high volume of actions in parallel with exports."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = f"source_{getuid()}"

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            number_of_parts=10,
            number_of_partitions=10,
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get starting data"):
        source_data = select_action(table_name=source_table)

    with And("I slow the network"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.5)

    with When(
        f"I export parts to the S3 table in parallel with {select_action.__name__}"
    ):
        select_results = []

        with Pool(10) as executor:
            for _ in range(100):
                Step(test=export_parts, parallel=True, executor=executor)(
                    source_table=source_table,
                    destination_table=s3_table_name,
                    parts=[get_random_part(table_name=source_table)],
                    exitcode=1,
                )
                Step(test=select_and_collect, parallel=True, executor=executor)(
                    table_name=source_table,
                    select_action=select_action,
                    results_list=select_results,
                )
            join()

    with Then("Check data is consistent"):
        assert len(select_results) == 100, error()
        assert all(result == source_data for result in select_results), error()

    with And("Check part log matches destination"):
        part_log_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Concurrency_NonBlocking("1.0"))
def inserts_and_selects_not_blocked(self):
    """Test non-blocking inserts and selects during exports."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = f"source_{getuid()}"
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get initial source data"):
        initial_source_data = select_all_ordered(table_name=source_table)

    with And("I stop MinIO"):
        kill_minio()

    with When("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("I run inserts and selects on the source table"):
        for _ in range(10):
            before_insert_data = select_all_ordered(
                table_name=source_table,
            )
            insert_into_table(table_name=source_table)
            after_insert_data = select_all_ordered(
                table_name=source_table,
            )
            assert after_insert_data != before_insert_data, error()

    with And("I start MinIO"):
        start_minio()

    with Then("Check source matches destination"):
        part_log_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )
        destination_data = select_all_ordered(table_name=s3_table_name)
        assert initial_source_data == destination_data, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_QueryCancellation("1.0"))
def kill_export(self):
    """Check that KILL queries do not break exports."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = f"source_{getuid()}"

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            number_of_parts=10,
            number_of_partitions=10,
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I slow the network"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.5)

    with When(f"I export parts to the S3 table in parallel with kill queries"):
        for _ in range(100):
            query_id = str(uuid.uuid4())
            Step(test=export_parts, parallel=True)(
                source_table=source_table,
                destination_table=s3_table_name,
                parts=[get_random_part(table_name=source_table)],
                settings=[("query_id", query_id)],
                exitcode=1,
            )
            Step(test=kill_query, parallel=True)(
                node=self.context.node,
                query_id=query_id,
            )
        join()

    with Then("Check part log matches destination"):
        part_log_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestOutline(Scenario)
@Examples(
    "delete_method, delete_condition, description",
    [
        ("DELETE FROM", "i = 1", "one row"),
        ("DELETE FROM", "i IN (1, 3)", "multiple rows"),
        ("DELETE FROM", "p = 1", "all rows"),
        ("ALTER DELETE", "i = 1", "one row"),
        ("ALTER DELETE", "i IN (1, 3)", "multiple rows"),
        ("ALTER DELETE", "p = 1", "all rows"),
    ],
)
@Requirements(RQ_ClickHouse_ExportPart_DeletedRows("1.0"))
def after_delete_rows(self, delete_method, delete_condition, description):
    """Test that exports correctly exclude deleted rows."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = f"source_{getuid()}"
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            populate=False,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I create partitions with sequential uint64 values"):
        create_partitions_with_sequential_uint64(
            table_name=source_table,
        )

    with When(f"I delete rows using {delete_method} ({description})"):
        if delete_method == "DELETE FROM":
            delete_from(
                table_name=source_table,
                condition=delete_condition,
            )
        else:
            alter_table_delete_rows(
                table_name=source_table,
                condition=delete_condition,
            )

    with And("I wait for mutations to complete"):
        wait_for_all_mutations_to_complete(table_name=source_table)

    with And("I stop merges to prevent parts from becoming outdated"):
        stop_merges(table_name=source_table)

    with And("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with Then("Check source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestFeature
@Name("concurrent other")
def feature(self):
    """Check that exports work correctly with explicitly parallel tests."""

    Scenario(test=multiple_sources_same_destination)(num_tables=5)
    Scenario(run=insert_parts)
    Scenario(run=select_parts)
    Scenario(run=optimize_parts)
    Scenario(run=merge_during_export_retains_parts_on_disk)
    Scenario(run=stress_select)
    Scenario(run=inserts_and_selects_not_blocked)
    Scenario(run=after_delete_rows)
    Scenario(run=kill_export)
