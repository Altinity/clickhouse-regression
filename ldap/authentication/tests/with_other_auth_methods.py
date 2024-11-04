from testflows.core import *
from testflows.asserts import error
from ldap.authentication.tests.common import *
from ldap.authentication.requirements import *

servers = {
    "openldap1": {
        "host": "openldap1",
        "port": "389",
        "enable_tls": "no",
        "auth_dn_prefix": "cn=",
        "auth_dn_suffix": ",ou=users,dc=company,dc=com",
    },
    "openldap2": {
        "host": "openldap2",
        "port": "636",
        "enable_tls": "yes",
        "auth_dn_prefix": "cn=",
        "auth_dn_suffix": ",ou=users,dc=company,dc=com",
        "tls_require_cert": "never",
    },
}


@TestStep(Then)
def login_and_execute_query(self, username, password, exitcode=None, message=None):
    """Execute `SELECT currentUser()` query with provided username and password."""
    return self.context.node.query(
        "SELECT currentUser() FORMAT TabSeparated",
        settings=[("user", username), ("password", password)],
        exitcode=exitcode or 0,
        message=message,
    )


@TestScenario
def ldap_with_other_auth_methods(
    self,
    server,
):
    """Check that user can have multiple authentications methods in LDAP."""
    self.context.ldap_node = self.context.cluster.node(server)
    ldap_password = "foo1"
    username = "User_" + getuid()

    ch_user = {}
    user = {"cn": username, "userpassword": ldap_password}
    node = self.context.node

    try:
        with ldap_user(**user) as user:
            ch_user["username"] = user["cn"]
            ch_user["server"] = user["_server"]

            with Given("create user with multiple authentication methods"):
                default_password = "foo2"
                plaintext_password = "foo3"
                bcrypt_password = "foo4"
                node.query(
                    (
                        f"CREATE USER {username} IDENTIFIED BY '{default_password}', "
                        f"LDAP SERVER '{ch_user['server']}', plaintext_password BY '{plaintext_password}', "
                        f"bcrypt_password BY '{bcrypt_password}'"
                    )
                )

            with Then("login with ldap"):
                r = login_and_execute_query(username=username, password="foo1")
                assert r.output == username, error()

            with And("login with default auth method"):
                r = login_and_execute_query(username=username, password="foo2")
                assert r.output == username, error()

            with And("login with plaintext_password"):
                r = login_and_execute_query(username=username, password="foo3")
                assert r.output == username, error()

            with And("login with bcrypt_password"):
                r = login_and_execute_query(username=username, password="foo4")
                assert r.output == username

            with And("check that user can not login with invalid password"):
                message = (
                    f"DB::Exception: {username}: Authentication failed: password is incorrect, "
                    "or there is no user with such name."
                )
                r = login_and_execute_query(
                    username=username, password="invalid", exitcode=4, message=message
                )

    finally:
        node.query(f"DROP USER IF EXISTS {username}")


@TestFeature
@Name("multiple authentications methods")
def feature(self, servers=None, node="clickhouse1"):
    """Check that user can authenticate using different methods
    like LDAP, password, and plaintext_password."""

    self.context.node = self.context.cluster.node(node)

    if servers is None:
        servers = globals()["servers"]

    with ldap_servers(servers):
        for scenario in loads(current_module(), Scenario):
            scenario(server="openldap1")
