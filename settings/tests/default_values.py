from testflows.core import *
from testflows.asserts import snapshot, values, error
from helpers.common import (
    check_if_altinity_build,
    check_if_not_antalya_build,
    get_snapshot_id,
    check_clickhouse_version,
    check_if_antalya_build,
)


@TestStep()
def get_all_settings(self):
    """Get list of all settings from system.settings table."""
    return self.context.node.query(
        f"SELECT name FROM system.settings ORDER BY name"
    ).output.splitlines()


@TestScenario
def check_default_value(self, setting):
    """Check default value for the setting."""
    node = self.context.node

    with Given(f"check the default value for {setting}"):
        default_and_changed = node.query(
            f"SELECT default FROM system.settings WHERE name = '{setting}' FORMAT JSONEachRow"
        )
        snapshot_name = f"{setting}"

    with Then("compare with snapshot"):
        with values() as that:
            assert that(
                snapshot(
                    default_and_changed.output.strip(),
                    name=snapshot_name,
                    id=self.context.snapshot_id,
                    mode=snapshot.CHECK,
                )
            ), error()


@TestFeature
@Name("default values")
def feature(self):
    """Check default values in `system.settings` table."""
    versions = [
        ">=25.11",
        ">=25.10",
        ">=25.8",
        ">=25.7",
        ">=25.6",
        ">=25.5",
        ">=25.4",
        ">=25.3",
        ">=25.2",
        ">=25.1",
        ">=24.12",
        ">=24.8",
        ">=24.3",
        ">=23.8",
        ">=23.3",
        ">=22.8",
    ]

    for version in versions:
        if check_clickhouse_version(version)(self):
            self.context.snapshot_id = get_snapshot_id(clickhouse_version=version)
            break
    else:
        self.context.snapshot_id = get_snapshot_id()

    if check_if_antalya_build(self):
        self.context.snapshot_id += "_antalya"
    
    if check_clickhouse_version(">=25.8")(self) and check_if_altinity_build(self) and check_if_not_antalya_build(self):
        self.context.snapshot_id += "_altinity"

    with Given("get all settings from system.settings table"):
        all_settings = get_all_settings()

    with Pool() as pool:
        for setting in all_settings:
            Scenario(
                name=f"{setting}",
                test=check_default_value,
                parallel=True,
                executor=pool,
            )(setting=setting)
        join()
