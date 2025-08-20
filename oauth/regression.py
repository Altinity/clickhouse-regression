#!/usr/bin/env python3
import sys

from testflows.core import *

append_path(sys.path, "..")

from azure.identity import ClientSecretCredential
from helpers.cluster import create_cluster
from helpers.argparser import argparser as base_argparser
from helpers.argparser import CaptureClusterArgs
from oauth.requirements.requirements import *
from msgraph.graph_service_client import GraphServiceClient


def argparser(parser):
    """Add arguments to the argument parser for OAuth tests."""
    base_argparser(parser)

    parser.add_argument(
        "--tenant-id",
        type=Secret(name="tenant_id"),
        dest="tenant_id",
        help="Tenant ID for Azure AD",
        metavar="path",
        default=None,
    )

    parser.add_argument(
        "--client-id",
        type=str,
        dest="client_id",
        help="Client ID for Azure AD application",
        metavar="string",
        default=None,
    )

    parser.add_argument(
        "--client-secret",
        type=Secret(name="client_secret"),
        dest="client_secret",
        help="Client secret for Azure AD application",
        metavar="path",
        default=None,
    )

    parser.add_argument(
        "--identity-provider",
        type=str,
        dest="identity_provider",
        help="Identity provider to use for OAuth authentication",
        metavar="string",
        default="Keycloak",
    )


xfails = {}

ffails = {}


@TestFeature
@Name("oauth")
@FFails(ffails)
@Specifications(SRS_042_OAuth_Authentication_in_ClickHouse)
@XFails(xfails)
@ArgumentParser(argparser)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
    identity_provider=None,
    tenant_id=None,
    client_id=None,
    client_secret=None,
):
    """Run tests for OAuth in Clickhouse."""
    nodes = {
        "clickhouse": ("clickhouse1",),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    if identity_provider == "Azure":
        self.context.redirect_uris = ["http://localhost:3000/login/azuread"]
        self.context.home_page_url = "http://localhost:3000"
        self.context.logout_url = "http://localhost:3000/logout"
        self.context.tenant_id = tenant_id
        self.context.client_id = client_id
        self.context.client_secret = client_secret
        cred = ClientSecretCredential(tenant_id, client_id, client_secret)
        self.context.client = GraphServiceClient(
            credentials=cred, scopes=["https://graph.microsoft.com/.default"]
        )

    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node2 = self.context.cluster.node("clickhouse2")
    self.context.node3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.cluster.node(node) for node in nodes["clickhouse"]
    ]

    Scenario(run=load("oauth.tests.sanity", "feature"))


if main():
    regression()
