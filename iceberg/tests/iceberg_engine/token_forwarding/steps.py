"""Steps for the DataLakeCatalog token forwarding tests (Altinity/ClickHouse#2329).

Users authenticate to ClickHouse with HS256 JWTs validated by a
``jwt_static_key`` token processor and are materialized by a ``token`` user
directory with the ``token_users`` role. Catalog traffic goes to the
``token-mocks`` service (``mock/token_mocks.py``), which records every
credential ClickHouse presents and proxies catalog calls to the
``token-forwarding-rest`` Iceberg REST fixture.
"""

import json
import time
import urllib.parse

import jwt
import pyarrow as pa
import requests

from testflows.core import *
from testflows.asserts import error

from helpers.common import add_config, create_xml_config_content, getuid

import iceberg.tests.steps.catalog as catalog_steps

USER_SECRET = "token_forwarding_user_secret"
ISSUED_SECRET = "token_forwarding_issued_secret"
TOKEN_PROCESSOR = "token_forwarding_hs256"
TOKEN_ROLE = "token_users"

MOCK_CONTROL_URL = "http://localhost:8195"
CATALOG_URL = "http://token-mocks:8181/v1"
TOKEN_EXCHANGE_URL = "http://token-mocks:8190/token"
STS_URL = "http://token-mocks:8191"
LOCAL_REST_URL = "http://localhost:8196/"
STORAGE_ENDPOINT = "http://minio:9000/warehouse"
WAREHOUSE = "s3://bucket1/"
SERVICE_CLIENT_ID = "clickhouse"
SERVICE_CLIENT_SECRET = "service_secret"
SERVICE_CREDENTIAL = f"{SERVICE_CLIENT_ID}:{SERVICE_CLIENT_SECRET}"
ROLE_ARN = "arn:aws:iam::000000000000:role/data-lake-reader"

ACCESS_TOKEN_TYPE = "urn:ietf:params:oauth:token-type:access_token"
JWT_TOKEN_TYPE = "urn:ietf:params:oauth:token-type:jwt"
ID_TOKEN_TYPE = "urn:ietf:params:oauth:token-type:id_token"
TOKEN_EXCHANGE_GRANT = "urn:ietf:params:oauth:grant-type:token-exchange"

ALLOWED_HOSTS = [
    "token-mocks",
    "rest",
    "minio",
    "localstack",
    "ice-rest-catalog",
    "localhost",
    "clickhouse1",
    "clickhouse2",
    "clickhouse3",
]

# clickhouse-client exits with the server error code modulo 256.
BAD_ARGUMENTS = 36
UNACCEPTABLE_URL = 491 % 256
ACCESS_DENIED = 497 % 256
DATALAKE_DATABASE_ERROR = 736 % 256
CATALOG_USER_TOKEN_NOT_AVAILABLE = 780 % 256

NOT_AVAILABLE = "CATALOG_USER_TOKEN_NOT_AVAILABLE"
FORWARDING_DISABLED_MESSAGE = (
    "requires token forwarding. Set `enable_token_forwarding = 1` and reconnect"
)
NO_TOKEN_MESSAGE = "this session carries no bearer token"

INSERT_SETTINGS = [
    ("allow_insert_into_iceberg", 1),
    ("write_full_path_in_iceberg_metadata", 1),
]


def feature_available(node):
    """Return True when the server knows `enable_token_forwarding`."""
    result = node.query(
        "SELECT count() FROM system.server_settings WHERE name = 'enable_token_forwarding'",
        steps=False,
        no_checks=True,
    )
    return result.output.strip() == "1"


def make_token(sub, **claims):
    """Mint an HS256 user token that ClickHouse accepts.

    Extra claims change the token (and its fingerprint) without changing the user.
    """
    return jwt.encode({"sub": sub, **claims}, USER_SECRET, algorithm="HS256")


def token_sub(token):
    return jwt.decode(token, options={"verify_signature": False}).get("sub")


def table_identifier(database, namespace, table):
    """Backtick-escaped `database.namespace.table` identifier for `node.query`."""
    return f"{database}.\\`{namespace}.{table}\\`"


def http_table_identifier(database, namespace, table):
    """Unescaped identifier for queries sent over HTTP."""
    return f"{database}.`{namespace}.{table}`"


def mock_call(method, path, payload=None, timeout=180):
    response = requests.request(
        method, f"{MOCK_CONTROL_URL}{path}", json=payload, timeout=timeout
    )
    response.raise_for_status()
    return response.json()


@TestStep(Given)
def mocks_are_running(self, timeout=60):
    """Wait for the `token-mocks` service to answer its health check."""
    deadline = time.time() + timeout
    while True:
        try:
            mock_call("GET", "/_mock/health", timeout=5)
            return
        except requests.RequestException as e:
            if time.time() > deadline:
                fail(f"token-mocks service is not reachable at {MOCK_CONTROL_URL}: {e}")
            time.sleep(1)


@TestStep(Given)
def clean_mocks(self):
    """Reset recorded requests and mock behaviour before and after the test."""
    mock_call("POST", "/_mock/reset")
    try:
        yield
    finally:
        with Finally("reset token-mocks"):
            mock_call("POST", "/_mock/reset")


@TestStep(Given)
def configure_mocks(self, **services):
    """Change mock behaviour, e.g. `configure_mocks(catalog={"require_token": True})`."""
    return mock_call("POST", "/_mock/configure", services)


@TestStep(When)
def reset_recorded_requests(self):
    """Forget recorded requests but keep the configured behaviour."""
    config = mock_call("POST", "/_mock/configure", {})
    mock_call("POST", "/_mock/reset")
    mock_call("POST", "/_mock/configure", config)


def recorded_requests(service=None):
    path = "/_mock/requests" + (f"?service={service}" if service else "")
    return mock_call("GET", path)


def catalog_requests():
    """Catalog API calls (without the client credentials grant)."""
    return [
        r
        for r in recorded_requests("catalog")
        if not r["path"].endswith("/oauth/tokens")
    ]


def service_token_requests():
    return [
        r for r in recorded_requests("catalog") if r["path"].endswith("/oauth/tokens")
    ]


def token_requests():
    return recorded_requests("token")


def sts_requests():
    return recorded_requests("sts")


@TestStep(When)
def http_query(
    self,
    sql,
    token=None,
    user=None,
    password=None,
    params=None,
    node=None,
    expected_status=None,
):
    """Send `sql` to the ClickHouse HTTP interface through the mock relay.

    Returns `(status, body)`. The bearer token is not written to the test log.
    """
    if node is None:
        node = self.context.node

    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    if user is not None:
        headers["X-ClickHouse-User"] = user
        headers["X-ClickHouse-Key"] = password or ""

    query = urllib.parse.urlencode(params or {})
    url = f"http://{node.name}:8123/" + (f"?{query}" if query else "")
    identity = f"token of {token_sub(token)}" if token else f"user {user}"
    note(f"POST {url} as {identity}: {sql}")

    result = mock_call(
        "POST",
        "/_mock/relay",
        {"url": url, "method": "POST", "headers": headers, "body": sql},
    )
    note(f"HTTP {result['status']}: {result['body'][:2000]}")

    if expected_status is not None:
        assert result["status"] == expected_status, error(
            f"expected HTTP {expected_status}, got {result['status']}: {result['body']}"
        )
    return result["status"], result["body"]


@TestStep(When)
def jwt_query(self, sql, token, node=None, settings=None, **kwargs):
    """Run `sql` with `clickhouse client --jwt <token>`."""
    if node is None:
        node = self.context.node
    return node.query(sql, settings=[("jwt", token)] + list(settings or []), **kwargs)


def token_forwarding_config_entries(enable_token_forwarding=True, allowed_hosts=None):
    entries = {
        "enable_token_forwarding": "1" if enable_token_forwarding else "0",
        "token_processors": {
            TOKEN_PROCESSOR: {
                "type": "jwt_static_key",
                "algo": "HS256",
                "static_key": USER_SECRET,
                "static_key_in_base64": "false",
                "allow_no_expiration": "true",
            }
        },
        "user_directories": {
            "token": {
                "processor": TOKEN_PROCESSOR,
                "default_profile": "default",
                "common_roles": {TOKEN_ROLE: ""},
            }
        },
    }
    if allowed_hosts is not None:
        entries["remote_url_allow_hosts"] = [{"host": host} for host in allowed_hosts]
    return entries


@TestStep(Given)
def token_role(self, node=None):
    """Create the role every token user receives through the token user directory."""
    if node is None:
        node = self.context.node
    try:
        node.query(f"CREATE ROLE IF NOT EXISTS {TOKEN_ROLE}")
        node.query(
            f"GRANT SHOW, SELECT, INSERT, CHECK, CREATE TABLE, DROP TABLE, ALTER, "
            f"S3, REMOTE ON *.* TO {TOKEN_ROLE}"
        )
        yield TOKEN_ROLE
    finally:
        with Finally(f"drop role {TOKEN_ROLE}"):
            node.query(f"DROP ROLE IF EXISTS {TOKEN_ROLE}")


@TestStep(Given)
def server_config_file(self, config, node):
    """Add a `config.d` file to `node` and restart it; removed on cleanup."""
    return add_config(config, restart=True, node=node)


@TestStep(Given)
def token_forwarding_server_config(
    self, nodes=None, enable_token_forwarding=True, allowed_hosts=None
):
    """Enable token authentication and token forwarding on `nodes` (restarts them)."""
    if nodes is None:
        nodes = self.context.nodes

    entries = token_forwarding_config_entries(
        enable_token_forwarding=enable_token_forwarding, allowed_hosts=allowed_hosts
    )
    for node in nodes:
        with By(f"creating the {TOKEN_ROLE} role on {node.name}"):
            token_role(node=node)
        with And(f"adding the token forwarding config on {node.name}"):
            server_config_file(
                config=create_xml_config_content(entries, "token_forwarding.xml"),
                node=node,
            )


@TestStep(When)
def set_token_forwarding(self, enabled, node=None):
    """Toggle `enable_token_forwarding` and apply it with `SYSTEM RELOAD CONFIG`."""
    if node is None:
        node = self.context.node
    path = "/etc/clickhouse-server/config.d/token_forwarding.xml"
    old, new = ("0", "1") if enabled else ("1", "0")
    node.command(
        f"sed -i 's|<enable_token_forwarding>{old}</enable_token_forwarding>|"
        f"<enable_token_forwarding>{new}</enable_token_forwarding>|' {path}",
        exitcode=0,
    )
    node.query("SYSTEM RELOAD CONFIG")


@TestStep(Given)
def token_forwarding_disabled(self, node=None):
    """Turn `enable_token_forwarding` off for the test and back on afterwards."""
    if node is None:
        node = self.context.node
    try:
        set_token_forwarding(enabled=False, node=node)
        yield
    finally:
        with Finally("turn token forwarding back on"):
            set_token_forwarding(enabled=True, node=node)


def settings_clause(settings):
    def value(v):
        if isinstance(v, bool):
            return "1" if v else "0"
        if isinstance(v, int):
            return str(v)
        return "'" + str(v) + "'"

    return ", ".join(f"{name} = {value(v)}" for name, v in settings.items())


def forwarding_database_settings(
    catalog="rest", exchange=False, actor=False, **overrides
):
    if catalog == "glue":
        settings = {
            "catalog_type": "glue",
            "region": "us-east-1",
            "storage_endpoint": STORAGE_ENDPOINT,
            "aws_role_arn": ROLE_ARN,
            "aws_sts_endpoint": STS_URL,
            "oauth_forward_user_token": 1,
        }
    else:
        settings = {
            "catalog_type": "rest",
            "warehouse": WAREHOUSE,
            "storage_endpoint": STORAGE_ENDPOINT,
            "oauth_forward_user_token": 1,
        }
        if exchange:
            settings["catalog_credential"] = SERVICE_CREDENTIAL
            settings["oauth_token_exchange_uri"] = TOKEN_EXCHANGE_URL
        if actor:
            settings["oauth_forward_actor_token"] = 1
    settings.update(overrides)
    return {k: v for k, v in settings.items() if v is not None}


def create_database_query(
    database_name,
    catalog="rest",
    url=None,
    s3_access_key_id=None,
    s3_secret_access_key=None,
    settings=None,
):
    if url is None:
        url = "http://localstack:4566" if catalog == "glue" else CATALOG_URL

    arguments = f"'{url}'"
    if s3_access_key_id is not None:
        arguments += f", '{s3_access_key_id}', '{s3_secret_access_key}'"

    experimental = (
        "allow_experimental_database_glue_catalog"
        if catalog == "glue"
        else "allow_experimental_database_iceberg"
    )
    query = f"SET {experimental} = 1; CREATE DATABASE {database_name} ENGINE = DataLakeCatalog({arguments})"
    if settings:
        query += f" SETTINGS {settings_clause(settings)}"
    return query


@TestStep(Given)
def forwarding_database(
    self,
    database_name=None,
    catalog=None,
    exchange=False,
    actor=False,
    url=None,
    with_storage_keys=True,
    node=None,
    exitcode=None,
    message=None,
    **settings,
):
    """Create a DataLakeCatalog database with `oauth_forward_user_token = 1`.

    Extra keyword arguments override database settings (`None` removes one).
    """
    if node is None:
        node = self.context.node
    if catalog is None:
        catalog = getattr(self.context, "catalog", "rest")
    if database_name is None:
        database_name = f"token_forwarding_{getuid()}"

    keys = {}
    if with_storage_keys and catalog != "glue":
        keys = {
            "s3_access_key_id": self.context.minio_root_user,
            "s3_secret_access_key": self.context.minio_root_password,
        }

    query = create_database_query(
        database_name,
        catalog=catalog,
        url=url,
        settings=forwarding_database_settings(
            catalog=catalog, exchange=exchange, actor=actor, **settings
        ),
        **keys,
    )
    try:
        node.query(
            query,
            exitcode=exitcode,
            message=message,
            ignore_exception=exitcode is not None,
        )
        yield database_name
    finally:
        with Finally(f"drop database {database_name}"):
            node.query(f"DROP DATABASE IF EXISTS {database_name} SYNC")


@TestStep(Given)
def local_rest_catalog(self):
    """PyIceberg client that talks to the `rest` fixture directly (not through the proxy)."""
    return catalog_steps.create_catalog(
        uri=LOCAL_REST_URL,
        catalog_type=catalog_steps.CATALOG_TYPE,
        s3_endpoint="http://localhost:9002",
        s3_access_key_id=self.context.minio_root_user,
        s3_secret_access_key=self.context.minio_root_password,
        clean_up_minio_bucket=False,
    )


@TestStep(Given)
def catalog_table(self, namespace=None, table_name=None, rows=None):
    """Create a namespace and a three column table in the `rest` fixture.

    Returns `(namespace, table_name, rows)`; `rows` are `(name, integer)` pairs.
    """
    if namespace is None:
        namespace = f"ns_{getuid()}"
    if table_name is None:
        table_name = f"t_{getuid()}"
    if rows is None:
        rows = [("alice_row", 1), ("bob_row", 2), ("carol_row", 3)]

    catalog = local_rest_catalog()

    with By(f"creating namespace {namespace}"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"creating table {namespace}.{table_name}"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            location=f"s3://warehouse/data/{namespace}/{table_name}",
        )

    if rows:
        with And(f"inserting {len(rows)} rows"):
            table.append(
                pa.Table.from_pylist(
                    [
                        {"name": name, "double": 1.0, "integer": value}
                        for name, value in rows
                    ]
                )
            )

    return namespace, table_name, rows


def expected_rows(rows):
    return "\n".join(f"{name}\t{value}" for name, value in sorted(rows))


def select_rows_sql(database, namespace, table, escaped=True):
    identifier = (
        table_identifier(database, namespace, table)
        if escaped
        else http_table_identifier(database, namespace, table)
    )
    return f"SELECT name, integer FROM {identifier} ORDER BY name"


def query_log_profile_event(node, query_id, event):
    node.query("SYSTEM FLUSH LOGS")
    result = node.query(
        f"SELECT sum(ProfileEvents['{event}']) FROM system.query_log "
        f"WHERE query_id = '{query_id}' "
        f"AND type IN ('QueryFinish', 'ExceptionBeforeStart', 'ExceptionWhileProcessing')"
    )
    return int(result.output.strip() or 0)


def event_value(node, event):
    """Server-wide `system.events` counter."""
    result = node.query(f"SELECT sum(value) FROM system.events WHERE event = '{event}'")
    return int(result.output.strip() or 0)


def metric_value(node, metric):
    result = node.query(
        f"SELECT sum(value) FROM system.metrics WHERE metric = '{metric}'"
    )
    return int(result.output.strip() or 0)


def tokens_presented(requests_, kind=None):
    """Distinct `(token_kind, sub)` pairs presented to the catalog."""
    return {
        (r["token_kind"], r["sub"])
        for r in requests_
        if kind is None or r["token_kind"] == kind
    }


def assert_not_in_logs(node, secret, what):
    """Check that `secret` is absent from the server logs and system tables."""
    with By(f"checking the server log files for {what}"):
        result = node.command(
            f"grep -rF -- '{secret}' /var/log/clickhouse-server/ | head -c 2000",
            no_checks=True,
            steps=False,
        )
        assert result.output.strip() == "", error(f"{what} found in the server logs")

    with And(f"checking system log tables for {what}"):
        node.query("SYSTEM FLUSH LOGS")
        existing = node.query(
            "SELECT name FROM system.tables WHERE database = 'system' "
            "AND name IN ('query_log', 'text_log')"
        ).output.split()
        for table, column in (
            ("query_log", "query || ' ' || exception"),
            ("text_log", "message"),
        ):
            if table not in existing:
                continue
            table = f"system.{table}"
            result = node.query(
                f"SELECT count() FROM {table} WHERE position({column}, '{secret}') > 0",
                no_checks=True,
            )
            assert result.output.strip() in ("0", ""), error(f"{what} found in {table}")
