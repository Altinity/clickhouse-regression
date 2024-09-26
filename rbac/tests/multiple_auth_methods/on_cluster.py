from testflows.core import *

from rbac.requirements import *
from helpers.common import getuid
import rbac.tests.multiple_auth_methods.common as common
import rbac.tests.multiple_auth_methods.errors as errors


@TestScenario
def check_alter_identified_on_cluster(self, auth_methods, cluster="replicated_cluster"):
    """Check `ALTER USER ON CLUSTER IDENTIFIED WITH` statement with multiple auth methods."""
    user_name = f"user_{getuid()}"
    correct_passwords = define("initial users's passwords", ["123", "456"])
    wrong_passwords = define(
        "new user's passwords", [auth_method[1] for auth_method in auth_methods]
    )

    with Given("create user on cluster with two plaintext passwords"):
        identified = "plaintext_password BY '123',plaintext_password BY '456'"
        common.create_user(
            user_name=user_name,
            identified=identified,
            cluster=cluster,
        )

    with And("change user's authentication methods on cluster"):
        auth_methods_str = define("auth methods", ", ".join(j[0] for j in auth_methods))
        if "no_password" in auth_methods_str and len(auth_methods) > 1:
            common.alter_identified(
                user_name=user_name,
                identified=auth_methods_str,
                cluster=cluster,
                expected=errors.no_password_cannot_coexist_with_others(),
            )
        else:
            common.alter_identified(
                user_name=user_name,
                identified=auth_methods_str,
                cluster=cluster,
            )
            if "no_password" in auth_methods_str:  # no_password is the only auth method
                correct_passwords.extend(wrong_passwords)
                wrong_passwords = []  # can login with any password
            else:
                correct_passwords, wrong_passwords = define(
                    "new correct passwords", wrong_passwords
                ), define("wrong passwords", correct_passwords)

        with Then("check that user can login only with correct passwords on all nodes"):
            common.check_login_with_correct_and_wrong_passwords_on_cluster(
                user_name=user_name,
                correct_passwords=correct_passwords,
                wrong_passwords=wrong_passwords,
            )


@TestScenario
def check_alter_add_identified_on_cluster(
    self, auth_methods, cluster="replicated_cluster"
):
    """Check `ALTER USER ON CLUSTER ADD IDENTIFIED WITH` statement with multiple
    auth methods."""

    user_name = f"user_{getuid()}"

    with Given("create user on cluster with two plaintext passwords"):
        identified = "plaintext_password BY '123', plaintext_password BY '456'"
        correct_passwords = define("initial users's passwords", ["123", "456"])
        common.create_user(
            user_name=user_name,
            identified=identified,
            cluster=cluster,
        )

    with And("define correct and new passwords"):
        new_passwords = define(
            "new user's passwords", [auth_method[1] for auth_method in auth_methods]
        )

    with And("add new authentication methods to user on cluster"):
        auth_methods_str = define("auth methods", ", ".join(j[0] for j in auth_methods))
        if "no_password" in auth_methods_str:
            common.add_identified(
                user_name=user_name,
                identified=auth_methods_str,
                cluster=cluster,
                expected=errors.syntax_error(),
            )
        else:
            correct_passwords = define(
                "new correct passwords", correct_passwords + new_passwords
            )
            common.add_identified(
                user_name=user_name,
                identified=auth_methods_str,
                cluster=cluster,
            )

        with Then("check that user can login only with correct passwords on all nodes"):
            wrong_passwords = define(
                "wrong passwords",
                [f"wrong_{password}" for password in correct_passwords],
            )
            common.check_login_with_correct_and_wrong_passwords_on_cluster(
                user_name=user_name,
                correct_passwords=correct_passwords,
                wrong_passwords=wrong_passwords,
            )


@TestScenario
def check_reset_to_new_on_cluster(self, auth_methods, cluster="replicated_cluster"):
    """Check RESET AUTHENTICATION METHODS TO NEW on cluster."""
    user_name = f"user_{getuid()}"
    user_created = False

    with Given("create user on cluster with specified authentication methods"):
        auth_methods_str = define("auth methods", ", ".join(j[0] for j in auth_methods))
        if "no_password" in auth_methods_str and len(auth_methods) > 1:
            common.create_user(
                user_name=user_name,
                identified=auth_methods_str,
                cluster=cluster,
                expected=errors.no_password_cannot_coexist_with_others(),
            )
        else:
            common.create_user(
                user_name=user_name, identified=auth_methods_str, cluster=cluster
            )
            user_created = True

    if user_created:
        with And("reset authentication methods to new on cluster"):
            common.reset_auth_methods_to_new(user_name=user_name, cluster=cluster)

        with Then("check that user can login only with correct passwords on all nodes"):
            correct_passwords = define("correct passwords", [auth_methods[-1][1]])
            wrong_passwords = define(
                "wrong passwords", [auth_method[1] for auth_method in auth_methods[:-1]]
            )
            common.check_login_with_correct_and_wrong_passwords_on_cluster(
                user_name=user_name,
                correct_passwords=correct_passwords,
                wrong_passwords=wrong_passwords,
            )


@TestScenario
def create_user_on_cluster(self, auth_methods, cluster="replicated_cluster"):
    """Check `CREATE USER ON CLUSTER` statement with multiple auth methods."""

    user_name = f"user_{getuid()}"

    with Given("define correct and wrong passwords for authentication"):
        correct_passwords = define(
            "correct passwords",
            [auth_methods[1] for auth_methods in auth_methods],
        )
        wrong_passwords = define(
            "wrong passwords",
            [f"wrong_{password}" for password in correct_passwords],
        )

    with And("create user on cluster with specified authentication methods"):
        auth_methods_str = define("auth methods", ", ".join(j[0] for j in auth_methods))
        if "no_password" in auth_methods_str and len(auth_methods) > 1:
            common.create_user(
                user_name=user_name,
                identified=auth_methods_str,
                cluster=cluster,
                expected=errors.no_password_cannot_coexist_with_others(),
            )
            correct_passwords = define("correct passwords", [])
            wrong_passwords = define(
                "wrong passwords", correct_passwords + wrong_passwords
            )
        else:
            common.create_user(
                user_name=user_name, identified=auth_methods_str, cluster=cluster
            )
            if "no_password" in auth_methods_str:
                correct_passwords = define(
                    "correct passwords", correct_passwords + wrong_passwords
                )
                wrong_passwords = define("wrong passwords", [])

    with Then("check that user can login only with correct passwords on all nodes"):
        common.check_login_with_correct_and_wrong_passwords_on_cluster(
            user_name=user_name,
            correct_passwords=correct_passwords,
            wrong_passwords=wrong_passwords,
        )


@TestFeature
@Name("on cluster")
def feature(self):
    """Check that user's authentication methods can be manipulated on cluster."""
    auth_methods_combinations = common.generate_auth_combinations(
        auth_methods_dict=common.authentication_methods_with_passwords
    )
    with Pool(4) as executor:
        for scenario in loads(current_module(), Scenario):
            for num, auth_methods in enumerate(auth_methods_combinations):
                Scenario(
                    f"{num} {scenario.__name__}",
                    test=scenario,
                    parallel=True,
                    executor=executor,
                )(auth_methods=auth_methods)
        join()
