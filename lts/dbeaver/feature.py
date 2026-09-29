"""DBeaver sub-suite feature loaded by the LTS orchestrator."""

import os
import re
import time
import urllib.request

from testflows.core import *

from lts.dbeaver.requirements.requirements import (
    SRS_106_DBeaver_JDBC_Compatibility_Smoke_Testing,
    RQ_SRS_106_DBeaver_Driver,
    RQ_SRS_106_DBeaver_SmokeChecks,
    RQ_SRS_106_DBeaver_Compatibility_LTS,
)
from lts.steps.upstream import run_upstream_tests

PLUGIN_XML = (
    "https://raw.githubusercontent.com/dbeaver/dbeaver/{version}/"
    "plugins/org.jkiss.dbeaver.ext.clickhouse/plugin.xml"
)


@TestStep(Given)
def dbeaver_driver_versions(self, dbeaver_version):
    """Return the clickhouse-jdbc and httpclient5 versions that the DBeaver
    ClickHouse plugin declares at tag ``dbeaver_version``.

    The plugin lists them as ``maven:/<group>:<artifact>:RELEASE[<version>]``.
    """
    url = PLUGIN_XML.format(version=dbeaver_version)
    for attempt in range(1, 6):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                plugin_xml = response.read().decode()
            break
        except urllib.error.HTTPError as error:
            if error.code == 404:
                fail(f"DBeaver {dbeaver_version} has no ClickHouse plugin at {url}")
            last_error = error
        except OSError as error:
            last_error = error
        note(f"attempt {attempt} to read {url} failed: {last_error}")
        time.sleep(10)
    else:
        fail(f"could not read {url}: {last_error}")

    versions = {}
    for key, artifact in (
        ("driver", "com.clickhouse:clickhouse-jdbc"),
        ("httpclient", "org.apache.httpcomponents.client5:httpclient5"),
    ):
        match = re.search(re.escape(artifact) + r":RELEASE\[([^\]]+)\]", plugin_xml)
        if match is None:
            fail(f"{artifact} is not declared in {url}")
        versions[key] = match.group(1)

    note(
        f"DBeaver {dbeaver_version} uses clickhouse-jdbc {versions['driver']} "
        f"and httpclient5 {versions['httpclient']}"
    )
    return versions["driver"], versions["httpclient"]


@TestFeature
@Name("dbeaver")
@Specifications(SRS_106_DBeaver_JDBC_Compatibility_Smoke_Testing)
@Requirements(
    RQ_SRS_106_DBeaver_Driver("1.0"),
    RQ_SRS_106_DBeaver_SmokeChecks("1.0"),
    RQ_SRS_106_DBeaver_Compatibility_LTS("1.0"),
)
def feature(self, dbeaver_version="26.2.1", timeout=1800):
    """Replay DBeaver's connect, navigator and data editor queries through the
    JDBC driver that DBeaver ``dbeaver_version`` bundles, and report each check."""
    with Given("the JDBC driver version DBeaver bundles"):
        driver_version, httpclient_version = dbeaver_driver_versions(
            dbeaver_version=dbeaver_version
        )

    run_upstream_tests(
        suite="dbeaver",
        configs_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs"),
        build_args={"CLICKHOUSE_IMAGE": self.context.clickhouse_image},
        env={
            "DRIVER_VERSION": driver_version,
            "HTTPCLIENT_VERSION": httpclient_version,
        },
        mounts={"lts-maven-cache": "/root/.m2"},
        timeout=timeout,
        # Smoke.java always reports all 18 checks.
        min_tests=18,
        max_skipped=0,
    )
