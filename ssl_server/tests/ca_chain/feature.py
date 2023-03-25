from ssl_server.tests.ca_chain.steps import *


@TestOutline
def check_using_ca_chain(self, ca_store, cas, nodes=None):
    """Check secure connection using server certificate signed by a specified CA and CAs chain."""
    if nodes is None:
        nodes = self.context.cluster.nodes["clickhouse"]

    with And("I create CA chain certificate"):
        ca_chain_crt = create_ca_chain_certificate(
            outfile=f"{os.path.join(self.context.tmpdir, 'ca_chain.crt')}", cas=cas
        )

    for node_name in nodes:
        with Given("I create and add server certificate to {node_name}"):
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
        with And("I add SSL configuration to {node_name}"):
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


@TestScenario
def use_root_ca(self):
    """Check using root CA to sign server certificate."""

    ca_store = define("CA store", self.context.root_store)
    cas = define("CAs", [os.path.join(self.context.root_store, "ca.crt")])

    check_using_ca_chain(ca_store=ca_store, cas=cas)


@TestScenario
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

    check_using_ca_chain(ca_store=ca_store, cas=cas)


@TestScenario
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

    check_using_ca_chain(ca_store=ca_store, cas=cas)


@TestFeature
@Name("ca chain")
def feature(self):
    """Check using certificates signed using different CA chains."""

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

    for scenario in loads(current_module(), Scenario):
        scenario()
