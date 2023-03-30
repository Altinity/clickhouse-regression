from ssl_server.tests.ca_chain.steps import *


@TestOutline
def with_caconfig(
    self,
    ca_store,
    ca_chain_crt,
    nodes=None,
    message=None,
    validate_certificate_using_ca_chain_crt=True,
):
    """Check secure connection using server certificate signed by a specified CA and CAs chain
    when <caConfig> is explicitly specified in server and clickhouse-client SSL configurations."""
    if nodes is None:
        nodes = self.context.cluster.nodes["clickhouse"]

    for node_name in nodes:
        with Given(f"I create and add server certificate to {node_name}"):
            create_node_server_certificate_and_dh_params(
                node=self.context.cluster.node(node_name),
                name=node_name,
                common_name=node_name,
                ca_key=f"{os.path.join(ca_store, 'ca.key')}",
                ca_crt=f"{os.path.join(ca_store, 'ca.crt')}",
                ca_chain_crt=ca_chain_crt,
                tmpdir=self.context.tmpdir,
            )

    for node_name in nodes:
        with And(f"I add SSL configuration to {node_name}"):
            add_ssl_configuration(
                node=self.context.cluster.node(node_name),
                server_key=f"/{node_name}.key",
                server_crt=f"/{node_name}.crt",
                dh_params=f"/{node_name}.dh",
                ca_config="/ca_chain.crt",
            )

    with Then("check secure connection from each clickhouse server to the other"):
        for from_name in nodes:
            for to_name in nodes:
                with Then(f"from {from_name} to {to_name}"):
                    check_secure_connection(
                        from_node=self.context.cluster.node(from_name),
                        to_node=self.context.cluster.node(to_name),
                    )


@TestOutline
def with_caconfig_missing_ca_in_chain(
    self, ca_store, nodes_ca_chain_crt, nodes_messages, nodes=None
):
    """Check secure connection using server certificate signed by a specified CA and CAs chain
    when <caConfig> is explicitly specified in server and clickhouse-client SSL configurations
    but with one node CA chain certificate missing some CAs."""
    if nodes is None:
        nodes = self.context.cluster.nodes["clickhouse"]

    for node_name in nodes:
        with Given(f"I create and add server certificate to {node_name}"):
            ca_chain_crt, validate_certificate_using_ca = nodes_ca_chain_crt[node_name]

            create_node_server_certificate_and_dh_params(
                node=self.context.cluster.node(node_name),
                name=node_name,
                common_name=node_name,
                ca_key=f"{os.path.join(ca_store, 'ca.key')}",
                ca_crt=f"{os.path.join(ca_store, 'ca.crt')}",
                ca_chain_crt=ca_chain_crt,
                validate_certificate_using_ca=validate_certificate_using_ca,
                tmpdir=self.context.tmpdir,
            )

    for node_name in nodes:
        with And(f"I add SSL configuration to {node_name}"):
            add_ssl_configuration(
                node=self.context.cluster.node(node_name),
                server_key=f"/{node_name}.key",
                server_crt=f"/{node_name}.crt",
                dh_params=f"/{node_name}.dh",
                ca_config="/ca_chain.crt",
            )

    with Then("check secure connection from each clickhouse server to the other"):
        for from_name in nodes:
            for to_name in nodes:
                with Then(f"from {from_name} to {to_name}"):
                    check_secure_connection(
                        from_node=self.context.cluster.node(from_name),
                        to_node=self.context.cluster.node(to_name),
                        message=nodes_messages[(from_name, to_name)],
                    )


@TestScenario
def with_caconfig_missing_first_ca_in_chain_on_one_node(
    self, ca_store, ca_chain_crt, cas
):
    """Check when clickhouse1 node is missing first CA in chain certificate.
    We will check that connections from clickhouse1 to any other node including itself
    fails with certificate verify error and connections from any nodes other than
    clickhouse1 to clickhouse1 fails as well with unknown CA error.
    """

    with Given(
        "I create CA chain certificate that missing first certificate in the chain"
    ):
        missing_ca_chain_crt = create_ca_chain_certificate(
            outfile=f"{os.path.join(self.context.tmpdir, 'missing_ca_chain.crt')}",
            cas=cas[1:],
        )

    with_caconfig_missing_ca_in_chain(
        ca_store=ca_store,
        nodes_ca_chain_crt={
            "clickhouse1": (missing_ca_chain_crt, False),
            "clickhouse2": (ca_chain_crt, True),
            "clickhouse3": (ca_chain_crt, True),
        },
        nodes_messages={
            ("clickhouse1", "clickhouse1"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse2"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse3"): error_certificate_verify_failed,
            ("clickhouse2", "clickhouse1"): error_tlsv1_alert_unknown_ca,
            ("clickhouse2", "clickhouse2"): None,
            ("clickhouse2", "clickhouse3"): None,
            ("clickhouse3", "clickhouse1"): error_tlsv1_alert_unknown_ca,
            ("clickhouse3", "clickhouse2"): None,
            ("clickhouse3", "clickhouse3"): None,
        },
    )


@TestScenario
def with_caconfig_missing_last_ca_in_chain_on_one_node(
    self, ca_store, ca_chain_crt, cas
):
    """Check when clickhouse1 node is missing last CA in chain certificate.
    We will check that connections from clickhouse1 to any other node including itself
    fails with certificate verify error and connections from any nodes other than
    clickhouse1 to clickhouse1 fails as well with unknown CA error.
    """

    with Given(
        "I create CA chain certificate that missing last certificate in the chain"
    ):
        missing_ca_chain_crt = create_ca_chain_certificate(
            outfile=f"{os.path.join(self.context.tmpdir, 'missing_ca_chain.crt')}",
            cas=cas[:-1],
        )

    with_caconfig_missing_ca_in_chain(
        ca_store=ca_store,
        nodes_ca_chain_crt={
            "clickhouse1": (missing_ca_chain_crt, False),
            "clickhouse2": (ca_chain_crt, True),
            "clickhouse3": (ca_chain_crt, True),
        },
        nodes_messages={
            ("clickhouse1", "clickhouse1"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse2"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse3"): error_certificate_verify_failed,
            ("clickhouse2", "clickhouse1"): error_tlsv1_alert_unknown_ca,
            ("clickhouse2", "clickhouse2"): None,
            ("clickhouse2", "clickhouse3"): None,
            ("clickhouse3", "clickhouse1"): error_tlsv1_alert_unknown_ca,
            ("clickhouse3", "clickhouse2"): None,
            ("clickhouse3", "clickhouse3"): None,
        },
    )


@TestScenario
def with_caconfig_missing_middle_ca_in_chain_on_one_node(
    self, ca_store, ca_chain_crt, cas
):
    """Check when clickhouse1 node is missing middle CA in chain certificate.
    We will check that connections from clickhouse1 to any other node including itself
    fails with certificate verify error and connections from any nodes other than
    clickhouse1 to clickhouse1 fails as well with unknown CA error.
    """

    with Given(
        "I create CA chain certificate that missing middle certificate in the chain"
    ):
        missing_ca_chain_crt = create_ca_chain_certificate(
            outfile=f"{os.path.join(self.context.tmpdir, 'missing_ca_chain.crt')}",
            cas=(cas[:-2] + cas[2:]),
        )

    with_caconfig_missing_ca_in_chain(
        ca_store=ca_store,
        nodes_ca_chain_crt={
            "clickhouse1": (missing_ca_chain_crt, False),
            "clickhouse2": (ca_chain_crt, True),
            "clickhouse3": (ca_chain_crt, True),
        },
        nodes_messages={
            ("clickhouse1", "clickhouse1"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse2"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse3"): error_certificate_verify_failed,
            ("clickhouse2", "clickhouse1"): error_tlsv1_alert_unknown_ca,
            ("clickhouse2", "clickhouse2"): None,
            ("clickhouse2", "clickhouse3"): None,
            ("clickhouse3", "clickhouse1"): error_tlsv1_alert_unknown_ca,
            ("clickhouse3", "clickhouse2"): None,
            ("clickhouse3", "clickhouse3"): None,
        },
    )


@TestScenario
def with_caconfig_missing_ca_in_chain_on_all_nodes(self, ca_store, ca_chain_crt, cas):
    """Check when each node is missing some CA in chain certificate.
    We will check that connections from any node to any other node fails
    with certificate verify error.
    """

    with Given(
        "I create CA chain certificate that missing first certificate in the chain"
    ):
        missing_first_ca_chain_crt = create_ca_chain_certificate(
            outfile=f"{os.path.join(self.context.tmpdir, 'missing_first_ca_chain.crt')}",
            cas=cas[1:],
        )

    with And(
        "I create CA chain certificate that missing first certificate in the chain"
    ):
        missing_middle_ca_chain_crt = create_ca_chain_certificate(
            outfile=f"{os.path.join(self.context.tmpdir, 'missing_middle_ca_chain.crt')}",
            cas=(cas[:-2] + cas[2:]),
        )

    with And(
        "I create CA chain certificate that missing last certificate in the chain"
    ):
        missing_last_ca_chain_crt = create_ca_chain_certificate(
            outfile=f"{os.path.join(self.context.tmpdir, 'missing_last_ca_chain.crt')}",
            cas=cas[:-1],
        )

    with_caconfig_missing_ca_in_chain(
        ca_store=ca_store,
        nodes_ca_chain_crt={
            "clickhouse1": (missing_middle_ca_chain_crt, False),
            "clickhouse2": (missing_first_ca_chain_crt, False),
            "clickhouse3": (missing_last_ca_chain_crt, False),
        },
        nodes_messages={
            ("clickhouse1", "clickhouse1"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse2"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse3"): error_certificate_verify_failed,
            ("clickhouse2", "clickhouse1"): error_certificate_verify_failed,
            ("clickhouse2", "clickhouse2"): error_certificate_verify_failed,
            ("clickhouse2", "clickhouse3"): error_certificate_verify_failed,
            ("clickhouse3", "clickhouse1"): error_certificate_verify_failed,
            ("clickhouse3", "clickhouse2"): error_certificate_verify_failed,
            ("clickhouse3", "clickhouse3"): error_certificate_verify_failed,
        },
    )


@TestOutline
def without_caconfig(self, ca_store, ca_chain_crt, trusted_cas, nodes=None):
    """Check secure connection using server certificate signed by a specified CA and CAs chain
    but without specifying <caConfig> parameter either in server or clickhouse-client SSL configuration
    to check using CAs provided by the system."""
    if nodes is None:
        nodes = self.context.cluster.nodes["clickhouse"]

    for node_name in nodes:
        with Given(f"I create and add server certificate to {node_name}"):
            create_node_server_certificate_and_dh_params(
                node=self.context.cluster.node(node_name),
                name=node_name,
                common_name=node_name,
                ca_key=f"{os.path.join(ca_store, 'ca.key')}",
                ca_crt=f"{os.path.join(ca_store, 'ca.crt')}",
                ca_chain_crt=ca_chain_crt,
                trusted_cas=trusted_cas,
                tmpdir=self.context.tmpdir,
            )

    for node_name in nodes:
        with And(
            f"I add SSL configuration to {node_name} without specifying any caConfig"
        ):
            add_ssl_configuration(
                node=self.context.cluster.node(node_name),
                server_key=f"/{node_name}.key",
                server_crt=f"/{node_name}.crt",
                dh_params=f"/{node_name}.dh",
            )

    with Then("check secure connection from each clickhouse server to the other"):
        for from_name in nodes:
            for to_name in nodes:
                with Then(f"from {from_name} to {to_name}"):
                    check_secure_connection(
                        from_node=self.context.cluster.node(from_name),
                        to_node=self.context.cluster.node(to_name),
                    )


@TestScenario
def without_caconfig_missing_trusted_ca(
    self, ca_store, ca_chain_crt, nodes_trusted_cas, nodes_messages, nodes=None
):
    """Check secure connection using server certificate signed by a specified CA and CAs chain
    but without specifying <caConfig> parameter either in server or clickhouse-client SSL configuration
    to check when CAs are provided by the system on some nodes but missing on others."""
    if nodes is None:
        nodes = self.context.cluster.nodes["clickhouse"]

    for node_name in nodes:
        with Given(f"I create and add server certificate to {node_name}"):
            create_node_server_certificate_and_dh_params(
                node=self.context.cluster.node(node_name),
                name=node_name,
                common_name=node_name,
                ca_key=f"{os.path.join(ca_store, 'ca.key')}",
                ca_crt=f"{os.path.join(ca_store, 'ca.crt')}",
                ca_chain_crt=ca_chain_crt,
                trusted_cas=None,
                tmpdir=self.context.tmpdir,
            )

    if nodes_trusted_cas is not None:
        for node_name, trusted_cas in nodes_trusted_cas:
            with And(f"I add trusted CA certificates to {node_name}"):
                for trusted_ca in trusted_cas:
                    name = "_".join(trusted_ca.split(os.path.sep)[-2:])
                    with By(f"adding {name}"):
                        add_trusted_ca_certificate(
                            node=self.context.cluster.node(node_name),
                            certificate=trusted_ca,
                            name=name,
                        )

    for node_name in nodes:
        with And(
            f"I add SSL configuration to {node_name} without specifying any caConfig"
        ):
            add_ssl_configuration(
                node=self.context.cluster.node(node_name),
                server_key=f"/{node_name}.key",
                server_crt=f"/{node_name}.crt",
                dh_params=f"/{node_name}.dh",
            )

    with Then("check secure connection from each clickhouse server to the other"):
        for from_name in nodes:
            for to_name in nodes:
                with Then(
                    f"from {from_name} to {to_name}",
                    description=f"expect message {nodes_messages[(from_name, to_name)]}",
                ):
                    check_secure_connection(
                        from_node=self.context.cluster.node(from_name),
                        to_node=self.context.cluster.node(to_name),
                        message=nodes_messages[(from_name, to_name)],
                    )


@TestScenario
def without_caconfig_missing_first_trusted_ca_on_one_node(
    self, ca_store, ca_chain_crt, cas
):
    """Check when clickhouse1 node is missing first CA in the system trust store.
    We will check that connections from clickhouse1 to any other node including itself
    fails with certificate verify error and connections from any nodes other than
    clickhouse1 to clickhouse1 fails as well with unknown CA error.
    """

    without_caconfig_missing_trusted_ca(
        ca_store=ca_store,
        ca_chain_crt=ca_chain_crt,
        nodes_trusted_cas=[
            ("clickhouse1", cas[1:]),
            ("clickhouse2", cas),
            ("clickhouse3", cas),
        ],
        nodes_messages={
            ("clickhouse1", "clickhouse1"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse2"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse3"): error_certificate_verify_failed,
            ("clickhouse2", "clickhouse1"): error_tlsv1_alert_unknown_ca,
            ("clickhouse2", "clickhouse2"): None,
            ("clickhouse2", "clickhouse3"): None,
            ("clickhouse3", "clickhouse1"): error_tlsv1_alert_unknown_ca,
            ("clickhouse3", "clickhouse2"): None,
            ("clickhouse3", "clickhouse3"): None,
        },
    )


@TestScenario
def without_caconfig_missing_last_trusted_ca_on_one_node(
    self, ca_store, ca_chain_crt, cas
):
    """Check when clickhouse1 node is missing last CA in the system trust store.
    We will check that connections from clickhouse1 to any other node including itself
    fails with certificate verify error and connections from any nodes other than
    clickhouse1 to clickhouse1 fails as well with unknown CA error.
    """

    without_caconfig_missing_trusted_ca(
        ca_store=ca_store,
        ca_chain_crt=ca_chain_crt,
        nodes_trusted_cas=[
            ("clickhouse1", cas[:-1]),
            ("clickhouse2", cas),
            ("clickhouse3", cas),
        ],
        nodes_messages={
            ("clickhouse1", "clickhouse1"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse2"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse3"): error_certificate_verify_failed,
            ("clickhouse2", "clickhouse1"): error_tlsv1_alert_unknown_ca,
            ("clickhouse2", "clickhouse2"): None,
            ("clickhouse2", "clickhouse3"): None,
            ("clickhouse3", "clickhouse1"): error_tlsv1_alert_unknown_ca,
            ("clickhouse3", "clickhouse2"): None,
            ("clickhouse3", "clickhouse3"): None,
        },
    )


@TestScenario
def without_caconfig_missing_middle_trusted_ca_on_one_node(
    self, ca_store, ca_chain_crt, cas
):
    """Check when clickhouse1 node is missing middle CA in the system trust store.
    We will check that connections from clickhouse1 to any other node including itself
    fails with certificate verify error and connections from any nodes other than
    clickhouse1 to clickhouse1 fails as well with unknown CA error.
    """

    without_caconfig_missing_trusted_ca(
        ca_store=ca_store,
        ca_chain_crt=ca_chain_crt,
        nodes_trusted_cas=[
            ("clickhouse1", cas[:-2] + cas[2:]),
            ("clickhouse2", cas),
            ("clickhouse3", cas),
        ],
        nodes_messages={
            ("clickhouse1", "clickhouse1"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse2"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse3"): error_certificate_verify_failed,
            ("clickhouse2", "clickhouse1"): error_tlsv1_alert_unknown_ca,
            ("clickhouse2", "clickhouse2"): None,
            ("clickhouse2", "clickhouse3"): None,
            ("clickhouse3", "clickhouse1"): error_tlsv1_alert_unknown_ca,
            ("clickhouse3", "clickhouse2"): None,
            ("clickhouse3", "clickhouse3"): None,
        },
    )


@TestScenario
def without_caconfig_missing_trusted_ca_on_all_nodes(self, ca_store, ca_chain_crt, cas):
    """Check when one of the CAs in the chain is missing in the system trust store
    on different nodes.
    """

    without_caconfig_missing_trusted_ca(
        ca_store=ca_store,
        ca_chain_crt=ca_chain_crt,
        nodes_trusted_cas=[
            ("clickhouse1", cas[:-2] + cas[2:]),
            ("clickhouse2", cas[1:]),
            ("clickhouse3", cas[:-1]),
        ],
        nodes_messages={
            ("clickhouse1", "clickhouse1"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse2"): error_certificate_verify_failed,
            ("clickhouse1", "clickhouse3"): error_certificate_verify_failed,
            ("clickhouse2", "clickhouse1"): error_certificate_verify_failed,
            ("clickhouse2", "clickhouse2"): error_certificate_verify_failed,
            ("clickhouse2", "clickhouse3"): error_certificate_verify_failed,
            ("clickhouse3", "clickhouse1"): error_certificate_verify_failed,
            ("clickhouse3", "clickhouse2"): error_certificate_verify_failed,
            ("clickhouse3", "clickhouse3"): error_certificate_verify_failed,
        },
    )


@TestFeature
def use_root_ca(self):
    """Check using root CA to sign server certificate."""

    ca_store = define("CA store", self.context.root_store)
    cas = define(
        "CAs",
        [
            os.path.join(self.context.root_store, "ca.crt"),
        ],
    )

    with Given("I create CA chain certificate"):
        ca_chain_crt = create_ca_chain_certificate(
            outfile=f"{os.path.join(self.context.tmpdir, 'ca_chain.crt')}", cas=cas
        )

    with Feature(
        "with caconfig",
        description="Check secure connection when caConfig parameter is set.",
    ):
        Scenario("all certificates in chain", test=with_caconfig)(
            ca_store=ca_store, ca_chain_crt=ca_chain_crt
        )
        Scenario(
            "invalid first CA in chain on one node",
            test=with_caconfig_missing_first_ca_in_chain_on_one_node,
        )(
            ca_store=ca_store,
            ca_chain_crt=ca_chain_crt,
            cas=[
                os.path.join(self.context.root_store, "ca.crt"),
                os.path.join(self.context.sub1_store, "ca.crt"),
            ],
        )

    with Feature(
        "without caconfig",
        description="Check secure connection when caConfig parameter is not set.",
    ):
        Scenario("all trusted", test=without_caconfig)(
            ca_store=ca_store, ca_chain_crt=ca_chain_crt, trusted_cas=cas
        )
        Scenario(
            "missing first trusted CA on one node",
            test=without_caconfig_missing_first_trusted_ca_on_one_node,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)


@TestFeature
def use_first_intermediate_ca(self):
    """Check using first intermediate CA to sign server certificate."""

    ca_store = define("CA store", self.context.sub1_store)
    cas = define(
        "CAs",
        [
            os.path.join(self.context.sub1_store, "ca.crt"),
            os.path.join(self.context.root_store, "ca.crt"),
        ],
    )

    with Given("I create CA chain certificate"):
        ca_chain_crt = create_ca_chain_certificate(
            outfile=f"{os.path.join(self.context.tmpdir, 'ca_chain.crt')}", cas=cas
        )

    with Feature(
        "with caconfig",
        description="Check secure connection when caConfig parameter is set.",
    ):
        Scenario("all certificates in chain", test=with_caconfig)(
            ca_store=ca_store, ca_chain_crt=ca_chain_crt
        )
        Scenario(
            "missing first CA in chain on one node",
            test=with_caconfig_missing_first_ca_in_chain_on_one_node,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)
        Scenario(
            "missing last CA in chain on one node",
            test=with_caconfig_missing_last_ca_in_chain_on_one_node,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)

    Scenario(test=with_caconfig)(ca_store=ca_store, ca_chain_crt=ca_chain_crt)

    with Feature(
        "without caconfig",
        description="Check secure connection when caConfig parameter is not set",
    ):
        Scenario(test=without_caconfig)(
            ca_store=ca_store, ca_chain_crt=ca_chain_crt, trusted_cas=cas
        )
        Scenario(
            "missing first trusted CA on one node",
            test=without_caconfig_missing_first_trusted_ca_on_one_node,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)
        Scenario(
            "missing last trusted CA on one node",
            test=without_caconfig_missing_first_trusted_ca_on_one_node,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)


@TestFeature
def use_second_intermediate_ca(self):
    """Check using second intermediate CA to sign server certificate."""

    ca_store = define("CA store", self.context.sub2_store)
    cas = define(
        "CAs",
        [
            os.path.join(self.context.sub2_store, "ca.crt"),
            os.path.join(self.context.sub1_store, "ca.crt"),
            os.path.join(self.context.root_store, "ca.crt"),
        ],
    )

    with Given("I create CA chain certificate"):
        ca_chain_crt = create_ca_chain_certificate(
            outfile=f"{os.path.join(self.context.tmpdir, 'ca_chain.crt')}", cas=cas
        )

    with Feature(
        "with caconfig",
        description="Check secure connection when caConfig parameter is set.",
    ):
        Scenario("all certificates in chain", test=with_caconfig)(
            ca_store=ca_store, ca_chain_crt=ca_chain_crt
        )
        Scenario(
            "missing first CA in chain on one node",
            test=with_caconfig_missing_first_ca_in_chain_on_one_node,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)
        Scenario(
            "missing middle CA in chain on one node",
            test=with_caconfig_missing_middle_ca_in_chain_on_one_node,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)
        Scenario(
            "missing last CA in chain on one node",
            test=with_caconfig_missing_last_ca_in_chain_on_one_node,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)
        Scenario(
            "missing some CA in chain on all nodes",
            test=with_caconfig_missing_ca_in_chain_on_all_nodes,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)

    with Feature(
        "without caconfig",
        description="Check secure connection when caConfig parameter is not set",
    ):
        Scenario(test=without_caconfig)(
            ca_store=ca_store, ca_chain_crt=ca_chain_crt, trusted_cas=cas
        )
        Scenario(
            "missing first trusted CA on one node",
            test=without_caconfig_missing_first_trusted_ca_on_one_node,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)
        Scenario(
            "missing middle trusted CA on one node",
            test=without_caconfig_missing_middle_trusted_ca_on_one_node,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)
        Scenario(
            "missing last trusted CA on one node",
            test=without_caconfig_missing_first_trusted_ca_on_one_node,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)
        Scenario(
            "missing trusted CA on all nodes",
            test=without_caconfig_missing_trusted_ca_on_all_nodes,
        )(ca_store=ca_store, ca_chain_crt=ca_chain_crt, cas=cas)


@TestFeature
@Name("ca chain")
def feature(self):
    """Check certificates signed using different CA chains."""

    with Given("I create temporary directory where I will create CA stores"):
        self.context.tmpdir = create_local_tmpdir()

    with And("I create root CA store"):
        self.context.root_store = create_root_ca_store(
            path=self.context.tmpdir, name="root"
        )

    with And("I create first intermediate sub1 CA store"):
        self.context.sub1_store = create_intermediate_ca_store(
            path=self.context.tmpdir, name="sub1", root_store=self.context.root_store
        )

    with And("I create second intermediate sub2 CA store"):
        self.context.sub2_store = create_intermediate_ca_store(
            path=self.context.tmpdir, name="sub2", root_store=self.context.sub1_store
        )

    Feature(run=use_root_ca)
    Feature(run=use_first_intermediate_ca)
    Feature(run=use_second_intermediate_ca)
