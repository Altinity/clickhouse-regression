import random

from testflows.core import *
from testflows.combinatorics import product

from helpers.common import getuid

import jwt_authentication.tests.steps as steps
from jwt_authentication.tests.static_key.model import (
    User,
    Validator,
    Token,
    Model,
    Key,
)

random.seed(42)


def debug_note(user, token, validator):
    """Generate and log debug notes."""
    note(
        f"""
        Debug Notes:
        ============================
        User Information:
        - User Name: {user.user_name}

        Token Information:
        - Algorithm: {token.algorithm}
        - Secret: {token.secret}
        - User Name: {token.user_name}
        - Expiration Minutes: {token.expiration_minutes}
        - Private key algorithm: {token.key.algorithm if token.key else None}

        Validator Information:
        - Algorithm: {validator.algorithm}
        - Secret: {validator.secret}
        - Static Key in Base64: {validator.static_key_in_base64}
        - Config Static Key in Base64: {validator.config_static_key_in_base64}
        - Public key algorithm: {validator.key.algorithm if validator.key else None}
        ============================
        """
    )


@TestStep(Given)
def create_tokens(
    self,
    user_names,
    token_algorithms,
    token_secrets,
    expiration_minutes,
    keys,
):
    """Create tokens for users."""
    tokens = []

    symmetrical_algorithms = [alg for alg in token_algorithms if alg.startswith("HS")]
    asymmetrical_algorithms = [
        alg for alg in token_algorithms if alg not in symmetrical_algorithms
    ]

    for user_name, token_algorithm, token_secret, expiration in product(
        user_names, symmetrical_algorithms, token_secrets, expiration_minutes
    ):
        token = Token(
            user_name=user_name,
            secret=token_secret,
            algorithm=token_algorithm,
            expiration_minutes=expiration,
        )
        token.create_token()
        tokens.append(token)

    for user_name, token_algorithm, key, expiration in product(
        user_names, asymmetrical_algorithms, keys, expiration_minutes
    ):
        if steps.algorithm_from_same_group(token_algorithm, key.algorithm):
            token = Token(
                user_name=user_name,
                algorithm=token_algorithm,
                key=key,
                expiration_minutes=expiration,
            )
            token.create_token()
            tokens.append(token)

    # for i in range(10):
    #     corrupted_token = tokens[i]

    return tokens


@TestStep(Given)
def create_validators(
    self,
    validator_algorithms=[None],
    validator_secrets=[None],
    config_static_key_in_base64_values=[None],
    static_key_in_base64_values=[None],
    keys=[None],
):
    """Create validators."""
    validators = []
    for (
        algorithm,
        secret,
        static_key_in_base64,
        config_static_key_in_base64,
        key,
    ) in product(
        validator_algorithms,
        validator_secrets,
        static_key_in_base64_values,
        config_static_key_in_base64_values,
        keys,
    ):
        if static_key_in_base64 == "true" and secret is not None:
            secret = steps.to_base64(secret)

        validator_id = f"validator_{getuid()}"
        validator = Validator(
            validator_id=validator_id,
            algorithm=algorithm,
            secret=secret,
            config_static_key_in_base64=config_static_key_in_base64,
            static_key_in_base64=static_key_in_base64,
            key=key,
        )
        validators.append(validator)

    return validators


@TestStep(Given)
def create_key_pairs(self, algorithms):
    """Create key pairs."""
    keys = []
    for algorithm in algorithms:
        key = Key(algorithm=algorithm).generate_keys()
        keys.append(key)
    return keys + [None]


@TestCheck
@Name("check jwt authentication for given combination")
def check_combination(self, user_name, token, validator, node=None):
    """Check jwt authentication for given combination."""
    if node is None:
        node = self.context.node

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
def run_combinations(self, node, combinations):
    """Run combinations for given node."""
    for num, combination in enumerate(combinations):
        user_name, token, validator = combination
        Check(name=f"combination {num}", test=check_combination)(
            user_name=user_name, token=token, validator=validator, node=node
        )


@TestScenario
def jwt_authentication_combinatorics(self):
    """Check jwt authentication with static key validator."""

    with Given("defining parameters for tokens and validators"):
        token_algorithms = [
            "HS256",
            "HS384",
            "HS512",
            "RS256",
            "RS384",
            "RS512",
            "ES256",
            "ES384",
            "ES512",
            "Ed25519",
            # ---need to investigate why they are not working---
            # "ES256K",
            # "PS256",
            # "PS384",
            # "PS512",
            # "Ed448",
        ]
        validator_algorithms = [
            "HS256",
            "HS384",
            "HS512",
            "RS256",
            "RS384",
            "RS512",
            "ES256",
            "ES384",
            "ES512",
            "Ed25519",
            # ---need to investigate why they are not working---
            # "ES256K",
            # "PS256",
            # "PS384",
            # "PS512",
            # "Ed448",
        ]
        key_pair_algorithms = [
            "RS256",
            "RS384",
            "RS512",
            "ES256",
            "ES384",
            "ES512",
            "Ed25519",
        ]
        user_names = [f"user1_{getuid()}", f"user2_{getuid()}"]
        token_secrets = ["combinatorial_secret_1", "combinatorial_secret_2"]
        validator_secrets = ["combinatorial_secret_1", "combinatorial_secret_2", None]
        config_static_key_in_base64_values = ["true", "false", None]
        static_key_in_base64_values = ["true", "false", None]
        expiration_minutes = [60 * 5, -5, None]
        if self.context.stress:
            expiration_minutes = [
                -5,
                None,
            ]  # since test might take a long time and token can expire

    with And("create public and private keys for validators"):
        keys = create_key_pairs(algorithms=key_pair_algorithms)

    with And("create tokens for users"):
        tokens = create_tokens(
            user_names=user_names,
            token_algorithms=token_algorithms,
            token_secrets=token_secrets,
            expiration_minutes=expiration_minutes,
            keys=keys,
        )

    with And("create validators"):
        validators = create_validators(
            validator_algorithms=validator_algorithms,
            validator_secrets=validator_secrets,
            config_static_key_in_base64_values=config_static_key_in_base64_values,
            static_key_in_base64_values=static_key_in_base64_values,
            keys=keys,
        )

    with And("create all possible combinations of users, tokens, and validators"):
        combinations = list(product(user_names, tokens, validators))
        note(f"Total number of combinations: {len(combinations)}")

    with And("if stress is not enabled, select 60 random combinations"):
        if not self.context.stress:
            combinations = random.sample(combinations, 100)

    with And("define nodes and split combinations between them"):
        nodes = [
            self.context.node,
            self.context.node2,
            self.context.node3,
            self.context.node4,
            self.context.node5,
            self.context.node6,
            self.context.node7,
            self.context.node8,
            self.context.node9,
            self.context.node10,
        ]
        split_combinations = [combinations[i :: len(nodes)] for i in range(len(nodes))]

    with Pool(10) as executor:
        for node_index, (node, node_combinations) in enumerate(
            zip(nodes, split_combinations)
        ):
            Scenario(
                f"run on node #{node_index}",
                test=run_combinations,
                parallel=True,
                executor=executor,
            )(node=node, combinations=node_combinations)
        join()
