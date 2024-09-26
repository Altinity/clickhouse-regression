from testflows.core import *
from testflows.asserts import error

from rbac.requirements import *

from helpers.common import getuid, get_settings_value, check_clickhouse_version

import rbac.tests.multiple_auth_methods.common as common
import rbac.tests.multiple_auth_methods.errors as errors


@TestScenario
@Name("omit WITH and auth type")
def omit_with_and_auth_type(self):
    """Check that it is possible to omit WITH keyword and auth type when creating user identified
    by some passwords. Default auth type should be used."""
    try:
        with Given("construct a valid query"):
            user_name = f"user_{getuid()}"
            query = f"CREATE USER {user_name} IDENTIFIED BY '123'"
            note(query)

        with Then("execute query"):
            common.execute_query(query=query)

        with And("login with specified password"):
            common.login(user_name=user_name, password="123")
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("create user with NO_PASSWORD upper case")
def no_password_upper_case(self):
    """Check that user can be created with no password using IDENTIFIED WITH NO_PASSWORD clause."""
    try:
        with Given("construct CREATE USER query with NO_PASSWORD auth method"):
            user_name = f"user_{getuid()}"
            query = f"CREATE USER {user_name} IDENTIFIED WITH NO_PASSWORD"
            note(query)

        with Then("execute query, expect success"):
            common.execute_query(query=query)

        with And("login without password"):
            common.login(user_name=user_name)
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("create user with no_password lower case")
def no_password_lower_case(self):
    """Check that user can be created with no password using IDENTIFIED WITH no_password clause."""
    try:
        with Given("construct CREATE USER query with no_password auth method"):
            user_name = f"user_{getuid()}"
            query = f"CREATE USER {user_name} IDENTIFIED WITH no_password"
            note(query)

        with Then("execute query, expect success"):
            common.execute_query(query=query)

        with And("login without password"):
            common.login(user_name=user_name)
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("create user not identified")
def create_user_not_identified(self):
    """Check that user can be created with no password by using NOT IDENTIFIED clause."""
    try:
        with Given(
            "construct CREATE USER query with no_password using NOT IDENTIFIED clause"
        ):
            user_name = f"user_{getuid()}"
            query = f"CREATE USER {user_name} NOT IDENTIFIED"
            note(query)

        with Then("execute query, expect success"):
            common.execute_query(query=query)

        with And("login without password"):
            common.login(user_name=user_name)
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
def check_default_value_of_setting(self):
    """Check that default value of `max_authentication_methods_per_user` is 100."""
    with Given("get default value of `max_authentication_methods_per_user`"):
        default_value = get_settings_value(
            "max_authentication_methods_per_user", table="system.server_settings"
        )

    with Then("check that default value is 100"):
        assert default_value == "100", f"expected 100, got {default_value}"


@TestScenario
def column_types_in_system_table(self):
    """Check the column types of the 'system.users' table."""

    node = self.context.node

    with By("check the type of auth_type column of system.users table"):
        typename = node.query(f"SELECT toTypeName(auth_type) FROM system.users").output
        if check_clickhouse_version("<24.9")(self):
            assert "Enum" in typename, error()
        else:
            assert "Array(Enum" in typename, error()

    with By("check the type of auth_params column of system.users table"):
        typename = node.query(
            f"SELECT toTypeName(auth_params) FROM system.users"
        ).output
        if check_clickhouse_version("<24.9")(self):
            assert "String" in typename, error()
        else:
            assert "Array(String)" in typename, error()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_AddIdentified_AddToNoPassword(
        "1.0"
    ),
)
def check_add_to_no_password(self):
    """Check that when adding authentication methods to a user identified with NO_PASSWORD,
    NO_PASSWORD will be replaced with the new methods."""

    user_name = f"user_{getuid()}"

    with Given("create user with NO_PASSWORD"):
        common.create_user(user_name=user_name, identified="NO_PASSWORD")

    with When("add authentication methods to t  he user"):
        identified = "plaintext_password BY '123', plaintext_password BY '456'"
        common.alter_identified(user_name=user_name, identified=identified)
        correct_passwords = ["123", "456"]

    with Then("check that user can login with new authentication methods"):
        for password in correct_passwords:
            common.login(user_name=user_name, password=password)

    with And("check that user can not login with no password"):
        common.login(
            user_name=user_name,
            password=None,
            expected=errors.wrong_password(user_name),
        )

    with And("check that NO_PASSWORD is not in SHOW CREATE USER"):
        create_user = self.context.node.query(f"SHOW CREATE USER {user_name}").output
        assert "no_password" not in create_user.lower(), error()

    with And(
        "check that changed authentication methods are reflected in system.users table"
    ):
        common.check_changes_reflected_in_system_table(
            user_name=user_name, correct_passwords=correct_passwords
        )


@TestScenario
def different_auth_methods_on_different_node(
    self, cluster="replicated_cluster", **kwargs
):
    """Check that on cluster statements with multiple authentication methods
    work correctly when user has different authentication methods on different nodes."""

    user_name = f"user_{getuid()}"
    with Given("create user on cluster with no_password authentication method"):
        common.create_user(
            user_name=user_name,
            identified="no_password",
            cluster=cluster,
        )

    with And("set different authentication methods on different nodes"):
        common.alter_identified(
            user_name=user_name,
            identified="sha256_password BY '1', plaintext_password BY '2'",
            node=self.context.node,
        )
        common.alter_identified(
            user_name=user_name,
            identified="plaintext_password BY '3', sha256_password BY '4'",
            node=self.context.node_2,
        )
        common.alter_identified(
            user_name=user_name,
            identified="plaintext_password BY '5', bcrypt_password BY '6'",
            node=self.context.node_3,
        )

    with When("reset authentication methods to new on cluster"):
        common.reset_auth_methods_to_new(user_name=user_name, cluster=cluster)

    with Then("check that user can not login with other passwords"):
        for correct, wrong, node in zip(
            [["2"], ["4"], ["6"]], [["1"], ["3"], ["5"]], self.context.nodes
        ):
            common.check_login_with_correct_and_wrong_passwords(
                user_name=user_name,
                correct_passwords=correct,
                wrong_passwords=wrong,
                node=node,
            )


@TestFeature
@Name("sanity check")
def feature(self):
    """Check syntax when creating or altering user with one or multiple auth methods."""
    with Pool(3) as executor:
        for scenario in loads(current_module(), Scenario):
            Scenario(run=scenario, flags=TE, parallel=True, executor=executor)
        join()
