from testflows.core import *
from testflows.asserts import error

from rbac.requirements import *

from helpers.common import getuid, check_clickhouse_version

import rbac.tests.multiple_auth_methods.common as common
import rbac.tests.multiple_auth_methods.errors as errors


def generate_ssh_keys(number_of_keys, type="rsa"):
    """Generate SSH keys and return the public keys and private key files paths."""
    node = current().context.node
    public_keys = []
    private_key_files = []
    for i in range(number_of_keys):
        private_key_file = f"private_key_{i}_{getuid()}"
        public_key_file = private_key_file + ".pub"
        private_key_files.append(private_key_file)
        node.command(f"ssh-keygen -t {type} -N '' -f {private_key_file}", exitcode=0)
        public_key = (
            node.command(f"cat {public_key_file}", exitcode=0).output.strip().split()[1]
        )
        public_keys.append(public_key)

    if number_of_keys == 1:
        return public_keys[0], private_key_files[0]

    return public_keys, private_key_files


def clean_up_files(private_key_files):
    """Remove generated ssh key files."""
    node = current().context.node
    for private_key_file in private_key_files:
        node.command(f"[ -f {private_key_file} ] && rm {private_key_file}", exitcode=0)
        node.command(
            f"[ -f {private_key_file}.pub ] && rm {private_key_file}.pub", exitcode=0
        )


@TestScenario
@Name("multiple ssh keys")
def multiple_ssh_keys(self, number_of_keys=5):
    """Check that user can have multiple SSH keys and the user can authenticate
    using any of the SSH keys."""

    node = self.context.node
    user_name = f"user_{getuid()}"

    try:
        with Given("generate SSH keys"):
            public_keys, private_key_files = generate_ssh_keys(number_of_keys)

        with And("create user with multiple SSH keys"):
            query = f"CREATE USER {user_name} IDENTIFIED WITH ssh_key BY KEY '{public_keys[0]}' TYPE 'ssh-rsa'"
            for public_key in public_keys[1:]:
                query += f", ssh_key BY KEY '{public_key}' TYPE 'ssh-rsa'"
            node.query(query)

        with Then("check that user can login using any of the SSH keys"):
            for private_key_file in private_key_files:
                common.login_ssh(user_name=user_name, ssh_key_file=private_key_file)

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER IF EXISTS {user_name}")

        with And("clean up generated files"):
            clean_up_files(private_key_files)


@TestScenario
@Name("multiple ssh keys without BY clause")
def multiple_ssh_keys_without_BY_clause(self, number_of_keys=5):
    """Check that user can have multiple SSH keys and the user can authenticate
    using any of the SSH keys. The SSH keys after first one are specified without
    the `BY` clause."""
    node = self.context.node
    user_name = f"user_{getuid()}"

    try:
        with Given("generate SSH keys"):
            public_keys, private_key_files = generate_ssh_keys(number_of_keys)

        with And("create user with multiple SSH keys"):
            query = f"CREATE USER {user_name} IDENTIFIED WITH ssh_key BY KEY '{public_keys[0]}' TYPE 'ssh-rsa'"
            for public_key in public_keys[1:]:
                query += f", KEY '{public_key}' TYPE 'ssh-rsa'"
            node.query(query)

        with Then("check that user can login using any of the SSH keys"):
            for private_key_file in private_key_files:
                common.login_ssh(user_name=user_name, ssh_key_file=private_key_file)

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER IF EXISTS {user_name}")

        with And("clean up generated files"):
            clean_up_files(private_key_files)


@TestScenario
@Name("multiple ssh keys exceeding limit")
def multiple_ssh_keys_exceed_limit(self, number_of_keys=101):
    """Check that user cannot have more than `max_authentication_methods_per_user`
    SSH keys when they are specified without the `BY` clause."""

    node = self.context.node
    user_name = f"user_{getuid()}"

    try:
        with Given("generate SSH keys"):
            public_keys, private_key_files = generate_ssh_keys(number_of_keys)

        with And("create user with multiple SSH keys"):
            query = f"CREATE USER {user_name} IDENTIFIED WITH ssh_key BY KEY '{public_keys[0]}' TYPE 'ssh-rsa'"
            for public_key in public_keys[1:]:
                query += f", KEY '{public_key}' TYPE 'ssh-rsa'"
                exitcode, message = 36, (
                    "DB::Exception: User can not be created/updated because "
                    "it exceeds the allowed quantity of authentication methods per user."
                )
            node.query(query, exitcode=exitcode, message=message)

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER IF EXISTS {user_name}")

        with And("clean up generated files"):
            clean_up_files(private_key_files)


@TestScenario
@Name("different form of multiple ssh keys")
def different_form_of_multiple_ssh_keys(self):
    """Check that user can have multiple SSH keys and the user can authenticate
    using any of the SSH keys. The SSH keys are specified in different forms: with
    specified `ssh_key BY` clause and without it."""
    node = self.context.node
    user_name = f"user_{getuid()}"

    try:
        with Given("generate SSH keys"):
            number_of_keys = 5
            public_keys, private_key_files = generate_ssh_keys(number_of_keys)

        with And("create user with multiple SSH keys"):
            query = f"CREATE USER {user_name} IDENTIFIED WITH ssh_key BY KEY '{public_keys[0]}' TYPE 'ssh-rsa'"
            query += f", ssh_key BY KEY '{public_keys[1]}' TYPE 'ssh-rsa'"
            query += f", KEY '{public_keys[2]}' TYPE 'ssh-rsa'"
            query += f", KEY '{public_keys[3]}' TYPE 'ssh-rsa'"
            query += f", ssh_key by KEY '{public_keys[4]}' TYPE 'ssh-rsa'"

            node.query(query)

        with Then("check that user can login using any of the SSH keys"):
            for private_key_file in private_key_files:
                common.login_ssh(user_name=user_name, ssh_key_file=private_key_file)

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER IF EXISTS {user_name}")

        with And("clean up generated files"):
            clean_up_files(private_key_files)


@TestScenario
@Name("different form of multiple ssh keys with other auth methods")
def different_form_of_multiple_ssh_keys_with_other_auth_methods(self):
    """Check that user can have multiple authentication methods, including an SSH key,
    and the user can authenticate using the SSH key and other authentication methods.
    SSH keys are specified in different forms: with specified `ssh_key BY` clause and
    without it."""
    node = self.context.node
    user_name = f"user_{getuid()}"
    password1 = "foo1"
    password2 = "foo2"

    try:
        with Given("generate SSH keys"):
            number_of_keys = 5
            public_keys, private_key_files = generate_ssh_keys(number_of_keys)

        with And("create user with multiple SSH keys"):
            query = f"CREATE USER {user_name} IDENTIFIED WITH ssh_key BY KEY '{public_keys[0]}' TYPE 'ssh-rsa'"
            query += f", ssh_key BY KEY '{public_keys[1]}' TYPE 'ssh-rsa'"
            query += f", KEY '{public_keys[2]}' TYPE 'ssh-rsa'"
            query += f", BY '{password1}'"
            query += f", ssh_key by KEY '{public_keys[4]}' TYPE 'ssh-rsa'"
            query += f", KEY '{public_keys[3]}' TYPE 'ssh-rsa'"
            query += f", plaintext_password BY '{password2}'"

            node.query(query)

        with Then("check that user can login using any of the SSH keys"):
            for private_key_file in private_key_files:
                common.login_ssh(user_name=user_name, ssh_key_file=private_key_file)

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER IF EXISTS {user_name}")

        with And("clean up generated files"):
            clean_up_files(private_key_files)


@TestScenario
@Name("specifying key without `BY` clause after some other auth method")
def key_without_BY_clause_after_other_auth_method(self):
    """Check that ssh key without `BY` clause can not be specified after some other
    authentication method rather than ssh key."""
    node = self.context.node
    user_name = f"user_{getuid()}"
    password1 = "foo1"

    try:
        with Given("generate SSH keys"):
            number_of_keys = 2
            public_keys, private_key_files = generate_ssh_keys(number_of_keys)

        with And("create user with multiple SSH keys"):
            query = f"CREATE USER {user_name} IDENTIFIED WITH ssh_key BY KEY '{public_keys[0]}' TYPE 'ssh-rsa'"
            query += f", BY '{password1}'"
            query += f", KEY '{public_keys[1]}' TYPE 'ssh-rsa'"
            exitcode, message = (
                62,
                "DB::Exception: Syntax error: failed at position 660 ('KEY')",
            )
            if check_clickhouse_version(">=25.2")(self):
                exitcode, message = (
                    62,
                    "DB::Exception: Syntax error: failed at position 660 (KEY)",
                )

            node.query(query, exitcode=exitcode, message=message)

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER IF EXISTS {user_name}")

        with And("clean up generated files"):
            clean_up_files(private_key_files)


@TestCheck
@Name("identified with SSH key")
def ssh_key_with_other_auth_methods(self, type="rsa"):
    """Check that user can have multiple authentication methods, including an SSH key,
    and the user can authenticate using the SSH key and other authentication methods."""
    node = self.context.node
    user_name = f"user_{getuid()}"

    try:
        with Given("generate SSH keys"):
            public_key, private_key_file = generate_ssh_keys(1, type=type)

        with And("create user with password and SSH key authentication methods"):
            password = "foo1"
            query = (
                f"CREATE USER {user_name} IDENTIFIED BY '{password}', "
                f"ssh_key BY KEY '{public_key}' TYPE 'ssh-{type}'"
            )
            node.query(query)

        with Then("check that user can login using the password"):
            common.login(user_name=user_name, password=password)

        with And("check that user can login using the SSH key"):
            common.login_ssh(user_name=user_name, ssh_key_file=private_key_file)

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER IF EXISTS {user_name}")

        with And("clean up generated files"):
            clean_up_files([private_key_file])


@TestCheck
@Name("identified with SSH key only")
def auth_with_ssh_key(self, type="rsa"):
    """Check that a user can authenticate using an SSH key only."""
    node = self.context.node
    user_name = f"user_{getuid()}"

    try:
        with Given("generate SSH keys"):
            public_key, private_key_file = generate_ssh_keys(1, type=type)

        with And("create user with SSH key authentication method"):
            query = f"CREATE USER {user_name} IDENTIFIED WITH ssh_key BY KEY '{public_key}' TYPE 'ssh-{type}'"
            node.query(query)

        with Then("check that user can login using the SSH key"):
            node.command(
                f"clickhouse client --user {user_name} --ssh-key-file {private_key_file} --ssh-key-passphrase '' -q 'SELECT 1'",
                exitcode=0,
            )

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER IF EXISTS {user_name}")

        with And("clean up generated files"):
            clean_up_files([private_key_file])


@TestScenario
@Name("run with different ssh key types")
def run_with_different_types(self):
    types = ["rsa", "ecdsa", "ed25519"]  # "ecdsa-sha2-nistp256"
    for type in types:
        Scenario(name=f"{type} auth with ssh key", test=auth_with_ssh_key)(type=type)
        Scenario(
            name=f"{type} auth with ssh key and other auth method",
            test=ssh_key_with_other_auth_methods,
        )(type=type)


@TestFeature
@Name("ssh key")
def feature(self):
    """Run ssh_key authentication tests."""
    with Pool(3) as executor:
        for scenario in loads(current_module(), Scenario):
            Scenario(test=scenario, flags=TE, parallel=True, executor=executor)()
        join()
