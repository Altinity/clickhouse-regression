import time

from testflows.core import *
from dns.requirements import *
from helpers.common import *


@TestScenario
@Requirements(RQ_SRS_031_ClickHouse_DNS_Lookup("1.0"))
@Name("lookup")
def scenario(self):
    """Check that clickhouse nodes are able to communicate using DNS."""

    cluster = self.context.cluster

    with Given("I have the COREDNS IP"):
        x = cluster.command(
            None, "docker ps | grep coredns | cut -d ' ' -f 1 | head -n 1"
        ).output
        query = (
            "docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "
            + x
        )
        COREDNS_IP = cluster.command(None, query).output

    with And("I write the COREDNS IP into resolv.conf"):
        cluster.command(
            "clickhouse1", f"echo 'nameserver {COREDNS_IP}' > /etc/resolv.conf"
        )
        cluster.command("clickhouse1", "echo 'options ndots:0' >> /etc/resolv.conf")

    with And("I have the CLIENT IP"):
        x = cluster.command(
            None, "docker ps | grep clickhouse2 | cut -d ' ' -f 1 | head -n 1"
        ).output
        query = (
            "docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "
            + x
        )
        CLIENT_IP = cluster.command(None, query).output

    with And("I am listening in the background to port 8123 and 53"):
        cluster.node("clickhouse1").command(
            "tcpdump -i any -w http_and_dns.pcap port 8123 or port 53 &"
        )

    with When("I write the CLIENT IP into example.com"):
        cluster.command(
            None,
            f"echo '{CLIENT_IP} test1.example.com' > regression/dns/tests/lookup/example.com",
        )
        time.sleep(1)

    with And("I perform DNS lookup on the CLIENT IP"):
        cluster.node("clickhouse1").command(f"host -t PTR {CLIENT_IP}")

    with And("I drop the DNS CACHE"):
        cluster.node("clickhouse1").query(f"SYSTEM DROP DNS CACHE")

    with Then("I check that I see the same clickhouse version locally and remotely"):
        client_version = (
            cluster.node("clickhouse2")
            .command(
                "curl 'http://clickhouse1:8123/?user=test_dns&query=SELECT+version()'"
            )
            .output
        )
        server_version = cluster.node("clickhouse1").query(f"SELECT version()").output
        assert client_version == server_version, error()

    with When("I kill the background port listening"):
        cluster.node("clickhouse1").command("killall tcpdump")

    with And("I copy the http_and_dns.pcap file off of the docker container"):
        x = cluster.command(
            None, "docker ps | grep clickhouse1 | head -n 1 | cut -d ' ' -f 1"
        ).output
        cluster.command(
            None, f"docker cp {x}:/http_and_dns.pcap regression/dns/tests/lookup/"
        )

    with And("I update example.com with more urls."):
        cluster.command(
            None,
            f"echo '{CLIENT_IP} test3.example.com test2.example.com test1.example.com' > regression/dns/tests/lookup/example.com",
        )
        time.sleep(1)

    with And("I perform DNS lookup on the CLIENT IP"):
        cluster.node("clickhouse1").command(f"host -t PTR {CLIENT_IP}")

    with And("I drop the DNS CACHE"):
        cluster.node("clickhouse1").query(f"SYSTEM DROP DNS CACHE")

    with Then("I check that I see the same clickhouse version locally and remotely"):
        client_version = (
            cluster.node("clickhouse2")
            .command(
                "curl 'http://clickhouse1:8123/?user=test_dns&query=SELECT+version()'"
            )
            .output
        )
        server_version = cluster.node("clickhouse1").query(f"SELECT version()").output
        assert client_version == server_version, error()
