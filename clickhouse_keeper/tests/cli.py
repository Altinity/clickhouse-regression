import time
from helpers.common import getuid
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
        node.command(f"clickhouse keeper {option}", exitcode=exitcode, message=message)


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_CommandLineOptions_Version("1.0"))
def version(self, node=None):
    """Check -V/--version options."""
    node = self.context.node if node is None else node
    exitcode = 0
    message = "ClickHouse keeper version"

    with When("using -V"):
        node.command("clickhouse keeper -V", exitcode=exitcode, message=message)

    with When("using --version"):
        node.command("clickhouse keeper --version", exitcode=exitcode, message=message)


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_CommandLineOptions_ConfigFile("1.0"))
def config(self, node=None):
    """Check -C, --config-file options."""
    node = self.context.node if node is None else node
    exitcode = 78
    message = "Missing option argument: config-file requires <file>"

    with When("using -C"):
        node.command("clickhouse keeper -C", exitcode=exitcode, message=message)

    with When("using --config-file"):
        node.command(
            "clickhouse keeper --config-file", exitcode=exitcode, message=message
        )


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_CommandLineOptions_Daemon("1.0"))
def daemon(self, node=None):
    """Launch and kill `clickhouse-keeper` cluster with --daemon option."""
    node = self.context.node if node is None else node
    pidfilepath = f"/tmp/clickhouse-keeper-{getuid()}.pid"
    try:
        with Given("I have created keeper server config file"):
            create_keeper_cluster_configuration(
                check_preprocessed=False,
                restart=False,
                modify=False,
            )

        with When("I start `clickhouse-keeper` cluster with --daemon option."):
            with By("starting keeper process"):
                node.command(
                    "clickhouse keeper --config /etc/clickhouse-server/config.xml"
                    f" --pidfile={pidfilepath} --daemon",
                    exitcode=0,
                )
                # avoid race condition in below assertions if the program crashes right away
                time.sleep(0.05)
                with And("checking that keeper pid file was created"):
                    node.command(
                        f"ls {pidfilepath}",
                        exitcode=0,
                        message=pidfilepath,
                    )

    finally:
        with Finally("I stop keeper"):
            with By("sending kill -TERM to keeper process"):
                if node.command(f"ls {pidfilepath}", exitcode=0):
                    pid = int(
                        node.command(f"cat {pidfilepath}", exitcode=0).output.strip()
                    )
                    node.command(f"kill -TERM {pid}", exitcode=0)
            with And("checking pid does not exist"):
                retry(node.command, timeout=100, delay=2)(
                    f"ps {pid}", exitcode=1, steps=False
                )


@TestFeature
@Name("cli")
def feature(self, node="clickhouse1"):
    """Check clickhouse-keeper command line options."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
