from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle import insert_rids, row_for_rid
from cas.soak_tests.oracle.workload import (
    delete_sql,
    insert_values_sql,
    select_range_sql,
    select_recent_sql,
    truncate_sql,
    update_sql,
)


@TestScenario
@Name("insert sql carries model row_fp")
def insert_sql_carries_model_row_fp(self):
    rids = insert_rids(op_id=0, n=3)
    sql = insert_values_sql(seed=1, op_id=0, n=3, table="ca_stress")
    with Then("each row_fp is in the INSERT and ts uses toDateTime64"):
        for rid in rids:
            assert str(row_for_rid(1, rid)["row_fp"]) in sql, error()
        assert sql.startswith("INSERT INTO ca_stress"), error()
        assert "toDateTime64(" in sql, error()
        assert "VALUES" in sql, error()


@TestScenario
@Name("settings precede values")
def settings_precede_values(self):
    sql = insert_values_sql(
        seed=1, op_id=0, n=1, table="t", settings="SETTINGS async_insert=0"
    )
    with Then("SETTINGS is before VALUES"):
        assert sql.index("SETTINGS") < sql.index("VALUES"), error()


@TestScenario
@Name("update sql bumps v and version by bucket")
def update_sql_bumps_v_and_version_by_bucket(self):
    sql = update_sql(table="ca_stress", bucket=7)
    assert "UPDATE v = v + 1, version = version + 1" in sql, error()
    assert "WHERE bucket = 7" in sql, error()


@TestScenario
@Name("delete sql")
def delete_sql_by_bucket(self):
    assert "DELETE WHERE bucket = 3" in delete_sql(table="ca_stress", bucket=3), error()


@TestScenario
@Name("truncate sql")
def truncate_sql_is_exact(self):
    assert truncate_sql(table="ca_stress") == "TRUNCATE TABLE ca_stress", error()


@TestScenario
@Name("select range sql filters and touches payload")
def select_range_sql_filters_bucket_and_k_range_and_touches_payload(self):
    sql = select_range_sql(table="ca_stress", bucket=5, k_lo=1000, k_hi=5000)
    assert "WHERE bucket = 5 AND k BETWEEN 1000 AND 5000" in sql, error()
    assert "payload" in sql, error()
    assert sql.startswith("SELECT"), error()
    assert "SELECT *" not in sql, error()


@TestScenario
@Name("select recent sql filters bucket and window")
def select_recent_sql_filters_bucket_and_recent_window(self):
    sql = select_recent_sql(table="ca_stress", bucket=9, seconds=600)
    assert "WHERE bucket = 9 AND ts >= now() - INTERVAL 600 SECOND" in sql, error()
    assert sql.startswith("SELECT"), error()


@TestFeature
@Name("workload")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
