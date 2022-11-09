from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *
from helpers.common import *


@TestOutline
def four_letter_word_commands(
    self, four_letter_word_command="ruok", output="imok", node_name="clickhouse1"
):
    """Check 4lw command outline."""
    cluster = self.context.cluster
    try:
        with Given(f"I check that {four_letter_word_command} returns {output}"):
            retry(cluster.node("bash-tools").cmd, timeout=100, delay=1)(
                f"echo {four_letter_word_command} | nc {node_name} 2181",
                exitcode=0,
                message=f"{output}",
            )
    finally:
        with Finally("I clean up"):
            clean_coordination_on_all_nodes()


@TestScenario
def mntr_command(self, four_letter_word_command="mntr", output="zk_version"):
    """Check 'mntr' has in output "zk_version"."""
    four_letter_word_commands(
        four_letter_word_command=four_letter_word_command, output=output
    )


@TestScenario
def srvr_command(
    self, four_letter_word_command="srvr", output="ClickHouse Keeper version:"
):
    """Check 'srvr' has in output "ClickHouse Keeper version:"."""
    four_letter_word_commands(
        four_letter_word_command=four_letter_word_command, output=output
    )


@TestScenario
def stat_command(self, four_letter_word_command="stat", output="Clients:"):
    """Check 'stat' has in output "Clients:"."""
    four_letter_word_commands(
        four_letter_word_command=four_letter_word_command, output=output
    )


@TestScenario
def conf_command(self, four_letter_word_command="conf", output="server_id=1"):
    """Check 'conf' has in output "server_id=1"."""
    four_letter_word_commands(
        four_letter_word_command=four_letter_word_command, output=output
    )


@TestScenario
def cons_command(self, four_letter_word_command="cons", output="recved"):
    """Check 'cons' has in output "recved"."""
    four_letter_word_commands(
        four_letter_word_command=four_letter_word_command, output=output
    )


@TestScenario
def crst_command(
    self, four_letter_word_command="crst", output="Connection stats reset."
):
    """Check 'crst' has in output "Connection stats reset."."""
    four_letter_word_commands(
        four_letter_word_command=four_letter_word_command, output=output
    )


@TestScenario
def envi_command(self, four_letter_word_command="envi", output="host.name=clickhouse1"):
    """Check 'envi' has in output "host.name=clickhouse1"."""
    four_letter_word_commands(
        four_letter_word_command=four_letter_word_command, output=output
    )


@TestScenario
def dirs_command(self, four_letter_word_command="dirs", output="snapshot_dir_size:"):
    """Check 'dirs' has in output "snapshot_dir_size:"."""
    four_letter_word_commands(
        four_letter_word_command=four_letter_word_command, output=output
    )


@TestScenario
def isro_command(self, four_letter_word_command="isro", output="rw"):
    """Check 'isro' has in output "rw:"."""
    four_letter_word_commands(
        four_letter_word_command=four_letter_word_command, output=output
    )


@TestScenario
def wchs_command(
    self, four_letter_word_command="wchs", output="connections watching 1 paths"
):
    """Check 'isro' has in output "rw:"."""
    four_letter_word_commands(
        four_letter_word_command=four_letter_word_command, output=output
    )


@TestScenario
def wchc_command(
    self, four_letter_word_command="wchc", output="/clickhouse/task_queue/ddl"
):
    """Check 'wchc' has in output "/clickhouse/task_queue/ddl"."""
    if check_clickhouse_version("<22.8")(self):
        four_letter_word_commands(
            four_letter_word_command=four_letter_word_command, output=output
        )
    else:
        xfail("doesn't work from 22.8")
        four_letter_word_commands(
            four_letter_word_command=four_letter_word_command, output=output
        )


@TestScenario
def srst_command(self, four_letter_word_command="srst", output="Server stats reset."):
    """Check 'srst' has in output "Server stats reset."."""
    four_letter_word_commands(
        four_letter_word_command=four_letter_word_command, output=output
    )


@TestScenario
def ruok_command(self, four_letter_word_command="ruok", output="imok"):
    """Check 'ruok' has in output "imok"."""
    four_letter_word_commands(
        four_letter_word_command=four_letter_word_command, output=output
    )


@TestFeature
@Requirements(RQ_SRS_024_ClickHouse_Keeper_4lwCommands("1.0"))
@Name("four letter word commands")
def feature(self):
    """Four letter word commands check tests."""
    cluster = self.context.cluster

    with Given("I start three ClickHouse keeper env"):
        start_mixed_keeper(
            cluster_nodes=cluster.nodes["clickhouse"][:9],
            control_nodes=cluster.nodes["clickhouse"][0:3],
            rest_cluster_nodes=cluster.nodes["clickhouse"][3:9],
        )

    for scenario in loads(current_module(), Scenario):
        scenario()
