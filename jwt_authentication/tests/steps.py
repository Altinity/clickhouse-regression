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

from jwt_authentication.tests.static_key.model import Model


from helpers.common import (
    create_xml_config_content,
    add_config,
    remove_config,
    getuid,
)

algorithm_groups = {
    "HMAC": ["HS256", "HS384", "HS512"],
    "RSA": ["RS256", "RS384", "RS512"],
    "ECDSA": ["ES256", "ES384", "ES512", "ES256K"],
    "PSS": ["PS256", "PS384", "PS512"],
    "EdDSA": ["Ed25519", "Ed448"],
}


def algorithm_from_same_group(algorithm1: str, algorithm2: str) -> bool:
    """Check if two algorithms are from the same group."""
    group1 = next(
        (group for group, algs in algorithm_groups.items() if algorithm1 in algs), None
    )
    group2 = next(
        (group for group, algs in algorithm_groups.items() if algorithm2 in algs), None
    )
    return group1 == group2


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
        or algorithm.startswith("PS")
    ):
        if private_key_path is None:
            raise ValueError(
                "Private key path must be provided for asymmetric algorithms"
            )
        with open(
            private_key_path,
            "r",
        ) as key_file:
            private_key = key_file.read()

        if algorithm.startswith("Ed"):
            algorithm = "EdDSA"

        note(algorithm)
        return jwt.encode(payload, private_key, algorithm=algorithm, headers=headers)


def get_public_key_from_private(private_key_path: str) -> str:
    """Get the public key from the private key."""
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )

    public_key = private_key.public_key()

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return public_key_pem.decode()


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
    node: Node = None,
):
    """Add static key validator to the config.xml."""

    entries = {"jwt_validators": {}}
    entries["jwt_validators"][f"{validator_id}"] = {}

    if algorithm is not None:
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
        node=node,
    )


def to_base64_url(data):
    """Convert data to base64 URL encoding."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def to_base64(data: str) -> str:
    """Convert string to base64 encoding."""
    base64_data = base64.b64encode(data.encode("utf-8")).decode("utf-8")
    return base64_data


def get_modulus(public_key: str) -> str:
    """Get the modulus from the public key."""
    public_key = serialization.load_pem_public_key(public_key.encode())
    return to_base64_url(
        public_key.public_numbers().n.to_bytes(
            (public_key.public_numbers().n.bit_length() + 7) // 8, byteorder="big"
        )
    )


def get_exponent(public_key: str) -> str:
    """Get the exponent from the public key."""
    public_key = serialization.load_pem_public_key(public_key.encode())
    return to_base64_url(
        public_key.public_numbers().e.to_bytes(
            (public_key.public_numbers().e.bit_length() + 7) // 8, byteorder="big"
        )
    )


@TestStep(Given)
def create_static_jwks_key_content(
    self,
    algorithm: str = None,
    public_key_str: str = None,
    key_id: str = None,
    key_type: str = None,
) -> dict:
    """Create static JWKS content."""
    result = {}

    with By("retrieve modulus and exponent from public key"):
        if public_key_str is not None:
            modulus = define("modulus", get_modulus(public_key_str))
            exponent = define("exponent", get_exponent(public_key_str))
            result["n"] = modulus
            result["e"] = exponent

    if key_type is None:
        result["kty"] = key_type

    if algorithm is not None:
        result["alg"] = algorithm

    if key_id is not None:
        result["kid"] = key_id

    return result


@TestStep(Given)
def add_static_jwks_validator_to_config_xml(
    self,
    validator_id: str,
    keys: list = None,
    algorithm: str = "RS256",
    key_id: str = "mykid",
    public_key_str: str = None,
    key_type: str = "RSA",
    node: Node = None,
):
    """Add static key validator to the config.xml."""
    if node is None:
        node = self.context.node

    with By("create static JWKS content"):
        if keys is None:
            keys = [
                create_static_jwks_key_content(
                    algorithm=algorithm,
                    public_key_str=public_key_str,
                    key_id=key_id,
                    key_type=key_type,
                )
            ]

    with And("build entries and add static jwks validator to the config.xml"):
        entries = {"jwt_validators": {}}
        entries["jwt_validators"][f"{validator_id}"] = {}
        static_jwks_content = {
            "keys": keys,
        }
        entries["jwt_validators"][f"{validator_id}"]["static_jwks"] = json.dumps(
            static_jwks_content
        )

        change_clickhouse_config(
            entries=entries,
            config_d_dir="/etc/clickhouse-server/config.d",
            preprocessed_name="config.xml",
            node=node,
        )


@TestStep(Given)
def update_json_content(
    self, keys, node=None, url="http://jwks_server:8080/parameters"
):
    """Update JWKS content on the server."""
    if node is None:
        node = self.context.node

    json_data = json.dumps(keys)

    curl_command = (
        "curl "
        "--request POST "
        "--header 'Content-Type: application/json' "
        f"--data '{json_data}' "
        f"{url}"
    )

    result = node.command(curl_command)

    note(result.output)


@TestStep(Given)
def add_dynamic_jwks_validator_to_config_xml(
    self,
    validator_id: str = None,
    keys: list = None,
    algorithm: str = "RS256",
    key_id: str = "mykid",
    public_key_str: str = None,
    key_type: str = "RSA",
    node: Node = None,
    uri=None,
):
    """Add static key validator to the config.xml."""
    if node is None:
        node = self.context.node

    with By("create keys content"):
        if keys is None:
            keys = [
                create_static_jwks_key_content(
                    algorithm=algorithm,
                    public_key_str=public_key_str,
                    key_id=key_id,
                    key_type=key_type,
                )
            ]

    if uri is not None:
        with By("build entries and add dynamic jwks validator to the config.xml"):
            if validator_id is None:
                validator_id = f"jwks_server_{getuid()}"

            entries = {"jwt_validators": {}}
            entries["jwt_validators"][f"{validator_id}"] = {"uri": uri}

            change_clickhouse_config(
                entries=entries,
                config_d_dir="/etc/clickhouse-server/config.d",
                preprocessed_name="config.xml",
                node=node,
            )

    with And("update JSON content"):
        jwks_content = define(
            "jwks content",
            {
                "keys": keys,
            },
        )
        update_json_content(keys=jwks_content, node=node)

    with And("check that handle was updated"):
        curl_command = f"curl http://jwks_server:8080/.well-known/jwks.json"
        result = node.command(curl_command)
        note(result.output)
        note(jwks_content)
        for retry in retries(10, delay=1):
            with retry:
                assert result.output == json.dumps(jwks_content), error()


@TestStep(Given)
def create_user_with_jwt_auth(
    self,
    user_name: str,
    node: Node = None,
    claims: dict = {},
    cluster: str = None,
    if_not_exists: bool = False,
):
    """Create a user with JWT authentication."""
    if node is None:
        node = self.context.node

    if_not_exists = "IF NOT EXISTS" if if_not_exists else ""

    query = f"CREATE USER {if_not_exists} {user_name} "

    if cluster is not None:
        query += f"ON CLUSTER {cluster} "

    query += "IDENTIFIED WITH JWT "

    if claims is not None:
        query += f"CLAIMS '{claims}' "

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
    use_model: Model = None,
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

    if use_model is not None:
        expect = use_model.expect()
        expect(r=res)

    if exitcode == 0 and not no_checks:
        assert res.output == user_name, error()

    return res


@TestStep(Then)
def check_clickhouse_client_password_login(
    self,
    user_name: str,
    password: str = "",
    node: Node = None,
    exitcode: int = 0,
    message: str = None,
    no_checks: bool = False,
):
    """Check password authentication for the specified user with clickhouse-client."""
    if node is None:
        node = self.context.node

    with By("check jwt authentication with clickhouse-client"):
        res = node.query(
            "SELECT currentUser()",
            settings=[("password", password), ("user", user_name)],
            exitcode=exitcode,
            message=message,
            no_checks=no_checks,
        )

    if exitcode == 0 and not no_checks:
        assert res.output == user_name, error()

    if exitcode != 0:
        assert "DB::Exception" in res.output, error()
        assert message in res.output, error()
        assert res.exitcode == exitcode, error()

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
    ignore_ssl_verification = "-k" if https else ""
    port = 8443 if https else 8123

    with By(f"check jwt authentication with {http_prefix}"):
        curl = (
            f'curl {ignore_ssl_verification} -H "X-ClickHouse-JWT-Token: Bearer {token}" '
            f'"{http_prefix}://{ip}:{port}/?query=SELECT%20currentUser()"'
        )
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
    check_http_https_jwt_login(
        user_name=user_name,
        token=token,
        https=True,
        node=node,
        message=message,
        no_checks=no_checks,
    )


@TestStep(Then)
def expect_jwt_authentication_error(self, token):
    """Expect that JWT authentication fails."""
    res = check_clickhouse_client_jwt_login(
        token=token,
        no_checks=True,
    )
    exitcode = 4
    message = "Authentication failed: password is incorrect, or there is no user with such name."

    assert (
        res.exitcode == exitcode
    ), f"expected exitcode {exitcode} but got {res.exitcode}"
    assert "DB::Exception" in res.output, f"expected 'DB::Exception' in '{res.output}'"
    assert message in res.output, f"expected '{message}' in '{res.output}'"


@TestStep(Given)
def generate_ssh_keys(self, key_type: str = None, algorithm: str = "RS256"):
    """Generate SSH keys and return the public key and private key file path."""
    private_key_file = f"private_key_{getuid()}"
    public_key_file = f"{private_key_file}.pub"

    if algorithm in algorithm_groups["RSA"] + algorithm_groups["PSS"]:
        key_type = "rsa"
        command = f"openssl genpkey -algorithm {key_type} -out {private_key_file}"
    elif algorithm in algorithm_groups["ECDSA"]:
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
    elif algorithm in algorithm_groups["EdDSA"]:
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


def flip_symbol(segment: str, index=None) -> str:
    """Flip one symbol in the given segment. If index is not specified, choose a random index."""
    segment_chars = set(segment)

    if index is None:
        index = random.randrange(len(segment))

    available_chars = segment_chars - {segment[index]}
    new_symbol = random.choice(list(available_chars))
    return segment[:index] + new_symbol + segment[index + 1 :]


def swap_two_random_symbols(segment: str, idx1=None, idx2=None) -> str:
    """Swap two random symbols in the given segment, ensuring the swap changes the segment."""
    if len(segment) < 2:
        return segment

    # Check if all characters are identical
    if len(set(segment)) == 1:
        return segment

    segment_list = list(segment)

    while True:
        if idx1 is None or idx2 is None:
            idx1, idx2 = random.sample(range(len(segment_list)), 2)

        if segment_list[idx1] != segment_list[idx2]:
            break

    segment_list[idx1], segment_list[idx2] = segment_list[idx2], segment_list[idx1]
    return "".join(segment_list)


def corrupt_segment(
    segment: str, swap: bool, flip: bool, flip_idx=None, swap_idx1=None, swap_idx2=None
) -> str:
    """Corrupt a segment by swapping or flipping symbols."""
    if flip:
        note("Flipping a symbol")
        segment = flip_symbol(segment=segment, index=flip_idx)
    if swap:
        note("Swapping two symbols")
        segment = swap_two_random_symbols(
            segment=segment, idx1=swap_idx1, idx2=swap_idx2
        )
    return segment


@TestStep(Given)
def corrupt_token_part(
    self,
    token: str,
    part: str = "payload",
    swap=False,
    flip=False,
    flip_idx=None,
    swap_idx1=None,
    swap_idx2=None,
) -> str:
    """Corrupt the token by swapping two symbols or flipping a symbol
    in the specified part."""

    header, payload, signature = token.split(".")

    if part == "header":
        header = corrupt_segment(
            segment=header,
            swap=swap,
            flip=flip,
            flip_idx=flip_idx,
            swap_idx1=swap_idx1,
            swap_idx2=swap_idx2,
        )
    elif part == "payload":
        payload = corrupt_segment(
            segment=payload,
            swap=swap,
            flip=flip,
            flip_idx=flip_idx,
            swap_idx1=swap_idx1,
            swap_idx2=swap_idx2,
        )
    elif part == "signature":
        signature = corrupt_segment(
            segment=signature,
            swap=swap,
            flip=flip,
            flip_idx=flip_idx,
            swap_idx1=swap_idx1,
            swap_idx2=swap_idx2,
        )
    else:
        raise ValueError(
            "Invalid part specified. Choose 'header', 'payload', or 'signature'."
        )

    return f"{header}.{payload}.{signature}"


@TestStep(Then)
def expect_corrupted_token_error(self, token: str):
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


@TestStep(Then)
def expect_authentication_error(self, r):
    """Expect given exitcode and message in the output."""
    exitcode = 4
    message = "Authentication failed: password is incorrect, or there is no user with such name."

    assert r.exitcode == exitcode, f"expected exitcode {exitcode} but got {r.exitcode}"
    assert "DB::Exception" in r.output, f"expected 'DB::Exception' in '{r.output}'"
    assert message in r.output, f"expected '{message}' in '{r.output}'"


@TestStep(Then)
def expect_successful_login(self, r, user_name=None):
    """Expect successful authentication."""
    assert r.exitcode == 0, f"expected exitcode 0 but got {r.exitcode}"
    assert (
        "DB::Exception" not in r.output
    ), f"unexpected 'DB::Exception' in '{r.output}'"
    assert user_name in r.output, f"expected '{user_name}' in '{r.output}'"


def flip_bits(binary_string, idx=None, n=None):
    """
    Flips bits in a binary string. If an index is provided, flips only the bit at that index.
    If n is provided, flips n random bits."""
    binary_list = list(binary_string)

    if idx is not None:
        if 0 <= idx < len(binary_list):
            binary_list[idx] = "1" if binary_list[idx] == "0" else "0"
        else:
            raise ValueError("Index out of range.")

    if n is not None:
        for _ in range(n):
            idx = random.randint(0, len(binary_list) - 1)
            binary_list[idx] = "1" if binary_list[idx] == "0" else "0"

    return "".join(binary_list)


def base64_to_binary(base64_str):
    """Converts a Base64-encoded string into a binary sequence (0 and 1)."""
    padded_base64_str = base64_str + "=" * (4 - len(base64_str) % 4)
    byte_data = base64.urlsafe_b64decode(padded_base64_str)

    binary_sequence = "".join(f"{byte:08b}" for byte in byte_data)
    return binary_sequence


def binary_to_base64(binary_sequence):
    """Converts a binary sequence (0 and 1) back into a Base64-encoded string."""
    byte_data = bytes(
        int(binary_sequence[i : i + 8], 2) for i in range(0, len(binary_sequence), 8)
    )
    base64_str = base64.urlsafe_b64encode(byte_data).rstrip(b"=").decode("utf-8")
    return base64_str
