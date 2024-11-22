#!/usr/bin/env python3
import sys
import os

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
    "/jwt authentication/static jwks/feature/login fails with mismatched algorithm": [
        (Fail, "Needs investigation")
    ],
    "/jwt authentication/static key/invalid token/login with invalid token": [
        (Fail, "Unexpected LOGICAL_ERROR")
    ],
}

ffails = {
    "/jwt authentication": (Skip, "Not yet implemented"),
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

    self.context.node = self.context.cluster.node("clickhouse1")

    Scenario(run=load("jwt_authentication.tests.static_key.feature", "feature"))
    Scenario(run=load("jwt_authentication.tests.jwks.feature", "feature"))


if main():
    regression()
