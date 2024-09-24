from testflows.core import *

from helpers.common import getuid

import rbac.tests.multiple_auth_methods.common as common
import rbac.tests.multiple_auth_methods.errors as errors


@TestScenario
@Name("create user without WITH after IDENTIFIED")
def create_user_identified_without_with_syntax_error(self):
    """Check that the WITH keyword can not be omitted when creating a user with an identification
    method and a specified authentication type."""
    with Given("construct CREATE USER query without WITH after IDENTIFIED"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED plaintext_password BY '123'"
        note(query)

    with Then("expect syntax error"):
        common.execute_query(query=query, expected=errors.syntax_error)

    with And("check that user was not created"):
        common.login(
            user_name=user_name,
            password="123",
            expected=errors.no_user_with_such_name(user_name),
        )


@TestScenario
@Name("alter user without WITH after IDENTIFIED")
def alter_user_identified_without_with_syntax_error(self):
    """Check that the WITH keyword can not be omitted after (ADD) IDENTIFIED
    when altering user's authentication methods."""
    try:
        with Given("create user with a plaintext_password authentication method"):
            user_name = f"user_{getuid()}"
            query = (
                f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password BY '123';"
            )
            common.execute_query(query=query)

        with And("construct ALTER USER query without WITH after IDENTIFIED"):
            query = f"ALTER USER {user_name} IDENTIFIED plaintext_password BY '456'"
            note(query)

        with Then("expect syntax error"):
            common.execute_query(query=query, expected=errors.syntax_error)

        with And("construct ALTER USER query without WITH after ADD IDENTIFIED"):
            query = f"ALTER USER {user_name} ADD IDENTIFIED plaintext_password BY '789'"
            note(query)

        with And("expect to see syntax error"):
            common.execute_query(query=query, expected=errors.syntax_error)

        with And("check that user can only login with initial password"):
            common.login(
                user_name=user_name,
                password="123",
            )
            common.login(
                user_name=user_name,
                password="456",
                expected=errors.no_user_with_such_name(user_name),
            )
            common.login(
                user_name=user_name,
                password="789",
                expected=errors.no_user_with_such_name(user_name),
            )
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("create user without auth type and password after IDENTIFIED WITH")
def create_user_without_auth_type_and_password_syntax_error(self):
    """Check that it is mandatory to specify both the authentication type and password
    after the IDENTIFIED WITH clause when creating a user."""
    with Given(
        "construct CREATE USER query without auth type and password after IDENTIFIED WITH"
    ):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED WITH"
        note(query)

    with Then("expect syntax error"):
        common.execute_query(query=query, expected=errors.syntax_error)

    with And("check that user was not created"):
        common.login(
            user_name=user_name,
            expected=errors.no_user_with_such_name(user_name),
        )


@TestScenario
@Name("alter user without auth type and password after IDENTIFIED WITH")
def alter_user_without_auth_type_and_password_syntax_error(self):
    """Check that it is mandatory to specify both the authentication type and password
    after the IDENTIFIED WITH clause when altering user's authentication methods."""
    try:
        with Given("create user with a plaintext_password authentication method"):
            user_name = f"user_{getuid()}"
            query = (
                f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password BY '123';"
            )
            common.execute_query(query=query)

        with And(
            "construct ALTER USER query without auth type and password after IDENTIFIED WITH clause"
        ):
            query = f"ALTER USER {user_name} IDENTIFIED WITH"
            note(query)

        with Then("expect syntax error"):
            common.execute_query(query=query, expected=errors.syntax_error)

        with And(
            "construct ALTER USER query without auth type and password after ADD IDENTIFIED WITH clause"
        ):
            query = f"ALTER USER {user_name} ADD IDENTIFIED WITH"
            note(query)

        with And("expect syntax error"):
            common.execute_query(query=query, expected=errors.syntax_error)

        with And("check that user can login only with initial password"):
            common.login(
                user_name=user_name,
                password="123",
            )
            common.login(
                user_name=user_name,
                expected=errors.no_user_with_such_name(user_name),
            )
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("create user without password after IDENTIFIED BY")
def create_without_password_syntax_error(self):
    """Check that it is mandatory to specify a password after the IDENTIFIED BY clause
    when creating user."""
    with Given(
        "construct CREATE USER query without password after IDENTIFIED BY clause"
    ):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED BY"
        note(query)

    with Then("expect syntax error"):
        common.execute_query(query=query, expected=errors.syntax_error)

    with And("check that user was not created"):
        common.login(
            user_name=user_name,
            expected=errors.no_user_with_such_name(user_name),
        )


@TestScenario
@Name("create user without IDENTIFIED and with auth methods")
def create_user_without_identified_and_with_auth_methods_syntax_error(self):
    """Check that the IDENTIFIED keyword can not be omitted when creating a user with
    an identification method."""
    with Given("construct CREATE USER query without IDENTIFIED keyword"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} WITH plaintext_password BY '123', plaintext_password BY '456'"
        note(query)

    with Then("expect syntax error"):
        common.execute_query(query=query, expected=errors.syntax_error)

    with And("check that user was not created"):
        common.login(
            user_name=user_name,
            password="123",
            expected=errors.no_user_with_such_name(user_name),
        )


@TestScenario
@Name("alter user without IDENTIFIED and with password")
def alter_user_without_identified_syntax_error(self):
    """Check that the IDENTIFIED keyword can not be omitted when altering
    user's authentication methods."""
    try:
        with Given("create user with a plaintext_password authentication method"):
            user_name = f"user_{getuid()}"
            query = (
                f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password BY '123';"
            )
            common.execute_query(query=query)

        with And("construct ALTER USER query without IDENTIFIED keyword"):
            query = f"ALTER USER {user_name} WITH plaintext_password BY '456'"
            note(query)

        with Then("expect syntax error"):
            common.execute_query(query=query, expected=errors.syntax_error)

        with And("construct ALTER USER query without IDENTIFIED keyword after ADD"):
            query = f"ALTER USER {user_name} ADD plaintext_password BY '789'"
            note(query)

        with And("expect syntax error"):
            common.execute_query(query=query, expected=errors.syntax_error)

        with And("check that user can login only with initial password"):
            common.login(
                user_name=user_name,
                password="123",
            )
            common.login(
                user_name=user_name,
                password="456",
                expected=errors.no_user_with_such_name(user_name),
            )
            common.login(
                user_name=user_name,
                password="789",
                expected=errors.no_user_with_such_name(user_name),
            )
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("create user without auth type and with password")
def create_user_without_auth_type_and_with_password_syntax_error(self):
    """Check that the authentication type cannot be omitted when creating a user using
    the IDENTIFIED WITH clause and specifying the password using the BY clause."""
    with Given("construct query with syntax error"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED WITH BY '123'"
        note(query)

    with Then("expect syntax error"):
        common.execute_query(query=query, expected=errors.syntax_error)

    with And("check that user was not created"):
        common.login(
            user_name=user_name,
            password="123",
            expected=errors.no_user_with_such_name(user_name),
        )


@TestScenario
@Name("identified by no_password")
def identified_by_no_password_syntax_error(self):
    """Check that IDENTIFIED BY no_password is not valid statement."""
    with Given("construct query with syntax error"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED BY no_password"
        note(query)

    with Then("expect syntax error"):
        common.execute_query(query=query, expected=errors.syntax_error)

    with And("check that user was not created"):
        common.login(
            user_name=user_name,
            expected=errors.no_user_with_such_name(user_name),
        )


@TestScenario
@Name("password without quotes")
def password_without_quotes_syntax_error(self):
    """Check that password should be in quotes when creating user with authentication method."""
    with Given("construct a query with a password that is not in quotes"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password BY some_password"
        note(query)

    with Then("expect syntax error"):
        common.execute_query(query=query, expected=errors.syntax_error)

    with And("check that user was not created"):
        common.login(
            user_name=user_name,
            expected=errors.no_user_with_such_name(user_name),
        )


@TestScenario
@Name("trailing comma after single auth method in CREATE USER")
def create_user_trailing_comma_single_auth_method_syntax_error(self):
    """Check that a trailing comma after a single auth method in CREATE USER results in a syntax error."""
    try:
        with Given("CREATE USER with trailing comma after a single auth method"):
            user_name = f"user_{getuid()}"
            common.execute_query(
                query=f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password by '1',",
                expected=errors.syntax_error,
            )

        with Then("check that user was not created"):
            common.login(
                user_name=user_name,
                expected=errors.no_user_with_such_name(user_name),
            )
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("trailing comma after multiple auth methods in CREATE USER")
def create_user_trailing_comma_multiple_auth_methods_syntax_error(self):
    """Check that a trailing comma after multiple auth methods in CREATE USER results in a syntax error."""
    try:
        with Given("CREATE USER with trailing comma after a single auth method"):
            user_name = f"user_{getuid()}"
            common.execute_query(
                query=f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password by '1', plaintext_password by '2',",
                expected=errors.syntax_error,
            )

        with Then("check that user was not created"):
            common.login(
                user_name=user_name,
                expected=errors.no_user_with_such_name(user_name),
            )
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("alter user with trailing comma")
def alter_user_trailing_comma_syntax_error(self):
    """Check that trailing comma after auth method(s) is not allowed when altering user's authentication methods."""
    try:
        user_name = f"user_{getuid()}"
        with Given("create user with correct syntax"):
            common.execute_query(
                query=f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password by '123'"
            )

        with And(
            "ALTER USER ADD IDENTIFIED WITH with trailing comma after single auth method"
        ):
            query = (
                f"ALTER USER {user_name} ADD IDENTIFIED WITH plaintext_password by '1',"
            )
            common.execute_query(query=query, expected=errors.syntax_error)

        with And(
            "ALTER USER ADD IDENTIFIED WITH with trailing comma after multiple auth methods"
        ):
            query = f"ALTER USER {user_name} ADD IDENTIFIED WITH plaintext_password by '2', plaintext_password by '3',"
            common.execute_query(query=query, expected=errors.syntax_error)

        with And(
            "ALTER USER ADD IDENTIFIED BY with trailing comma after single auth method"
        ):
            query = f"ALTER USER {user_name} ADD IDENTIFIED BY '4',"
            common.execute_query(query=query, expected=errors.syntax_error)

        with And(
            "ALTER USER ADD IDENTIFIED BY with trailing comma after multiple auth methods"
        ):
            query = f"ALTER USER {user_name} ADD IDENTIFIED BY '5', BY '6',"
            common.execute_query(query=query, expected=errors.syntax_error)

        with Then(
            "ALTER USER IDENTIFIED WITH with trailing comma after single auth method"
        ):
            query = f"ALTER USER {user_name} IDENTIFIED WITH plaintext_password by '7',"
            common.execute_query(query=query, expected=errors.syntax_error)

        with And(
            "ALTER USER IDENTIFIED WITH with trailing comma after multiple auth methods"
        ):
            query = f"ALTER USER {user_name} IDENTIFIED WITH plaintext_password by '8', plaintext_password by '9',"
            common.execute_query(query=query, expected=errors.syntax_error)

        with And(
            "ALTER USER IDENTIFIED BY with trailing comma after single auth method"
        ):
            query = f"ALTER USER {user_name} IDENTIFIED BY '10',"
            common.execute_query(query=query, expected=errors.syntax_error)

        with And(
            "ALTER USER IDENTIFIED BY with trailing comma after multiple auth methods"
        ):
            query = f"ALTER USER {user_name} IDENTIFIED BY '11', BY '12',"
            common.execute_query(query=query, expected=errors.syntax_error)

        with Then("check that user can login with only initial password"):
            common.login(
                user_name=user_name,
                password="123",
            )
            for password in [str(i) for i in range(1, 13)]:
                common.login(
                    user_name=user_name,
                    password=password,
                    expected=errors.wrong_password(user_name),
                )
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("invalid query ALTER USER ADD NOT IDENTIFIED")
def alter_user_add_not_identified_syntax_error(self):
    """Check that ALTER USER ADD NOT IDENTIFIED is invalid query."""
    try:
        with Given("create user with no password"):
            user_name = f"user_{getuid()}"
            common.execute_query(query=f"CREATE USER {user_name}")

        with When("construct ALTER USER ADD NOT IDENTIFIED query"):
            query = f"ALTER USER {user_name} ADD NOT IDENTIFIED"
            note(query)

        with Then("expect syntax error"):
            common.execute_query(query=query, expected=errors.syntax_error)

        with And("check that user can login without password"):
            common.login(user_name=user_name)
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("invalid create with alter add identified")
def invalid_create_with_alter_add_identified(self):

    user_name = f"user_{getuid()}"
    with Given("create user without authentication methods"):
        common.create_user(user_name=user_name)

    with Then("execute invalid alter query"):
        common.execute_query(
            query=f"CREATE USER {user_name} ADD IDENTIFIED WITH plaintext_password BY '1'",
            expected=errors.syntax_error,
        )


@TestFeature
@Name("syntax")
def feature(self):
    """Check syntax when creating or altering user with one or multiple auth methods."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
