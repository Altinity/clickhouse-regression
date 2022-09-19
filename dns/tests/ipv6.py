import time
import docker

from testflows.core import *
from dns.requirements import *
from helpers.common import *

@TestFeature
@Name("ipv6")
def feature(self):
    """Check that clickhouse nodes are able to use ipv6."""

    cluster = self.context.cluster
    docker_client = docker.from_env()

    def get_instance_docker_id(instance_name):
        return "dns_env" + "_" + instance_name + "_1"

    def get_instance_ip(instance_name):
        docker_id = get_instance_docker_id(instance_name)
        handle = docker_client.containers.get(docker_id)
        return list(handle.attrs["NetworkSettings"]["Networks"].values())[0][
            "IPAddress"
        ]

    def get_instance_global_ipv6(instance_name):
        docker_id = get_instance_docker_id(instance_name)
        handle = docker_client.containers.get(docker_id)
        return list(handle.attrs["NetworkSettings"]["Networks"].values())[0][
            "GlobalIPv6Address"
        ]

    def setup_dns_server(ip):
        domains_string = "test3.example.com test2.example.com test1.example.com"
        example_file_path = f'regression/dns/tests/lookup/example.com'
        cluster.command(None, f"echo '{ip} {domains_string}' > {example_file_path}")

    def setup_ch_server(dns_server_ip):
        cluster.node('clickhouse1').command(f"echo 'nameserver {dns_server_ip}' > /etc/resolv.conf")
        cluster.node('clickhouse1').command("echo 'options ndots:0' >> /etc/resolv.conf")
        cluster.node('clickhouse1').query("SYSTEM DROP DNS CACHE")

    def build_endpoint_v4(ip):
        return f"'http://{ip}:8123/?query=SELECT+1&user=test_dns'"

    def build_endpoint_v6(ip):
        return build_endpoint_v4(f"[{ip}]")

    with Scenario("Test host regexp multiple ptr v4 fails with wrong resolution"):
        server_ip = get_instance_ip("clickhouse1")
        random_ip = "9.9.9.9"
        dns_server_ip = get_instance_ip("coredns")

        with When("I setup the DNS server"):
            setup_dns_server(random_ip)

        with And("I setup Clickhouse server"):
            setup_ch_server(dns_server_ip)

        endpoint = build_endpoint_v4(server_ip)

        assert "1\n" != cluster.node('clickhouse2').command(f"curl {endpoint}")

    with Scenario("Test host regexp multiple ptr v4"):
        server_ip = get_instance_ip("clickhouse1")
        client_ip = get_instance_ip("clickhouse2")
        dns_server_ip = get_instance_ip("coredns")

        setup_dns_server(client_ip)
        setup_ch_server(dns_server_ip)

        endpoint = build_endpoint_v4(server_ip)

        assert "1\n" != cluster.node('clickhouse2').command(f"curl {endpoint}")

    with Scenario("Test host regexp multiple ptr v6"):
        setup_dns_server('2001:3984:3989::1:1111')
        setup_ch_server(get_instance_global_ipv6("coredns"))

        endpoint = build_endpoint_v6('2001:3984:3989::1:1111')

        assert "1\n" != cluster.node('clickhouse2').command(f"curl -6 {endpoint}")
