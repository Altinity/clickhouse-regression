from testflows.core import *


@TestFeature
@Name("integration")
def feature(self):
    """Run the ClickHouse integration tests."""

    with When("I run the integration tests"):
        self.context.cluster.command(
            None,
            f"test_files/integration_tests/runner --disable-net-host --binary {self.context.cluster.clickhouse_binary_path} --base-configs-dir configs/clickhouse --cases-dir test_files/integration_tests --src-dir test_files/integration_tests/src",
        )
