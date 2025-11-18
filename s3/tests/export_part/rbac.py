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
def kill_privilege(self):
    """Check that user need not have KILL QUERY privilege to kill their own query,
    but need to have KILL QUERY privilege to kill other user's query."""

    with Given("I create a populated source table and 2 empty S3 tables"):
        source_table = "source_" + getuid()
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name_1 = create_s3_table(table_name="s3_1", create_new_bucket=True)
        s3_table_name_2 = create_s3_table(table_name="s3_2", create_new_bucket=True)

    with And("I create a user and query id"):
        user_name = "user_" + getuid()
        query_id_1 = str(uuid.uuid4())
        query_id_2 = str(uuid.uuid4())

    with And("I slow the network"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with user(node=self.context.node, name=user_name):
        with When(
            "I grant required privileges to run export and SELECT on system.processes"
        ):
            alter_privileges(node=self.context.node, user=user_name, table=source_table)
            insert_privileges(
                node=self.context.node, user=user_name, table=s3_table_name_1
            )
            select_privileges(
                node=self.context.node, user=user_name, table="system.processes"
            )

        with And("I export parts"):
            export_parts(
                source_table=source_table,
                destination_table=s3_table_name_1,
                node=self.context.node,
                settings=[("user", "default"), ("query_id", query_id_1)],
            )

        with And("I kill the query"):
            output = kill_query(
                node=self.context.node,
                query_id=query_id_1,
                settings=[("user", user_name)],
            )
            note(output.output)
            pause()

        # with And("I export parts from default user"):
        #     export_parts(
        #         source_table=source_table,
        #         destination_table=s3_table_name_2,
        #         node=self.context.node,
        #         settings=[("user", "default"), ("query_id", query_id_2)],
        #     )

        # with And("I kill the query"):
        #     kill_query(
        #         node=self.context.node,
        #         query_id=query_id_2,
        #         settings=[("user", user_name)],
        #     )

        with Then("Destination 1 data should be a subset of source data"):
            source_data = select_all_ordered(
                table_name=source_table,
                node=self.context.node,
            )
            destination_data = select_all_ordered(
                table_name=s3_table_name_1,
                node=self.context.node,
            )
            assert set(source_data) >= set(destination_data), error()
            pause()

        # with And("Destination 2 should match source"):
        #     source_matches_destination(
        #         source_table=source_table,
        #         destination_table=s3_table_name_2,
        #     )


@TestFeature
@Requirements(RQ_ClickHouse_ExportPart_Security("1.0"))
@Name("rbac")
def feature(self):
    """Test RBAC for export part."""

    Scenario(run=alter_insert_privilege)
    Scenario(run=kill_privilege)
