from testflows.core import *
from helpers.rbac import *
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from rbac.helper.common import *
from s3.requirements.export_part import *
from s3.tests.export_part.steps import *
from s3.requirements.export_part import *


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
            results = export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
                settings=[("user", user_name)],
                exitcode=1,
            )

        with And("I check the export failed"):
            assert results[0].exitcode == 241, error()
            assert "Not enough privileges" in results[0].output, error()

        with And("I grant ALTER privilege to the user"):
            alter_privileges(node=self.context.node, user=user_name, table=source_table)

        with And("I export with only ALTER privilege"):
            results = export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
                settings=[("user", user_name)],
                exitcode=1,
            )

        with And("I check the export failed"):
            assert results[0].exitcode == 241, error()
            assert "Not enough privileges" in results[0].output, error()

        with And("I grant INSERT privilege to the user"):
            insert_privileges(
                node=self.context.node, user=user_name, table=s3_table_name
            )

        with And("I export with ALTER and INSERT privileges"):
            results = export_parts(
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
    """Check that user need not have KILL QUERY privilege to kill their own query."""


@TestFeature
@Requirements(RQ_ClickHouse_ExportPart_Security("1.0"))
@Name("rbac")
def feature(self):
    """Test RBAC for export part."""

    Scenario(run=alter_insert_privilege)
