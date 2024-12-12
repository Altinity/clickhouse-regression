from platform import processor

from s3.tests.common import *
from s3.requirements import *
from lightweight_delete.tests.steps import *

DOCKER_NETWORK = "s3_env_default" if processor() == "x86_64" else "s3_env_arm64"


@TestStep(When)
def disconnect_reconnect(self, node=None):
    """Disconnect and reconnect the docker container."""
    if node is None:
        node = self.context.node

    with When("I disconnect the docker node"):
        self.context.cluster.command(
            None, f"docker network disconnect {DOCKER_NETWORK} s3_env_clickhouse1_1"
        )

    with And("I reconnect the docker node"):
        self.context.cluster.command(
            None, f"docker network connect {DOCKER_NETWORK} s3_env_clickhouse1_1"
        )


@TestOutline
def automatic_reconnection(self, policy_name, disk_name="external", node=None):
    """Check that ClickHouse is able to access data on a table stored externally after a reconnection."""
    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        s3_table(table_name=table_name, policy=policy_name)

    with When("I insert some data into the table"):
        node.query(f"INSERT INTO {table_name} VALUES (1, 2)")

    with And("I get container id and network id"):
        container_id = self.context.cluster.node_container_id(node="clickhouse1")
        network_id = self.context.cluster.command(
            None, f"docker network ls --filter 'name={DOCKER_NETWORK}' -q"
        ).output

    with And("I stop the connection to the node with the table"):
        self.context.cluster.command(
            None, f"docker network disconnect --force {network_id} {container_id}"
        )

    time.sleep(5)

    with And("I enable the connection to the node with the table"):
        self.context.cluster.command(
            None, f"docker network connect {network_id} {container_id}"
        )

    with Then("I check the table"):
        assert (
            node.query(f"SELECT * FROM {table_name} FORMAT TabSeparated").output
            == "1\t2"
        ), error()


@TestOutline
def automatic_reconnection_parallel(self, policy_name, disk_name="external", node=None):
    """Check that ClickHouse is able to access data on a table stored externally after a reconnection,
    if the disconnection happened during the insert.
    """
    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"
    self.context.table_engine = "MergeTree"

    with Given("I have a table"):
        s3_table(table_name=table_name, policy=policy_name)

    with When("I insert a lot of data"):
        Step(test=insert, parallel=True)(
            table_name=table_name, partitions=3, parts_per_partition=10
        )

    with And("I interrupt the connection and then reconnect"):
        Step(test=disconnect_reconnect, parallel=True)

    join()

    with Then("I check the table"):
        assert (
            node.query(f"SELECT count(*) FROM {table_name} FORMAT TabSeparated").output
            == "30000"
        ), error()


@TestScenario
@Requirements()
def local_and_s3_disk(self):
    """Setup storage policy that uses local and s3 disks."""

    with Given("I update the config to have s3 and local disks"):
        default_s3_and_local_disk()

    Scenario(test=automatic_reconnection)(policy_name="default_and_external")
    Scenario(test=automatic_reconnection_parallel)(policy_name="default_and_external")


@TestScenario
@Requirements()
def local_and_s3_volumes(self):
    """Setup storage policy that uses local and s3 volumes."""

    with Given("I update the config to have s3 and local disks"):
        default_s3_and_local_volume()

    Scenario(test=automatic_reconnection)(policy_name="default_and_external")
    Scenario(test=automatic_reconnection_parallel)(policy_name="default_and_external")


@TestScenario
@Requirements()
def s3_disk(self):
    """Setup storage policy that only uses s3 disk."""

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume()

    for outline in loads(current_module(), Outline):
        Scenario(test=outline)(policy_name="external")


@TestFeature
@Requirements(RQ_SRS_015_S3_AutomaticReconnects_AWS("1.0"))
@Name("reconnect")
def aws_s3(self, uri):
    """Check that ClickHouse reconnects to aws s3."""

    self.context.uri = uri

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)


@TestFeature
@Requirements(RQ_SRS_015_S3_AutomaticReconnects_GCS("1.0"))
@Name("reconnect")
def gcs(self, uri):
    """Check that ClickHouse reconnects to gcs."""

    self.context.uri = uri

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)


@TestFeature
@Name("reconnect")
def azure(self):
    """Check that ClickHouse reconnects to azure."""

    self.context.uri = None

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)


@TestFeature
@Requirements(RQ_SRS_015_S3_AutomaticReconnects_MinIO("1.0"))
@Name("reconnect")
def minio(self, uri):
    """Check that ClickHouse reconnects to minio."""

    self.context.uri = uri

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
