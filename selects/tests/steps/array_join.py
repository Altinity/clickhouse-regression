from selects.tests.steps.main_steps import *

@TestStep
def select_array_join(self, node=None):
    """Check SELECT query with `ARRAY JOIN` clause."""
    if node is None:
        node = self.context.node

    name = f"arrays_test{getuid()}"

    with Given("I create engines list for current test"):
        engines = define(
            "engines",
            [
                "ReplacingMergeTree",
                "AggregatingMergeTree",
                "SummingMergeTree",
                "MergeTree",
                "StripeLog",
                "TinyLog",
                "Log",
            ],
            encoder=lambda s: ", ".join(s),
        )

    with And(
        "I form `create` and `populate` queries for table with array data type and all engines from engine list"
    ):
        table = define(
            "array table query",
            """CREATE TABLE {name}
            (
                s String,
                arr Array(UInt8)
            ) ENGINE = {engine}
            {order}""",
        )

        insert = define(
            "array value insert query",
            f"INSERT INTO {name} VALUES ('Hello', [1,2]), ('World', [3,4,5]), ('Goodbye', []);",
        )

    for engine in engines:
        with When(f"{engine}"):
            try:
                with When(f"I create and populate table with array type"):
                    node.query(
                        f"{table.format(name=name, engine=engine, order='') if engine.endswith('Log') else table.format(name=name, engine=engine, order='ORDER BY s;')}"
                    )
                    node.query("SYSTEM STOP MERGES")
                    node.query(insert)
                    node.query(insert)

                with When("I execute query with force_select_final=1 setting"):
                    force_select_final = node.query(
                        f"SELECT count() FROM {name} ARRAY JOIN arr",
                        settings=[("final", 1)],
                    ).output.strip()

                with And(
                    "I execute the same query with FINAL modifier specified explicitly"
                ):
                    if engine.startswith("Merge") or engine.endswith("Log"):
                        explicit_final = node.query(
                            f"SELECT count() FROM {name} ARRAY JOIN arr"
                        ).output.strip()
                    else:
                        explicit_final = node.query(
                            f"SELECT count() FROM {name} FINAL ARRAY JOIN arr"
                        ).output.strip()

                with Then("I compare results are the same"):
                    assert explicit_final == force_select_final

            finally:
                node.query(f"DROP TABLE {name}")
