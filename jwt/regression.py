#!/usr/bin/env python3
import sys
import os


from testflows.core import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.common import experimental_analyzer

ffails = {}

@TestFeature
@Name("jwt")
@FFails(ffails)
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

    Scenario(run=load("jwt.tests.sanity", "scenario"))


if main():
    regression()
