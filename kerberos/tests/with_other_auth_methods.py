from testflows.core import *
from kerberos.tests.common import *
from kerberos.requirements.requirements import *


@TestScenario
@Requirements(RQ_SRS_016_Kerberos_ValidUser_RBACConfiguredUser("1.0"))
def multiple_auth_methods(self):
    """ClickHouse SHALL support multiple authentication methods when one of them is Kerberos."""
    node = self.context.node
    user_name = "User" + getuid()

    try:
        with Given("kinit for client"):
            kinit_no_keytab(node=self.context.bash_tools, principal=user_name)

        with And("kinit for server"):
            create_server_principal(node=node)

        with When("create user with Kerberos and other authentication methods"):
            node.query(
                f"CREATE USER {user_name} IDENTIFIED WITH kerberos REALM 'EXAMPLE.COM', plaintext_password BY 'some_password'"
            )

        with When("authenticate with Kerberos"):
            r = self.context.bash_tools.command(test_select_query(node=node))
            assert r.output == f"{user_name}", error()

        with And("authenticating with password"):
            r = node.query(
                "SELECT currentUser()",
                settings=[("user", user_name), ("password", "some_password")],
            )
            assert r.output == f"{user_name}", error()

        with And("authenticating with wrong password"):
            r = node.query(
                "SELECT currentUser()",
                settings=[("user", user_name), ("password", "some_wrong_password")],
                exitcode=4,
                message=f"DB::Exception: {user_name}: Authentication failed",
            )

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER {user_name}")


@TestScenario
@Name("kerberos with valid until and other authentication methods")
def kerberos_with_valid_until_and_other_methods(self):
    """ClickHouse SHALL support Kerberos authentication with `VALID UNTIL` clause and other authentication methods."""
    node = self.context.node
    user_name = "User_" + getuid()

    try:
        with Given("get future and past date"):
            get_future_date = node.query("SELECT now() + INTERVAL 1 DAY")
            future_date = get_future_date.output
            get_past_date = node.query("SELECT now() - INTERVAL 1 DAY")
            past_date = define("past date", get_past_date.output)

        with And("kinit for client"):
            kinit_no_keytab(node=self.context.bash_tools, principal=user_name)

        with And("kinit for server"):
            create_server_principal(node=node)

        with When("create user with Kerberos and other authentication methods"):
            node.query(
                (
                    f"CREATE USER {user_name} IDENTIFIED WITH kerberos REALM 'EXAMPLE.COM' "
                    f"VALID UNTIL '{past_date}', plaintext_password BY 'some_password' VALID UNTIL '{future_date}'"
                )
            )

        with Then("authenticate with Kerberos"):
            r = self.context.bash_tools.command(test_select_query(node=node))
            assert (
                f"DB::Exception: {user_name}: Authentication failed: "
                "password is incorrect, or there is no user with such name."
            ) in r.output, error()

        with And("authenticating with password"):
            r = node.query(
                "SELECT currentUser()",
                settings=[("user", user_name), ("password", "some_password")],
            )
            assert r.output == f"{user_name}", error()

        with And("authenticating with wrong password"):
            r = node.query(
                "SELECT currentUser()",
                settings=[("user", user_name), ("password", "some_wrong_password")],
                exitcode=4,
                message=f"DB::Exception: {user_name}: Authentication failed",
            )

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER {user_name}")


@TestScenario
@Name("add kerberos auth to existing user")
def add_kerberos_auth(self):
    """ClickHouse SHALL support adding Kerberos authentication to an existing user."""
    node = self.context.node
    user_name = "User_" + getuid()

    try:
        with Given("kinit for client"):
            kinit_no_keytab(node=self.context.bash_tools, principal=user_name)

        with And("kinit for server"):
            create_server_principal(node=node)

        with When("create user with other authentication methods"):
            node.query(f"CREATE USER {user_name} IDENTIFIED BY 'some_password'")

        with And("add Kerberos authentication"):
            node.query(
                f"ALTER USER {user_name} ADD IDENTIFIED WITH kerberos REALM 'EXAMPLE.COM'"
            )

        with Then("authenticate with Kerberos"):
            r = self.context.bash_tools.command(test_select_query(node=node))
            assert r.output == f"{user_name}", error()

        with And("authenticating with password"):
            r = node.query(
                "SELECT currentUser()",
                settings=[("user", user_name), ("password", "some_password")],
            )
            assert r.output == f"{user_name}", error()

        with And("authenticating with wrong password"):
            r = node.query(
                "SELECT currentUser()",
                settings=[("user", user_name), ("password", "some_wrong_password")],
                exitcode=4,
                message=f"DB::Exception: {user_name}: Authentication failed",
            )

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER {user_name}")


@TestScenario
@Name("kerberos with valid until")
def kerberos_with_valid_until(self):
    """Check that ClickHouse supports Kerberos authentication with `VALID UNTIL` clause."""
    node = self.context.node
    user_name = "User_" + getuid()

    try:
        with Given("get future and past date"):
            get_future_date = node.query("SELECT now() + INTERVAL 1 DAY")
            future_date = get_future_date.output
            get_past_date = node.query("SELECT now() - INTERVAL 1 DAY")
            past_date = define("past date", get_past_date.output)

        with And("kinit for client"):
            kinit_no_keytab(node=self.context.bash_tools, principal=user_name)

        with And("kinit for server"):
            create_server_principal(node=node)

        with When("create user with Kerberos and `VALID UNTIL` clause"):
            node.query(
                f"CREATE USER {user_name} IDENTIFIED WITH kerberos REALM 'EXAMPLE.COM' VALID UNTIL '{future_date}'"
            )

        with Then("authenticate with Kerberos"):
            r = self.context.bash_tools.command(test_select_query(node=node))
            assert r.output == f"{user_name}", error()

        with And("alter expiration date to the past"):
            node.query(f"ALTER USER {user_name} VALID UNTIL '{past_date}'")

        with And("authenticate with Kerberos"):
            r = self.context.bash_tools.command(test_select_query(node=node))
            assert (
                f"DB::Exception: {user_name}: Authentication failed"
            ) in r.output, error()

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER {user_name}")


@TestScenario
@Name("revoke kerberos auth from existing user")
def revoke_kerberos_auth(self):
    """ClickHouse SHALL support revoking Kerberos authentication from an existing user."""
    node = self.context.node
    user_name = "User_" + getuid()

    try:
        with Given("kinit for client"):
            kinit_no_keytab(node=self.context.bash_tools, principal=user_name)

        with And("kinit for server"):
            create_server_principal(node=node)

        with When("create user with Kerberos authentication"):
            node.query(
                f"CREATE USER {user_name} IDENTIFIED WITH kerberos REALM 'EXAMPLE.COM', plaintext_password BY 'foo1', BY 'foo2'"
            )

        with And("revoke Kerberos authentication"):
            node.query(f"ALTER USER {user_name} RESET AUTHENTICATION METHODS TO NEW")

        with Then("authenticate with Kerberos"):
            r = self.context.bash_tools.command(test_select_query(node=node))
            assert (
                f"DB::Exception: {user_name}: Authentication failed"
            ) in r.output, error()

        with And("authenticating with password"):
            r = node.query(
                "SELECT currentUser()",
                settings=[("user", user_name), ("password", "foo2")],
            )
            assert r.output == f"{user_name}", error()

        with And("authenticating with revoked password"):
            r = node.query(
                "SELECT currentUser()",
                settings=[("user", user_name), ("password", "foo1")],
                exitcode=4,
                message=f"DB::Exception: {user_name}: Authentication failed",
            )

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER {user_name}")


@TestFeature
@Name("Multiple authentication methods with Kerberos")
def feature(self):
    """Test multiple authentication methods when one of them is Kerberos."""
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.krb_server = self.context.cluster.node("kerberos")
    self.context.bash_tools = self.context.cluster.node("bash-tools")

    for scenario in loads(current_module(), Scenario):
        Scenario(test=scenario, flags=TE)()
