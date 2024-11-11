from testflows.core import *

from ssl_server.tests.common import *
from ssl_server.tests.ssl_context import enable_ssl
from ssl_server.requirements import *
from clickhouse_keeper.tests.common import flask_server, certs_for_flask

default_ciphers = "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384"


@TestOutline
def http_server_url_function_checks(self):
    """Check the connection from clickhouse-server when it is acting as a client to an http server using `url` table function."""
    node = self.context.node

    with Given("I launch the http flask server"):
        flask_server(
            server_path="/http_app_file.py",
            port=5000,
            protocol="TLSv1.2",
            ciphers=default_ciphers,
        )

    with Check("I read data from the http server using `url` table function"):
        output = node.query(
            "SELECT * FROM url('http://bash-tools:5000/data', 'CSV') FORMAT CSV"
        ).output
        assert output == "12345", error()


@TestOutline
def https_server_url_function_checks(self):
    """Check the connection from clickhouse-server when it is acting as a client to https server with different configs using `url` table function."""

    with Given("I launch the https flask server"):
        flask_server(
            server_path="https_app_file.py",
            port=5001,
            protocol="TLSv1.2",
            ciphers=default_ciphers,
        )

    with Check("connection with no protocols should be rejected"):
        https_server_url_function_connection(
            options={
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2,tlsv1_3",
            },
            success=False,
            timeout=5,
        )

    with Check(f"TLSv1_2 suite connection should work"):
        https_server_url_function_connection(
            options={
                "requireTLSv1_2": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
            },
            success=True,
        )

    with Check("TLSv1 suite connection should be rejected"):
        https_server_url_function_connection(
            options={
                "requireTLSv1": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1_1,tlsv1_2,tlsv1_3",
            },
            success=False,
            timeout=5,
        )

    with Check("TLSv1_1 suite connection should be rejected"):
        https_server_url_function_connection(
            options={
                "requireTLSv1_1": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_2,tlsv1_3",
            },
            success=False,
            timeout=5,
        )

    with Check("TLSv1_3 suite connection should be rejected"):
        https_server_url_function_connection(
            options={
                "requireTLSv1_3": "true",
                "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2",
            },
            success=False,
            timeout=5,
        )

    with Check(f"just disabling TLSv1 suite connection should work"):
        https_server_url_function_connection(
            options={"disableProtocols": "tlsv1"},
            success=True,
        )

    with Check(f"just disabling TLSv1_1 suite connection should work"):
        https_server_url_function_connection(
            options={"disableProtocols": "tlsv1_1"},
            success=True,
        )

    with Check(f"just disabling TLSv1_3 suite connection should work"):
        https_server_url_function_connection(
            options={"disableProtocols": "tlsv1_3"},
            success=True,
        )

    for cipher in fips_compatible_tlsv1_2_cipher_suites:
        with Check(f"connection using FIPS compatible cipher {cipher} should work"):
            https_server_url_function_connection(
                options={
                    "requireTLSv1_2": "true",
                    "cipherList": cipher,
                    "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
                },
                success=True,
                timeout=5,
            )

    for cipher in all_ciphers:
        if cipher in fips_compatible_tlsv1_2_cipher_suites:
            continue
        with Check(
            f"connection using non-FIPS compatible cipher {cipher} should be rejected"
        ):
            https_server_url_function_connection(
                options={"cipherList": cipher, "disableProtocols": ""},
                success=False,
                timeout=5,
            )


@TestFeature
@Name("url table function")
@Requirements(RQ_SRS_017_ClickHouse_SSL_Server_UrlTableFunction("1.0"))
def feature(self, node="clickhouse1"):
    """Check clickhouse-server connections using `url` table function."""
    self.context.node = self.context.cluster.node(node)

    with Given("I enable SSL for clickhouse-server"):
        enable_ssl(my_own_ca_key_passphrase="", server_key_passphrase="")

    with Given("I generate private key and certificate for https server"):
        bash_tools = self.context.cluster.node("bash-tools")
        ca_cert = add_trusted_ca_certificate(
q            node=bash_tools, certificate=self.context.my_own_ca_crt
        )
        create_crt_and_key(
            name="https_server",
            common_name="bash-tools",
            node=bash_tools,
            node_ca_crt=ca_cert,
        )

    Suite(run=https_server_url_function_checks)
    Suite(run=http_server_url_function_checks)
