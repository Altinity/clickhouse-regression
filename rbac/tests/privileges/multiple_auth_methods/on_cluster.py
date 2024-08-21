from testflows.core import *

from rbac.requirements import *
from helpers.common import getuid
import rbac.tests.privileges.multiple_auth_methods.common as common
import rbac.tests.privileges.multiple_auth_methods.errors as errors


@TestStep(Then)
def check_login_on_cluster(self, user_name, wrong_passwords, correct_passwords):
    """Validate user login on all nodes."""
    for password in correct_passwords:
        common.login(user_name=user_name, password=password, nodes=self.context.nodes)

    for password in wrong_passwords:
        common.login(
            user_name=user_name,
            password=password,
            nodes=self.context.nodes,
            expected=errors.wrong_password(user_name),
        )


@TestScenario
def check_alter_identified_on_cluster(self, auth_methods, cluster="replicated_cluster"):
    """Check ALTER USER IDENTIFIED WITH on cluster with multiple auth methods."""
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
        auth_methods_string = ", ".join(j[0] for j in auth_methods)
        if "no_password" in auth_methods_string and len(auth_methods) > 1:
            common.alter_identified(
                user_name=user_name,
                identified=auth_methods_string,
                cluster=cluster,
                expected=errors.no_password_cannot_coexist_with_others(),
            )
        else:
            common.alter_identified(
                user_name=user_name,
                identified=auth_methods_string,
                cluster=cluster,
            )
            if (
                "no_password" in auth_methods_string
            ):  # no_password is the only auth method
                correct_passwords.extend(wrong_passwords)
                wrong_passwords = []  # can login with any password
            else:
                correct_passwords, wrong_passwords = define(
                    "new correct passwords", wrong_passwords
                ), define("wrong passwords", correct_passwords)

        with Then("check that user can login only with correct passwords on all nodes"):
            check_login_on_cluster(
                user_name=user_name,
                correct_passwords=correct_passwords,
                wrong_passwords=wrong_passwords,
            )


@TestScenario
def check_alter_add_identified_on_cluster(
    self, auth_methods, cluster="replicated_cluster"
):
    """Check ALTER USER ADD IDENTIFIED WITH on cluster with multiple auth methods."""
    user_name = f"user_{getuid()}"
    correct_passwords = define("initial users's passwords", ["123", "456"])
    new_passwords = define(
        "new user's passwords", [auth_method[1] for auth_method in auth_methods]
    )

    with Given("create user on cluster with two plaintext passwords"):
        identified = "plaintext_password BY '123', plaintext_password BY '456'"
        common.create_user(
            user_name=user_name,
            identified=identified,
            cluster=cluster,
        )

    with And("add new authentication methods to user on cluster"):
        auth_methods_string = ", ".join(j[0] for j in auth_methods)
        if "no_password" in auth_methods_string:
            common.add_identified(
                user_name=user_name,
                identified=auth_methods_string,
                cluster=cluster,
                expected=errors.no_password_cannot_coexist_with_others(),
            )
        else:
            common.add_identified(
                user_name=user_name,
                identified=auth_methods_string,
                cluster=cluster,
            )
            correct_passwords.extend(new_passwords)

        with Then("check that user can login only with correct passwords on all nodes"):
            wrong_passwords = define(
                "wrong passwords",
                [None] + [f"{password}_1" for password in correct_passwords],
            )
            check_login_on_cluster(
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
        auth_methods_string = ", ".join(j[0] for j in auth_methods)
        if "no_password" in auth_methods_string and len(auth_methods) > 1:
            common.create_user(
                user_name=user_name,
                identified=auth_methods_string,
                cluster=cluster,
                expected=errors.no_password_cannot_coexist_with_others(),
            )
        else:
            common.create_user(
                user_name=user_name, identified=auth_methods_string, cluster=cluster
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
            check_login_on_cluster(
                user_name=user_name,
                correct_passwords=correct_passwords,
                wrong_passwords=wrong_passwords,
            )


@TestScenario
def create_user_on_cluster(self, auth_methods, cluster="replicated_cluster"):
    """Check CREATE USER on cluster with multiple auth methods."""
    user_name = f"user_{getuid()}"
    correct_passwords = define(
        "correct passwords",
        [auth_methods[1] for auth_methods in auth_methods],
    )
    wrong_passwords = define(
        "wrong passwords",
        [f"{password}_1" for password in correct_passwords],
    )
    with Given("create user on cluster with specified authentication methods"):
        auth_methods_string = ", ".join(j[0] for j in auth_methods)
        if "no_password" in auth_methods_string and len(auth_methods) > 1:
            common.create_user(
                user_name=user_name,
                identified=auth_methods_string,
                cluster=cluster,
                expected=errors.no_password_cannot_coexist_with_others(),
            )
            correct_passwords = define("correct passwords", [])
            wrong_passwords = define(
                "wrong passwords", correct_passwords + wrong_passwords
            )
        else:
            common.create_user(
                user_name=user_name, identified=auth_methods_string, cluster=cluster
            )
            if "no_password" in auth_methods_string:
                correct_passwords = define(
                    "correct passwords", correct_passwords + wrong_passwords
                )
                wrong_passwords = define("wrong passwords", [])

    with Then("check that user can login only with correct passwords on all nodes"):
        check_login_on_cluster(
            user_name=user_name,
            correct_passwords=correct_passwords,
            wrong_passwords=wrong_passwords,
        )


@TestFeature
@Name("on cluster")
def feature(self):
    """Check that user's authentication methods can be manipulated on cluster."""
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node, self.context.node_2, self.context.node_3]

    auth_methods_combinations = common.generate_auth_combinations(
        auth_methods_dict=common.authentication_methods_with_passwords, max_length=2
    )
    with Pool(10) as executor:
        for scenario in loads(current_module(), Scenario):
            for num, auth_methods in enumerate(auth_methods_combinations):
                Scenario(
                    f"{num} {scenario.__name__}",
                    test=scenario,
                    parallel=True,
                    executor=executor,
                )(auth_methods=auth_methods)
            join()
