#!/usr/bin/env python3
import os
import sys
from testflows.core import *
from testflows.core.name import clean

append_path(sys.path, "..", "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from ldap.external_user_directory.requirements import *
from helpers.common import check_clickhouse_version, experimental_analyzer


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
    # 23.3
    "user authentications/:verification cooldown:/:": [
        (Fail, issue_51323, check_clickhouse_version(">=23"))
    ],
    "user authentications/verification cooldown:/:": [
        (Fail, issue_51323, check_clickhouse_version(">=23"))
    ],
}

ffails = {
    "user authentications/verification cooldown performance/:": (
        Skip,
        "causes timeout on 21.8",
        (
            lambda test: check_clickhouse_version(">=21.8")(test)
            and check_clickhouse_version("<21.9")(test)
        ),
    ),
    # 23.3
    "/external user directory/restart/parallel login": (
        XFail,
        "fails on 22.3",
        check_clickhouse_version(">=22"),
    ),
    "/external user directory/roles/not present role added": (
        XFail,
        "roles are not being applied to active clickhouse-client connections in 23.8 ",
        check_clickhouse_version(">=23.8"),
    ),
}


@TestFeature
@Name("external user directory")
@ArgumentParser(argparser)
@Specifications(SRS_009_ClickHouse_LDAP_External_User_Directory)
@Requirements(RQ_SRS_009_LDAP_ExternalUserDirectory_Authentication("1.0"))
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
    """ClickHouse LDAP external user directory regression module."""
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
    Scenario(run=load("ldap.external_user_directory.tests.simple", "scenario"))
    Feature(run=load("ldap.external_user_directory.tests.restart", "feature"))
    Feature(run=load("ldap.external_user_directory.tests.server_config", "feature"))
    Feature(
        run=load(
            "ldap.external_user_directory.tests.external_user_directory_config",
            "feature",
        )
    )
    Feature(run=load("ldap.external_user_directory.tests.connections", "feature"))
    Feature(run=load("ldap.external_user_directory.tests.authentications", "feature"))
    Feature(run=load("ldap.external_user_directory.tests.roles", "feature"))


if main():
    regression()
