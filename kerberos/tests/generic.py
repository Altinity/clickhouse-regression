from testflows.core import *
from kerberos.tests.common import *
from kerberos.requirements.requirements import *

import time


@TestScenario
@Requirements(RQ_SRS_016_Kerberos_Ping("1.0"))
def ping(self):
    """Containers should be reachable"""
    ch_nodes = self.context.ch_nodes
    cmd = "timeout 0.1 curl -v telnet://kerberos:88"

    for i in range(3):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                with When(f"ch_{i} {cmd}"):
                    r = ch_nodes[i].command(cmd, no_checks=True)
                with Then(f"Connection should succeed"):
                    assert (
                        "Connected to kerberos" in r.output
                        or "Established connection to kerberos" in r.output
                    ), error()


@TestScenario
@Requirements(RQ_SRS_016_Kerberos_ValidUser_XMLConfiguredUser("1.0"))
def xml_configured_user(self):
    """ClickHouse SHALL accept Kerberos authentication for valid XML-configured user"""
    ch_nodes = self.context.ch_nodes

    with Given("kinit for client"):
        kinit_no_keytab(node=self.context.bash_tools)

    with And("kinit for server"):
        create_server_principal(node=ch_nodes[0])

    with When("I attempt to authenticate"):
        r = self.context.bash_tools.command(test_select_query(node=ch_nodes[0]))

    with Then(f"I expect 'kerberos_user'"):
        assert r.output == "kerberos_user", error()


@TestScenario
@Requirements(RQ_SRS_016_Kerberos_ValidUser_RBACConfiguredUser("1.0"))
def rbac_configured_user(self):
    """ClickHouse SHALL accept Kerberos authentication for valid RBAC-configured user"""
    ch_nodes = self.context.ch_nodes

    with Given("kinit for client"):
        kinit_no_keytab(node=self.context.bash_tools, principal="krb_rbac")

    with And("kinit for server"):
        create_server_principal(node=ch_nodes[0])

    with When("I create a RBAC user"):
        ch_nodes[0].query(
            "CREATE USER krb_rbac IDENTIFIED WITH kerberos REALM 'EXAMPLE.COM'"
        )

    with When("I attempt to authenticate"):
        r = self.context.bash_tools.command(test_select_query(node=ch_nodes[0]))

    with Then("I restore server original state"):
        ch_nodes[0].query("DROP USER krb_rbac")

    with Finally("I expect 'krb_rbac'"):
        assert r.output == "krb_rbac", error()


@TestScenario
@Requirements(RQ_SRS_016_Kerberos_KerberosNotAvailable_InvalidServerTicket("1.0"))
def invalid_server_ticket(self):
    """ClickHouse SHALL reject Kerberos authentication no Kerberos server is reachable
    and CH-server has no valid ticket (or the existing ticket is outdated).
    """
    ch_nodes = self.context.ch_nodes

    with Given("kinit for client"):
        kinit_no_keytab(node=self.context.bash_tools)

    with And("setting up server principal"):
        create_server_principal(node=ch_nodes[0])

    with And("I kill kerberos-server"):
        self.context.krb_server.stop()

    with When("I attempt to authenticate as kerberos_user"):
        r = self.context.bash_tools.command(test_select_query(node=ch_nodes[0]))

    with Then("I start kerberos server again"):
        self.context.krb_server.start()
        kdestroy(self.context.bash_tools)
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                kinit_no_keytab(node=self.context.bash_tools)
                user = self.context.bash_tools.command(
                    test_select_query(node=ch_nodes[0])
                ).output
                assert user == "kerberos_user", error()
        kdestroy(self.context.bash_tools)

    with And("I expect the user to be default"):
        assert r.output == "default", error()


@TestScenario
@Requirements(RQ_SRS_016_Kerberos_KerberosNotAvailable_InvalidClientTicket("1.0"))
def invalid_client_ticket(self):
    """ClickHouse SHALL reject Kerberos authentication in case client has
    no valid ticket (or the existing ticket is outdated).
    """
    ch_nodes = self.context.ch_nodes
    kerberos = self.context.krb_server

    with Given("kinit for client"):
        kinit_no_keytab(node=self.context.bash_tools, lifetime_option="-l 00:00:05")

    with And("setting up server principal"):
        create_server_principal(node=ch_nodes[0])

    with And("I wait until client ticket is expired"):
        time.sleep(10)

    with When("I attempt to authenticate as kerberos_user"):
        r = self.context.bash_tools.command(test_select_query(node=ch_nodes[0]))

    with Then("I expect the user to be default"):
        assert r.output == "default", error()

    with Finally(""):
        try:
            retry(kerberos.command, timeout=30, delay=1)(
                f"echo pwd | kinit -l 10:00 kerberos_user",
                exitcode=0,
                shell_command="sh",
            )

            for attempt in retries(timeout=30, delay=1):
                with attempt:
                    if (
                        self.context.bash_tools.command(
                            test_select_query(node=ch_nodes[0])
                        ).output
                        == "kerberos_user"
                    ):
                        break
        finally:
            kdestroy(self.context.bash_tools)


@TestCase
@Requirements(RQ_SRS_016_Kerberos_KerberosNotAvailable_ValidTickets("1.0"))
def kerberos_unreachable_valid_tickets(self):
    """ClickHouse SHALL accept Kerberos authentication if no Kerberos server is reachable
    but both CH-server and client have valid tickets.
    """
    ch_nodes = self.context.ch_nodes

    with Given("kinit for client"):
        kinit_no_keytab(node=self.context.bash_tools)

    with And("setting up server principal"):
        create_server_principal(node=ch_nodes[0])

    with And("make sure server obtained ticket"):
        self.context.bash_tools.command(test_select_query(node=ch_nodes[0]))

    with And("I kill kerberos-server"):
        self.context.krb_server.stop()

    with When("I attempt to authenticate as kerberos_user"):
        r = self.context.bash_tools.command(test_select_query(node=ch_nodes[0]))

    with Then("I expect the user to be default"):
        assert r.output == "kerberos_user", error()

    with Finally("I start kerberos server again"):
        self.context.krb_server.start()
        kdestroy(self.context.bash_tools)
        attempts = 0
        while attempts < 20:
            attempts += 1
            kinit_no_keytab(node=self.context.bash_tools)
            if (
                self.context.bash_tools.command(
                    test_select_query(node=ch_nodes[0])
                ).output
                == "kerberos_user"
            ):
                break
            time.sleep(1)
        else:
            assert False, error()
        kdestroy(self.context.bash_tools)


@TestScenario
@Requirements(RQ_SRS_016_Kerberos_ValidUser_KerberosNotConfigured("1.0"))
def kerberos_not_configured(self):
    """ClickHouse SHALL reject Kerberos authentication if user is not a kerberos-auth user."""
    ch_nodes = self.context.ch_nodes

    with Given("kinit for client"):
        kinit_no_keytab(node=self.context.bash_tools, principal="unkerberized")

    with And("Kinit for server"):
        create_server_principal(node=ch_nodes[0])

    with By("I add non-Kerberos user to ClickHouse"):
        ch_nodes[0].query(
            "CREATE USER unkerberized IDENTIFIED WITH plaintext_password BY 'qwerty'"
        )

    with When("I attempt to authenticate"):
        r = self.context.bash_tools.command(
            test_select_query(node=ch_nodes[0]), no_checks=True
        )

    with Then("I expect authentication failure"):
        assert "Authentication failed" in r.output, error()

    with Finally("I drop the user"):
        ch_nodes[0].query("DROP USER unkerberized")


@TestScenario
@Requirements(RQ_SRS_016_Kerberos_KerberosServerRestarted("1.0"))
def kerberos_server_restarted(self):
    """ClickHouse SHALL accept Kerberos authentication if Kerberos server was restarted."""
    ch_nodes = self.context.ch_nodes
    krb_server = self.context.krb_server

    with Given("I obtain keytab for user"):
        kinit_no_keytab(node=self.context.bash_tools)
    with And("I create server principal"):
        create_server_principal(node=ch_nodes[0])
    with And("I obtain server ticket"):
        self.context.bash_tools.command(
            test_select_query(node=ch_nodes[0]), no_checks=True
        )
    with By("I dump, restart and restore kerberos server"):
        krb_server.command("kdb5_util dump dump.dmp", shell_command="/bin/sh")
        krb_server.restart()
        krb_server.command("kdb5_util load dump.dmp", shell_command="/bin/sh")

    with When("I attempt to authenticate"):
        r = self.context.bash_tools.command(test_select_query(node=ch_nodes[0]))

    with And("I wait for kerberos to be healthy"):
        kdestroy(self.context.bash_tools)
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                kinit_no_keytab(node=self.context.bash_tools)
                user = self.context.bash_tools.command(
                    test_select_query(node=ch_nodes[0])
                ).output
                assert user == "kerberos_user", error()

    with Then(f"I expect kerberos_user"):
        assert r.output == "kerberos_user", error()


@TestScenario
@Requirements(RQ_SRS_016_Kerberos_InvalidUser("1.0"))
def invalid_user(self):
    """ClickHouse SHALL reject Kerberos authentication for invalid principal"""
    ch_nodes = self.context.ch_nodes

    with Given("I obtain keytab for invalid user"):
        kinit_no_keytab(node=self.context.bash_tools, principal="invalid")

    with And("I create server principal"):
        create_server_principal(node=ch_nodes[0])

    with When("I attempt to authenticate"):
        r = self.context.bash_tools.command(
            test_select_query(node=ch_nodes[0]), no_checks=True
        )

    with Then(f"I expect default"):
        assert ("Authentication failed: password is incorrect" in r.output) and (
            "or there is no user with such name" in r.output
        ), error()


@TestScenario
@Requirements(RQ_SRS_016_Kerberos_InvalidUser_UserDeleted("1.0"))
def user_deleted(self):
    """ClickHouse SHALL reject Kerberos authentication if Kerberos user was deleted prior to query."""
    ch_nodes = self.context.ch_nodes

    with Given("I obtain keytab for a user"):
        kinit_no_keytab(node=self.context.bash_tools, principal="krb_rbac")

    with And("I create server principal"):
        create_server_principal(node=ch_nodes[0])

    with And("I create and then delete kerberized user"):
        ch_nodes[0].query(
            "CREATE USER krb_rbac IDENTIFIED WITH kerberos REALM 'EXAMPLE.COM'"
        )
        ch_nodes[0].query("DROP USER krb_rbac")

    with When("I attempt to authenticate"):
        r = self.context.bash_tools.command(
            test_select_query(node=ch_nodes[0]), no_checks=True
        )

    with Then(f"I expect error"):
        message = r.output
        assert "Authentication failed: password is incorrect" in message, error()
        assert "or there is no user with such name" in message, error()


@TestScenario
@Requirements(RQ_SRS_016_Kerberos_Performance("1.0"))
def authentication_performance(self):
    """ClickHouse's performance for Kerberos authentication SHALL shall be comparable to regular authentication."""
    ch_nodes = self.context.ch_nodes

    with Given("I obtain keytab for a user"):
        kinit_no_keytab(node=self.context.bash_tools)

    with And("I create server principal"):
        create_server_principal(node=ch_nodes[0])

    with And("I create a password-identified user"):
        ch_nodes[0].query(
            "CREATE USER pwd_user IDENTIFIED WITH plaintext_password BY 'pwd'"
        )

    with When("I measure kerberos auth time"):
        start_time_krb = time.time()
        for i in range(100):
            self.context.bash_tools.command(test_select_query(node=ch_nodes[0]))
        krb_time = (time.time() - start_time_krb) / 100

    with And("I measure password auth time"):
        start_time_usual = time.time()
        for i in range(100):
            self.context.bash_tools.command(
                f"echo 'SELECT 1 FORMAT TabSeparated' | curl 'http://pwd_user:pwd@clickhouse1:8123/' -d @-"
            )
        usual_time = (time.time() - start_time_usual) / 100

    with Then("measuring the performance compared to password auth"):
        metric(
            "percentage_improvement",
            units="%",
            value=100 * (krb_time - usual_time) / usual_time,
        )

    with Finally("I drop pwd_user"):
        ch_nodes[0].query("DROP USER pwd_user")


@TestFeature
def generic(self):
    """Perform ClickHouse Kerberos authentication testing"""

    self.context.ch_nodes = [
        self.context.cluster.node(f"clickhouse{i}") for i in range(1, 4)
    ]
    self.context.krb_server = self.context.cluster.node("kerberos")
    self.context.bash_tools = self.context.cluster.node("bash-tools")

    for scenario in loads(current_module(), Scenario, Suite):
        Scenario(run=scenario, flags=TE)  # , setup=instrument_clickhouse_server_log)
