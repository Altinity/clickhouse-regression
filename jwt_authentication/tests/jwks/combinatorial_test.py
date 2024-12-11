from testflows.core import *
from testflows.combinatorics import product, combinations

from helpers.common import getuid

import jwt_authentication.tests.steps as steps
from jwt_authentication.tests.jwks.model import (
    User,
    Validator,
    Token,
    Model,
    Key,
    SSH_key,
)

import random

random.seed(42)


def debug_note(user, token, validator):
    """Generate and log debug notes for a given user, token, and validator."""
    keys = [(key.key["kid"], key.key["alg"]) for key in validator.keys]
    keys_str = "\n".join(
        [
            f"Key ID #{num}: {key[0]}, Algorithm #{num}: {key[1]}"
            for num, key in enumerate(keys)
        ]
    )
    note(
        f"""
        Debug Notes:
        ============================
        User Information:
        - User Name: {user.user_name}

        Token Information:
        - Algorithm: {token.algorithm}
        - key_id: {token.key_id}
        - User Name: {token.user_name}
        - Expiration Minutes: {token.expiration_minutes}
        

        Validator Information:
        - Keys: {keys_str}
        ============================
        """
    )


@TestStep(Given)
def create_tokens(
    self, user_names, token_algorithms, ssh_keys, key_ids, expiration_minutes
):
    """Create tokens by combining given parameters and return a list of generated tokens."""
    tokens = []
    for user_name, token_algorithm, ssh_key, key_id, expiration in product(
        user_names, token_algorithms, ssh_keys, key_ids, expiration_minutes
    ):
        if ssh_key is not None:
            token = Token(
                user_name=user_name,
                ssh_key=ssh_key,
                algorithm=token_algorithm,
                key_id=key_id,
                expiration_minutes=expiration,
            )
            token.create_token()
            tokens.append(token)

    return tokens


@TestStep(Given)
def create_jwks_validators(
    self,
    keys,
):
    """Create validators using single keys and all possible key pairs.
    Returns a list of created validators."""
    validators = []

    for key in keys:
        validator_id = f"validator_{getuid()}"
        validator = Validator(
            validator_id=validator_id,
            keys=[key],
        )
        validators.append(validator)

    for key_pair in combinations(keys, 2):
        validator_id = f"validator_{getuid()}"
        validator = Validator(
            validator_id=validator_id,
            keys=list(key_pair),
        )
        validators.append(validator)

    return validators


@TestStep(Given)
def create_keys(self, algorithms, ssh_keys, key_ids=None, key_types=None):
    """Generate JWKS keys for given algorithms and SSH keys.
    Returns the generated keys and their corresponding IDs."""
    keys = []
    key_ids = []
    for algorithm, ssh_key in product(algorithms, ssh_keys):
        key_id = f"key_id_{getuid()}"
        key_ids.append(key_id)
        key = Key(algorithm=algorithm, ssh_key=ssh_key, key_id=key_id)
        key.create_key_content()
        keys.append(key)

    return keys, key_ids


@TestStep(Given)
def create_ssh_key_pairs(self, number=1):
    """Generate the specified number of RSA SSH key pairs.
    Returns a list of generated keys along with a `None`."""
    keys = []
    for _ in range(number):
        key = SSH_key().generate_keys()
        keys.append(key)
    return keys + [None]


@TestCheck
def check_jwks_authentication(self, user_name, token, validator, node=None):
    """Verify JWT authentication using a static key validator.
    Adds the validator to the config, creates a user, and
    validates the JWT token against the ClickHouse client.
    """
    with Given("add validator to the config.xml"):
        validator.add_to_config(node=node)

    with And("create user with jwt authentication"):
        user = User(user_name=user_name, auth_type="jwt")
        user.create_user(node=node)

    with And("add debug notes"):
        debug_note(user, token, validator)

    with Then("check jwt authentication with given token and validator"):
        model = Model(user=user, token=token, validator=validator)
        steps.check_clickhouse_client_jwt_login(
            user_name=user.user_name,
            token=token.jwt_token,
            no_checks=True,
            use_model=model,
            node=node,
        )


@TestScenario
def run_combinations(self, node, node_index):
    """Execute test combinations for a specific node.
    Iterates over combinations of user, token, and validator."""
    combinations = self.context.split_combinations[node_index]
    for num, combination in enumerate(combinations):
        user_name, token, validator = combination
        Check(name=f"combination {num}", test=check_jwks_authentication)(
            user_name=user_name, token=token, validator=validator, node=node
        )


@TestScenario
@Name("static jwks combinatorial test")
def feature(self):
    """Check JWT authentication using static key validators."""

    token_algorithms = [
        "RS256",
        "RS384",
        "RS512",
    ]
    validator_key_algorithms = [
        "RS256",
        "RS384",
        "RS512",
    ]
    user_names = [f"user1_{getuid()}", f"user2_{getuid()}"]
    expiration_minutes = [60 * 5, -5, None]

    with Given("create pairs of ssh keys"):
        ssh_keys = create_ssh_key_pairs(number=2)

    with And("create keys for validators"):
        keys, key_ids = create_keys(
            algorithms=validator_key_algorithms,
            ssh_keys=ssh_keys,
        )

    with And("create validators"):
        validators = create_jwks_validators(
            keys=keys,
        )

    with Given("create tokens for users"):
        tokens = create_tokens(
            user_names=user_names,
            token_algorithms=token_algorithms,
            ssh_keys=ssh_keys,
            key_ids=key_ids,
            expiration_minutes=expiration_minutes,
        )

    with And("create all possible combinations of users, tokens, and validators"):
        combinations = list(product(user_names, tokens, validators))
        note(f"Total number of combinations: {len(combinations)}")

    with And("if stress is not enabled, select 60 random combinations"):
        if not self.context.stress:
            combinations = random.sample(combinations, 60)

    with And("define nodes and split combinations between them"):
        nodes = self.context.nodes
        split_combinations = [combinations[i :: len(nodes)] for i in range(len(nodes))]
        assert len(split_combinations) == len(nodes)
        self.context.split_combinations = split_combinations

    with Pool(10) as executor:
        for node_index, node in enumerate(nodes):
            Scenario(
                f"run on node #{node_index}",
                test=run_combinations,
                parallel=True,
                executor=executor,
            )(node=node, node_index=node_index)
        join()
