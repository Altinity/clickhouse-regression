from testflows.core import *
from helpers.rbac import *
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from rbac.helper.common import *
from s3.requirements.export_part import *
from s3.tests.export_part.steps import *
from s3.requirements.export_part import *
from alter.stress.tests.tc_netem import *


@TestScenario
def alter_insert_privilege(self):
    """Check that user must have alter privilege to export part."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I create a user"):
        user_name = "user_" + getuid()

    with user(node=self.context.node, name=user_name):
        with When("I try to export without any privileges"):
            results_1 = export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
                settings=[("user", user_name)],
                exitcode=1,
            )

        with And("I check the export failed"):
            assert results_1[0].exitcode == 241, error()
            assert "Not enough privileges" in results_1[0].output, error()

        with And("I grant ALTER privilege to the user"):
            alter_privileges(node=self.context.node, user=user_name, table=source_table)

        with And("I export with only ALTER privilege"):
            results_2 = export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
                settings=[("user", user_name)],
                exitcode=1,
            )

        with And("I check the export failed"):
            assert results_2[0].exitcode == 241, error()
            assert "Not enough privileges" in results_2[0].output, error()

        with And("I grant INSERT privilege to the user"):
            insert_privileges(
                node=self.context.node, user=user_name, table=s3_table_name
            )

        with And("I export with ALTER and INSERT privileges"):
            export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
                settings=[("user", user_name)],
            )

        with Then("Source matches destination"):
            source_matches_destination(
                source_table=source_table,
                destination_table=s3_table_name,
            )


@TestScenario
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

    with And("I create a user and query id"):
        user_name = "user_" + getuid()

    with And("I slow the network"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.5)

    with user(node=self.context.node, name=user_name):
        with When(
            "I grant required privileges to run export and SELECT on system.processes"
        ):
            alter_privileges(node=self.context.node, user=user_name, table=source_table)
            insert_privileges(
                node=self.context.node, user=user_name, table=s3_table_name
            )
            select_privileges(
                node=self.context.node, user=user_name, table="system.processes"
            )

        with When(f"I export parts to the S3 table in parallel with kill queries"):
            for _ in range(100):
                query_id = str(uuid.uuid4())
                Step(test=export_parts, parallel=True)(
                    source_table=source_table,
                    destination_table=s3_table_name,
                    node=self.context.node,
                    parts=[get_random_part(table_name=source_table)],
                    settings=[("user", user_name), ("query_id", query_id)],
                    exitcode=1,
                )
                Step(test=kill_query, parallel=True)(
                    node=self.context.node,
                    query_id=query_id,
                    settings=[("user", user_name)],
                )
            join()

        with And("I wait for all exports and merges to complete"):
            wait_for_all_exports_to_complete(node=self.context.node)
            wait_for_all_merges_to_complete(
                node=self.context.node, table_name=source_table
            )

        with Then("Check successfully exported parts are present in destination"):
            part_log = get_part_log(node=self.context.node, table_name=source_table)
            destination_parts = get_s3_parts(table_name=s3_table_name)
            assert part_log == destination_parts, error()


@TestFeature
@Requirements(RQ_ClickHouse_ExportPart_Security("1.0"))
@Name("rbac")
def feature(self):
    """Test RBAC for export part."""

    Scenario(run=alter_insert_privilege)
    Scenario(run=kill_export)
