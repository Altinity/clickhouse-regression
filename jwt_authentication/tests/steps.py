from testflows.core import *
from testflows.asserts import error

import jwt
import datetime

from helpers.common import (
    create_xml_config_content,
    add_config,
    remove_config,
)


def create_static_jwt(
    user_name: str,
    secret: str = "my_secret",
    algorithm: str = "HS256",
    payload: dict = None,
    expiration_minutes: int = None,
) -> str:
    """
    Create a JWT using a static secret and a specified encryption algorithm.
    Supported algorithms:
    | HMSC  | RSA   | ECDSA  | PSS   | EdDSA   |
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

    if expiration_minutes:
        expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=expiration_minutes
        )
        payload["exp"] = expiration

    return jwt.encode(payload, secret, algorithm=algorithm)


@TestStep(Given)
def change_clickhouse_settings(
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
    """Change clickhouse configuration files: users.xml and config.xml."""
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
        return add_config(config, restart=restart, modify=modify, user=user, node=node)


@TestStep(Given)
def remove_jwt_user_from_users_xml(
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
    change_clickhouse_settings(entries=entries)


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
    user_name: str,
    token: str,
    node: Node = None,
    exitcode: int = 0,
    message: str = None,
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
        )

        if exitcode == 0:
            assert res.output == user_name, error()


@TestStep(Then)
def check_http_https_jwt_login(
    self,
    user_name: str,
    token: str,
    ip: str = "localhost",
    https: bool = False,
    node: Node = None,
    message: str = None,
):
    """Check JWT authentication for the specified user with http/https."""
    if node is None:
        node = self.context.node

    http_prefix = "https" if https else "http"

    with By(f"check jwt authentication with {http_prefix}"):
        curl = f'curl -H "X-ClickHouse-JWT-Token: Bearer {token}" "{http_prefix}://{ip}:8123/?query=SELECT%20currentUser()"'
        res = node.command(curl, message=message).output

        if message is None:
            assert res == user_name, error()


@TestStep(Then)
def check_jwt_login(
    self,
    user_name: str,
    token: str,
    node: Node = None,
    exitcode: int = 0,
    message: str = None,
):
    """Check JWT authentication for the specified user with clickhouse-client and http/https."""
    check_clickhouse_client_jwt_login(
        user_name=user_name, token=token, node=node, exitcode=exitcode, message=message
    )
    check_http_https_jwt_login(
        user_name=user_name, token=token, node=node, message=message
    )
    # check_http_https_jwt_login(user_name=user_name, token=token, https=True, node=node, exitcode=exitcode, message=message)