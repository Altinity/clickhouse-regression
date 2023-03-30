from ssl_server.tests.common import *

error_certificate_verify_failed = (
    "Exception: error:1000007d:SSL routines:OPENSSL_internal:CERTIFICATE_VERIFY_FAILED"
)
error_tlsv1_alert_unknown_ca = (
    "Exception: error:10000418:SSL routines:OPENSSL_internal:TLSV1_ALERT_UNKNOWN_CA"
)


@TestStep(Given)
def create_node_server_certificate_with_chain_and_dh_params(
    self,
    node,
    name,
    common_name,
    ca_key,
    ca_crt,
    ca_chain_crt,
    ca_root_crt,
    trusted_cas=None,
    passphrase="",
    ca_passphrase="",
    tmpdir=None,
    use_stash=False,
    validate=True,
):
    """Create signed server certificate and dh params and copy them to the node."""

    if tmpdir is None:
        with Given(
            "I create temporary directory to create server certificate and dh parameters"
        ):
            tmpdir = create_local_tmpdir()

    common_path = define("common path", os.path.join(tmpdir, name))

    with Given("I generate DH parameters"):
        dh_params = create_dh_params(outfile=f"{common_path}.dh", use_stash=use_stash)

    with And("I generate server key"):
        server_key = create_rsa_private_key(
            outfile=f"{common_path}.key", passphrase=passphrase, use_stash=use_stash
        )

    with And("I generate server certificate signing request"):
        server_csr = create_certificate_signing_request(
            outfile=f"{common_path}.csr",
            common_name=common_name,
            key=server_key,
            passphrase=passphrase,
            use_stash=use_stash,
        )

    with And("I sign server certificate with CA"):
        server_crt = sign_certificate(
            outfile=f"{common_path}.crt",
            csr=server_csr,
            ca_certificate=ca_crt,
            ca_key=ca_key,
            ca_passphrase=ca_passphrase,
            use_stash=use_stash,
        )

    with And("I create server certificate with chain"):
        server_chain_crt = create_chain_certificate(
            outfile=f"{os.path.join(self.context.tmpdir, f'{name}_chain.crt')}",
            certificates=[server_crt, ca_chain_crt],
        )

    with And(
        "I copy server certificate with chain, key, dh params and root CA certificate to the node",
        description=f"{node}",
    ):
        copy(dest_node=node, src_path=server_chain_crt, dest_path=f"/{name}_chain.crt")
        copy(dest_node=node, src_path=server_key, dest_path=f"/{name}.key")
        copy(dest_node=node, src_path=dh_params, dest_path=f"/{name}.dh")
        copy(dest_node=node, src_path=ca_root_crt, dest_path=f"/ca_root.crt")

    if validate:
        with And("I validate server certificate with chain against root CA"):
            validate_certificate(
                certificate=f"/{name}_chain.crt",
                ca_certificate=f"/ca_root.crt",
                node=node,
            )

    if trusted_cas is not None:
        with And("I add trusted CA certificates to the node"):
            for trusted_ca in trusted_cas:
                name = "_".join(trusted_ca.split(os.path.sep)[-2:])
                with By(f"adding {name}"):
                    add_trusted_ca_certificate(
                        node=node, certificate=trusted_ca, name=name
                    )

    with And("I set correct permission on server key file"):
        node.command(f'chmod 600 "/{name}.key"')


@TestStep(Given)
def create_node_server_certificate_and_dh_params(
    self,
    node,
    name,
    common_name,
    ca_key,
    ca_crt,
    ca_chain_crt=None,
    trusted_cas=None,
    passphrase="",
    ca_passphrase="",
    tmpdir=None,
    use_stash=False,
    validate_certificate_using_ca=True,
):
    """Create signed server certificate and dh params and copy them to the node."""

    if tmpdir is None:
        with Given(
            "I create temporary directory to create server certificate and dh parameters"
        ):
            tmpdir = create_local_tmpdir()

    common_path = define("common path", os.path.join(tmpdir, name))

    with Given("I generate DH parameters"):
        dh_params = create_dh_params(outfile=f"{common_path}.dh", use_stash=use_stash)

    with And("I generate server key"):
        server_key = create_rsa_private_key(
            outfile=f"{common_path}.key", passphrase=passphrase, use_stash=use_stash
        )

    with And("I generate server certificate signing request"):
        server_csr = create_certificate_signing_request(
            outfile=f"{common_path}.csr",
            common_name=common_name,
            key=server_key,
            passphrase=passphrase,
            use_stash=use_stash,
        )

    with And("I sign server certificate with CA"):
        server_crt = sign_certificate(
            outfile=f"{common_path}.crt",
            csr=server_csr,
            ca_certificate=ca_crt,
            ca_key=ca_key,
            ca_passphrase=ca_passphrase,
            use_stash=use_stash,
        )

    with And(
        "I copy server certificate, key, dh params and CA certificate to the node",
        description=f"{node}",
    ):
        copy(dest_node=node, src_path=server_crt, dest_path=f"/{name}.crt")
        copy(dest_node=node, src_path=server_key, dest_path=f"/{name}.key")
        copy(dest_node=node, src_path=dh_params, dest_path=f"/{name}.dh")
        copy(dest_node=node, src_path=ca_crt, dest_path=f"/ca.crt")

    if ca_chain_crt is not None:
        with And("I copy CA chain certificate to the node", description=f"{node}"):
            copy(dest_node=node, src_path=ca_chain_crt, dest_path=f"/ca_chain.crt")

    if validate_certificate_using_ca:
        if ca_chain_crt is not None:
            with And("I validate server certificate against CA chain certificate"):
                validate_certificate(
                    certificate=f"/{name}.crt",
                    ca_certificate=f"/ca_chain.crt",
                    node=node,
                )

        else:
            with And("I validate server certificate against CA"):
                validate_certificate(
                    certificate=f"/{name}.crt", ca_certificate=f"/ca.crt", node=node
                )

    if trusted_cas is not None:
        with And("I add trusted CA certificates to the node"):
            for trusted_ca in trusted_cas:
                name = "_".join(trusted_ca.split(os.path.sep)[-2:])
                with By(f"adding {name}"):
                    add_trusted_ca_certificate(
                        node=node, certificate=trusted_ca, name=name
                    )

    with And("I set correct permission on server key file"):
        node.command(f'chmod 600 "/{name}.key"')


@TestStep(Then)
def check_secure_connection(self, from_node, to_node, message=None):
    """Check secure connection."""

    with When("I execute query using secure connection"):
        r = from_node.query(
            "SELECT 1", message=message, secure=True, settings=[("host", to_node.name)]
        )

    if message is None:
        with Then("it should work"):
            assert r.output == "1", error()


@TestStep(Given)
def add_ssl_configuration(
    self,
    node,
    server_crt,
    server_key,
    dh_params,
    server_key_passphrase=None,
    ca_config=None,
):
    """Add SSL configuration to specified ClickHouse node."""

    with By("adding SSL server configuration file"):
        entries = {
            "certificateFile": f"{server_crt}",
            "privateKeyFile": f"{server_key}",
            "dhParamsFile": f"{dh_params}",
            "verificationMode": "strict",
            "cacheSessions": "true",
            "preferServerCiphers": "true",
        }
        if ca_config is not None:
            entries["caConfig"] = f"{ca_config}"
            entries["loadDefaultCAFile"] = "false"
        else:
            entries["loadDefaultCAFile"] = "true"

        if server_key_passphrase:
            entries["privateKeyPassphraseHandler"] = {
                "name": "KeyFileHandler",
                "options": [{"password": server_key_passphrase}],
            }
        add_ssl_server_configuration_file(node=node, entries=entries)

    with And("adding SSL ports configuration file, then restarting the server"):
        add_secure_ports_configuration_file(node=node, restart=True, timeout=300)

    with And(
        "adding clickhouse client SSL configuration that uses servers certificate"
    ):
        entries = {
            "certificateFile": f"{server_crt}",
            "privateKeyFile": f"{server_key}",
            "verificationMode": "strict",
            "loadDefaultCAFile": "true",
            "cacheSessions": "true",
            "preferServerCiphers": "true",
        }
        if ca_config is not None:
            entries["caConfig"] = f"{ca_config}"
            entries["loadDefaultCAFile"] = "false"
        else:
            entries["loadDefaultCAFile"] = "true"

        if server_key_passphrase:
            entries["privateKeyPassphraseHandler"] = {
                "name": "KeyFileHandler",
                "options": [{"password": server_key_passphrase}],
            }

        add_ssl_clickhouse_client_configuration_file(node=node, entries=entries)


@TestStep(Given)
def add_custom_ssl_configuration(
    self,
    node,
    server_entries=None,
    client_entries=None,
    clickhouse_client_entries=None,
):
    """Add custom SSL configuration for server, client (server acting as client), and clickhouse client
    to specified ClickHouse node."""

    if server_entries is not None:
        with By("adding SSL server configuration file"):
            add_ssl_server_configuration_file(node=node, entries=server_entries)

    if client_entries is not None:
        with By("adding SSL server configuration file"):
            add_ssl_client_configuration_file(node=node, entries=server_entries)

    with By("adding SSL ports configuration file, then restarting the server"):
        add_secure_ports_configuration_file(node=node, restart=True, timeout=300)

    if clickhouse_client_entries is not None:
        with By(
            "adding clickhouse client SSL configuration that uses servers certificate"
        ):
            add_ssl_clickhouse_client_configuration_file(
                node=node, entries=clickhouse_client_entries
            )
