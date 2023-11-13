import time

from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *
from helpers.common import *


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Config_CoordinationSettings_StartupTimeout("1.0")
)
def startup_timeout(self):
    """I check ClickHouse Keeper coordination setting startup_timeout (30000 ms)"""

    cluster = self.context.cluster
    exitcode = 70
    message = "DB::Exception: Failed to wait RAFT initialization"
    startup_timeout = 10000

    try:
        with Given("I create Keeper Raft Config File and start cluster"):
            start_mixed_keeper(
                control_nodes=cluster.nodes["clickhouse"][:3],
                cluster_nodes=cluster.nodes["clickhouse"][:3],
                rest_cluster_nodes="no_rest_nodes",
                test_setting_name="startup_timeout",
                test_setting_value="10000",
            )

        with When("I stop all clickhouse servers"):
            for name in cluster.nodes["clickhouse"][:3]:
                retry(cluster.node(name).stop_clickhouse, timeout=100, delay=1)()

        with Then(
            "I wait keeper to exit with an error",
            description=f"""
                    keeper exits with exitcode: {exitcode} and shows message: {message} cause
                    startup_timeout failed""",
        ) as start_keeper:
            cluster.node("clickhouse1").command(
                "clickhouse keeper --config /etc/clickhouse-server/config.xml",
                exitcode=exitcode,
                message=message,
            )

        with And(f"I check startup_timeout time value is {startup_timeout} ms"):
            assert current_time(test=start_keeper) < 10.3, error()
            time.sleep(5)

        with Then("I start clickhouse servers"):
            for name in cluster.nodes["clickhouse"][:3]:
                self.context.cluster.node(name).start_clickhouse(wait_healthy=False)
    finally:
        with Finally("I clean up coordination folder"):
            clean_coordination_on_all_nodes()


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_Config_ServerID("1.0"))
def server_id(self):
    """I check ClickHouse Keeper setting server_id"""

    cluster = self.context.cluster
    message = "[PRE-VOTE INIT] my id 1"

    try:
        with Given("I create Keeper Raft Config File and start cluster"):
            start_mixed_keeper(
                control_nodes=cluster.nodes["clickhouse"][:3],
                cluster_nodes=cluster.nodes["clickhouse"][:3],
                rest_cluster_nodes="no_rest_nodes",
                test_setting_name="startup_timeout",
                test_setting_value="10000",
            )

        with When("I stop all clickhouse servers"):
            for name in cluster.nodes["clickhouse"][:3]:
                retry(cluster.node(name).stop_clickhouse, timeout=100, delay=1)()

        with Then("I wait  keeper message: {message}"):
            cluster.node("clickhouse1").command(
                "clickhouse keeper --config /etc/clickhouse-server/config.xml",
                message=message,
            )
            time.sleep(5)

        with Then("I start clickhouse servers"):
            for name in cluster.nodes["clickhouse"][:3]:
                retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)(
                    wait_healthy=False
                )
    finally:
        with Finally("I clean up coordination folder"):
            clean_coordination_on_all_nodes()


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Config_CoordinationSettings_ElectionTimeoutUpperBoundMS(
        "1.0"
    )
)
def election_timeout_upper_bound_ms(self):
    """I check ClickHouse Keeper coordination setting election_timeout_upper_bound_ms (10000 ms)"""
    cluster = self.context.cluster
    election_timeout_upper_bound_ms = 10000

    try:
        with Given("I create Keeper Raft Config File and start cluster"):
            start_mixed_keeper(
                control_nodes=cluster.nodes["clickhouse"][:3],
                cluster_nodes=cluster.nodes["clickhouse"][:3],
                rest_cluster_nodes="no_rest_nodes",
                test_setting_name="election_timeout_upper_bound_ms",
                test_setting_value="10000",
            )

        with When("I stop all clickhouse servers"):
            for name in cluster.nodes["clickhouse"][:3]:
                retry(cluster.node(name).stop_clickhouse, timeout=100, delay=1)()

        with Then(
            "I wait for failure message in Keeper messages",
            description=f"""keeper ping that
                    election_timeout_upper_bound_ms timed out""",
        ) as start_keeper:
            with cluster.node("clickhouse1").command(
                "clickhouse keeper --config /etc/clickhouse-server/config.xml"
                " --pidfile=/tmp/clickhouse-keeper.pid",
                no_checks=True,
                asynchronous=True,
            ) as keeper_process:
                keeper_process.app.expect("failure count 1")
                keeper_process.app.send("\03")

        with And(
            f"I check election_timeout_upper_bound_ms time value is {election_timeout_upper_bound_ms} ms"
        ):
            assert current_time(test=start_keeper) < 22.3, error()

        with Then("I start clickhouse servers"):
            for name in cluster.nodes["clickhouse"][:3]:
                retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)(
                    wait_healthy=False
                )

    finally:
        with Finally("I clean up coordination folder"):
            clean_coordination_on_all_nodes()


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Config_CoordinationSettings_ElectionTimeoutLowerBoundMS(
        "1.0"
    )
)
def election_timeout_lower_bound_ms(self):
    """I check ClickHouse Keeper coordination setting election_timeout_lower_bound_ms (1000 ms)"""
    cluster = self.context.cluster
    election_timeout_lower_bound_ms = 1000

    try:
        with Given("I create Keeper Raft Config File and start cluster"):
            start_mixed_keeper(
                control_nodes=cluster.nodes["clickhouse"][:3],
                cluster_nodes=cluster.nodes["clickhouse"][:3],
                rest_cluster_nodes="no_rest_nodes",
                test_setting_name="election_timeout_lower_bound_ms",
                test_setting_value="1000",
            )

        with When("I stop all clickhouse servers"):
            for name in cluster.nodes["clickhouse"][:3]:
                retry(cluster.node(name).stop_clickhouse, timeout=100, delay=1)()

        with Then(
            "I wait for failure message in Keeper messages",
            description=f"""keeper ping that
                    election_timeout_lower_bound_ms timed out""",
        ) as start_keeper:
            with cluster.node("clickhouse1").command(
                "clickhouse keeper --config /etc/clickhouse-server/config.xml"
                " --pidfile=/tmp/clickhouse-keeper.pid",
                no_checks=True,
                asynchronous=True,
            ) as keeper_process:
                keeper_process.app.expect("failure count 1", timeout=300)
                keeper_process.app.send("\03")

        with And(
            f"I check election_timeout_lower_bound_ms time value is {election_timeout_lower_bound_ms} ms"
        ):
            assert 2 < current_time(test=start_keeper) < 60, error()

        with Then("I start clickhouse servers"):
            for name in cluster.nodes["clickhouse"][:3]:
                retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)(
                    wait_healthy=False
                )

    finally:
        with Finally("I clean up coordination folder"):
            clean_coordination_on_all_nodes()


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_Config_LogStoragePath("1.0"))
def log_storage_path(self):
    """I check ClickHouse Keeper setting log_storage_path creates log file."""
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")

    try:
        start_mixed_keeper(
            control_nodes=cluster.nodes["clickhouse"][:3],
            cluster_nodes=cluster.nodes["clickhouse"][:3],
            rest_cluster_nodes="no_rest_nodes",
        )

        with When("I check log file has been created on the correct path"):
            retry(node.command, timeout=100, delay=1)(
                "ls var/lib/clickhouse/coordination/log/",
                exitcode=0,
                message="changelog_1_10000.bin.zstd",
            )

    finally:
        with Finally("I clean up coordination folder"):
            clean_coordination_on_all_nodes()


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_Config_SnapshotStoragePath("1.0"))
def snapshot_storage_path(self):
    """I check ClickHouse Keeper setting snapshot_storage_path creates snapshot file."""
    cluster = self.context.cluster
    try:
        with Given("I create Keeper Raft Config File and start cluster"):
            start_mixed_keeper(
                control_nodes=cluster.nodes["clickhouse"][:3],
                cluster_nodes=cluster.nodes["clickhouse"][:3],
                rest_cluster_nodes="no_rest_nodes",
                test_setting_name="snapshot_distance",
                test_setting_value=10,
            )

        with Then("I check snapshot file has been created on the correct path"):
            retry(cluster.node("clickhouse1").command, timeout=100, delay=2)(
                "ls " "/var/lib/clickhouse/coordination/snapshots",
                exitcode=0,
                message="snapshot_10.bin.zstd",
            )

    finally:
        with Finally("I clean up coordination folder"):
            clean_coordination_on_all_nodes()


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Config_CoordinationSettings_SnapshotsToKeep("1.0")
)
def snapshots_to_keep(self):
    """I check ClickHouse Keeper setting snapshots_to_keep keeps only 3 files."""
    cluster = self.context.cluster
    try:
        with Given("I create Keeper Raft Config File and start cluster"):
            start_mixed_keeper(
                control_nodes=cluster.nodes["clickhouse"][:3],
                cluster_nodes=cluster.nodes["clickhouse"][:3],
                rest_cluster_nodes="no_rest_nodes",
                test_setting_name="snapshot_distance",
                test_setting_value=1,
            )

        with And("I check that there are only 3 snapshot files in the folder"):
            retry(cluster.node("clickhouse1").command, timeout=100, delay=1)(
                "ls " "/var/lib/clickhouse/coordination/snapshots" " | wc -l",
                exitcode=0,
                message="3",
            )

        with Then(
            "I wait 10 sec and check again that there are steal only 3 snapshot files in the folder"
        ):
            time.sleep(10)
            cluster.node("clickhouse1").command(
                "ls /var/lib/clickhouse/coordination/snapshots | wc -l",
                exitcode=0,
                message="3",
            )

    finally:
        with Finally("I clean up coordination folder"):
            clean_coordination_on_all_nodes()


@TestOutline
@Requirements(RQ_SRS_024_ClickHouse_Keeper_Config_TCPPortSecure_Configuration("1.0"))
def tcp_port_conf(
    self,
    tcp_port=2181,
    tcp_port_secure=False,
    secure=0,
    invalid_config=None,
    keeper_modify=False,
    cluster_modify=False,
):
    """tcp_port tests environment."""
    cluster = self.context.cluster
    cluster_nodes = cluster.nodes["clickhouse"][:1]
    control_nodes = cluster.nodes["clickhouse"][:1]
    try:
        with Given("I create remote config"):
            entries = {
                "cluster_1replica_1shard": {
                    "shard": {"replica": {"host": "clickhouse1", "port": "9000"}}
                }
            }
            create_remote_configuration(entries=entries, nodes=cluster_nodes)
            create_ssl_configuration(nodes=cluster_nodes)

        with Given("I stop all ClickHouse server nodes"):
            for name in cluster_nodes:
                retry(cluster.node(name).stop_clickhouse, timeout=500, delay=1)(
                    safe=False
                )

        with Given("I clean ClickHouse Keeper server nodes"):
            clean_coordination_on_all_nodes()

            # create_ssl_configuration(nodes=cluster_nodes, check_preprocessed=False, restart=False, modify=False)

        with And("I create server Keeper config"):
            create_config_section(
                control_nodes=control_nodes,
                cluster_nodes=cluster_nodes,
                secure=secure,
                check_preprocessed=False,
                restart=False,
                modify=False,
            )

        with And("I create mixed 3 nodes Keeper server config file"):
            if invalid_config:
                create_keeper_cluster_configuration(
                    nodes=control_nodes,
                    tcp_port=tcp_port,
                    tcp_port_secure=tcp_port_secure,
                    test_setting_name="force_sync",
                    test_setting_value="false",
                    check_preprocessed=False,
                    restart=False,
                    modify=cluster_modify,
                    invalid_config=True,
                )
            else:
                create_keeper_cluster_configuration(
                    nodes=control_nodes,
                    tcp_port=tcp_port,
                    tcp_port_secure=tcp_port_secure,
                    test_setting_name="force_sync",
                    test_setting_value="false",
                    check_preprocessed=False,
                    restart=False,
                    modify=keeper_modify,
                )

        with And("I start mixed ClickHouse server nodes"):
            for name in control_nodes:
                retry(cluster.node(name).start_clickhouse, timeout=500, delay=1)(
                    wait_healthy=True
                )
        yield
    finally:
        with Finally("I clean created data"):
            clean_coordination_on_all_nodes()


# @TestScenario
# @Requirements(RQ_SRS_024_ClickHouse_Keeper_Config_TCPPort("1.0"))
# def valid_tcp_port(self):
#     """I check behavior of ClickHouse server and ClickHouse Keeper with valid tcp_port."""
#     cluster = self.context.cluster
#     cluster_name = "'cluster_1replica_1shard'"
#     try:
#         with Given("I create configs with valid tcp_port option"):
#             tcp_port_conf(tcp_port=2181, tcp_port_secure=False, secure=0)
#
#         with Then("I create table and I expect replicated table creation"):
#             retry(cluster.node("clickhouse1").query, timeout=500, delay=1)(
#                 f"CREATE TABLE IF NOT EXISTS"
#                 f" zookeeper_bench on CLUSTER {cluster_name}"
#                 f" (p UInt64, x UInt64) "
#                 "ENGINE = ReplicatedSummingMergeTree"
#                 "('/clickhouse/tables/replicated/{shard}"
#                 f"/zookeeper_bench'"
#                 ", '{replica}') "
#                 "ORDER BY tuple() PARTITION BY p ",
#                 steps=False,
#             )
#     finally:
#         with Finally("I clean created data"):
#             cluster.node("clickhouse1").query(
#                 f"DROP TABLE IF EXISTS zookeeper_bench ON CLUSTER {cluster_name} SYNC"
#             )
#
#
# @TestScenario
# @Requirements(RQ_SRS_024_ClickHouse_Keeper_Config_TCPPortSecure("1.0"))
# def tcp_port_secure(self):
#     """I check behavior of ClickHouse server and ClickHouse Keeper with correct tcp_port_secure config option."""
#     cluster = self.context.cluster
#     cluster_name = "'cluster_1replica_1shard'"
#     try:
#         with Given("I create configs with valid tcp_port_secure and secure option"):
#             tcp_port_conf(tcp_port=2181, tcp_port_secure=True, secure=1)
#
#         with Then("I create table and I expect replicated table creation"):
#             retry(cluster.node("clickhouse1").query, timeout=500, delay=1)(
#                 f"CREATE TABLE IF NOT EXISTS"
#                 f" zookeeper_bench on CLUSTER {cluster_name}"
#                 f" (p UInt64, x UInt64) "
#                 "ENGINE = ReplicatedSummingMergeTree"
#                 "('/clickhouse/tables/replicated/{shard}"
#                 f"/zookeeper_bench'"
#                 ", '{replica}') "
#                 "ORDER BY tuple() PARTITION BY p ",
#                 steps=False,
#             )
#     finally:
#         with Finally("I clean created data"):
#             cluster.node("clickhouse1").query(
#                 f"DROP TABLE IF EXISTS zookeeper_bench ON CLUSTER {cluster_name} SYNC"
#             )
#             clean_coordination_on_all_nodes()


# @TestScenario
# @Requirements(
#     RQ_SRS_024_ClickHouse_Keeper_Config_WrongTCPPort("1.0")
# )
# def wrong_tcp_port(self):
#     """I check behavior of ClickHouse server and ClickHouse Keeper with wrong tcp_port.
#     """
#     cluster = self.context.cluster
#     cluster_name = '\'cluster_1replica_1shard\''
#     cluster_nodes = cluster.nodes["clickhouse"][:1]
#     control_nodes = cluster.nodes["clickhouse"][:1]
#     try:
#         with Given("I create configs with invalid tcp_port option"):
#             tcp_port_conf(tcp_port=2182, tcp_port_secure=False, secure=0, keeper_modify=True)
#
#         with Then("I create table and I expect replicated table creation failed"):
#             retry(cluster.node("clickhouse1").query, timeout=100, delay=1)(f"CREATE TABLE IF NOT EXISTS"
#                                                                            f" zookeeper_bench on CLUSTER {cluster_name}"
#                                                                            f" (p UInt64, x UInt64) "
#                                                                            "ENGINE = ReplicatedSummingMergeTree"
#                                                                            "('/clickhouse/tables/replicated/{shard}"
#                                                                            f"/zookeeper_bench'"
#                                                                            ", '{replica}') "
#                                                                            "ORDER BY tuple() PARTITION BY p ",
#                                                                            steps=False,
#                                                                            exitcode=231,
#                                                                            message="Code: 999. DB::Exception: Received from"
#                                                                                    " localhost:9000. DB::Exception: "
#                                                                                    "All connection tries failed while"
#                                                                                    " connecting to ZooKeeper.")
#
#         with Given("I stop all ClickHouse server nodes"):
#             for name in cluster_nodes:
#                 retry(cluster.node(name).stop_clickhouse, timeout=100, delay=1)(safe=False)
#
#         with And("I create mixed 3 nodes Keeper server config file"):
#             create_keeper_cluster_configuration(
#                 nodes=control_nodes,
#                 tcp_port=2181, tcp_port_secure=False,
#                 test_setting_name="force_sync",
#                 test_setting_value="false",
#                 check_preprocessed=False, restart=False, modify=False
#             )
#
#         with And("I start mixed ClickHouse server nodes"):
#             for name in control_nodes:
#                 retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)(wait_healthy=True)
#
#     finally:
#         with Finally("I clean created data"):
#             clean_coordination_on_all_nodes()
#
#
# @TestScenario
# @Requirements(
#     RQ_SRS_024_ClickHouse_Keeper_Config_TCPPortSecure_UnsecureServer("1.0")
# )
# def tcp_port_unsecure_server(self):
#     """I check system behavior when ClickHouse server with unsecure port connects to
#     ClickHouse Keeper tcp_port_secure.
#     """
#     cluster = self.context.cluster
#     cluster_name = '\'cluster_1replica_1shard\''
#     cluster_nodes = cluster.nodes["clickhouse"][:1]
#     control_nodes = cluster.nodes["clickhouse"][:1]
#     try:
#         with Given("I create ClickHouse server with unsecure port and ClickHouse Keeper tcp_port_secure"):
#             tcp_port_conf(tcp_port=2181, tcp_port_secure=True, secure=0, keeper_modify=True)
#
#         with Then("I create table and I expect replicated table creation failed"):
#             retry(cluster.node("clickhouse1").query, timeout=100, delay=1)(f"CREATE TABLE IF NOT EXISTS"
#                                                                            f" zookeeper_bench on CLUSTER {cluster_name}"
#                                                                            f" (p UInt64, x UInt64) "
#                                                                            "ENGINE = ReplicatedSummingMergeTree"
#                                                                            "('/clickhouse/tables/replicated/{shard}"
#                                                                            f"/zookeeper_bench'"
#                                                                            ", '{replica}') "
#                                                                            "ORDER BY tuple() PARTITION BY p ",
#                                                                            steps=False,
#                                                                            exitcode=231,
#                                                                            message="Code: 999. DB::Exception: Received from"
#                                                                                    " localhost:9000. DB::Exception: "
#                                                                                    "All connection tries failed while"
#                                                                                    " connecting to ZooKeeper.")
#
#         with Given("I stop all ClickHouse server nodes"):
#             for name in cluster_nodes:
#                 retry(cluster.node(name).stop_clickhouse, timeout=100, delay=1)(safe=False)
#
#         with And("I create mixed 3 nodes Keeper server config file"):
#             create_keeper_cluster_configuration(
#                 nodes=control_nodes,
#                 tcp_port=2181, tcp_port_secure=False,
#                 test_setting_name="force_sync",
#                 test_setting_value="false",
#                 check_preprocessed=False, restart=False, modify=False
#             )
#
#         with And("I start mixed ClickHouse server nodes"):
#             for name in control_nodes:
#                 retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)(wait_healthy=True)
#
#     finally:
#         with Finally("I clean created data"):
#             clean_coordination_on_all_nodes()
#
#
# @TestScenario
# @Requirements(
#     RQ_SRS_024_ClickHouse_Keeper_Config_TCPPortSecure_UnsecureKeeper("1.0")
# )
# def tcp_port_unsecure_keeper(self):
#     """I check system behavior when ClickHouse server with secure port connects to
#     ClickHouse Keeper tcp_port.
#     """
#     cluster = self.context.cluster
#     cluster_name = '\'cluster_1replica_1shard\''
#     cluster_nodes = cluster.nodes["clickhouse"][:1]
#     control_nodes = cluster.nodes["clickhouse"][:1]
#     try:
#         with Given("I create ClickHouse server with secure port and ClickHouse Keeper tcp_port"):
#             tcp_port_conf(tcp_port=2181, tcp_port_secure=False, secure=1, keeper_modify=True, cluster_modify=True)
#
#         with Then("I create table and I expect replicated table creation failed"):
#             retry(cluster.node("clickhouse1").query, timeout=100, delay=1)(f"CREATE TABLE IF NOT EXISTS"
#                                                                            f" zookeeper_bench on CLUSTER {cluster_name}"
#                                                                            f" (p UInt64, x UInt64) "
#                                                                            "ENGINE = ReplicatedSummingMergeTree"
#                                                                            "('/clickhouse/tables/replicated/{shard}"
#                                                                            f"/zookeeper_bench'"
#                                                                            ", '{replica}') "
#                                                                            "ORDER BY tuple() PARTITION BY p ",
#                                                                            steps=False,
#                                                                            exitcode=231,
#                                                                            message="Code: 999. DB::Exception: Received from"
#                                                                                    " localhost:9000. DB::Exception: "
#                                                                                    "All connection tries failed while"
#                                                                                    " connecting to ZooKeeper.")
#
#     finally:
#         with Finally("I clean created data"):
#             clean_coordination_on_all_nodes()


@TestOutline
def coordination_option_values(
    self,
    message="client timeout 0",
    test_setting_name="operation_timeout_ms",
    test_setting_value=0,
):
    """Coordination options values check environment."""
    cluster = self.context.cluster
    try:
        with Given("I create Keeper Raft Config File and start cluster"):
            start_mixed_keeper(
                control_nodes=cluster.nodes["clickhouse"][:3],
                cluster_nodes=cluster.nodes["clickhouse"][:3],
                rest_cluster_nodes="no_rest_nodes",
                test_setting_name=test_setting_name,
                test_setting_value=test_setting_value,
            )

        with When("I stop all clickhouse servers"):
            for name in cluster.nodes["clickhouse"][:3]:
                retry(cluster.node(name).stop_clickhouse, timeout=100, delay=1)()

        with Then("I start keeper and wait for message: {message}"):
            with cluster.node("clickhouse1").command(
                "clickhouse keeper --config /etc/clickhouse-server/config.xml",
                no_checks=True,
                asynchronous=True,
            ) as keeper_process:
                keeper_process.app.expect(message)
                keeper_process.app.send("\03")
                time.sleep(2)

        with Then("I start clickhouse servers"):
            for name in cluster.nodes["clickhouse"][:3]:
                retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)(
                    wait_healthy=False
                )

    finally:
        with Finally("I start clickhouse servers and clean up coordination folder"):
            clean_coordination_on_all_nodes()


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Config_CoordinationSettings_OperationTimeoutMS("1.0")
)
def operation_timeout_ms(self):
    """I check ClickHouse Keeper coordination setting operation_timeout_ms is correct value
    by checking log information.
    """
    coordination_option_values(
        message="client timeout 10",
        test_setting_name="operation_timeout_ms",
        test_setting_value=10,
    )


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Config_CoordinationSettings_HeartBeatIntervalsMS("1.0")
)
def heart_beat_interval_ms(self):
    """I check ClickHouse Keeper coordination setting heart_beat_interval_ms correct value."""
    coordination_option_values(
        message="heartbeat 1000",
        test_setting_name="heart_beat_interval_ms",
        test_setting_value=1000,
    )


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Config_CoordinationSettings_SnapshotDistance("1.0")
)
def snapshot_distance(self):
    """I check ClickHouse Keeper coordination setting snapshot_distance correct value"""
    coordination_option_values(
        message="snapshot distance 50000",
        test_setting_name="snapshot_distance",
        test_setting_value=50000,
    )


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Config_CoordinationSettings_ReservedLogItems("1.0")
)
def reserved_log_items(self):
    """I check ClickHouse Keeper coordination setting reserved_log_items correct value."""
    coordination_option_values(
        message="reserved logs 50000",
        test_setting_name="reserved_log_items",
        test_setting_value=50000,
    )


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_Config_CoordinationSettings_ForseSync("1.0"))
def force_sync(self):
    """I check ClickHouse Keeper coordination setting force_sync correct value."""
    coordination_option_values(
        message="force_sync enabled",
        test_setting_name="force_sync",
        test_setting_value=True,
    )


@TestFeature
@Name("coordination settings")
def feature(self):
    """Check coordination settings to ClickHouse Keeper."""
    for scenario in loads(current_module(), Scenario):
        scenario()
