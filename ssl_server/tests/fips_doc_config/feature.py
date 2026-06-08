from testflows.core import *

from ssl_server.tests.fips_doc_config.common import *


def _run_doc_fixture_scenario(apply_steps, verify_steps):
    """Apply fixtures, run checks, then tear fixtures down explicitly."""
    try:
        with Given("stock Altinity FIPS image config is active"):
            use_stock_fips_server_config()
        apply_steps()
        verify_steps()
    finally:
        remove_byoc_metrics_simulation(restart=False)
        remove_fips_doc_client_fixture()
        remove_fips_doc_server_fixtures(restart=False)
        restore_regression_server_config()


@TestScenario
@Name("fips-server")
def fips_server_doc_fixture(self):
    """ClickHouse server fixture from docs/fips-config.md."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    def apply_steps():
        with When("I apply the fips server fixture"):
            apply_fips_doc_server_fixtures()

    def verify_steps():
        with Then("preprocessed config should reflect the fixture"):
            verify_doc_fixture_preprocessed(marker="<tcp_port_secure>9440</tcp_port_secure>")
            verify_doc_fixture_installed(marker="<interserver_http_port remove")
            verify_doc_fixture_installed(marker="<mysql_port remove")
            verify_doc_fixture_installed(marker="<postgresql_port remove")
            verify_doc_fixture_preprocessed(marker="<interserver_https_port>")
            verify_doc_fixture_preprocessed(marker="RejectCertificateHandler")

        with And("only configured listener ports should be open"):
            verify_server_listening_ports(allowed_ports=DOC_SERVER_PORTS)

        with And("secure native TCP should accept queries"):
            verify_secure_native_tcp()

        with And("HTTPS should accept queries"):
            verify_secure_https()

        with And("HTTPS metrics endpoint should return Prometheus text"):
            verify_https_metrics_endpoint()

    _run_doc_fixture_scenario(apply_steps, verify_steps)


@TestScenario
@Name("fips-client")
def fips_client_doc_fixture(self):
    """ClickHouse client fixture from docs/fips-config.md."""
    with Given("certificates for doc config fixtures are installed"):
        setup_fips_doc_certificates()

    def apply_steps():
        with When("I apply the fips server and client fixtures"):
            apply_fips_doc_server_fixtures()
            apply_fips_doc_client_fixture()

    def verify_steps():
        with Then("only configured listener ports should be open"):
            verify_server_listening_ports(allowed_ports=DOC_SERVER_PORTS)

        with And("secure native TCP should accept queries"):
            verify_secure_native_tcp()

        with And("HTTPS should accept queries"):
            verify_secure_https()

    _run_doc_fixture_scenario(apply_steps, verify_steps)


@TestFeature
@Name("doc config")
def feature(self):
    """Regression coverage for fips doc configs."""
    Scenario(run=fips_server_doc_fixture)
    Scenario(run=fips_client_doc_fixture)
