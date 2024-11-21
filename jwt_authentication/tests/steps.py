from testflows.core import *
from testflows.asserts import error

import base64
import datetime
import json
import os
import random
import subprocess

import jwt
from cryptography.hazmat.primitives import serialization


from helpers.common import (
    create_xml_config_content,
    add_config,
    remove_config,
    getuid,
)

HMAC_algorithms = ["HS256", "HS384", "HS512"]
RSA_algorithms = ["RS256", "RS384", "RS512"]
ECDSA_algorithms = ["ES256", "ES384", "ES512", "ES256K"]
PSS_algorithms = ["PS256", "PS384", "PS512"]
EdDSA_algorithms = ["Ed25519", "Ed448"]


def create_static_jwt(
    user_name: str = None,
    secret: str = None,
    algorithm: str = "HS256",
    payload: dict = None,
    expiration_minutes: int = None,
    private_key_path: str = None,
    headers: dict = None,
    key_id: str = None,
) -> str:
    """
    Create a JWT using a static secret and a specified encryption algorithm.
    Supported algorithms:
    | HMAC  | RSA   | ECDSA  | PSS   | EdDSA   |
    | ----- | ----- | ------ | ----- | ------- |
    | HS256 | RS256 | ES256  | PS256 | Ed25519 |
    | HS384 | RS384 | ES384  | PS384 | Ed448   |
    | HS512 | RS512 | ES512  | PS512 |         |
    |       |       | ES256K |       |         |
    And None

    :param payload: The payload to include in the JWT (as a dictionary).
    :param secret: The secret key used to sign the JWT.
    :param algorithm: The encryption algorithm to use (default is 'HS256').
    :param expiration_minutes: The time until the token expires (default is 60 minutes).
    :return: The encoded JWT as a string.
    """
    if payload is None:
        payload = {"sub": f"{user_name}"}

    if key_id is not None:
        if headers is None:
            headers = {}
        headers["kid"] = key_id

    if expiration_minutes is not None:
        expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=expiration_minutes
        )
        payload["exp"] = expiration

    if secret is not None:
        return jwt.encode(payload, secret, algorithm=algorithm)

    if (
        algorithm.startswith("RS")
        or algorithm.startswith("ES")
        or algorithm.startswith("Ed")
    ):
        if private_key_path is None:
            raise ValueError("RSA private key path must be provided for RSA algorithms")
        with open(
            private_key_path,
            "r",
        ) as key_file:
            private_key = key_file.read()

        if algorithm.startswith("Ed"):
            algorithm = "EdDSA"

        note(algorithm)
        return jwt.encode(payload, private_key, algorithm=algorithm, headers=headers)


@TestStep(Given)
def change_clickhouse_config(
    self,
    entries: dict,
    modify: bool = False,
    restart: bool = True,
    format: str = None,
    user: str = None,
    config_file="change_settings.xml",
    config_d_dir: str = "/etc/clickhouse-server/users.d",
    preprocessed_name: str = "users.xml",
    node: Node = None,
):
    """Change clickhouse configuration files: users.xml and config.xml."""
    with By("converting config file content to xml"):
        config = create_xml_config_content(
            entries,
            config_file=config_file,
            config_d_dir=config_d_dir,
            preprocessed_name=preprocessed_name,
        )
        if format is not None:
            for key, value in format.items():
                config.content = config.content.replace(key, value)

    with And("adding xml config file to the server"):
        return add_config(config, restart=restart, modify=modify, user=user, node=node)


@TestStep(Given)
def remove_from_clickhouse_config(
    self,
    entries: dict,
    modify: bool = False,
    restart: bool = True,
    format: str = None,
    user: str = None,
    config_d_dir: str = "/etc/clickhouse-server/users.d",
    preprocessed_name: str = "users.xml",
    node: Node = None,
):
    """Remove a user with JWT authentication from the users.xml configuration file."""
    with By("converting config file content to xml"):
        config = create_xml_config_content(
            entries,
            "change_settings.xml",
            config_d_dir=config_d_dir,
            preprocessed_name=preprocessed_name,
        )
        if format is not None:
            for key, value in format.items():
                config.content = config.content.replace(key, value)

    with And("adding xml config file to the server"):
        return remove_config(
            config, restart=restart, modify=modify, user=user, node=node
        )


@TestStep(Given)
def add_jwt_user_to_users_xml(self, user_name: str, claim: dict = {}):
    """Add a user with JWT authentication to the users.xml configuration file."""
    entries = {"users": {f"{user_name}": {"jwt": claim}}}
    change_clickhouse_config(entries=entries)


@TestStep(Given)
def remove_jwt_user_from_users_xml(self, user_name: str, claim: dict = {}):
    """Remove a user with JWT authentication from the users.xml configuration file."""
    entries = {"users": {f"{user_name}": {"jwt": claim}}}
    remove_from_clickhouse_config(entries=entries)


@TestStep(Given)
def add_static_key_validator_to_config_xml(
    self,
    validator_id: str,
    algorithm: str = "hs256",
    secret: str = None,
    static_key_in_base64: str = None,
    public_key: str = None,
    restart=True,
):
    """Add static key validator to the config.xml."""

    entries = {"jwt_validators": {}}
    entries["jwt_validators"][f"{validator_id}"] = {}
    entries["jwt_validators"][f"{validator_id}"]["algo"] = algorithm.lower()

    if secret is not None:
        entries["jwt_validators"][f"{validator_id}"]["static_key"] = secret
        if static_key_in_base64 is not None:
            entries["jwt_validators"][f"{validator_id}"][
                "static_key_in_base64"
            ] = static_key_in_base64

    if public_key is not None:
        entries["jwt_validators"][f"{validator_id}"]["public_key"] = public_key

    change_clickhouse_config(
        entries=entries,
        config_d_dir="/etc/clickhouse-server/config.d",
        preprocessed_name="config.xml",
        restart=restart,
        config_file=f"{validator_id}.xml",
    )


def to_base64_url(data):
    """Convert data to base64 URL encoding."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def to_base64(data: str) -> str:
    """Convert string to base64 encoding."""
    base64_data = base64.b64encode(data.encode("utf-8")).decode("utf-8")
    return base64_data


@TestStep(Given)
def add_static_jwks_validator_to_config_xml(
    self,
    validator_id: str,
    algorithm: str = "RS256",
    key_id: str = "mykid",
    public_key_str: str = None,
):
    """Add static key validator to the config.xml."""
    with By("retrieve modulus and exponent from public key"):
        public_key = serialization.load_pem_public_key(
            public_key_str.encode(),
        )
        modulus = define(
            "modulus",
            to_base64_url(
                public_key.public_numbers().n.to_bytes(
                    (public_key.public_numbers().n.bit_length() + 7) // 8,
                    byteorder="big",
                )
            ),
        )
        exponent = define(
            "exponent",
            to_base64_url(
                public_key.public_numbers().e.to_bytes(
                    (public_key.public_numbers().e.bit_length() + 7) // 8,
                    byteorder="big",
                )
            ),
        )

    with And("build entries and add static jwks validator to the config.xml"):
        entries = {"jwt_validators": {}}
        entries["jwt_validators"][f"{validator_id}"] = {}
        static_jwks_content = {
            "keys": [
                {
                    "kty": "RSA",
                    "alg": algorithm,
                    "kid": key_id,
                    "n": modulus,
                    "e": exponent,
                }
            ]
        }
        entries["jwt_validators"][f"{validator_id}"]["static_jwks"] = json.dumps(
            static_jwks_content
        )

        change_clickhouse_config(
            entries=entries,
            config_d_dir="/etc/clickhouse-server/config.d",
            preprocessed_name="config.xml",
        )


@TestStep(Given)
def create_user_with_jwt_auth(
    self,
    user_name: str,
    node: Node = None,
    claims: dict = {},
):
    """Create a user with JWT authentication."""
    if node is None:
        node = self.context.node

    query = f"CREATE USER {user_name} IDENTIFIED WITH JWT"

    if claims:
        query += f" CLAIMS '{claims}'"

    try:
        node.query(query)
        yield

    finally:
        with Finally("drop user"):
            node.query(f"DROP USER IF EXISTS {user_name}")


@TestStep(Then)
def check_clickhouse_client_jwt_login(
    self,
    token: str,
    user_name: str = None,
    node: Node = None,
    exitcode: int = 0,
    message: str = None,
    no_checks: bool = False,
):
    """Check JWT authentication for the specified user with clickhouse-client."""
    if node is None:
        node = self.context.node

    with By("check jwt authentication with clickhouse-client"):
        res = node.query(
            "SELECT currentUser()",
            settings=[("jwt", token)],
            exitcode=exitcode,
            message=message,
            no_checks=no_checks,
        )

        if exitcode == 0 and not no_checks:
            assert res.output == user_name, error()

        return res


@TestStep(Then)
def check_http_https_jwt_login(
    self,
    token: str,
    user_name: str = None,
    ip: str = "localhost",
    https: bool = False,
    node: Node = None,
    message: str = None,
    no_checks: bool = False,
):
    """Check JWT authentication for the specified user with http/https."""
    if node is None:
        node = self.context.node

    http_prefix = "https" if https else "http"

    with By(f"check jwt authentication with {http_prefix}"):
        curl = f'curl -H "X-ClickHouse-JWT-Token: Bearer {token}" "{http_prefix}://{ip}:8123/?query=SELECT%20currentUser()"'
        res = node.command(curl, no_checks=no_checks)

        if message is None and not no_checks:
            assert res.output == user_name, error()

        return res


@TestStep(Then)
def check_jwt_login(
    self,
    token: str,
    user_name: str = None,
    node: Node = None,
    exitcode: int = 0,
    message: str = None,
    no_checks: bool = False,
):
    """Check JWT authentication for the specified user with clickhouse-client and http/https."""
    check_clickhouse_client_jwt_login(
        user_name=user_name,
        token=token,
        node=node,
        exitcode=exitcode,
        message=message,
        no_checks=no_checks,
    )
    check_http_https_jwt_login(
        user_name=user_name,
        token=token,
        node=node,
        message=message,
        no_checks=no_checks,
    )
    # check_http_https_jwt_login(user_name=user_name, token=token, https=True, node=node, exitcode=exitcode, message=message)


@TestStep(Given)
def generate_ssh_keys(self, key_type: str = None, algorithm: str = "RS256"):
    """Generate SSH keys and return the public key and private key file path."""
    private_key_file = f"private_key_{getuid()}"
    public_key_file = f"{private_key_file}.pub"

    if algorithm in RSA_algorithms + PSS_algorithms:
        key_type = "rsa"
        command = f"openssl genpkey -algorithm {key_type} -out {private_key_file}"
    elif algorithm in ECDSA_algorithms:
        key_type = "ec"
        curve_map = {
            "ES256": "prime256v1",
            "ES384": "secp384r1",
            "ES512": "secp521r1",
            "ES256K": "secp256k1",
        }
        curve_name = curve_map.get(algorithm)
        command = (
            f"openssl ecparam -name {curve_name} -genkey -noout -out {private_key_file}"
        )
    elif algorithm in EdDSA_algorithms:
        key_type = algorithm
        command = f"openssl genpkey -algorithm {key_type} -out {private_key_file}"
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    try:
        subprocess.run(command, shell=True, check=True)
        subprocess.run(
            f"openssl pkey -in {private_key_file} -pubout -out {public_key_file}",
            shell=True,
            check=True,
        )

        with open(public_key_file, "r") as pub_key_file:
            public_key = pub_key_file.read()

        yield public_key, private_key_file

    finally:
        with Finally("clean up files"):
            if os.path.exists(private_key_file):
                os.remove(private_key_file)
            if os.path.exists(public_key_file):
                os.remove(public_key_file)


def flip_symbol(segment: str) -> str:
    """Flip a specified number of symbols in a Base64 URL-encoded segment."""
    base64_url_chars = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    )
    index = random.randrange(len(segment))
    new_symbol = random.choice(base64_url_chars.replace(segment[index], ""))
    return segment[:index] + new_symbol + segment[index + 1 :]


def swap_two_random_symbols(segment: str) -> str:
    """Swap two random symbols in the given segment, ensuring the swap changes the segment."""
    if len(segment) < 2:
        return segment

    # Check if all characters are identical
    if len(set(segment)) == 1:
        return segment

    segment_list = list(segment)

    while True:
        idx1, idx2 = random.sample(range(len(segment_list)), 2)
        if segment_list[idx1] != segment_list[idx2]:
            break

    segment_list[idx1], segment_list[idx2] = segment_list[idx2], segment_list[idx1]
    return "".join(segment_list)


def corrupt_segment(segment: str, swap: bool, flip: bool) -> str:
    """Corrupt a segment by swapping or flipping symbols."""
    if flip:
        segment = flip_symbol(segment)
    if swap:
        segment = swap_two_random_symbols(segment)
    return segment


@TestStep(Given)
def corrupt_token(
    self, token: str, part: str = "payload", swap=False, flip=False
) -> str:
    """Corrupt the token by swapping two symbols or flipping a symbol
    in the specified part."""

    header, payload, signature = token.split(".")

    if part == "header":
        header = corrupt_segment(header, swap, flip)
    elif part == "payload":
        payload = corrupt_segment(payload, swap, flip)
    elif part == "signature":
        signature = corrupt_segment(signature, swap, flip)
    else:
        raise ValueError(
            "Invalid part specified. Choose 'header', 'payload', or 'signature'."
        )

    return f"{header}.{payload}.{signature}"


@TestStep(Then)
def check_jwt_login_with_corrupted_token(self, token: str):
    """Check that JWT authentication fails with a corrupted token."""

    res_client = check_clickhouse_client_jwt_login(
        token=token,
        no_checks=True,
    )
    res_http = check_http_https_jwt_login(
        token=token,
        no_checks=True,
    )
    assert res_client.exitcode == 131 or res_client.exitcode == 4, error()
    assert (
        "Failed to validate jwt" in res_client.output
        or "Authentication failed" in res_client.output
    ), error()
    assert (
        "Failed to validate jwt" in res_http.output
        or "Authentication failed" in res_http.output
    ), error()
