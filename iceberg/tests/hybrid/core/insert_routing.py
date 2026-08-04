from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_Insert_FirstSegmentOnly,
)

from iceberg.tests.hybrid.core.common import (
    LEFT_PREDICATE,
    RIGHT_PREDICATE,
    PREFER_LOCALHOST,
    create_mt_mt_hybrid,
    settings_clause,
    values_sql,
)


def insert_sql(table, row, extra_settings=None):
    """Build INSERT with SETTINGS before VALUES.

    SETTINGS after VALUES is parsed as insert data (async insert path).
    Client ``--setting`` flags also proved unreliable for Hybrid INSERT in
    this suite (query never reached the server). Place SETTINGS before VALUES.
    """
    settings = {
        "enable_analyzer": 1,
        "async_insert": 0,
        "distributed_foreground_insert": 1,
    }
    if extra_settings:
        settings.update(extra_settings)
    settings_sql = ", ".join(f"{k} = {v}" for k, v in settings.items())
    return (
        f"INSERT INTO {table} (id, value, date_col) "
        f"SETTINGS {settings_sql} "
        f"VALUES {values_sql((row,))}"
    )


@TestScenario
@Name("insert goes to first segment only")
def insert_first_segment_only(self):
    """INSERT INTO Hybrid lands on the left (first) segment, not the right."""
    node = self.context.node

    with Given("MT+MT Hybrid with exclusive watermark"):
        ctx = create_mt_mt_hybrid()

    new_row = (99, 999, "2025-12-01")
    select_settings = settings_clause(PREFER_LOCALHOST)

    with When("INSERT a hot-side row through Hybrid"):
        node.query(insert_sql(ctx["hybrid"], new_row), exitcode=0)

    with Then("row is present on the left segment"):
        left_count = node.query(
            f"SELECT count() FROM {ctx['left']} WHERE id = 99"
        ).output.strip()
        assert left_count == "1", error()

    with And("row is absent on the right segment"):
        right_count = node.query(
            f"SELECT count() FROM {ctx['right']} WHERE id = 99"
        ).output.strip()
        assert right_count == "0", error()

    with And("Hybrid SELECT returns the inserted row"):
        hybrid_count = node.query(
            f"SELECT count() FROM {ctx['hybrid']} WHERE id = 99 {select_settings}"
        ).output.strip()
        assert hybrid_count == "1", error()


@TestScenario
@Name("insert matching right predicate still goes left")
def insert_matching_right_predicate_still_left(self):
    """INSERT always targets first segment even if values match the right watermark."""
    node = self.context.node

    with Given("MT+MT Hybrid"):
        ctx = create_mt_mt_hybrid()

    # Cold-side date — still must land on left.
    cold_row = (98, 888, "2024-01-01")
    select_settings = settings_clause(PREFER_LOCALHOST)

    with When("INSERT a cold-dated row through Hybrid"):
        node.query(insert_sql(ctx["hybrid"], cold_row), exitcode=0)

    with Then("left segment has the row"):
        assert (
            node.query(f"SELECT count() FROM {ctx['left']} WHERE id = 98").output.strip()
            == "1"
        ), error()

    with And("right segment does not"):
        assert (
            node.query(
                f"SELECT count() FROM {ctx['right']} WHERE id = 98"
            ).output.strip()
            == "0"
        ), error()

    with And("Hybrid does not return it under exclusive watermarks"):
        # Left predicate excludes cold dates, so Hybrid should not surface it.
        assert (
            node.query(
                f"SELECT count() FROM {ctx['hybrid']} WHERE id = 98 {select_settings}"
            ).output.strip()
            == "0"
        ), error()
        assert LEFT_PREDICATE and RIGHT_PREDICATE  # watermarks in force


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_Insert_FirstSegmentOnly("1.0"),
)
@Name("insert routing")
def feature(self):
    """INSERT always forwards to the first Hybrid segment."""
    for scenario in (
        insert_first_segment_only,
        insert_matching_right_predicate_still_left,
    ):
        Scenario(run=scenario)
