#!/usr/bin/env python3
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs


xfails = {}

ffails = {
    "/jwt authentication/static key": (Skip, "Under development"),
    "/jwt authentication/static jwks": (Skip, "Under development"),
    "/jwt authentication/dynamic jwks": (Skip, "Under development"),
}


@TestFeature
@Name("jwt authentication")
@FFails(ffails)
@XFails(xfails)
@ArgumentParser(argparser)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """Run tests for JWT authentication in Clickhouse."""
    nodes = {
        "clickhouse": (
            "clickhouse1",
            "clickhouse2",
            "clickhouse3",
            "clickhouse4",
            "clickhouse5",
            "clickhouse6",
            "clickhouse7",
            "clickhouse8",
            "clickhouse9",
            "clickhouse10",
        ),
        "jwks_server": ("jwks_server",),
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

    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node2 = self.context.cluster.node("clickhouse2")
    self.context.node3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.cluster.node(node) for node in nodes["clickhouse"]
    ]

    Scenario(run=load("jwt_authentication.tests.static_key.feature", "feature"))
    Scenario(run=load("jwt_authentication.tests.jwks.feature", "feature"))
    Scenario(run=load("jwt_authentication.tests.dynamic_jwks.feature", "feature"))


if main():
    regression()
