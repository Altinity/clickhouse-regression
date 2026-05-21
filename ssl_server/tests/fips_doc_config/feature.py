from testflows.core import *

from ssl_server.tests.fips_doc_config.common import *


@TestScenario
@Name("fips-server-minimal")
def fips_server_minimal_doc_fixture(self):
    """Minimum inbound server fixture from docs/fips-config.md."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    with When("I apply the fips-server-minimal server fixture"):
        apply_fips_doc_server_fixtures(fixtures="server/fips-server-minimal.xml")
        verify_doc_fixture_preprocessed(marker="<tcp_port_secure>")
        verify_secure_native_tcp()


@TestScenario
@Name("fips-server-inbound-production")
def fips_server_inbound_production_doc_fixture(self):
    """Recommended inbound server fixture (production verification mode)."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    with When("I apply the fips-server-inbound-production server fixture"):
        apply_fips_doc_server_fixtures(
            fixtures="server/fips-server-inbound-production.xml"
        )
        verify_doc_fixture_preprocessed(marker="<verificationMode>relaxed</verificationMode>")
        verify_secure_native_tcp()
        verify_secure_https()


@TestScenario
@Name("fips-server-inbound-lab")
def fips_server_inbound_lab_doc_fixture(self):
    """Recommended inbound server fixture (lab / self-signed)."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    with When("I apply the fips-server-inbound-lab server fixture"):
        apply_fips_doc_server_fixtures(fixtures="server/fips-server-inbound-lab.xml")
        verify_doc_fixture_preprocessed(marker="<verificationMode>none</verificationMode>")
        verify_secure_native_tcp()
        verify_secure_https()


@TestScenario
@Name("fips-server-outbound-production")
def fips_server_outbound_production_doc_fixture(self):
    """Outbound server client block (production) with minimal inbound listener."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    with When("I apply the outbound production and minimal server fixtures"):
        apply_fips_doc_server_fixtures(
            fixtures=[
                "server/fips-server-minimal.xml",
                "server/fips-server-outbound-production.xml",
            ]
        )
        verify_doc_fixture_preprocessed(marker="<interserver_https_port>")
        verify_doc_fixture_preprocessed(marker="RejectCertificateHandler")
        verify_secure_native_tcp()


@TestScenario
@Name("fips-server-outbound-lab")
def fips_server_outbound_lab_doc_fixture(self):
    """Outbound server client block (lab) with minimal inbound listener."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    with When("I apply the outbound lab and minimal server fixtures"):
        apply_fips_doc_server_fixtures(
            fixtures=[
                "server/fips-server-minimal.xml",
                "server/fips-server-outbound-lab.xml",
            ]
        )
        verify_doc_fixture_preprocessed(marker="AcceptCertificateHandler")
        verify_secure_native_tcp()


@TestScenario
@Name("fips-client-minimal")
def fips_client_minimal_doc_fixture(self):
    """Minimum clickhouse-client fixture with matching server listener."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    with When("I apply the fips-server-minimal and fips-client-minimal fixtures"):
        apply_fips_doc_server_fixtures(fixtures="server/fips-server-minimal.xml")
        apply_fips_doc_client_fixture(fixture="client/fips-client-minimal.xml")
        verify_secure_native_tcp()


@TestScenario
@Name("fips-client-production")
def fips_client_production_doc_fixture(self):
    """Full clickhouse-client fixture (production) with inbound server fixture."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    with When("I apply the inbound production and client production fixtures"):
        apply_fips_doc_server_fixtures(
            fixtures="server/fips-server-inbound-production.xml"
        )
        apply_fips_doc_client_fixture(fixture="client/fips-client-production.xml")
        verify_secure_native_tcp()
        verify_secure_https()


@TestScenario
@Name("fips-client-lab")
def fips_client_lab_doc_fixture(self):
    """Full clickhouse-client fixture (lab) with inbound server fixture."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    with When("I apply the inbound lab and client lab fixtures"):
        apply_fips_doc_server_fixtures(fixtures="server/fips-server-inbound-lab.xml")
        apply_fips_doc_client_fixture(fixture="client/fips-client-lab.xml")
        verify_secure_native_tcp()
        verify_secure_https()


@TestFeature
@Name("doc config")
def feature(self):
    """Regression coverage for docs/fips-config.md fixture files."""
    Scenario(run=fips_server_minimal_doc_fixture)
    Scenario(run=fips_server_inbound_production_doc_fixture)
    Scenario(run=fips_server_inbound_lab_doc_fixture)
    Scenario(run=fips_server_outbound_production_doc_fixture)
    Scenario(run=fips_server_outbound_lab_doc_fixture)
    Scenario(run=fips_client_minimal_doc_fixture)
    Scenario(run=fips_client_production_doc_fixture)
    Scenario(run=fips_client_lab_doc_fixture)
