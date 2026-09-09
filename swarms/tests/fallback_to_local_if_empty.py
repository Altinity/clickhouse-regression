from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from iceberg.tests.steps.icebergS3 import (
    read_data_with_icebergS3_table_function,
    read_data_with_icebergS3Cluster_table_function,
)
import iceberg.tests.steps.iceberg_engine as iceberg_engine
from swarms.requirements.requirements import (
    RQ_SRS_044_Swarm_Settings_object_storage_cluster_fallback_to_local_if_empty,
)

import swarms.tests.steps.swarm_steps as swarm_steps
import swarms.tests.steps.s3_steps as s3_steps


EXPECTED_DATA = "('Alice',195.23,20),('Bob',123.45,30),('Charlie',67.89,40),('David',45.67,50),('Eve',89.01,60),('Frank',12.34,70),('Grace',56.78,80),('Heidi',90.12,90),('Ivan',34.56,100),('Judy',78.9,110),('Karl',23.45,120),('Leo',67.89,130),('Mallory',11.12,140),('Nina',34.56,150)"

FALLBACK = ("object_storage_cluster_fallback_to_local_if_empty", 1)
CLUSTER_NOT_FOUND_EXITCODE = 189


def fallback_settings(*extra):
    """Query settings with local fallback enabled, plus any extras."""
    return [FALLBACK, *extra]


@TestStep(Given)
def setup_observer_only_swarm(self, minio_root_user, minio_root_password, node=None):
    """Create Iceberg parquet data and a swarm that has only an observer.

    The cluster name is configured but never registered (SHOW CLUSTERS omits it),
    which is the empty-swarm case ``object_storage_cluster_fallback_to_local_if_empty``
    is meant to cover.
    """
    if node is None:
        node = self.context.node

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    cluster_name = "swarm_cluster" + getuid()
    path = f"/clickhouse/discovery/{cluster_name}"

    with And("create swarm cluster with one observer node"):
        swarm_steps.add_node_to_swarm(
            node=node,
            observer=True,
            cluster_name=cluster_name,
            path=path,
        )

    with Then("cluster is not registered because it has no worker nodes"):
        output = swarm_steps.show_clusters(node=node)
        assert cluster_name not in output.output, error()

    return cluster_name, path


@TestStep(Then)
def assert_hosts(self, result, must_include=None, must_exclude=None):
    """Assert hostName() output contains / does not contain the given hosts."""
    if must_include:
        for host in must_include:
            assert host in result.output, error(
                f"expected {host} in query result, got: {result.output}"
            )
    if must_exclude:
        for host in must_exclude:
            assert host not in result.output, error(
                f"did not expect {host} in query result, got: {result.output}"
            )


@TestStep(Then)
def read_s3_by_host(
    self,
    minio_root_user,
    minio_root_password,
    object_storage_cluster,
    extra_settings=None,
    node=None,
    exitcode=None,
    message=None,
):
    """SELECT hostName() from s3() with the given cluster / settings."""
    return s3_steps.read_data_with_s3_table_function(
        columns="hostName()",
        s3_access_key_id=minio_root_user,
        s3_secret_access_key=minio_root_password,
        object_storage_cluster=object_storage_cluster,
        extra_settings=extra_settings,
        node=node,
        exitcode=exitcode,
        message=message,
    )


@TestStep(Then)
def read_s3_rows(
    self,
    minio_root_user,
    minio_root_password,
    object_storage_cluster,
    extra_settings=None,
    node=None,
):
    """Read full s3() rows and check they match the Iceberg fixture."""
    result = s3_steps.read_data_with_s3_table_function(
        columns="*",
        order_by="tuple(*)",
        format="Values",
        s3_access_key_id=minio_root_user,
        s3_secret_access_key=minio_root_password,
        object_storage_cluster=object_storage_cluster,
        extra_settings=extra_settings,
        node=node,
    )
    assert result.output == EXPECTED_DATA, error()
    return result


@TestScenario
def s3_fallback_on_observer_only_swarm(
    self, minio_root_user, minio_root_password, node=None
):
    """s3() with object_storage_cluster pointing at an observer-only swarm.

    Without fallback the query fails with CLUSTER_DOESNT_EXIST (existing
    contract, also covered by cluster_with_only_one_observer_node).
    With fallback the initiator reads locally.
    """
    if node is None:
        node = self.context.node

    with Given("setup observer-only swarm"):
        cluster_name, _ = setup_observer_only_swarm(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=node,
        )

    with Then("without fallback the empty swarm still errors"):
        read_s3_by_host(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            node=node,
            exitcode=CLUSTER_NOT_FOUND_EXITCODE,
            message=f"DB::Exception: Requested cluster '{cluster_name}' not found.",
        )

    with And("with fallback s3() reads on the initiator"):
        result = read_s3_by_host(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=fallback_settings(),
            node=node,
        )
        assert_hosts(
            result=result,
            must_include=[node.name],
            must_exclude=["clickhouse2", "clickhouse3"],
        )
        read_s3_rows(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=fallback_settings(),
            node=node,
        )


@TestScenario
def s3Cluster_does_not_fallback(
    self, minio_root_user, minio_root_password, node=None
):
    """Explicit s3Cluster() must not apply object_storage_cluster_fallback_to_local_if_empty."""
    if node is None:
        node = self.context.node

    with Given("setup observer-only swarm"):
        cluster_name, _ = setup_observer_only_swarm(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=node,
        )

    with Then("s3Cluster still fails on the empty swarm with fallback enabled"):
        s3_steps.read_data_with_s3Cluster_table_function(
            cluster_name=cluster_name,
            columns="hostName() AS host",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            extra_settings=fallback_settings(),
            node=node,
            exitcode=CLUSTER_NOT_FOUND_EXITCODE,
            message=f"DB::Exception: Requested cluster '{cluster_name}' not found.",
        )

    with And("s3Cluster still fails when fallback is combined with OSC setting"):
        s3_steps.read_data_with_s3Cluster_table_function(
            cluster_name=cluster_name,
            columns="hostName() AS host",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            extra_settings=fallback_settings(
                ("object_storage_cluster", cluster_name),
            ),
            node=node,
            exitcode=CLUSTER_NOT_FOUND_EXITCODE,
            message=f"DB::Exception: Requested cluster '{cluster_name}' not found.",
        )


@TestScenario
def iceberg_fallback_on_observer_only_swarm(
    self, minio_root_user, minio_root_password, node=None
):
    """icebergS3() / iceberg() alternative syntax falls back; icebergS3Cluster() does not."""
    if node is None:
        node = self.context.node

    with Given("setup observer-only swarm"):
        cluster_name, _ = setup_observer_only_swarm(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=node,
        )

    with Then("icebergS3() with fallback reads on the initiator"):
        result = read_data_with_icebergS3_table_function(
            columns="hostName(), count()",
            group_by="hostName()",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
            settings=fallback_settings(),
            node=node,
        )
        assert_hosts(
            result=result,
            must_include=[node.name],
            must_exclude=["clickhouse2", "clickhouse3"],
        )
        rows = read_data_with_icebergS3_table_function(
            columns="*",
            order_by="tuple(*)",
            format="Values",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
            settings=fallback_settings(),
            node=node,
        )
        assert rows.output == EXPECTED_DATA, error()

    with And("icebergS3Cluster() ignores fallback"):
        read_data_with_icebergS3Cluster_table_function(
            cluster_name=cluster_name,
            columns="hostName() AS host",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            settings=fallback_settings(),
            node=node,
            exitcode=CLUSTER_NOT_FOUND_EXITCODE,
            message=f"DB::Exception: Requested cluster '{cluster_name}' not found.",
        )


@TestScenario
def write_does_not_fallback(self, minio_root_user, minio_root_password, node=None):
    """Writes must stay fail-closed when the swarm is empty, even with fallback.

    Applying fallback to INSERT would make the write succeed on an empty swarm
    and fail once workers join.
    """
    if node is None:
        node = self.context.node

    cluster_name = "swarm_cluster" + getuid()
    path = f"/clickhouse/discovery/{cluster_name}"

    with Given("create observer-only swarm"):
        swarm_steps.add_node_to_swarm(
            node=node,
            observer=True,
            cluster_name=cluster_name,
            path=path,
        )

    file_name = f"fallback_write_{getuid()}.tsv"
    url = f"http://minio:9000/warehouse/{file_name}"

    try:
        with Then("INSERT into s3() with empty OSC and fallback still fails"):
            result = node.query(
                f"""
                INSERT INTO FUNCTION s3(
                    '{url}',
                    '{minio_root_user}',
                    '{minio_root_password}',
                    'TSV',
                    'x UInt32'
                )
                SELECT number FROM numbers(5)
                SETTINGS
                    object_storage_cluster = '{cluster_name}',
                    object_storage_cluster_fallback_to_local_if_empty = 1
                """,
                no_checks=True,
            )
            assert result.exitcode != 0, error(
                "INSERT with empty object_storage_cluster must not succeed "
                f"when fallback is enabled, got: {result.output}"
            )
            assert (
                "CLUSTER_DOESNT_EXIST" in result.output
                or "not found" in result.output
                or "NOT_IMPLEMENTED" in result.output
                or "write is not supported" in result.output
            ), error(
                "expected CLUSTER_DOESNT_EXIST or write-not-supported, "
                f"got: {result.output}"
            )
    finally:
        with Finally(f"delete leftover object {file_name} from MinIO"):
            self.context.cluster.command(
                "mc",
                f"mc rm minio/warehouse/{file_name}",
                exitcode=None,
            )


@TestScenario
def s3_engine_fallback(self, minio_root_user, minio_root_password, node=None):
    """ENGINE=S3 with object_storage_cluster in table SETTINGS follows the same fallback."""
    if node is None:
        node = self.context.node

    cluster_name = "swarm_cluster" + getuid()
    path = f"/clickhouse/discovery/{cluster_name}"
    table_name = f"engine_osc_fallback_{getuid()}"
    file_name = f"{table_name}.tsv"
    url = f"http://minio:9000/warehouse/{file_name}"

    with Given("create observer-only swarm"):
        swarm_steps.add_node_to_swarm(
            node=node,
            observer=True,
            cluster_name=cluster_name,
            path=path,
        )

    try:
        with And("write a simple TSV object without object_storage_cluster"):
            node.query(
                f"""
                INSERT INTO FUNCTION s3(
                    '{url}',
                    '{minio_root_user}',
                    '{minio_root_password}',
                    'TSV',
                    'x UInt32'
                )
                SELECT number FROM numbers(10)
                SETTINGS s3_truncate_on_insert = 1
                """
            )

        with And("create S3 engine table bound to the empty swarm"):
            node.query(
                f"""
                CREATE TABLE {table_name} (x UInt32)
                ENGINE = S3(
                    '{url}',
                    '{minio_root_user}',
                    '{minio_root_password}',
                    'TSV'
                )
                SETTINGS object_storage_cluster = '{cluster_name}'
                """
            )

        with Then("without fallback SELECT still errors"):
            node.query(
                f"SELECT count() FROM {table_name}",
                exitcode=CLUSTER_NOT_FOUND_EXITCODE,
                message=f"DB::Exception: Requested cluster '{cluster_name}' not found.",
            )

        with And("with fallback SELECT runs on the initiator"):
            result = node.query(
                f"""
                SELECT hostName(), count(), sum(x)
                FROM {table_name}
                GROUP BY hostName()
                SETTINGS object_storage_cluster_fallback_to_local_if_empty = 1
                """
            )
            assert_hosts(
                result=result,
                must_include=[node.name],
                must_exclude=["clickhouse2", "clickhouse3"],
            )
            assert "10\t45" in result.output, error(
                f"expected 10 rows summing to 45, got: {result.output}"
            )
    finally:
        with Finally("drop S3 engine table and object"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")
            self.context.cluster.command(
                "mc",
                f"mc rm minio/warehouse/{file_name}",
                exitcode=None,
            )


@TestScenario
def iceberg_engine_table_fallback(
    self, minio_root_user, minio_root_password, node=None
):
    """DataLakeCatalog / Iceberg table reads with object_storage_cluster fall back locally."""
    if node is None:
        node = self.context.node

    database_name = f"datalakecatalog_db_{getuid()}"

    with Given("setup Iceberg table"):
        _, table_name, namespace = swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    cluster_name = "swarm_cluster" + getuid()
    path = f"/clickhouse/discovery/{cluster_name}"

    with And("create observer-only swarm"):
        swarm_steps.add_node_to_swarm(
            node=node,
            observer=True,
            cluster_name=cluster_name,
            path=path,
        )

    with And("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    qualified = f"{database_name}.\\`{namespace}.{table_name}\\`"

    with Then("without fallback the empty swarm still errors"):
        node.query(
            f"""
            SELECT count()
            FROM {qualified}
            SETTINGS object_storage_cluster = '{cluster_name}'
            """,
            exitcode=CLUSTER_NOT_FOUND_EXITCODE,
            message=f"DB::Exception: Requested cluster '{cluster_name}' not found.",
        )

    with And("with fallback the Iceberg table is read on the initiator"):
        result = node.query(
            f"""
            SELECT hostName(), count()
            FROM {qualified}
            GROUP BY hostName()
            SETTINGS
                object_storage_cluster = '{cluster_name}',
                object_storage_cluster_fallback_to_local_if_empty = 1
            """
        )
        assert_hosts(
            result=result,
            must_include=[node.name],
            must_exclude=["clickhouse2", "clickhouse3"],
        )


@TestScenario
def fallback_does_not_change_healthy_swarm(
    self, minio_root_user, minio_root_password, node=None
):
    """Fallback must not reroute a live swarm query onto the initiator."""
    if node is None:
        node = self.context.node

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    cluster_name = "swarm_cluster" + getuid()
    path = f"/clickhouse/discovery/{cluster_name}"

    with And("create swarm with observer and one worker"):
        swarm_steps.add_node_to_swarm(
            node=node, observer=True, cluster_name=cluster_name, path=path
        )
        swarm_steps.add_node_to_swarm(
            node=self.context.node2, cluster_name=cluster_name, path=path
        )

    with Then("wait until the worker is visible on the initiator"):
        for retry in retries(count=10, delay=2):
            with retry:
                hosts = swarm_steps.check_cluster_hostnames(
                    cluster_name=cluster_name, node=node
                )
                assert "clickhouse2" in hosts, error()

    with And("without fallback s3() already executes on the swarm worker"):
        result = read_s3_by_host(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            node=node,
        )
        assert_hosts(
            result=result,
            must_include=["clickhouse2"],
            must_exclude=[node.name],
        )

    with And("s3() with fallback still executes on the swarm worker"):
        result = read_s3_by_host(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=fallback_settings(),
            node=node,
        )
        assert_hosts(
            result=result,
            must_include=["clickhouse2"],
            must_exclude=[node.name],
        )
        read_s3_rows(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=fallback_settings(),
            node=node,
        )


@TestScenario
def fallback_after_last_worker_removed(
    self, minio_root_user, minio_root_password, node=None
):
    """After the last worker leaves, s3() with fallback reads locally; s3Cluster still fails."""
    if node is None:
        node = self.context.node

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    cluster_name = "swarm_cluster" + getuid()
    path = f"/clickhouse/discovery/{cluster_name}"

    with And("create swarm with observer and one worker"):
        swarm_steps.add_node_to_swarm(
            node=node, observer=True, cluster_name=cluster_name, path=path
        )
        swarm_steps.add_node_to_swarm(
            node=self.context.node2, cluster_name=cluster_name, path=path
        )

    with And("wait until the swarm is registered"):
        for retry in retries(count=10, delay=2):
            with retry:
                output = swarm_steps.show_clusters(node=node)
                assert cluster_name in output.output, error()

    with When("remove the only swarm worker"):
        swarm_steps.remove_node_from_swarm(
            node=self.context.node2, cluster_name=cluster_name, path=path
        )

    with Then("wait until the cluster disappears"):
        for retry in retries(count=10, delay=2):
            with retry:
                output = swarm_steps.show_clusters(node=node)
                assert cluster_name not in output.output, error()

    with And("without fallback s3() still errors"):
        read_s3_by_host(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            node=node,
            exitcode=CLUSTER_NOT_FOUND_EXITCODE,
            message=f"DB::Exception: Requested cluster '{cluster_name}' not found.",
        )

    with And("with fallback s3() reads on the initiator"):
        result = read_s3_by_host(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=fallback_settings(),
            node=node,
        )
        assert_hosts(
            result=result,
            must_include=[node.name],
            must_exclude=["clickhouse2", "clickhouse3"],
        )

    with And("s3Cluster still does not fall back"):
        s3_steps.read_data_with_s3Cluster_table_function(
            cluster_name=cluster_name,
            columns="hostName() AS host",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            extra_settings=fallback_settings(),
            node=node,
            exitcode=CLUSTER_NOT_FOUND_EXITCODE,
            message=f"DB::Exception: Requested cluster '{cluster_name}' not found.",
        )


@TestScenario
def unknown_cluster_name_fallback(
    self, minio_root_user, minio_root_password, node=None
):
    """Unknown object_storage_cluster name with fallback runs locally (no swarm config at all)."""
    if node is None:
        node = self.context.node

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    cluster_name = f"non_existent_swarm_{getuid()}"

    with Then("s3() with fallback reads on the initiator"):
        result = read_s3_by_host(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=fallback_settings(),
            node=node,
        )
        assert_hosts(result=result, must_include=[node.name])
        read_s3_rows(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=fallback_settings(),
            node=node,
        )


@TestScenario
def remote_initiator_falls_back_when_swarm_empty(
    self, minio_root_user, minio_root_password, node=None
):
    """OSC may be unknown on the querying node and empty on the remote initiator.

    Decision about falling back must be made on the remote initiator: the local
    node sends plain s3() plus the object_storage_cluster setting.
    """
    if node is None:
        node = self.context.node

    remote_node = self.context.node4
    with Given("setup observer-only swarm"):
        cluster_name, _ = setup_observer_only_swarm(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=node,
        )

    with Then(
        "from a node that does not know the swarm, remote initiator + fallback succeeds"
    ):
        result = read_s3_by_host(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=fallback_settings(
                ("object_storage_remote_initiator", 1),
                (
                    "object_storage_remote_initiator_cluster",
                    "replicated_cluster_two_nodes",
                ),
            ),
            node=remote_node,
        )
        assert result.output.strip() != "", error()
        read_s3_rows(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=fallback_settings(
                ("object_storage_remote_initiator", 1),
                (
                    "object_storage_remote_initiator_cluster",
                    "replicated_cluster_two_nodes",
                ),
            ),
            node=remote_node,
        )

    with And("without fallback the same remote-initiator query still errors"):
        result = s3_steps.read_data_with_s3_table_function(
            columns="count()",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=[
                ("object_storage_remote_initiator", 1),
                (
                    "object_storage_remote_initiator_cluster",
                    "replicated_cluster_two_nodes",
                ),
            ],
            node=remote_node,
            no_checks=True,
        )
        # Error is raised on the remote initiator, so the client may surface
        # CLUSTER_DOESNT_EXIST (189) or a wrapped remote exception.
        assert result.exitcode != 0, error(
            f"expected remote initiator to fail without fallback, got: {result.output}"
        )
        assert (
            "not found" in result.output or "CLUSTER_DOESNT_EXIST" in result.output
        ), error(f"expected CLUSTER_DOESNT_EXIST, got: {result.output}")


@TestScenario
def remote_initiator_missing_cluster_not_masked(
    self, minio_root_user, minio_root_password, node=None
):
    """A missing object_storage_remote_initiator_cluster must not be masked by OSC fallback."""
    if node is None:
        node = self.context.node

    with Given("setup observer-only swarm"):
        cluster_name, _ = setup_observer_only_swarm(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=node,
        )

    with Then("bad remote-initiator cluster still reports CLUSTER_DOESNT_EXIST"):
        missing_ri_cluster = f"missing_ri_cluster_{getuid()}"
        read_s3_by_host(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=fallback_settings(
                ("object_storage_remote_initiator", 1),
                (
                    "object_storage_remote_initiator_cluster",
                    missing_ri_cluster,
                ),
            ),
            node=node,
            exitcode=CLUSTER_NOT_FOUND_EXITCODE,
            message=f"DB::Exception: Requested cluster '{missing_ri_cluster}' not found.",
        )


@TestScenario
def remote_initiator_without_ri_cluster_falls_back_locally(
    self, minio_root_user, minio_root_password, node=None
):
    """Unknown OSC + remote_initiator=1 without remote_initiator_cluster + fallback -> local."""
    if node is None:
        node = self.context.node

    with Given("setup observer-only swarm"):
        cluster_name, _ = setup_observer_only_swarm(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=node,
        )

    with Then("fallback reads locally on the querying node"):
        result = read_s3_by_host(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=fallback_settings(
                ("object_storage_remote_initiator", 1),
            ),
            node=node,
        )
        assert_hosts(
            result=result,
            must_include=[node.name],
            must_exclude=["clickhouse2", "clickhouse3"],
        )


@TestScenario
def empty_osc_plus_remote_initiator_still_bad_arguments(
    self, minio_root_user, minio_root_password, node=None
):
    """Empty OSC + remote_initiator without remote_initiator_cluster stays BAD_ARGUMENTS."""
    if node is None:
        node = self.context.node

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("fallback does not replace the missing cluster name"):
        s3_steps.read_data_with_s3_table_function(
            columns="count()",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            extra_settings=fallback_settings(
                ("object_storage_remote_initiator", 1),
            ),
            node=node,
            exitcode=36,
            message="DB::Exception: Setting 'object_storage_remote_initiator'",
        )


@TestScenario
def asymmetric_osc_local_fallback(
    self, minio_root_user, minio_root_password, node=None
):
    """Query from a node that does not know the swarm: fallback reads locally there.

    Live swarm on clickhouse1/clickhouse2 must not be used when the querying node
    has no object_storage_cluster and is not using a remote initiator.
    """
    if node is None:
        node = self.context.node

    querying_node = self.context.node4

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    cluster_name = "swarm_cluster" + getuid()
    path = f"/clickhouse/discovery/{cluster_name}"

    with And("create a live swarm that the querying node does not know"):
        swarm_steps.add_node_to_swarm(
            node=node, observer=True, cluster_name=cluster_name, path=path
        )
        swarm_steps.add_node_to_swarm(
            node=self.context.node2, cluster_name=cluster_name, path=path
        )

    with Then("wait until the worker is visible on the observer"):
        for retry in retries(count=10, delay=2):
            with retry:
                hosts = swarm_steps.check_cluster_hostnames(
                    cluster_name=cluster_name, node=node
                )
                assert "clickhouse2" in hosts, error()

    with And("without fallback the unknown-locally swarm errors on the querying node"):
        read_s3_by_host(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            node=querying_node,
            exitcode=CLUSTER_NOT_FOUND_EXITCODE,
            message=f"DB::Exception: Requested cluster '{cluster_name}' not found.",
        )

    with And("with fallback the querying node reads locally"):
        result = read_s3_by_host(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            object_storage_cluster=cluster_name,
            extra_settings=fallback_settings(),
            node=querying_node,
        )
        assert_hosts(
            result=result,
            must_include=[querying_node.name],
            must_exclude=["clickhouse1", "clickhouse2", "clickhouse3"],
        )


@TestFeature
@Name("fallback to local if empty")
@Requirements(
    RQ_SRS_044_Swarm_Settings_object_storage_cluster_fallback_to_local_if_empty("1.0")
)
def feature(self, minio_root_user, minio_root_password):
    """Cover object_storage_cluster_fallback_to_local_if_empty in swarm topology.

    https://github.com/Altinity/ClickHouse/pull/2221

    Reads with s3() / icebergS3() / ENGINE tables may fall back to the local node
    when object_storage_cluster names an unknown or empty swarm. Writes and
    explicit *Cluster table functions stay fail-closed.
    """
    Scenario(test=s3_fallback_on_observer_only_swarm)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=s3Cluster_does_not_fallback)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=iceberg_fallback_on_observer_only_swarm)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=write_does_not_fallback)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=s3_engine_fallback)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=iceberg_engine_table_fallback)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=fallback_does_not_change_healthy_swarm)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=fallback_after_last_worker_removed)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=unknown_cluster_name_fallback)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=remote_initiator_falls_back_when_swarm_empty)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=remote_initiator_missing_cluster_not_masked)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=remote_initiator_without_ri_cluster_falls_back_locally)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=empty_osc_plus_remote_initiator_still_bad_arguments)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=asymmetric_osc_local_fallback)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
