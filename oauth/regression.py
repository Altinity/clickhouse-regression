#!/usr/bin/env python3
import sys
import os

from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from testflows.core import *


append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser as base_argparser
from helpers.argparser import CaptureClusterArgs
from oauth.requirements.requirements import *
from oauth.tests.steps import azure_application as azure
from oauth.tests.steps import keycloak_realm as keycloak
from oauth.tests.steps.azure_application import setup_azure_application


def argparser(parser):
    """Add arguments to the argument parser for OAuth tests."""
    base_argparser(parser)

    parser.add_argument(
        "--tenant-id",
        # type=Secret(name="tenant_id"),
        type=str,
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
        # type=Secret(name="client_secret"),
        type=str,
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


def write_env_file(identity_provider, tenant_id, client_id, client_secret):
    env_dir = os.path.join(
        current_dir(),
        "envs",
        f"{identity_provider.lower()}",
        f"{identity_provider.lower()}_env",
    )
    os.makedirs(env_dir, exist_ok=True)
    env_path = os.path.join(env_dir, ".env")
    print(env_path)
    with open(env_path, "w") as f:
        f.write(
            f"TENANT_ID = {tenant_id}\n"
            f"CLIENT_SECRET = {client_secret}\n"
            f"CLIENT_ID = {client_id}\n"
        )


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
        "clickhouse": (
            "clickhouse1",
            "clickhouse2",
            "clickhouse3",
        ),
        "grafana": ("grafana",),
    }
    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        providers = {"keycloak": keycloak, "azure": azure}

        docker_compose_config = os.path.join(
            current_dir(), "envs", identity_provider.lower()
        )

        if identity_provider.lower() == "azure":
            cred = ClientSecretCredential(tenant_id, client_id, client_secret)
            self.context.client = GraphServiceClient(
                credentials=cred, scopes=["https://graph.microsoft.com/.default"]
            )
            application = setup_azure_application()

            self.context.tenant_id = tenant_id
            self.context.client_id = application.app_id
            self.context.client_secret = application.password_credentials[0].secret_text

            write_env_file(
                identity_provider,
                tenant_id,
                self.context.client_id,
                self.context.client_secret,
            )
        elif identity_provider.lower() == "keycloak":
            self.context.keycloak_url = "http://localhost:8080"
            self.context.username = "demo"
            self.context.password = "demo"
            self.context.client_secret = "grafana-secret"
            self.context.client_id = "grafana-client"
            self.context.realm_name = "grafana"

        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=docker_compose_config,
        )

        self.context.cluster = cluster
        self.context.provider_client = providers[identity_provider.lower()]
        self.context.provider_name = identity_provider

    self.context.node = self.context.cluster.node("clickhouse1")
    pause()
    # self.context.node2 = self.context.cluster.node("clickhouse2")
    # self.context.node3 = self.context.cluster.node("clickhouse3")
    # self.context.nodes = [
    #     self.context.cluster.node(node) for node in nodes["clickhouse"]
    # ]

    Scenario(run=load("oauth.tests.sanity", "feature"))
    Scenario(run=load("oauth.tests.configuration", "feature"))
    Scenario(run=load("oauth.tests.authentication", "feature"))
    Scenario(run=load("oauth.tests.setup", "feature"))
    Scenario(run=load("oauth.tests.tokens", "feature"))
    Scenario(run=load("oauth.tests.parameters_and_caching", "feature"))
    Scenario(run=load("oauth.tests.actions", "feature"))


if main():
    regression()
