from selects.tests.steps import *


@TestStep(When)
@Name("SELECT ... WHERE")
def select_where_query(
    self,
    name,
    final_manual=False,
    final_force=1,
    final_modifier_available=True,
    check_results=False,
    final_manual_check=True,
    final_force_check=0,
    negative=0,
    node=None,
):
    """Select with `WHERE` query step."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT ... {'FINAL' if final_manual else ''} WHERE ... ` "
        f"{'with enabled force select final modifier' if final_force == 1 else ''} from table {name}"
    ):
        result1 = node.query(
            f"SELECT * FROM {name} {'FINAL' if final_manual and final_modifier_available else ''}"
            f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", final_force)],
        ).output.strip()

        if check_results:
            with Then(
                f"I compare previous query result with check query result "
                f"`SELECT ... {'FINAL' if final_manual_check else ''} WHERE ...` "
                f"{'with enabled force select final modifier' if final_force_check == 1 else ''} from table {name}"
            ):
                result2 = node.query(
                    f"SELECT * FROM {name} {'FINAL' if final_manual_check and final_modifier_available else ''}"
                    f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                    settings=[("final", final_force_check)],
                ).output.strip()

                if negative:
                    with Then("I check that compare results are different"):
                        if (
                            final_modifier_available
                            and node.query(
                                f"SELECT * FROM {name}"
                                f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
                            ).output.strip()
                            != node.query(
                                f"SELECT * FROM {name} FINAL"
                                f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
                            ).output.strip()
                        ):
                            assert result1 != result2
                        else:
                            exception("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2
