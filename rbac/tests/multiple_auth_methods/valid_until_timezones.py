from testflows.core import *

from rbac.requirements import *

from helpers.common import getuid
from helpers.cluster import *

import rbac.tests.multiple_auth_methods.common as common
import rbac.tests.multiple_auth_methods.errors as errors


@TestScenario
def session_timezone(self):
    """Check that if password is valid in one timezone, it is valid in another timezone."""
    node = self.context.node
    user_name = f"user_{getuid()}"

    try:
        with Given(
            "set expiration time to 1 hour from now in America/Aruba(GMT+4) timezone"
        ):
            get_future_date = node.query(
                (
                    "SET session_timezone='America/Aruba';"
                    "SELECT now() + INTERVAL 1 HOUR FORMAT TabSeparated;"
                )
            )
            future_date = define("future date", get_future_date.output)

        with And(
            "create user with password and with expiration date in America/Aruba(GMT+4) timezone"
        ):
            query = (
                "SET session_timezone='America/Aruba';"
                f"CREATE USER {user_name} IDENTIFIED BY '123' VALID UNTIL '{future_date}';"
            )
            node.query(query)

        with And("check that user can login with this password in another timezones"):
            timezones = [
                "Asia/Novosibirsk",
                "UTC",
                "Etc/GMT-4",
                "Etc/Greenwich",
                "Etc/GMT+4",
                "Etc/GMT0",
                "Etc/GMT+12",
                "Etc/GMT-12",
            ]
            for timezone in timezones:
                with By(f"login in {timezone} timezone"):
                    common.login(
                        node=node,
                        user_name=user_name,
                        password="123",
                        session_timezone=timezone,
                    )

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER IF EXISTS {user_name}")


@TestScenario
def server_timezone(self):
    """Check that user can login only if absolute value of the password's expiration
    date is less than server timezone."""

    node = self.context.node
    user_name = f"user_{getuid()}"

    with Given("set timezone to GMT"):
        common.change_server_settings(setting="timezone", value="GMT")
        common.check_timezone(timezone="GMT")

    with And("set expiration time to 6 hours from now"):
        get_future_date = node.query(
            "SELECT now() + INTERVAL 6 HOUR FORMAT TabSeparated"
        )
        future_date = define("future date", get_future_date.output)

    with And("create user with password and with expiration date"):
        common.create_user(
            node=node,
            user_name=user_name,
            identified_by="123",
            valid_until=future_date,
        )
        node.query(f"SHOW CREATE USER {user_name} FORMAT TabSeparated")
        node.query(f"SELECT now() FORMAT TabSeparated")

    with Then("check that user can login with this password in GMT timezone"):
        common.login(node=node, user_name=user_name, password="123")

    with And("set timezone to America/Aruba(GMT+4)"):
        common.change_server_settings(setting="timezone", value="America/Aruba")
        common.check_timezone(timezone="America/Aruba")

    with And(
        "check that user can login with this password in America/Aruba(GMT+4) timezone"
    ):
        common.login(node=node, user_name=user_name, password="123")

    with And("set timezone to Asia/Novosibirsk(GMT-7)"):
        common.change_server_settings(setting="timezone", value="Asia/Novosibirsk")
        common.check_timezone(timezone="Asia/Novosibirsk")

    with And(
        "check that user can not login with this password in Asia/Novosibirsk(GMT-7) timezone"
    ):
        common.login(
            node=node,
            user_name=user_name,
            password="123",
            expected=errors.wrong_password(user_name=user_name),
        )


@TestFeature
@Name("valid until")
def feature(self):
    """Check VALID UNTIL clause with multiple authentication methods."""

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
