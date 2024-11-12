#!/usr/bin/env python3
import os
import sys
from testflows.core import *
from testflows.core.name import clean

append_path(sys.path, "..", "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.common import check_clickhouse_version, experimental_analyzer
from ldap.authentication.requirements import *

issue_51323 = "https://github.com/ClickHouse/ClickHouse/issues/51323"

# Cross-outs of known fails
xfails = {
    "connection protocols/tls/"
    + clean("tls_require_cert='try'"): [
        (Fail, "can't be tested with self-signed certificates")
    ],
    "connection protocols/tls/"
    + clean("tls_require_cert='demand'"): [
        (Fail, "can't be tested with self-signed certificates")
    ],
    "connection protocols/starttls/"
    + clean("tls_require_cert='try'"): [
        (Fail, "can't be tested with self-signed certificates")
    ],
    "connection protocols/starttls/"
    + clean("tls_require_cert='demand'"): [
        (Fail, "can't be tested with self-signed certificates")
    ],
    "connection protocols/tls require cert default demand": [
        (Fail, "can't be tested with self-signed certificates")
    ],
    "connection protocols/starttls with custom port": [
        (
            Fail,
            "it seems that starttls is not enabled by default on custom plain-text ports in LDAP server",
        )
    ],
    "connection protocols/tls cipher suite": [(Fail, "can't get it to work")],
    # bug
    "user authentications/:/verification cooldown/verification cooldown reset when invalid password is provided": [
        (Fail, issue_51323)
    ],
    # 23.3
    "user authentications/:/verification cooldown/:": [
        (Fail, issue_51323, check_clickhouse_version(">=23"))
    ],
}

ffails = {
    "/authentication/multiple authentications methods": (
        Skip,
        "multiple authentication methods were introduced in 24.9",
        check_clickhouse_version("<24.9"),
    ),
}


@TestFeature
@Name("authentication")
@ArgumentParser(argparser)
@Specifications(SRS_007_ClickHouse_Authentication_of_Users_via_LDAP)
@Requirements(RQ_SRS_007_LDAP_Authentication("1.0"))
@XFails(xfails)
@FFails(ffails)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """ClickHouse integration with LDAP regression module."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
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

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    Scenario(run=load("ldap.authentication.tests.sanity", "scenario"))
    Scenario(run=load("ldap.authentication.tests.multiple_servers", "scenario"))
    Feature(run=load("ldap.authentication.tests.connections", "feature"))
    Feature(run=load("ldap.authentication.tests.server_config", "feature"))
    Feature(run=load("ldap.authentication.tests.user_config", "feature"))
    Feature(run=load("ldap.authentication.tests.authentications", "feature"))
    Feature(run=load("ldap.authentication.tests.with_other_auth_methods", "feature"))


if main():
    regression()
