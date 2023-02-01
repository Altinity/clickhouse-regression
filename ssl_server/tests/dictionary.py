from testflows.core import *

from ssl_server.tests.common import *
from ssl_server.tests.ssl_context import enable_ssl
from ssl_server.requirements import *


@TestOutline
def http_server_dictionary_checks(self):
    """Check the connection from clickhouse-server when it is acting as a client to an http server using a dictionary."""
    node = self.context.node
    name = "dictionary_" + getuid()

    with Given("I launch the http flask server"):
        flask_server(server_path="/http_app_file.py", port=5000)

    with Check("connection to http server using a dictionary"):
        try:
            with When("I create a dictionary using an https source"):
                node.query(
                    f"CREATE DICTIONARY {name} (c1 Int64) PRIMARY KEY c1 SOURCE(HTTP(URL 'http://127.0.0.1:5000/data' FORMAT 'CSV')) LIFETIME(MIN 0 MAX 0) LAYOUT(FLAT())"
                )

            with Then("I select data from the dictionary"):
                output = node.query(f"SELECT * FROM {name} FORMAT CSV").output
                assert output == "12345", error()

        finally:
            with Finally("I remove the dictionary"):
                node.query(f"DROP DICTIONARY IF EXISTS {name}")


@TestOutline
def https_server_dictionary_checks(self):
    """Check the connection from clickhouse-server when it is acting as a client to https server with different configs using a dictionary."""

    with Given(
        "I launch the https flask server",
        description=f"protocol: {https_protocol}, ciphers: {fips_compatible_tlsv1_2_cipher_suites}",
    ):
        flask_server(server_path="/https_app_file.py", port=5001)

    with Check("Connection with no protocols should be rejected"):
        https_server_https_dictionary_connection(
            options={
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2,tlsv1_3",
            },
            success=False,
        )

    with Check(f"TLSv1.2 suite connection should work"):
        https_server_https_dictionary_connection(
            options={
                "requireTLSv1_2": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
            },
            success=True,
        )

    with Check("TLSv1 suite connection should be rejected"):
        https_server_https_dictionary_connection(
            options={
                "requireTLSv1": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1_1,tlsv1_2,tlsv1_3",
            },
            success=False,
        )

    with Check("TLSv1.1 suite connection should be rejected"):
        https_server_https_dictionary_connection(
            options={
                "requireTLSv1_1": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_2,tlsv1_3",
            },
            success=False,
        )

    with Check("TLSv1.3 suite connection should be rejected"):
        https_server_https_dictionary_connection(
            options={
                "requireTLSv1_3": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2",
            },
            success=False,
        )

    with Check(f"just disabling TLSv1 suite connection should work"):
        https_server_https_dictionary_connection(
            options={"disableProtocols": "tlsv1"},
            success=True,
        )

    with Check(f"just disabling TLSv1.1 suite connection should work"):
        https_server_https_dictionary_connection(
            options={"disableProtocols": "tlsv1_1"},
            success=True,
        )

    with Check(f"just disabling TLSv1.3 suite connection should work"):
        https_server_https_dictionary_connection(
            options={"disableProtocols": "tlsv1_3"},
            success=True,
        )

    for cipher in fips_compatible_tlsv1_2_cipher_suites:
        with Check(f"connection using FIPS compatible cipher {cipher} should work"):
            https_server_https_dictionary_connection(
                options={
                    "requireTLSv1_2": "true",
                    "cipherList": cipher,
                    "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
                },
                success=True,
            )

    for cipher in all_ciphers:
        if cipher in fips_compatible_tlsv1_2_cipher_suites:
            continue
        with Check(
            f"connection using non-FIPS compatible cipher {cipher} should be rejected"
        ):
            https_server_https_dictionary_connection(
                options={"cipherList": cipher, "disableProtocols": ""},
                success=False,
            )


@TestFeature
@Name("dictionary")
@Requirements(RQ_SRS_017_ClickHouse_SSL_Server_Dictionary("1.0"))
def feature(self, node="clickhouse1"):
    """Check clickhouse-server connections using a dictionary."""
    self.context.node = self.context.cluster.node(node)

    with Given("I enable SSL"):
        enable_ssl(my_own_ca_key_passphrase="", server_key_passphrase="")

    with And("I generate private key and certificate for https server"):
        create_crt_and_key(name="https_server", common_name="127.0.0.1")

    Suite(run=https_server_dictionary_checks)
    Suite(run=http_server_dictionary_checks)
