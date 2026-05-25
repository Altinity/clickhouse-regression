from testflows.core import *

from ssl_server.tests.fips_doc_config.common import *


def _run_doc_fixture_scenario(apply_steps, verify_steps):
    """Apply fixtures, run checks, then tear fixtures down explicitly."""
    try:
        apply_steps()
        verify_steps()
    finally:
        remove_fips_doc_client_fixture()
        remove_fips_doc_server_fixtures()


@TestScenario
@Name("fips-server-minimal")
def fips_server_minimal_doc_fixture(self):
    """Minimum server fixture from docs."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    def apply_steps():
        with When("I apply the fips-server-minimal server fixture"):
            apply_fips_doc_server_fixtures(fixtures="server/fips-server-minimal.xml")

    def verify_steps():
        with Then("preprocessed config should reflect the fixture"):
            verify_doc_fixture_preprocessed(marker="<tcp_port_secure>")

        with And("only configured listener ports should be open"):
            verify_server_listening_ports(allowed_ports=DOC_SERVER_MINIMAL_PORTS)

        with And("secure native TCP should accept queries"):
            verify_secure_native_tcp()

    _run_doc_fixture_scenario(apply_steps, verify_steps)


@TestScenario
@Name("fips-server-production")
def fips_server_production_doc_fixture(self):
    """Recommended production server fixture (inbound and outbound TLS)."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    def apply_steps():
        with When("I apply the fips-server-production server fixture"):
            apply_fips_doc_server_fixtures(fixtures="server/fips-server-production.xml")

    def verify_steps():
        with Then("preprocessed config should reflect the fixture"):
            verify_doc_fixture_preprocessed(marker="<verificationMode>relaxed</verificationMode>")
            verify_doc_fixture_preprocessed(marker="<interserver_https_port>")
            verify_doc_fixture_preprocessed(marker="RejectCertificateHandler")

        with And("only configured listener ports should be open"):
            verify_server_listening_ports(allowed_ports=DOC_SERVER_FULL_PORTS)

        with And("secure native TCP should accept queries"):
            verify_secure_native_tcp()

        with And("HTTPS should accept queries"):
            verify_secure_https()

    _run_doc_fixture_scenario(apply_steps, verify_steps)


@TestScenario
@Name("fips-server-lab")
def fips_server_lab_doc_fixture(self):
    """Recommended lab server fixture (inbound and outbound TLS)."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    def apply_steps():
        with When("I apply the fips-server-lab server fixture"):
            apply_fips_doc_server_fixtures(fixtures="server/fips-server-lab.xml")

    def verify_steps():
        with Then("preprocessed config should reflect the fixture"):
            verify_doc_fixture_preprocessed(marker="<verificationMode>none</verificationMode>")
            verify_doc_fixture_preprocessed(marker="AcceptCertificateHandler")

        with And("only configured listener ports should be open"):
            verify_server_listening_ports(allowed_ports=DOC_SERVER_FULL_PORTS)

        with And("secure native TCP should accept queries"):
            verify_secure_native_tcp()

        with And("HTTPS should accept queries"):
            verify_secure_https()

    _run_doc_fixture_scenario(apply_steps, verify_steps)


@TestScenario
@Name("fips-client-minimal")
def fips_client_minimal_doc_fixture(self):
    """Minimum clickhouse-client fixture with matching server listener."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    def apply_steps():
        with When("I apply the fips-server-minimal and fips-client-minimal fixtures"):
            apply_fips_doc_server_fixtures(fixtures="server/fips-server-minimal.xml")
            apply_fips_doc_client_fixture(fixture="client/fips-client-minimal.xml")

    def verify_steps():
        with Then("only configured listener ports should be open"):
            verify_server_listening_ports(allowed_ports=DOC_SERVER_MINIMAL_PORTS)

        with And("secure native TCP should accept queries"):
            verify_secure_native_tcp()

    _run_doc_fixture_scenario(apply_steps, verify_steps)


@TestScenario
@Name("fips-client-production")
def fips_client_production_doc_fixture(self):
    """Full clickhouse-client fixture (production) with server fixture."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    def apply_steps():
        with When("I apply the production server and client production fixtures"):
            apply_fips_doc_server_fixtures(fixtures="server/fips-server-production.xml")
            apply_fips_doc_client_fixture(fixture="client/fips-client-production.xml")

    def verify_steps():
        with Then("only configured listener ports should be open"):
            verify_server_listening_ports(allowed_ports=DOC_SERVER_FULL_PORTS)

        with And("secure native TCP should accept queries"):
            verify_secure_native_tcp()

        with And("HTTPS should accept queries"):
            verify_secure_https()

    _run_doc_fixture_scenario(apply_steps, verify_steps)


@TestScenario
@Name("fips-client-lab")
def fips_client_lab_doc_fixture(self):
    """Full clickhouse-client fixture (lab) with server fixture."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    def apply_steps():
        with When("I apply the lab server and client lab fixtures"):
            apply_fips_doc_server_fixtures(fixtures="server/fips-server-lab.xml")
            apply_fips_doc_client_fixture(fixture="client/fips-client-lab.xml")

    def verify_steps():
        with Then("only configured listener ports should be open"):
            verify_server_listening_ports(allowed_ports=DOC_SERVER_FULL_PORTS)

        with And("secure native TCP should accept queries"):
            verify_secure_native_tcp()

        with And("HTTPS should accept queries"):
            verify_secure_https()

    _run_doc_fixture_scenario(apply_steps, verify_steps)


@TestFeature
@Name("doc config")
def feature(self):
    """Regression coverage for fips doc configs."""
    Scenario(run=fips_server_minimal_doc_fixture)
    Scenario(run=fips_server_production_doc_fixture)
    Scenario(run=fips_server_lab_doc_fixture)
    Scenario(run=fips_client_minimal_doc_fixture)
    Scenario(run=fips_client_production_doc_fixture)
    Scenario(run=fips_client_lab_doc_fixture)
