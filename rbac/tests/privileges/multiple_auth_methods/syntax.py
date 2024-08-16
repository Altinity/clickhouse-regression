from rbac.tests.privileges.multiple_auth_methods.common import *
from rbac.tests.privileges.multiple_auth_methods.errors import *


@TestScenario
@Name("create user without WITH after IDENTIFIED")
def create_user_identified_without_with_syntax_error(self):
    """Check that the WITH keyword cannot be omitted when creating a user with an identification
    method and a specified authentication type."""
    with Given("construct query with syntax error"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED plaintext_password BY '123'"
        note(query)

    with Then("expect syntax error"):
        execute_query(query=query, expected=syntax_error)

    with And("check that user was not created"):
        login(
            user_name=user_name,
            password="123",
            expected=no_user_with_such_name(user_name),
        )


@TestScenario
@Name("alter user without WITH after IDENTIFIED")
def alter_user_identified_without_with_syntax_error(self):
    """Check that the WITH keyword cannot be omitted when altering a user with an identification
    method and a specified authentication type."""
    with Given("create user with plaintext_password"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password BY '123';"
        execute_query(query=query)

    with And("construct ALTER USER query without WITH after IDENTIFIED"):
        query = f"ALTER USER {user_name} IDENTIFIED plaintext_password BY '456'"
        note(query)

    with Then("expect to see syntax error"):
        execute_query(query=query, expected=syntax_error)

    with And("check that user can only login with initial password"):
        login(
            user_name=user_name,
            password="123",
        )
        login(
            user_name=user_name,
            password="456",
            expected=no_user_with_such_name(user_name),
        )


@TestScenario
@Name("alter user without WITH after ADD IDENTIFIED")
def alter_user_add_identified_without_with_syntax_error(self):
    """Check that the WITH keyword cannot be omitted when adding an identification method to a user
    with a specified authentication type."""
    with Given("create user with plaintext_password"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password BY '123';"
        execute_query(query=query)

    with And("construct ALTER USER query without WITH after ADD IDENTIFIED"):
        query = f"ALTER USER {user_name} ADD IDENTIFIED plaintext_password BY '456'"
        note(query)

    with Then("expect to see syntax error"):
        execute_query(query=query, expected=syntax_error)

    with And("check that user can only login with initial password"):
        login(
            user_name=user_name,
            password="123",
        )
        login(
            user_name=user_name,
            password="456",
            expected=no_user_with_such_name(user_name),
        )


@TestScenario
@Name("create user without auth type and password after IDENTIFIED WITH")
def without_auth_type_and_password_syntax_error(self):
    """Check that it is mandatory to specify both the authentication type and password
    after the IDENTIFIED WITH clause."""
    with Given("construct query with syntax error"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED WITH"
        note(query)

    with Then("expect syntax error"):
        execute_query(query=query, expected=syntax_error)

    with And("check that user was not created"):
        login(
            user_name=user_name,
            password="123",
            expected=no_user_with_such_name(user_name),
        )


@TestScenario
@Name("create user without password after IDENTIFIED BY")
def without_password_syntax_error(self):
    """Check that it is mandatory to specify a password after the IDENTIFIED BY clause."""
    with Given("construct query with syntax error"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED BY"
        note(query)

    with Then("expect syntax error"):
        execute_query(query=query, expected=syntax_error)

    with And("check that user was not created"):
        login(
            user_name=user_name,
            password="123",
            expected=no_user_with_such_name(user_name),
        )


@TestScenario
@Name("without IDENTIFIED")
def without_identified_syntax_error(self):
    """Check that the IDENTIFIED keyword cannot be omitted when creating a user with
    an identification method."""
    with Given("construct query with syntax error"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} WITH plaintext_password BY '123'"
        note(query)

    with Then("expect syntax error"):
        execute_query(query=query, expected=syntax_error)

    with And("check that user was not created"):
        login(
            user_name=user_name,
            password="123",
            expected=no_user_with_such_name(user_name),
        )


@TestScenario
@Name("without auth type")
def without_auth_type_syntax_error(self):
    """Check that the authentication type cannot be omitted when creating a user using
    the IDENTIFIED WITH clause and specifying the password using the BY clause."""
    with Given("construct query with syntax error"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED WITH BY '123'"
        note(query)

    with Then("expect syntax error"):
        execute_query(query=query, expected=syntax_error)

    with And("check that user was not created"):
        login(
            user_name=user_name,
            password="123",
            expected=no_user_with_such_name(user_name),
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
        execute_query(query=query, expected=syntax_error)

    with And("check that user was not created"):
        login(
            user_name=user_name,
            expected=no_user_with_such_name(user_name),
        )


@TestScenario
@Name("password without quotes")
def password_without_quotes_syntax_error(self):
    """Check that password should be in quotes."""
    with Given("construct a query with password without quotes"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password BY some_password"
        note(query)

    with Then("expect syntax error"):
        execute_query(query=query, expected=syntax_error)

    with And("check that user was not created"):
        login(
            user_name=user_name,
            expected=no_user_with_such_name(user_name),
        )


@TestScenario
@Name("trailing coma")
def trailing_coma_syntax_error(self):
    """Check that trailing coma after auth method(s) is not allowed."""
    with Given("CREATE with trailing coma"):
        user_name = f"user_{getuid()}"
        execute_query(
            query=f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password by '1',",
            expected=syntax_error,
        )

    with And("create user with correct syntax"):
        execute_query(
            query=f"CREATE USER {user_name} IDENTIFIED WITH plaintext_password by '123'"
        )

    with And("ALTER USER ADD IDENTIFIED with trailing coma"):
        query = f"ALTER USER {user_name} ADD IDENTIFIED WITH plaintext_password by '2', plaintext_password by '2',"
        execute_query(query=query, expected=syntax_error)

    with And("ALTER USER IDENTIFIED with trailing coma"):
        query = f"ALTER USER {user_name} IDENTIFIED WITH plaintext_password by '3', plaintext_password by '4',"
        execute_query(query=query, expected=syntax_error)

    with And("CREATE USER IDENTIFIED BY with trailing coma"):
        execute_query(
            query=f"CREATE USER {user_name} IDENTIFIED BY '5', BY '7',",
            expected=syntax_error,
        )

    with And("ALTER USER ADD IDENTIFIED BY with trailing coma"):
        query = f"ALTER USER {user_name} ADD IDENTIFIED BY '6',"
        execute_query(query=query, expected=syntax_error)

    with And("ALTER USER IDENTIFIED BY with trailing coma"):
        query = f"ALTER USER {user_name} IDENTIFIED BY '5',"
        execute_query(query=query, expected=syntax_error)


@TestScenario
def many_auth_methods(self):
    """Check that user can have 1000 auth methods."""
    with Given("construct a query with user having 1000 auth methods"):
        user_name = f"user_{getuid()}"
        auth_methods = []
        passwords = []
        number_of_methods = 1000
        for i in range(number_of_methods):
            auth_methods.append(f"plaintext_password by '{i}'")
            passwords.append(f"{i}")

        auth_methods_string = ",".join(auth_methods)
        query = f"CREATE USER {user_name} IDENTIFIED WITH {auth_methods_string}"

    with Then("execute query"):
        execute_query(query=query)

    with And("login with every password"):
        for password in passwords:
            login(user_name=user_name, password=password)


@TestScenario
@Name("omit WITH and auth type")
def omit_with_and_auth_type(self):
    """Check that it is possible to omit WITH keyword and auth type when creating user identified
    by some passwords. Default auth type should be used."""
    with Given("construct a valid query"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED BY '123'"
        note(query)

    with Then("execute query"):
        execute_query(query=query)

    with And("login with specified password"):
        login(user_name=user_name, password="123")


@TestScenario
@Name("create user with NO_PASSWORD")
def no_password_upper_case(self):
    """Check that user can be created with no password using IDENTIFIED WITH NO_PASSWORD clause."""
    with Given("construct a valid query"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED WITH NO_PASSWORD"
        note(query)

    with Then("execute query"):
        execute_query(query=query)

    with And("login without password"):
        login(user_name=user_name)


@TestScenario
@Name("create user with no_password")
def no_password_lower_case(self):
    """Check that user can be created with no password using IDENTIFIED WITH no_password clause."""
    with Given("construct a valid query"):
        user_name = f"user_{getuid()}"
        query = f"CREATE USER {user_name} IDENTIFIED WITH no_password"
        note(query)

    with Then("execute query"):
        execute_query(query=query)

    with And("login without password"):
        login(user_name=user_name)


@TestScenario
@Name("create multiple users with same auth method")
def multiple_users_one_auth_method(self):
    """Check that I can create multiple users with same auth method."""
    with Given("construct a valid query"):
        number_of_users = random.randint(5, 20)
        user_names = [f"user_{i}_{getuid()}" for i in range(number_of_users)]
        users_string = ",".join(user_names)
        query = (
            f"CREATE USER {users_string} IDENTIFIED WITH plaintext_password BY '123'"
        )
        note(query)

    with Then("execute query"):
        execute_query(query=query)

    with And("login with every user"):
        for user_name in user_names:
            login(user_name=user_name, password="123")


@TestScenario
@Name("create multiple users with multiple auth methods")
def multiple_users_multiple_auth_methods(self):
    """Check that I can create multiple users with multiple auth methods."""
    with Given("construct a valid query"):
        number_of_users = random.randint(10, 100)
        user_names = [f"user_{i}_{getuid()}" for i in range(number_of_users)]
        users_string = ",".join(user_names)
        auth_methods = [
            "plaintext_password BY '123'",
            "plaintext_password BY '456'",
            "BY '789'",
        ]
        auth_methods_string = ",".join(auth_methods)
        query = f"CREATE USER {users_string} IDENTIFIED WITH {auth_methods_string}"
        note(query)

    with Then("execute query"):
        execute_query(query=query)

    with And("login with every user and with every auth method"):
        for user_name in user_names:
            for password in ["123", "456", "789"]:
                login(user_name=user_name, password=password)


@TestFeature
@Name("syntax")
def feature(self, node="clickhouse1"):
    """Check syntax when creating or altering user with one or multiple auth methods."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
