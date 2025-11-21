import uuid
import hashlib
import bcrypt

import testflows.settings as settings

from contextlib import contextmanager

from testflows.core.name import basename, parentname
from testflows._core.testtype import TestSubType
from testflows.core import *

from helpers.common import (
    create_xml_config_content,
    add_config,
    instrument_clickhouse_server_log,
    check_clickhouse_version,
)
from rbac.helper.tables import table_types


def permutations(table_count=1):
    return [*range((1 << table_count) - 1)]


def getuid():
    if current().subtype == TestSubType.Example:
        testname = (
            f"{basename(parentname(current().name)).replace(' ', '_').replace(',','')}"
        )
    else:
        testname = f"{basename(current().name).replace(' ', '_').replace(',','')}"
    return testname + "_" + str(uuid.uuid1()).replace("-", "_")


@contextmanager
def table(node, name, table_type_name="MergeTree"):
    table_type = table_types[table_type_name]
    try:
        names = name.split(",")
        for name in names:
            with Given(f"I have {name} with engine {table_type_name}"):
                node.query(f"DROP TABLE IF EXISTS {name}")
                node.query(table_type.create_statement.format(name=name))
        yield
    finally:
        for name in names:
            with Finally(f"I drop the table {name}"):
                if table_type.cluster:
                    node.query(
                        f"DROP TABLE IF EXISTS {name} ON CLUSTER {table_type.cluster}"
                    )
                else:
                    node.query(f"DROP TABLE IF EXISTS {name}")


@contextmanager
def user(node, name):
    try:
        names = name.split(",")
        for name in names:
            with Given("I have a user"):
                node.query(f"CREATE USER OR REPLACE {name}")
        yield
    finally:
        for name in names:
            with Finally("I drop the user"):
                node.query(f"DROP USER IF EXISTS {name}")


@contextmanager
def role(node, role):
    try:
        roles = role.split(",")
        for role in roles:
            with Given("I have a role"):
                node.query(f"CREATE ROLE OR REPLACE {role}")
        yield
    finally:
        for role in roles:
            with Finally("I drop the role"):
                node.query(f"DROP ROLE IF EXISTS {role}")


@TestStep(Given)
def row_policy(self, name, table, node=None):
    """Create a row policy with a given name on a given table."""
    if node is None:
        node = self.context.node

    try:
        with Given(f"I create row policy {name}"):
            node.query(f"CREATE ROW POLICY {name} ON {table}")
        yield

    finally:
        with Finally(f"I delete row policy {name}"):
            node.query(f"DROP ROW POLICY IF EXISTS {name} ON {table}")


@TestStep(Given)
def grant_select(self, user, table, node=None):
    """Grant select on a given table to a given user."""
    if node is None:
        node = self.context.node

    try:
        with Given(f"I grant select om table"):
            node.query(f"GRANT SELECT ON {table} TO {user}")
        yield

    finally:
        with Finally(f"I revoke select on table"):
            node.query(f"REVOKE SELECT ON {table} FROM {user}")


@TestStep(Given)
def grant_cluster(self, user, node=None):
    """Grant CLUSTER ON *.* to a given user."""
    if node is None:
        node = self.context.node

    try:
        with Given(f"I grant CLUSTER privilege"):
            node.query(f"GRANT CLUSTER ON *.* TO {user}")
        yield

    finally:
        with Finally(f"I revoke CLUSTER privilege"):
            node.query(f"REVOKE CLUSTER ON *.* FROM {user}")


tables = {
    "table0": 1 << 0,
    "table1": 1 << 1,
    "table2": 1 << 2,
    "table3": 1 << 3,
    "table4": 1 << 4,
    "table5": 1 << 5,
    "table6": 1 << 6,
    "table7": 1 << 7,
}


@contextmanager
def grant_select_on_table(node, grants, target_name, *table_names):
    try:
        tables_granted = []
        for table_number in range(len(table_names)):
            if grants & tables[f"table{table_number}"]:
                with When(f"I grant select privilege on {table_names[table_number]}"):
                    node.query(
                        f"GRANT SELECT ON {table_names[table_number]} TO {target_name}"
                    )

                    tables_granted.append(f"{table_names[table_number]}")

        yield (", ").join(tables_granted)

    finally:
        for table_number in range(len(table_names)):
            with Finally(
                f"I revoke the select privilege on {table_names[table_number]}"
            ):
                node.query(
                    f"REVOKE SELECT ON {table_names[table_number]} FROM {target_name}"
                )


@TestStep(Given)
def add_rbac_config_file(
    self,
    config_d_dir="/etc/clickhouse-server/users.d",
    config_file="rbac.xml",
    timeout=300,
    restart=False,
    node=None,
):
    """Add config to give `default` user ALL and ACCESS MANAGEMENT privileges."""
    entries = {
        "users": {
            "default": {
                "named_collection_control": "1",
                "show_named_collections": "1",
                "show_named_collections_secrets": "1",
            }
        }
    }

    node.command(f"mkdir -p {config_d_dir}")

    config = create_xml_config_content(
        entries, config_file=config_file, config_d_dir=config_d_dir, root="clickhouse"
    )

    return add_config(
        config,
        timeout=timeout,
        restart=restart,
        node=node,
        check_preprocessed=False,
        wait_healthy=False,
        modify=True,
    )


@TestStep(Given)
def create_user(
    self,
    node=None,
    user_name=None,
    identified=None,
    identified_by=None,
    exitcode=None,
    message=None,
    cluster=None,
    expected=None,
    not_identified=False,
    valid_until=None,
):
    """Create user with given name. If name is not provided, it will be generated."""
    if node is None:
        node = self.context.node

    if user_name is None:
        user_name = "user_" + getuid()

    if expected is not None:
        exitcode, message = expected

    query = f"CREATE USER {user_name}"

    if cluster is not None:
        query += f" ON CLUSTER {cluster}"

    if identified:
        query += f" IDENTIFIED WITH {identified}"

    if identified_by:
        query += f" IDENTIFIED BY '{identified_by}'"

    if not_identified:
        query += " NOT IDENTIFIED"

    if valid_until:
        query += f" VALID UNTIL '{valid_until}'"

    try:
        node.query(query, exitcode=exitcode, message=message)
        yield user_name

    finally:
        with Finally("I drop the user if exists"):
            node.query(f"DROP USER IF EXISTS {user_name}")


@TestStep(Given)
def add_identified(
    self,
    user_name,
    identified=None,
    identified_by=None,
    node=None,
    exitcode=None,
    message=None,
    cluster=None,
    expected=None,
):
    """Add new authentication methods to the user while keeping the existing ones."""
    if node is None:
        node = self.context.node

    if expected is not None:
        exitcode, message = expected

    query = f"ALTER USER {user_name}"

    if cluster is not None:
        query += f" ON CLUSTER {cluster}"

    if identified:
        query += f" ADD IDENTIFIED WITH {identified}"

    if identified_by:
        query += f" ADD IDENTIFIED BY {identified_by}"

    node.query(query, exitcode=exitcode, message=message)


@TestStep(Given)
def alter_identified(
    self,
    user_name,
    identified=None,
    identified_by=None,
    node=None,
    exitcode=None,
    message=None,
    cluster=None,
    expected=None,
    not_identified=False,
):
    """Change user's authentication methods."""
    if node is None:
        node = self.context.node

    if expected is not None:
        exitcode, message = expected

    query = f"ALTER USER {user_name}"

    if cluster is not None:
        query += f" ON CLUSTER {cluster}"

    if identified:
        query += f" IDENTIFIED WITH {identified}"

    if identified_by:
        query += f" IDENTIFIED BY {identified_by}"

    if not_identified:
        query += " NOT IDENTIFIED"

    node.query(query, exitcode=exitcode, message=message)


@TestStep(Given)
def reset_auth_methods_to_new(
    self, user_name, cluster=None, node=None, expected=None, exitcode=None, message=None
):
    if node is None:
        node = self.context.node

    if expected is not None:
        exitcode, message = expected

    query = f"ALTER USER {user_name}"

    if cluster is not None:
        query += f" ON CLUSTER {cluster}"

    query += f" RESET AUTHENTICATION METHODS TO NEW"

    node.query(query, exitcode=exitcode, message=message)


def generate_hashed_password_with_salt(password, salt="some_salt"):
    """Generate hashed password with salt using sha256 algorithm."""
    salted_password = password.encode("utf-8") + salt.encode("utf-8")
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return salt, hashed_password


def generate_hashed_password(password):
    """Generate hashed password using SHA-256 algorithm."""
    hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hashed_password


def generate_double_hashed_password(password):
    """Generate double hashed password using SHA-1 algorithm."""
    double_sha1_hash_password = hashlib.sha1(
        hashlib.sha1(password.encode("utf-8")).digest()
    ).hexdigest()
    return double_sha1_hash_password


def generate_bcrypt_hash(password):
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
    return hashed

def user_exists(node, user_name):
    """Check if a user exists in system.users and return True if found, False otherwise."""
    result = node.query(
        f"SELECT name FROM system.users WHERE name='{user_name}'",
    ).output.strip()
    return result == user_name