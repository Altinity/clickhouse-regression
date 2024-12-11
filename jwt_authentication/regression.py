#!/usr/bin/env python3
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs


xfails = {
    "/jwt authentication/static key/different algorithms/adding validator asymmetric algorithm/check ES256K algorithm": [
        (Fail, "ES256K algorithm is not working, need to investigate")
    ],
    "/jwt authentication/static key/different algorithms/adding validator asymmetric algorithm/check Ed448 algorithm": [
        (
            Fail,
            "Ed448 algorithm is not working, need to investigate",
        )
    ],
    "/jwt authentication/static jwks/feature/mismatched algorithms": [
        (Fail, "Needs investigation")
    ],
    "/jwt authentication/static key/invalid token/login with invalid token": [
        (Fail, "Unexpected LOGICAL_ERROR")
    ],
}

ffails = {
    "/jwt authentication/static key": (Skip, "Under development"),
    "/jwt authentication/static jwks": (Skip, "Under development"),
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
    self.context.node4 = self.context.cluster.node("clickhouse4")
    self.context.node5 = self.context.cluster.node("clickhouse5")
    self.context.node6 = self.context.cluster.node("clickhouse6")
    self.context.node7 = self.context.cluster.node("clickhouse7")
    self.context.node8 = self.context.cluster.node("clickhouse8")
    self.context.node9 = self.context.cluster.node("clickhouse9")
    self.context.node10 = self.context.cluster.node("clickhouse10")
    self.context.nodes = [self.context.cluster.node(node) for node in nodes["clickhouse"]]

    Scenario(run=load("jwt_authentication.tests.static_key.feature", "feature"))
    Scenario(run=load("jwt_authentication.tests.jwks.feature", "feature"))


if main():
    regression()
