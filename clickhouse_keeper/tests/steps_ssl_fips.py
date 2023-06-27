from testflows.core import *
from helpers.common import create_xml_config_content, add_config, add_invalid_config
import time
from helpers.common import getuid, instrument_clickhouse_server_log
from testflows.asserts import error
from testflows.connect import Shell

remote_entries_ssl = {
    "server": {
        "shard": {"replica": {"host": "clickhouse1", "port": "9440", "secure": "1"}}
    }
}

_entries_open_ssl = {
    "server": {
        "certificateFile": "/etc/clickhouse-server/config.d/server.crt",
        "privateKeyFile": "/etc/clickhouse-server/config.d/server.key",
        "dhParamsFile": "/etc/clickhouse-server/config.d/dhparam.pem",
        "verificationMode": "none",
        "caConfig": "/etc/clickhouse-server/config.d/altinity_blog_ca.crt",
        "loadDefaultCAFile": "false",
        "cacheSessions": "true",
        "requireTLSv1_2": "true",
        "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
        "cipherList": "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384",
        "preferServerCiphers": "true",
    },
    "client": {
        "certificateFile": "/etc/clickhouse-server/config.d/server.crt",
        "privateKeyFile": "/etc/clickhouse-server/config.d/server.key",
        "caConfig": "/etc/clickhouse-server/config.d/altinity_blog_ca.crt",
        "loadDefaultCAFile": "false",
        "cacheSessions": "true",
        "requireTLSv1_2": "true",
        "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
        "preferServerCiphers": "true",
        "verificationMode": "none",
        "invalidCertificateHandler": {"name": "AcceptCertificateHandler"},
    },
}


_entries_client_ssl = {
    "secure": "true",
    "openSSL": {
        "client": {
            "certificateFile": "/etc/clickhouse-server/config.d/server.crt",
            "privateKeyFile": "/etc/clickhouse-server/config.d/server.key",
            "caConfig": "/etc/clickhouse-server/config.d/altinity_blog_ca.crt",
            "loadDefaultCAFile": "false",
            "cacheSessions": "true",
            "requireTLSv1_2": "true",
            "disableProtocols": "sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_3",
            "preferServerCiphers": "true",
            "verificationMode": "none",
            "invalidCertificateHandler": {"name": "AcceptCertificateHandler"},
        }
    },
}


@TestStep(Given)
def create_client_ssl(
    self, config_d_dir="/etc/clickhouse-client/", config_file="config.xml"
):
    try:
        with Given("I create remote config"):
            create_configuration_ssl(
                root="config",
                config_d_dir=config_d_dir,
                config_file=config_file,
                nodes=None,
                entries=_entries_client_ssl,
                restart=False,
                modify=True,
                check_preprocessed=False,
            )
        yield
    finally:
        for name in self.context.cluster.nodes["clickhouse"][:13]:
            node = self.context.cluster.node(name)
            node.cmd(f"rm -rf {config_d_dir}{config_file} ")


@TestStep(Given)
def create_open_ssl(
    self, config_d_dir="/etc/clickhouse-server/config.d/", config_file="ssl_conf.xml"
):
    with Given("I create remote config"):
        try:
            create_configuration_ssl(
                section="openSSL",
                config_d_dir=config_d_dir,
                config_file=config_file,
                nodes=None,
                entries=_entries_open_ssl,
                restart=False,
                modify=True,
                check_preprocessed=False,
            )
            yield
        finally:
            for name in self.context.cluster.nodes["clickhouse"][:13]:
                node = self.context.cluster.node(name)
                node.cmd(f"rm -rf {config_d_dir}{config_file} ")


@TestStep(Given)
def create_3_3_cluster_config_ssl(self):
    with Given("I create remote config"):
        entries = {
            "Cluster_3shards_with_3replicas": [
                {
                    "shard": [
                        {
                            "replica": {
                                "host": "clickhouse1",
                                "port": "9440",
                                "secure": "1",
                            }
                        },
                        {
                            "replica": {
                                "host": "clickhouse2",
                                "port": "9440",
                                "secure": "1",
                            }
                        },
                        {
                            "replica": {
                                "host": "clickhouse3",
                                "port": "9440",
                                "secure": "1",
                            }
                        },
                    ]
                },
                {
                    "shard": [
                        {
                            "replica": {
                                "host": "clickhouse4",
                                "port": "9440",
                                "secure": "1",
                            }
                        },
                        {
                            "replica": {
                                "host": "clickhouse5",
                                "port": "9440",
                                "secure": "1",
                            }
                        },
                        {
                            "replica": {
                                "host": "clickhouse6",
                                "port": "9440",
                                "secure": "1",
                            }
                        },
                    ]
                },
                {
                    "shard": [
                        {
                            "replica": {
                                "host": "clickhouse7",
                                "port": "9440",
                                "secure": "1",
                            }
                        },
                        {
                            "replica": {
                                "host": "clickhouse8",
                                "port": "9440",
                                "secure": "1",
                            }
                        },
                        {
                            "replica": {
                                "host": "clickhouse9",
                                "port": "9440",
                                "secure": "1",
                            }
                        },
                    ]
                },
            ]
        }

        create_configuration_ssl(entries=entries, modify=True)


@TestStep(Given)
def create_configuration_ssl(
    self,
    root="clickhouse",
    section="remote_servers",
    config_d_dir="/etc/clickhouse-server/config.d/",
    config_file="remote.xml",
    nodes=None,
    entries=remote_entries_ssl,
    restart=False,
    modify=True,
    check_preprocessed=True,
):
    """Create ClickHouse remote servers configuration.

    :param config_d_dir: path to CLickHouse config.d folder
    :param config_file: name of config file
    :param nodes: nodes which will use remote config section
    :param entries: inside config information
    """

    nodes = self.context.cluster.nodes["clickhouse"][0:13] if nodes is None else nodes

    for name in nodes:
        node = self.context.cluster.node(name)

        if root is not "clickhouse":
            _entries = entries
        else:
            _entries = {section: entries}

        with Then("I converting config file content to xml"):
            config = create_xml_config_content(
                _entries, root=root, config_file=config_file, config_d_dir=config_d_dir
            )

        with And(f"I add config to {name}"):
            add_config_section_ssl(
                config=config,
                restart=restart,
                modify=modify,
                user=None,
                node=node,
                check_preprocessed=check_preprocessed,
            )


@TestStep(Given)
def add_config_section_ssl(
    self,
    config,
    timeout=300,
    restart=False,
    modify=True,
    node=None,
    user=None,
    wait_healthy=True,
    check_preprocessed=True,
):
    """Add config on cluster nodes."""
    return add_config(
        config=config,
        restart=restart,
        modify=modify,
        user=user,
        node=node,
        wait_healthy=wait_healthy,
        check_preprocessed=check_preprocessed,
    )


@TestStep(When)
def create_config_section_ssl(
    self,
    config_d_dir="/etc/clickhouse-server/config.d/",
    config_file="use_secure_keeper.xml",
    control_nodes=None,
    cluster_nodes=None,
    check_preprocessed=False,
    restart=False,
    modify=True,
):
    """Create section for ClickHouse servers config file.

    :param config_d_dir: path to CLickHouse config.d folder
    :param config_file: name of config file
    :param control_nodes: nodes which are using for Zookeeper or Keeper
    :param cluster_nodes: nodes which will be controlled by control_nodes cluster
    """
    try:
        secure = self.context.secure

        control_nodes = (
            self.context.cluster.nodes["clickhouse"][0:3]
            if control_nodes is None
            else control_nodes
        )
        cluster_nodes = (
            self.context.cluster.nodes["clickhouse"][0:12]
            if cluster_nodes is None
            else cluster_nodes
        )
        for name in cluster_nodes:
            node = self.context.cluster.node(name)
            node_part = []
            for name1 in control_nodes:
                node_element = {
                    "node": {"host": f"{name1}", "port": "9281", "secure": f"{secure}"}
                }
                node_part.append(node_element)
            _entries = {"zookeeper": node_part}
            with When(f"I add config to {name}"):
                config = create_xml_config_content(
                    _entries, config_file=config_file, config_d_dir=config_d_dir
                )

            with And(f"I add config to {name}"):
                add_config_section_ssl(
                    config=config,
                    restart=restart,
                    modify=modify,
                    user=None,
                    node=node,
                    check_preprocessed=check_preprocessed,
                )
        yield
    finally:
        for name in self.context.cluster.nodes["clickhouse"][:13]:
            node = self.context.cluster.node(name)
            node.cmd(f"rm -rf {config_d_dir}{config_file} ")


@TestStep(When)
def create_keeper_cluster_configuration_ssl(
    self,
    invalid_config=False,
    config_d_dir="/etc/clickhouse-server/config.d/",
    config_file="enable_secure_keeper.xml",
    nodes=None,
    test_setting_name="startup_timeout",
    test_setting_value="30000",
    check_preprocessed=False,
    tcp_port=9281,
    restart=False,
    modify=True,
):
    """Create ClickHouse Keeper raft configuration file.

    :param config_d_dir: path to CLickHouse config.d folder
    :param config_file: name of config file
    :param nodes: nodes which are used as Keeper nodes (standalone or mixed)
    """
    try:
        tcp_port_secure = self.context.tcp_port_secure

        nodes = (
            self.context.cluster.nodes["clickhouse"][0:3] if nodes is None else nodes
        )
        id2 = 0
        if tcp_port_secure:
            port = "tcp_port_secure"
        else:
            port = "tcp_port"

        for name in nodes:
            id2 = id2 + 1
            node = self.context.cluster.node(name)
            server_part = [{"secure": self.context.ssl}]
            id = 0
            for name1 in nodes:
                id = id + 1
                server_element = {
                    "server": {"id": f"{id}", "hostname": f"{name1}", "port": "9444"},
                }
                server_part.append(server_element)

            _entries = {
                "keeper_server": {
                    port: f"{tcp_port}",
                    "server_id": f"{id2}",
                    "log_storage_path": "/var/lib/clickhouse/coordination/log",
                    "snapshot_storage_path": "/var/lib/clickhouse/coordination/snapshots",
                    "coordination_settings": {
                        "operation_timeout_ms": "10000",
                        "session_timeout_ms": "30000",
                        "raft_logs_level": "information",
                        # "election_timeout_upper_bound_ms": "10000",
                        "rotate_log_storage_interval": "10000",
                        # "startup_timeout": "22000",
                        "heart_beat_interval_ms": "5000",
                        f"{test_setting_name}": f"{test_setting_value}",
                    },
                    "raft_configuration": server_part,
                }
            }
            with When(f"I create xml config content to {name}"):
                config = create_xml_config_content(
                    _entries, config_file=config_file, config_d_dir=config_d_dir
                )

            if invalid_config:
                xfail("need to finsh")

            else:
                with And(f"I add config to {name}"):
                    add_config_section_ssl(
                        config=config,
                        restart=restart,
                        modify=modify,
                        user=None,
                        node=node,
                        wait_healthy=False,
                        check_preprocessed=check_preprocessed,
                    )
        yield
    finally:
        for name in self.context.cluster.nodes["clickhouse"][:13]:
            node = self.context.cluster.node(name)
            node.cmd(f"rm -rf {config_d_dir}{config_file} ")


@TestStep(Given)
def start_mixed_keeper_ssl(
    self,
    control_nodes=None,
    cluster_nodes=None,
    rest_cluster_nodes=None,
    test_setting_name="startup_timeout",
    test_setting_value="30000",
):
    """Start 9 nodes ClickHouse server with one shared 3 nodes shard Keeper."""
    cluster = self.context.cluster
    control_nodes = (
        cluster.nodes["clickhouse"][6:9] if control_nodes is None else control_nodes
    )
    cluster_nodes = (
        cluster.nodes["clickhouse"][0:9] if cluster_nodes is None else cluster_nodes
    )
    rest_cluster_nodes = (
        cluster.nodes["clickhouse"][0:6]
        if rest_cluster_nodes is None
        else rest_cluster_nodes
    )
    try:
        with Given("I stop all ClickHouse server nodes"):
            for name in cluster_nodes:

                retry(cluster.node(name).stop_clickhouse, timeout=100, delay=1)(
                    safe=False
                )

        with And("I clean ClickHouse Keeper server nodes"):
            clean_coordination_on_all_nodes1()

        with And("I create server Keeper config"):
            create_config_section_ssl(
                control_nodes=control_nodes,
                cluster_nodes=cluster_nodes,
                check_preprocessed=False,
                restart=False,
                modify=True,
            )

        with And("I create server openSSL config"):
            create_open_ssl()

        with And("I create client openSSL config"):
            create_client_ssl()

        with And("I create mixed 3 nodes Keeper server config file"):
            create_keeper_cluster_configuration_ssl(
                nodes=control_nodes,
                test_setting_name=test_setting_name,
                test_setting_value=test_setting_value,
                check_preprocessed=False,
                restart=False,
                modify=True,
            )

        with And("I start mixed ClickHouse server nodes"):
            for name in control_nodes:
                retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)(
                    wait_healthy=False
                )

        with And(f"I check that ruok returns imok"):
            for name in control_nodes:
                retry(cluster.node("bash-tools").cmd, timeout=100, delay=1)(
                    f"echo ruok | nc {name} {self.context.port}",
                    exitcode=0,
                    message="F",
                )

        if rest_cluster_nodes != "no_rest_nodes":
            with And("I start rest ClickHouse server nodes"):
                for name in rest_cluster_nodes:
                    retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)()

        yield
    finally:
        with Finally("I clean up"):
            with By("I clean ClickHouse Keeper server nodes"):
                clean_coordination_on_all_nodes1()


@TestStep(Given)
def clean_coordination_on_all_nodes1(self, cluster_nodes=None):
    """Clean coordination on ClickHouse server nodes.

    :param cluster_nodes: Clickhouse server nodes
    """
    cluster_nodes = (
        self.context.cluster.nodes["clickhouse"][:12]
        if cluster_nodes is None
        else cluster_nodes
    )
    for name in cluster_nodes:
        node = self.context.cluster.node(name)
        node.cmd(
            f"rm -rf /var/lib/clickhouse/coordination/snapshots "
            f"&& rm -rf /var/lib/clickhouse/coordination/log "
        )


@TestStep(Given)
def start_keepers_ssl(self, standalone_keeper_nodes=None, manual_cleanup=False):
    """Start Keeper services.

    :param standalone_keeper_nodes: nodes which will be used for standalone Keeper cluster
    """
    standalone_keeper_nodes = (
        self.context.cluster.nodes["clickhouse"][9:12]
        if standalone_keeper_nodes is None
        else standalone_keeper_nodes
    )
    try:
        for name in standalone_keeper_nodes:
            node = self.context.cluster.node(name)
            with When(f"I start {name}"):
                with By("starting keeper process"):
                    node.cmd("rm -rf /tmp/clickhouse-keeper.pid")
                    node.cmd(
                        "clickhouse keeper --config /etc/clickhouse-server/config.xml"
                        " --pidfile=/tmp/clickhouse-keeper.pid --daemon",
                        exitcode=0,
                    )

                with And("checking that keeper pid file was created"):
                    node.cmd(
                        "ls /tmp/clickhouse-keeper.pid",
                        exitcode=0,
                        message="/tmp/clickhouse-keeper.pid",
                    )
        yield
    finally:
        with Given("I stop all keepers"):
            if manual_cleanup is False:
                for name in standalone_keeper_nodes:
                    node = self.context.cluster.node(name)
                    with When(f"I stop {name}"):
                        with By("sending kill -TERM to keeper process"):
                            if node.cmd("ls /tmp/clickhouse-keeper.pid", exitcode=0):
                                pid = node.cmd(
                                    "cat /tmp/clickhouse-keeper.pid"
                                ).output.strip()
                                node.cmd(f"kill -TERM {pid}", exitcode=0)
                        with And("checking pid does not exist"):
                            retry(node.cmd, timeout=100, delay=1)(
                                f"ps {pid}", exitcode=1, steps=False
                            )


@TestStep(Given)
def stop_keepers_ssl(self, cluster_nodes=None):
    """Stop ClickHouses group.

    :param cluster_nodes: Clickhouse server nodes
    """
    cluster_nodes = (
        self.context.cluster.nodes["clickhouse"][:9]
        if cluster_nodes is None
        else cluster_nodes
    )
    for name in cluster_nodes:
        node = self.context.cluster.node(name)
        with When(f"I stop {name}"):
            with By("sending kill -TERM to keeper process"):
                if node.cmd("ls /tmp/clickhouse-keeper.pid", exitcode=0):
                    pid = node.cmd("cat /tmp/clickhouse-keeper.pid").output.strip()
                    node.cmd(f"kill -TERM {pid}", exitcode=0)
            with And("checking pid does not exist"):
                retry(node.cmd, timeout=100, delay=1)(
                    f"ps {pid}", exitcode=1, steps=False
                )


@TestStep(Given)
def start_stand_alone_keeper_ssl(self):
    """Start 9 nodes ClickHouse server and standalone 3 nodes Keeper."""
    cluster = self.context.cluster
    try:
        with Given("I start standalone 3 nodes Keeper server"):
            time.sleep(10)
            create_keeper_cluster_configuration_ssl(
                nodes=cluster.nodes["clickhouse"][9:12]
            )

        with Given("I start all standalone Keepers nodes"):
            time.sleep(10)
            for name in cluster.nodes["clickhouse"][9:12]:
                cluster.node(name).stop_clickhouse()
            start_keepers_ssl(standalone_keeper_nodes=cluster.nodes["clickhouse"][9:12])

        with And("I add Keeper server configuration file"):
            time.sleep(3)
            create_config_section_ssl(
                control_nodes=cluster.nodes["clickhouse"][9:12],
                cluster_nodes=cluster.nodes["clickhouse"][:12],
            )

        with And("I start ClickHouse server"):
            time.sleep(3)
            for name in cluster.nodes["clickhouse"][:9]:
                cluster.node(name).restart_clickhouse()
        yield
    finally:
        with Finally("I clean up"):
            with By("I start clickhouse servers", flags=TE):
                stop_keepers_ssl(cluster_nodes=cluster.nodes["clickhouse"][9:12])
                for name in cluster.nodes["clickhouse"][9:12]:
                    self.context.cluster.node(name).start_clickhouse(wait_healthy=False)
                    time.sleep(5)

            clean_coordination_on_all_nodes1()


@TestStep
def openssl_check_step(self, node=None, port="9440"):
    """Check ClickHouse connection to Clickhouse Keeper is ssl."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    node.cmd(
        f"openssl s_client -connect clickhouse1:{port}",
        no_checks=True,
    )


@TestStep(Then)
def openssl_client_connection(
    self,
    options="",
    port=None,
    node=None,
    hostname=None,
    success=True,
    message=None,
    messages=None,
    exitcode=None,
):
    """Check SSL connection using openssl s_client utility."""
    if node is None:
        node = self.context.node

    if port is None:
        port = self.context.connection_port

    if hostname is None:
        hostname = node.name

    if exitcode is None:
        if success:
            exitcode = 0
        else:
            exitcode = "!= 0"

    node.command(
        f'openssl s_client -brief {options} -connect {hostname}:{port} <<< "Q"',
        message=message,
        messages=messages,
        exitcode=exitcode,
    )