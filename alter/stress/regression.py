#!/usr/bin/env python3
import sys
from testflows.core import *

append_path(sys.path, "../..")

from helpers.cluster import create_cluster
from helpers.common import experimental_analyzer
from helpers.argparser import (
    argparser_s3 as argparser_base,
    CaptureClusterArgs,
    CaptureS3Args,
)
from helpers.cas_storage import add_cas_arguments, apply_cas_context
from s3.tests.common import start_minio

# aws_s3 / gcs are not ALTER substrates; use the s3/ suite for those providers.
SUPPORTED_STORAGES = ("minio", "local")

xfails = {}

ffails = {}


def argparser(parser):
    """Add --unsafe and CAS flags to the parser."""
    argparser_base(parser)

    parser.add_argument(
        "--unsafe",
        action="store_true",
        help="Disable workarounds for known issues.",
    )

    add_cas_arguments(
        parser,
        cas_help="use a single CAS object-storage disk for the external and "
        "tiered policies (MinIO/RustFS only; requires Antalya >= 26.6)",
        s3_cache_help="like --cas, but layer a type=cache disk in front of the "
        "CAS disk (external and tiered policy names are unchanged)",
    )


@TestModule
@Name("local")
def local_storage(
    self,
    cluster_args,
    with_analyzer,
):
    """Setup and run local-disk tests."""
    nodes = {
        "zookeeper": ("zookeeper1", "zookeeper2", "zookeeper3"),
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
    }

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            use_zookeeper_nodes=True,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.node = self.context.cluster.node("clickhouse1")
        self.context.ch_nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]
        self.context.zk_nodes = [cluster.node(n) for n in cluster.nodes["zookeeper"]]
        self.context.minio_enabled = False

    with And("I enable or disable experimental analyzer if needed"):
        experimental_analyzer(
            node=cluster.node("clickhouse1"), with_analyzer=with_analyzer
        )

    Feature(run=load("alter.stress.tests.simplified", "feature"))
    Feature(run=load("alter.stress.tests.stress_insert", "feature"))
    Feature(run=load("alter.stress.tests.stress_alter", "feature"))


@TestModule
def minio(
    self,
    uri,
    root_user,
    root_password,
    cluster_args,
    with_analyzer=False,
):
    """Setup and run minio tests."""
    nodes = {
        "zookeeper": ("zookeeper1", "zookeeper2", "zookeeper3"),
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
    }

    root_user = root_user.value
    root_password = root_password.value
    uri = uri.value

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            use_zookeeper_nodes=True,
            configs_dir=current_dir(),
            environ={
                "MINIO_ROOT_PASSWORD": root_password,
                "MINIO_ROOT_USER": root_user,
            },
        )
        self.context.cluster = cluster
        self.context.node = self.context.cluster.node("clickhouse1")
        self.context.ch_nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]
        self.context.zk_nodes = [cluster.node(n) for n in cluster.nodes["zookeeper"]]
        self.context.access_key_id = root_user
        self.context.secret_access_key = root_password
        self.context.bucket_name = "root"
        self.context.bucket_path = "data/object-storage"

        self.context.minio_enabled = True

    with And("I enable or disable experimental analyzer if needed"):
        experimental_analyzer(
            node=cluster.node("clickhouse1"), with_analyzer=with_analyzer
        )

    with And("I have a minio client"):
        start_minio(access_key=root_user, secret_key=root_password)
        uri_bucket_file = uri + f"/{self.context.cluster.minio_bucket}" + "/data/"
        self.context.uri = uri_bucket_file

    Feature(run=load("alter.stress.tests.simplified", "feature"))
    Feature(run=load("alter.stress.tests.stress_alter", "feature"))


@TestModule
@Name("stress")
@ArgumentParser(argparser)
@XFails(xfails)
@FFails(ffails)
@CaptureClusterArgs
@CaptureS3Args
def regression(
    self,
    cluster_args: dict,
    s3_args: dict,
    clickhouse_version: str,
    stress: bool,
    with_analyzer=False,
    unsafe=False,
    use_cas=False,
    use_cas_s3_cache=False,
):
    """Stress testing regression."""

    self.context.clickhouse_version = clickhouse_version

    self.context.stress = stress
    self.context.unsafe = unsafe
    self.context.use_cas_storage = False
    self.context.use_cas_s3_cache = False

    storages = s3_args.pop("storages", None)
    if storages is None:
        storages = ["minio"]

    unsupported = [s for s in storages if s not in SUPPORTED_STORAGES]
    if unsupported:
        fail(
            "alter/stress only runs --storage minio and local; "
            f"got {unsupported}. Use the s3/ suite for aws_s3 and gcs."
        )

    # --cas-s3-cache implies CAS and wins if both flags are passed.
    if use_cas_s3_cache or use_cas:
        if storages != ["minio"]:
            fail("--cas / --cas-s3-cache requires --storage minio")
        apply_cas_context(self, s3_cache=bool(use_cas_s3_cache))

    module_args = dict(
        cluster_args=cluster_args,
        with_analyzer=with_analyzer,
    )

    for storage in storages:
        if storage == "minio":
            Module(test=minio)(
                uri=s3_args["minio_uri"],
                root_user=s3_args["minio_root_user"],
                root_password=s3_args["minio_root_password"],
                **module_args,
            )
        elif storage == "local":
            Module(test=local_storage)(
                **module_args,
            )


if main():
    regression()
