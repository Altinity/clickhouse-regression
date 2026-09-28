"""clickhouse-sqlalchemy sub-suite feature loaded by the LTS orchestrator."""

import os

from testflows.core import *

from lts.clickhouse_sqlalchemy.requirements.requirements import (
    SRS_104_ClickHouse_SQLAlchemy_Dialect_clickhouse_sqlalchemy_LTS_Testing,
    RQ_SRS_104_ClickHouseSQLAlchemy_UpstreamTests,
    RQ_SRS_104_ClickHouseSQLAlchemy_Compatibility_LTS,
)
from lts.steps.upstream import run_upstream_tests


@TestFeature
@Name("clickhouse-sqlalchemy")
@Specifications(SRS_104_ClickHouse_SQLAlchemy_Dialect_clickhouse_sqlalchemy_LTS_Testing)
@Requirements(
    RQ_SRS_104_ClickHouseSQLAlchemy_UpstreamTests("1.0"),
    RQ_SRS_104_ClickHouseSQLAlchemy_Compatibility_LTS("1.0"),
)
def feature(self, release="0.3.2", timeout=3600):
    """Run the clickhouse-sqlalchemy test suite at tag ``release`` against the
    ClickHouse image and report each upstream test."""
    run_upstream_tests(
        suite="clickhouse_sqlalchemy",
        configs_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs"),
        build_args={"CLICKHOUSE_IMAGE": self.context.clickhouse_image},
        env={"RELEASE": release},
        timeout=timeout,
        # 0.3.2 on 26.3: 406 tests, none skipped.
        min_tests=390,
        max_skipped=5,
        # pytest exits with 1 when some tests failed; 2-5 mean it did not run properly
        ok_exit_codes=(0, 1),
    )
