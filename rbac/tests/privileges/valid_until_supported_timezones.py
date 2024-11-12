from testflows.core import *
from testflows.asserts import error

from example.requirements import *
from helpers.common import *

supported_timezones = [
    "Mariehamn",
    "GMT-3",
    "GMT-8",
    "GMT0",
    "Jan_Mayen",
    "GMT-9",
    "Monticello",
    "GMT",
    "GMT-7",
    "GMT-14",
    "GMT-4",
    "Novokuznetsk",
    "GMT+6",
    "Montserrat",
    "GMT+5",
    "Monaco",
    "Moncton",
    "Martinique",
    "GMT+1",
    "GMT+11",
    "GMT+8",
    "GMT-10",
    "GMT-5",
    "Marigot",
    "Thunder_Bay",
    "GMT-13",
    "GMT-2",
    "Monrovia",
    "GMT+0",
    "GMT+4",
    "GMT+12",
    "Novosibirsk",
    "Marengo",
    "Mayotte",
    "GMT-6",
    "GMT+9",
    "Montevideo",
    "GMT+3",
    "GMT+2",
    "GMT+7",
    "GMT-1",
    "Montreal",
    "GMT-11",
    "Thule",
    "Monterrey",
    "Juneau",
    "GMT-12",
    "GMT+10",
    "Marquesas",
    "GMT-0",
    "UTC",
]


@TestStep(Given)
def get_timezones(self, node=None):
    """Get all timezones from ClickHouse system table."""
    if node is None:
        node = self.context.node

    timezones = (
        node.query("Select * from system.time_zones FORMAT TabSeparated")
        .output.strip()
        .split()
    )
    return timezones


@TestCheck
def check_create_user_with_timezone(self, timezone):
    """Check that user can be created with specified timezone."""
    node = self.context.node
    user_name = "user" + getuid()
    try:
        with Given(f"create user with timezone {timezone}"):
            r = node.query(
                f"CREATE USER {user_name} VALID UNTIL '2024-10-29 16:00:00 {timezone}'",
                no_checks=True,
            )
            if timezone in supported_timezones:
                assert r.exitcode == 0, error()
            else:
                if r.exitcode != 0:
                    xfail("https://github.com/ClickHouse/ClickHouse/issues/71215")
    finally:
        with Finally("drop the user if it was created"):
            node.query(f"DROP USER IF EXISTS {user_name}")


@TestScenario
def check_supported_timezones(self):
    """Check that ClickHouse returns 1 when user executes `SELECT 1` query."""
    node = self.context.node
    full_timezones = []

    with Given("get all timezones"):
        timezones = get_timezones(node=node)

    with When(
        "create list of all timezones including sub-timezones (e.g. Europe/Paris -> [Europe, Paris, Europe/Paris])"
    ):
        for timezone in timezones:
            full_timezones.append(timezone)
            new_timezone = timezone.split("/")
            for tz in new_timezone:
                full_timezones.append(tz)
        full_timezones = list(set(full_timezones))

    for timezone in full_timezones:
        with Then(f"check that user can be created with timezone {timezone}"):
            check_create_user_with_timezone(timezone=timezone)


@TestFeature
@Name("valid until timezones")
def feature(self, node="clickhouse1"):
    """Check VALID UNTIL clause."""
    self.context.node = self.context.cluster.node(node)
    Scenario(run=check_supported_timezones)
