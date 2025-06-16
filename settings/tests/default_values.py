from testflows.core import *
from testflows.asserts import snapshot, values, error
from helpers.common import get_snapshot_id, check_clickhouse_version


@TestStep()
def get_all_settings(self):
    """Get list of all settings from system.settings table."""
    return self.context.node.query(
        f"SELECT name FROM system.settings"
    ).output.splitlines()


@TestScenario
def check_default_value(self, setting):
    """Check default value for the setting."""
    with Given("I have a clickhouse node"):
        node = self.context.node

    with When("I check the default value for the setting"):
        default_and_changed = node.query(
            f"SELECT value, changed FROM system.settings WHERE name = '{setting}' FORMAT JSONEachRow"
        )
        snapshot_name = f"{setting}"

        with Check("import"):
            with Then("I check the output is correct"):
                with values() as that:
                    assert that(
                        snapshot(
                            default_and_changed.output.strip(),
                            name=(snapshot_name),
                            id=self.context.snapshot_id,
                            mode=snapshot.CHECK | snapshot.UPDATE,
                        )
                    ), error()


@TestFeature
@Name("default values")
def feature(self):
    """Check default values."""
    if check_clickhouse_version(">=25.6")(self):
        self.context.snapshot_id = get_snapshot_id(check_clickhouse_version(">=25.6"))
    else:
        self.context.snapshot_id = get_snapshot_id()

    with Given("get all settings"):
        all_settings = get_all_settings()

    for setting in all_settings:
        Scenario(name=f"{setting}", test=check_default_value)(setting=setting)
