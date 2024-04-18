from testflows.core import *
from helpers.common import *
from helpers.tables import *
from attach.tests.common import *
from attach.requirements.requirements import (
    RQ_SRS_039_ClickHouse_Attach_ReplicaPath_ActivePath,
)


@TestScenario
def check_active_path(self):
    """Check that it is not possible to attach a table with the active path."""
    node = self.context.node
    with Given("I create database"):
        database_name = create_database()

    with And("I create replicated table"):
        table_id = getuid()
        table1 = "table1_" + getuid()
        create_replicated_table(
            table_name=table1, database_name=database_name, table_id=table_id
        )

    with Then("I attach table with same replica path and expect an exception"):
        uuid = getuid()
        table2 = "table2_" + getuid()
        exitcode, message = (
            253,
            "DB::Exception: There already is an active replica with this replica path",
        )
        attach_table_UUID(
            table=table2,
            table_id=table_id,
            uuid=uuid,
            database_name=database_name,
            exitcode=exitcode,
            message=message,
        )

    with And("I try to insert data into both tables"):
        node.query(f"INSERT INTO {database_name}.{table1} (extra) VALUES (1)")
        exitcode, message = (
            60,
            f"DB::Exception: Table {database_name}.{table2} does not exist",
        )
        node.query(
            f"INSERT INTO {database_name}.{table2} (extra) VALUES (2)",
            exitcode=exitcode,
            message=message,
        )

    with Then("I check that data is inserted into the first table"):
        assert (
            node.query(
                f"SELECT extra FROM {database_name}.{table1} FORMAT TabSeparated"
            ).output
            == "1"
        )

    with Then("I check system.replicas"):
        node.query(
            f"SELECT table, replica_is_active, replica_path FROM system.replicas where table = '{table1}' or table='{table2}' FORMAT PrettyCompactMonoBlock"
        )


@TestFeature
@Name("active path")
@Requirements(RQ_SRS_039_ClickHouse_Attach_ReplicaPath_ActivePath)
def feature(self):
    """Check that it is not possible to attach a table with the active path."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
