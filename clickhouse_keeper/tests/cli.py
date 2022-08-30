from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *


@TestOutline(Scenario)
@Examples(
    "option",
    [
        ("-v",),
        ("--unknown",),
    ],
)
def unknown_option(self, option, node=None):
    """Check unknown options."""
    node = self.context.node if node is None else node
    exitcode = 78
    message = f"Unknown option specified"

    with When(f"using unknown option '{option}'"):
        node.cmd(f"clickhouse keeper {option}", exitcode=exitcode, message=message)


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_CommandLineOptions_Version("1.0"))
def version(self, node=None):
    """Check -V/--version options."""
    node = self.context.node if node is None else node
    exitcode = 0
    message = "ClickHouse keeper version"

    with When("using -V"):
        node.cmd("clickhouse keeper -V", exitcode=exitcode, message=message)

    with When("using --version"):
        node.cmd("clickhouse keeper --version", exitcode=exitcode, message=message)


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_CommandLineOptions_ConfigFile("1.0"))
def config(self, node=None):
    """Check -C, --config-file options."""
    node = self.context.node if node is None else node
    exitcode = 78
    message = "Missing option argument: config-file requires <file>"

    with When("using -C"):
        node.cmd("clickhouse keeper -C", exitcode=exitcode, message=message)

    with When("using --config-file"):
        node.cmd("clickhouse keeper --config-file", exitcode=exitcode, message=message)


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_CommandLineOptions_Daemon("1.0"))
def daemon(self, node=None):
    """Launch and kill `clickhouse-keeper` cluster with --daemon option."""
    node = self.context.node if node is None else node
    try:
        with When("I start `clickhouse-keeper` cluster with --daemon option."):
            with By("starting keeper process"):
                node.cmd(
                    "clickhouse keeper --config /etc/clickhouse-keeper/config.xml"
                    " --pidfile=/tmp/clickhouse-keeper.pid --daemon",
                    exitcode=0,
                )
                with And("checking that keeper pid file was created"):
                    node.cmd(
                        "ls /tmp/clickhouse-keeper.pid",
                        exitcode=0,
                        message="/tmp/clickhouse-keeper.pid",
                    )
    finally:
        with Finally("I stop keeper"):
            with When(f"I stop stop keeper process"):
                with By("sending kill -TERM to keeper process"):
                    if node.cmd("ls /tmp/clickhouse-keeper.pid", exitcode=0):
                        pid = node.cmd("cat /tmp/clickhouse-keeper.pid").output.strip()
                        node.cmd(f"kill -TERM {pid}", exitcode=0)
                with And("checking pid does not exist"):
                    retry(node.cmd, timeout=100, delay=1)(
                        f"ps {pid}", exitcode=1, steps=False
                    )


@TestFeature
@Name("cli")
def feature(self, node="clickhouse1"):
    """Check clickhouse-keeper command line options."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
