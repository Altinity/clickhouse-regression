#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser as argparser_base, CaptureClusterArgs
from helpers.common import check_clickhouse_version, experimental_analyzer

from engines.requirements import *
from helpers.cas_storage import add_cas_arguments
from engines.cas_mode import (
    enable_cas_default_storage,
    reset_cas_config,
)


def argparser(parser):
    argparser_base(parser)
    add_cas_arguments(
        parser,
        cas_help="use content-addressed storage as the default MergeTree disk",
    )


xfails = {
    "/engines/summing_merge_tree/zero row deletion with clear column": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/101953 - fixed in >=26.6",
            check_clickhouse_version("<26.6"),
        )
    ],
    "/engines/summing_merge_tree/clear column validation consistency": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/101953 - fixed in >=26.6",
            check_clickhouse_version("<26.6"),
        )
    ],
}
xflags = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@Name("engines")
@Specifications()
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
    use_cas=False,
    use_cas_s3_cache=False,
):
    """ClickHouse different ENGINES regression suite."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version
    self.context.use_cas_storage = False
    self.context.default_storage_policy = None

    if stress is not None:
        self.context.stress = stress

    if use_cas_s3_cache or use_cas:
        with Given(
            "content-addressed storage with an S3 cache disk as the default MergeTree disk"
            if use_cas_s3_cache
            else "content-addressed storage as the default MergeTree disk"
        ):
            enable_cas_default_storage(s3_cache=use_cas_s3_cache)
    else:
        with Given("no content-addressed storage configuration"):
            reset_cas_config()

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    Feature(
        run=load("engines.tests.replacing_merge_tree.replacing_merge_tree", "feature")
    )
    Feature(
        run=load(
            "engines.tests.replacing_merge_tree.replicated_replacing_merge_tree",
            "feature",
        )
    )
    Feature(
        run=load(
            "engines.tests.summing_merge_tree.summing_merge_tree",
            "feature",
        )
    )


if main():
    regression()
