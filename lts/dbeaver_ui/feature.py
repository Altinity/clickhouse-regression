"""DBeaver UI sub-suite feature loaded by the LTS orchestrator."""

from testflows.core import *

from lts.steps.docker import reset_suite_results_dir
from lts.dbeaver_ui.requirements.requirements import (
    SRS_107_DBeaver_UI_Smoke_Testing,
    RQ_SRS_107_DBeaver_UI_Compatibility_LTS,
)
from lts.dbeaver_ui.steps.environment import SUITE, dbeaver_running, desktop_container


@TestFeature
@Name("dbeaver-ui")
@Specifications(SRS_107_DBeaver_UI_Smoke_Testing)
@Requirements(RQ_SRS_107_DBeaver_UI_Compatibility_LTS("1.0"))
def feature(self, dbeaver_version="26.2.1"):
    """Run DBeaver ``dbeaver_version`` against the ClickHouse image and drive
    its user interface: connect, create a dataset, query it."""
    reset_suite_results_dir(SUITE)
    self.context.dbeaver_version = dbeaver_version
    note(f"ClickHouse image: {self.context.clickhouse_image}")
    note(f"DBeaver version: {dbeaver_version}")

    with Given("ClickHouse and a virtual display are running"):
        desktop_container(
            clickhouse_image=self.context.clickhouse_image,
            dbeaver_version=dbeaver_version,
        )

    with And("DBeaver is started"):
        dbeaver_running()

    Feature(run=load("lts.dbeaver_ui.tests.session", "feature"))
