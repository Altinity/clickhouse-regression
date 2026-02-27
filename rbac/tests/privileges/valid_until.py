from testflows.core import *
from testflows.asserts import error

from helpers.common import check_if_altinity_build, getuid, check_clickhouse_version

from rbac.requirements import *
import rbac.tests.multiple_auth_methods.common as common
import rbac.tests.multiple_auth_methods.errors as errors


@TestCheck
def test_non_expired_password_login(self, auth_method, password):
    """Check that user can be created with one authentication method and
    expiration date. Check that user can login with a non-expired password."""
    user_name = f"user_{getuid()}"

    try:
        with Given("get some future date"):
            get_future_date = self.context.node.query("SELECT now() + INTERVAL 1 DAY")
            future_date = get_future_date.output

        with And("create user with one auth method and expiration date"):
            auth_method_str = auth_method + f" VALID UNTIL '{future_date}'"
            common.create_user(
                user_name=user_name,
                identified=auth_method_str,
            )

        with Then("check that user can login with non-expired password"):
            common.login(
                user_name=user_name,
                password=password,
            )

        with Then("check that changes reflected in SHOW CREATE USER"):
            show_create_user = self.context.node.query(
                f"SHOW CREATE USER {user_name}"
            ).output
            auth_method = auth_method.split(" ")[0].replace("hash", "password")
            assert f"VALID UNTIL \\'{future_date}\\'" in show_create_user, error()

            if auth_method == "no_password" and not (
                check_clickhouse_version(">=24.9")(self)
                or (check_clickhouse_version("~24.8")(self) and check_if_altinity_build(self))
            ):
                assert auth_method not in show_create_user, error()
            else:
                assert auth_method in show_create_user, error()

    finally:
        with Finally("drop user"):
            self.context.node.query(f"DROP USER IF EXISTS {user_name}")


@TestCheck
def test_expired_password_rejection(self, auth_method, password):
    """Check that user can be created with one authentication method and expiration
    date. Ensure that the user can not login with an expired password."""
    user_name = f"user_{getuid()}"

    try:
        with Given("create user with one auth method and expiration date"):
            auth_method_str = auth_method + " VALID UNTIL '2023-12-12'"
            common.create_user(
                user_name=user_name,
                identified=auth_method_str,
            )

        with Then("check that user cannot login with expired password"):
            common.login(
                user_name=user_name,
                password=password,
                expected=errors.wrong_password(user_name),
            )

        with And("check that changes reflected in SHOW CREATE USER"):
            show_create_user = self.context.node.query(
                f"SHOW CREATE USER {user_name}"
            ).output
            auth_method = auth_method.split(" ")[0].replace("hash", "password")
            assert "VALID UNTIL \\'2023-12-12 00:00:00\\'" in show_create_user, error()

            if auth_method == "no_password" and not (
                check_clickhouse_version(">=24.9")(self)
                or (check_clickhouse_version("~24.8")(self) and check_if_altinity_build(self))
            ):
                assert auth_method not in show_create_user, error()
            else:
                assert auth_method in show_create_user, error()

    finally:
        with Finally("drop user"):
            self.context.node.query(f"DROP USER IF EXISTS {user_name}")


@TestScenario
def check_old_behavior(self):
    """Check that user can be created with one authentication method and
    expiration date. Ensure that the user can login with a non-expired
    password and cannot login with an expired password."""

    auth_methods = common.authentication_methods_with_passwords

    for auth_method, password in auth_methods.items():
        check_name = auth_method.split(" ")[0]
        Check(f"expired {check_name}", test=test_expired_password_rejection)(
            auth_method=auth_method, password=password
        )
        Check(f"non-expired {check_name}", test=test_non_expired_password_login)(
            auth_method=auth_method, password=password
        )


@TestScenario
def valid_until_invalid_date(self):
    """Check that Clickhouse throws an error if user is created with an invalid date
    in the `VALID UNTIL` clause."""
    user_name = f"user_{getuid()}"

    with Given("query with invalid date"):
        query = f"CREATE USER {user_name} IDENTIFIED BY '123' VALID UNTIL '2025-13-12'"
        note(query)

    with Then("check that Clickhouse throws an error"):
        exitcode, message = errors.unexpected_date()()
        self.context.node.query(query, exitcode=exitcode, message=message)

    with And("check that user was not created"):
        exitcode, message = (
            192,
            f"DB::Exception: There is no user `{user_name}` in user directories.",
        )

        if check_clickhouse_version(">=25.6")(self):
            message = (
                f"DB::Exception: There is no user `{user_name}` in `user directories`"
            )

        self.context.node.query(
            f"SHOW CREATE USER {user_name}", exitcode=exitcode, message=message
        )


@TestScenario
def invalid_string_in_valid_until_clause(self):
    """Check that Clickhouse throws an error if user is created with an invalid string
    in the `VALID UNTIL` clause."""
    user_name = f"user_{getuid()}"

    invalid_strings = [
        "foo",
        "bar",
        "baz",
        "1a",
        "0",
        "1,0",
        "nan",
        "\0",
        "10000",
        "090",
        ".",
        ",",
        "-1",
        "0-0",
        "32",
        "#",
        "()",
    ]

    for string in invalid_strings:
        with Given("check that Clickhouse throws an error"):
            query = (
                f"CREATE USER {user_name} IDENTIFIED BY '123' VALID UNTIL '{string}'"
            )
            exitcode, message = errors.unexpected_symbol()()
            self.context.node.query(query, exitcode=exitcode, message=message)

        with Then("check that user was not created"):
            exitcode, message = (
                192,
                f"DB::Exception: There is no user `{user_name}` in user directories.",
            )

            if check_clickhouse_version(">=25.6")(self):
                message = f"DB::Exception: There is no user `{user_name}` in `user directories`"

            self.context.node.query(
                f"SHOW CREATE USER {user_name}", exitcode=exitcode, message=message
            )


@TestScenario
def valid_string_in_valid_until_clause(self):
    """Check that user can be created with a valid string in the `VALID UNTIL` clause."""
    user_name = f"user_{getuid()}"

    valid_strings = [
        "1",
        "31",
        "2067",
        "9999+12",
        "12,1,1,1,1,1,1,1,1",
        "2025-5-12",
        "11.1",
    ]

    for string in valid_strings:
        with Given("create user with a valid string in VALID UNTIL clause"):
            query = (
                f"CREATE USER {user_name} IDENTIFIED BY '123' VALID UNTIL '{string}'"
            )
            self.context.node.query(query)

        with Then("check that user was created"):
            show_create_user = self.context.node.query(
                f"SHOW CREATE USER {user_name}"
            ).output
            assert (
                f"CREATE USER {user_name} IDENTIFIED WITH sha256_password VALID UNTIL"
                in show_create_user
            ), error()

        with Finally("drop user"):
            self.context.node.query(f"DROP USER IF EXISTS {user_name}")


@TestScenario
def valid_until_with_not_identified(self):
    """Check that user can be created with the `NOT IDENTIFIED` clause and an expiration date."""
    user_name = f"user_{getuid()}"

    try:
        with Given("get some future date"):
            get_future_date = self.context.node.query("SELECT now() + INTERVAL 1 DAY")
            future_date = get_future_date.output

        with And("create user with the `NOT IDENTIFIED` clause and an expiration date"):
            query = (
                f"CREATE USER {user_name} NOT IDENTIFIED VALID UNTIL '{future_date}'"
            )
            self.context.node.query(query)

        with Then("check that user can login without a password"):
            common.login(user_name=user_name, password="")

        with And("check that user can login with a random password"):
            common.login(user_name=user_name, password="123")

        with And("check that changes reflected in SHOW CREATE USER"):
            show_create_user = self.context.node.query(
                f"SHOW CREATE USER {user_name}"
            ).output
            if check_clickhouse_version(">=24.9")(self) or (
                check_clickhouse_version("~24.8")(self) and check_if_altinity_build(self)
            ):
                assert (
                    show_create_user
                    == f"CREATE USER {user_name} IDENTIFIED WITH no_password VALID UNTIL \\'{future_date}\\'"
                ), error()
            else:
                assert (
                    show_create_user
                    == f"CREATE USER {user_name} VALID UNTIL \\'{future_date}\\'"
                ), error()

    finally:
        with Finally("drop user"):
            self.context.node.query(f"DROP USER IF EXISTS {user_name}")


@TestScenario
def check_default_expiration_time(self):
    """Check that user can be created without expiration date."""
    user_name = f"user_{getuid()}"

    try:
        with Given("create user without `VALID UNTIL` clause"):
            query = f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password BY 'some_password'"
            self.context.node.query(query)

        with Then("check that user was created"):
            show_create_user = self.context.node.query(
                f"SHOW CREATE USER {user_name}"
            ).output
            assert (
                show_create_user
                == f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password"
            ), error()

        with And("check that user can login"):
            common.login(user_name=user_name, password="some_password")

    finally:
        with Finally("drop user"):
            self.context.node.query(f"DROP USER IF EXISTS {user_name}")


@TestScenario
def on_cluster(self):
    """Check that user can be created with an expiration date on a cluster."""
    node_1 = self.context.node
    node_2 = self.context.node_2
    node_3 = self.context.node_3
    nodes = [node_1, node_2, node_3]

    user_name = f"user_{getuid()}"

    try:
        with Given("defining future date"):
            get_future_date = node_1.query("SELECT now() + INTERVAL 1 DAY")
            future_date = define("future date", get_future_date.output)

        with And("create user with expiration date on a cluster"):
            query = (
                f"CREATE USER {user_name} IDENTIFIED BY '123' "
                f"VALID UNTIL '{future_date}' ON CLUSTER replicated_cluster"
            )
            node_1.query(query)

        with And("check that user can login on all nodes"):
            for node in nodes:
                common.login(user_name=user_name, password="123", node=node)

        with When("change expiration date on the second node to the past"):
            get_past_date = node_2.query("SELECT now() - INTERVAL 1 DAY")
            past_date = define("past date", get_past_date.output)
            node_2.query(f"ALTER USER {user_name} VALID UNTIL '{past_date}'")

        with Then("check that user cannot login on the second node"):
            common.login(
                user_name=user_name,
                password="123",
                node=node_2,
                expected=errors.wrong_password(user_name),
            )

        with And("check that user can login on the first and third nodes"):
            common.login(user_name=user_name, password="123", node=node_1)
            common.login(user_name=user_name, password="123", node=node_3)

        with And("change expiration date on cluster to the past"):
            node_1.query(
                f"ALTER USER {user_name} VALID UNTIL '{past_date}' ON CLUSTER replicated_cluster"
            )

        with Then("check that user cannot login on all nodes"):
            for node in nodes:
                common.login(
                    user_name=user_name,
                    password="123",
                    node=node,
                    expected=errors.wrong_password(user_name),
                )

    finally:
        with Finally("drop user"):
            self.context.node.query(
                f"DROP USER IF EXISTS {user_name} ON CLUSTER replicated_cluster"
            )


@TestScenario
def create_user_with_expiration_date_on_cluster(self):
    """Check that user can be created with an expiration date on a cluster."""
    user_name = f"user_{getuid()}"

    with Given("defining future date"):
        get_future_date = self.context.node.query("SELECT now() + INTERVAL 1 DAY")
        future_date = define("future date", get_future_date.output)

    with And("create user with an expiration date on a cluster"):
        query = f"CREATE USER {user_name} VALID UNTIL '{future_date}' ON CLUSTER replicated_cluster"
        self.context.node.query(query)

    with Then("check that user can login on all nodes"):
        for node in [self.context.node, self.context.node_2, self.context.node_3]:
            common.login(user_name=user_name, password="123", node=node)


@TestFeature
@Name("valid until")
def feature(self, node="clickhouse1"):
    """Check VALID UNTIL clause."""
    self.context.node = self.context.cluster.node(node)
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")

    with Pool(3) as executor:
        for scenario in loads(current_module(), Scenario):
            Scenario(run=scenario, flags=TE, parallel=True, executor=executor)
        join()
