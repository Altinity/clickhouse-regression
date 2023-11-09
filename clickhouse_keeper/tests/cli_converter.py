from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *
from helpers.common import getuid


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Converter_CommandLineOptions_ZookeeperSnapshotsDir(
        "1.0"
    )
)
def snapshot(self):
    """Check --zookeeper-snapshots-dir option"""
    with Given("I connect ZooKeeper to cluster"):
        connect_zookeeper()

    with And("I create simple table"):
        create_simple_table()

    with Then("Receive UID"):
        uid = getuid()

    with Given("I check --zookeeper-snapshots-dir option work correct"):
        message = "Magic deserialized, looks OK"
        self.context.cluster.node("clickhouse1").command(f"mkdir -p /share/{uid}/snapshots")
        self.context.cluster.node("clickhouse1").command(
            f"clickhouse keeper-converter"
            f" --zookeeper-logs-dir /share/zookeeper3/datalog/version-2"
            f" --zookeeper-snapshots-dir "
            f"/share/zookeeper3/data/version-2"
            f" --output-dir /share/{uid}/snapshots",
            exitcode=0,
            message=message,
        )


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Converter_CommandLineOptions_ZookeeperSnapshotsDir(
        "1.0"
    )
)
def snapshot_invalid_dir(self):
    """Check --zookeeper-snapshots-dir option"""
    with Given("I connect ZooKeeper to cluster"):
        connect_zookeeper()

    with And("I create simple table"):
        create_simple_table()

    with Then("Receive UID"):
        uid = getuid()

    with Given("I check --zookeeper-snapshots-dir option work correct"):
        message = "No such file or directory"
        self.context.cluster.node("clickhouse1").command(f"mkdir -p /share/{uid}/snapshots")
        self.context.cluster.node("clickhouse1").command(
            f"clickhouse keeper-converter"
            f" --zookeeper-logs-dir /share/zookeeper3/datalog/version-2"
            f" --zookeeper-snapshots-dir /share/notexists"
            f" --output-dir /share/{uid}/snapshots",
            exitcode=233,
            message=message,
        )


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Converter_CommandLineOptions_ZookeeperLogsDir("1.0")
)
def logs(self):
    """Check --zookeeper-logs-dir option"""
    with Given("I connect ZooKeeper to cluster"):
        connect_zookeeper()

    with And("I create simple table"):
        create_simple_table()

    with Then("Receive UID"):
        uid = getuid()

    with Given("I check --zookeeper-logs-dir option work correct"):
        message = "Header looks OK"
        self.context.cluster.node("clickhouse1").command(f"mkdir -p /share/{uid}/snapshots")
        self.context.cluster.node("clickhouse1").command(
            f"clickhouse keeper-converter"
            f" --zookeeper-logs-dir /share/zookeeper3/datalog/version-2"
            f" --zookeeper-snapshots-dir "
            f"/share/zookeeper3/data/version-2"
            f" --output-dir /share/{uid}/snapshots",
            exitcode=0,
            message=message,
        )


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Converter_CommandLineOptions_ZookeeperLogsDir("1.0")
)
def logs_invalid_dir(self):
    """Check --zookeeper-logs-dir option"""
    with Given("I connect ZooKeeper to cluster"):
        connect_zookeeper()

    with And("I create simple table"):
        create_simple_table()

    with Then("Receive UID"):
        uid = getuid()

    with Given("I check --zookeeper-logs-dir option work correct"):
        message = "No such file or directory"
        self.context.cluster.node("clickhouse1").command(f"mkdir -p /share/{uid}/snapshots")
        self.context.cluster.node("clickhouse1").command(
            f"clickhouse keeper-converter"
            f" --zookeeper-logs-dir /share/notexists"
            f" --zookeeper-snapshots-dir "
            f"/share/zookeeper3/data/version-2"
            f" --output-dir /share/{uid}/snapshots",
            exitcode=233,
            message=message,
        )


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Converter_CommandLineOptions_OutputDir("1.0")
)
def output_dir(self):
    """Check correct Keeper snapshot creation from ZooKeeper snapshots and logs"""
    with Given("I connect ZooKeeper to cluster"):
        connect_zookeeper()

    with And("I create simple table"):
        create_simple_table()

    with Then("Receive UID"):
        uid = getuid()

    with Given("I check --output-dir option work correct"):
        message = (
            "Snapshot serialized to path:/share"
            if check_clickhouse_version("<23.8")(self)
            else 'Snapshot serialized to path:"/share'
        )
        self.context.cluster.node("clickhouse1").command(f"mkdir -p /share/{uid}/snapshots")
        self.context.cluster.node("clickhouse1").command(
            f"clickhouse keeper-converter"
            f" --zookeeper-logs-dir /share/zookeeper3/datalog/version-2"
            f" --zookeeper-snapshots-dir "
            f"/share/zookeeper3/data/version-2"
            f" --output-dir /share/{uid}/snapshots",
            exitcode=0,
            message=message,
        )


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Converter_CommandLineOptions_OutputDir("1.0")
)
def output_dir_invalid(self):
    """Check correct Keeper snapshot creation from ZooKeeper snapshots and logs"""
    with Given("I connect ZooKeeper to cluster"):
        connect_zookeeper()

    with And("I create simple table"):
        create_simple_table()

    with Given("I check --output-dir option work correct"):
        message = "No such file or directory"
        self.context.cluster.node("clickhouse1").command(
            f"clickhouse keeper-converter"
            f" --zookeeper-logs-dir /share/zookeeper3/datalog/version-2"
            f" --zookeeper-snapshots-dir "
            f"/share/zookeeper3/data/version-2"
            f" --output-dir /share/notexists",
            exitcode=107,
            message=message,
        )


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Converter_CommandLineOptions_MissingArgumentValues(
        "1.0"
    )
)
def missing_arg_values(self):
    """Check error input in cli option"""
    with Given("I connect ZooKeeper to cluster"):
        connect_zookeeper()

    with And("I create simple table"):
        create_simple_table()

    with Then("Receive UID"):
        uid = getuid()

    with Given("I check error message when missing arg values inputted"):
        message = "std::exception. Code: 1001, type:"
        self.context.cluster.node("clickhouse1").command(
            f"clickhouse keeper-converter " f"--zookeeper-snapshots-dir smth wrong",
            exitcode=233,
            message=message,
        )


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_Converter_CommandLineOptions_Help("1.0"))
def help_option(self, node=None):
    """Check ClickHouse keeper-converter -h/--help options."""
    node = self.context.node if node is None else node
    exitcode = 0
    message = (
        "Usage: clickhouse --zookeeper-logs-dir /var/lib/zookeeper/data/version-2"
        " --zookeeper-snapshots-dir /var/lib/zookeeper/data/version-2"
        " --output-dir /var/lib/clickhouse/coordination/snapshots"
    )

    with When("using -h"):
        node.command("clickhouse keeper-converter -h", exitcode=exitcode, message=message)

    with When("using --help"):
        node.command(
            "clickhouse keeper-converter --help", exitcode=exitcode, message=message
        )


@TestFeature
@Name("cli converter")
def feature(self, node="clickhouse1"):
    """Check ClickHouse Keeper converter command line options."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
