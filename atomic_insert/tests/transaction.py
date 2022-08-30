from atomic_insert.requirements import *
from atomic_insert.tests.steps import *


@TestScenario
def parallel_insert_with_fail_transaction(
    self,
    table_engine,
    failure_mode,
):
    """Test transaction parallel INSERT with block fail."""
    node = self.context.cluster.node("clickhouse1")
    uid = getuid()

    database = f"test_database{uid}"

    tables = [
        f"test_database{uid}.table_A{uid}",
        f"test_database{uid}.table_B{uid}",
        f"test_database{uid}.table_B_mv{uid}",
    ]

    with Given("I create database and core table in this database"):
        create_table(
            table_engine=table_engine,
            node=node,
            database=database,
            core_table=tables[0],
        )

    with And("I add materialized view"):
        materialized_view(
            table_engine=table_engine,
            node=node,
            core_table=tables[0],
            mv_1=tables[2],
            mv_1_table=tables[1],
            failure_mode=failure_mode,
        )

    with And("I make 2 parallel transaction inserts: with block fail and not"):
        When(
            "I make fail block transaction insert insert",
            test=simple_transaction_insert_throwif,
            parallel=True,
        )(core_table=tables[0])
        When(
            "I make transaction insert", test=simple_transaction_insert, parallel=True
        )(core_table=tables[0])

    with And("I check that data was inserted only from second query"):
        for table_name in tables:
            with When(f"table {table_name}"):
                node.query(
                    f"SELECT count()+737 FROM {table_name}",
                    message="747",
                    exitcode=0,
                )


@TestFeature
@Name("simple_transaction")
def feature(self):
    """Check transactions."""
    if self.context.stress:
        self.context.engines = [
            "MergeTree",
        ]
    else:
        self.context.engines = ["MergeTree"]

    failure_mode = ["dummy"]

    falure_mode_1 = ["dummy", "throwIf"]

    for table_engine in self.context.engines:
        for fail in failure_mode:
            with Feature(f"{table_engine}"):
                for scenario in loads(current_module(), Scenario):
                    scenario(table_engine=table_engine, failure_mode=fail)
