"""clickhouse-driver sub-suite feature loaded by the LTS orchestrator."""

import os

from testflows.core import *

from lts.clickhouse_driver.requirements.requirements import (
    SRS_103_ClickHouse_Python_Driver_clickhouse_driver_LTS_Testing,
    RQ_SRS_103_ClickHouseDriver_TestSuite,
    RQ_SRS_103_ClickHouseDriver_Compatibility_LTS,
)
from lts.steps.tool_tests import run_tool_tests


@TestFeature
@Name("clickhouse-driver")
@Specifications(SRS_103_ClickHouse_Python_Driver_clickhouse_driver_LTS_Testing)
@Requirements(
    RQ_SRS_103_ClickHouseDriver_TestSuite("1.0"),
    RQ_SRS_103_ClickHouseDriver_Compatibility_LTS("1.0"),
)
def feature(self, release="0.2.10", timeout=3600):
    """Run the clickhouse-driver test suite at tag ``release`` against the
    ClickHouse image and report each test."""
    run_tool_tests(
        suite="clickhouse_driver",
        configs_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs"),
        build_args={"CLICKHOUSE_IMAGE": self.context.clickhouse_image},
        env={"RELEASE": release},
        timeout=timeout,
        # 0.2.10 on 26.3: 486 tests, 7 skipped (4 JSON by patch, 2 no-NumPy, 1 TLS).
        # Update these when the release or its patches change the counts.
        min_tests=460,
        max_skipped=10,
        # pytest exits with 1 when some tests failed; 2-5 mean it did not run properly
        ok_exit_codes=(0, 1),
    )
