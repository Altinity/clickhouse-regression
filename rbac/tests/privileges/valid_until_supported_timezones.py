from testflows.core import *
from testflows.asserts import error

from rbac.requirements import *
from helpers.common import *

supported_timezone_indicators = [
    "UTC",
    "GMT",
    "MSK",
    "MSD",
    "Z",
    "+00:00",
    "+01:00",
    "+02:00",
    "+03:00",
    "+04:00",
    "+05:00",
    "+05:30",
    "+05:45",
    "+06:00",
    "+06:30",
    "+07:00",
    "+08:00",
    "+09:00",
    "+09:30",
    "+10:00",
    "+11:00",
    "+12:00",
    "-01:00",
    "-02:00",
    "-03:00",
    "-03:30",
    "-04:00",
    "-05:00",
    "-06:00",
    "-07:00",
    "-08:00",
    "-09:00",
    "-09:30",
    "-10:00",
    "-11:00",
    "-12:00",
]


@TestCheck
def check_create_user_with_timezone(self, timezone):
    """Check that user can be created with VALID UNTIL using a supported timezone indicator."""
    node = self.context.node
    user_name = "user" + getuid()
    try:
        with Given(f"create user with timezone indicator {timezone}"):
            r = node.query(
                f"CREATE USER {user_name} VALID UNTIL '2024-10-29 16:00:00 {timezone}'",
                no_checks=True,
            )
            assert r.exitcode == 0, error()

        with And("check that user was created"):
            show_create_user = node.query(f"SHOW CREATE USER {user_name}").output
            assert user_name in show_create_user, error()

    finally:
        with Finally("drop the user"):
            node.query(f"DROP USER IF EXISTS {user_name}")


@TestScenario
def check_supported_timezones(self):
    """Check that VALID UNTIL accepts all timezone indicators supported by parseDateTimeBestEffort."""
    for timezone in supported_timezone_indicators:
        with Then(f"check timezone indicator {timezone}"):
            check_create_user_with_timezone(timezone=timezone)


@TestFeature
@Name("valid until timezones")
def feature(self, node="clickhouse1"):
    """Check VALID UNTIL clause with supported timezone indicators."""
    self.context.node = self.context.cluster.node(node)
    Scenario(run=check_supported_timezones)
