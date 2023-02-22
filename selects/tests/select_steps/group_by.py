from selects.tests.steps import *


@TestOutline(When)
@Name("SELECT ... GROUP BY")
def group_by_query(
    self,
    name,
    final_manual=False,
    final_force=1,
    final_modifier_available=True,
    check_results=False,
    final_manual_check=True,
    final_force_check=0,
    negative=False,
    node=None,
):
    """Outline to check all `SELECT GROUP BY` combinations with/without, final/force_final and compare results."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT ... {'FINAL' if final_manual else ''} GROUP BY ... ` "
        f"{'with enabled force select final modifier' if final_force == 1 else ''} from table {name}"
    ):
        result1 = node.query(
            f"SELECT id, count(x) as cx FROM {name} {'FINAL' if final_manual and final_modifier_available else ''}"
            f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
            settings=[("final", final_force)],
        ).output.strip()

        if check_results:
            with Then(
                f"I compare previous query result with check query result "
                f"`SELECT ... {'FINAL' if final_manual_check else ''} GROUP BY...` "
                f"{'with enabled force select final modifier' if final_force_check == 1 else ''} from table {name}"
            ):
                result2 = node.query(
                    f"SELECT id, count(x) as cx FROM  {name} {'FINAL' if final_manual_check and final_modifier_available else ''}"
                    f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
                    settings=[("final", final_force_check)],
                ).output.strip()

                if negative:
                    with Then("I check that compare results are different"):
                        if (
                            final_modifier_available
                            and node.query(
                                f"SELECT  id, count(x) as cx FROM {name}"
                                f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;"
                            ).output.strip()
                            != node.query(
                                f"SELECT  id, count(x) as cx FROM {name} FINAL"
                                f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;"
                            ).output.strip()
                        ):
                            assert result1 != result2
                        else:
                            xfail("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2


@TestStep
@Name("SELECT `GROUP BY`")
def group_by(self, name, final_modifier_available):
    """Select `GROUP BY` query step without `FINAL` without force final."""

    group_by_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=False,
        final_force=0,
    )


@TestStep
@Name("SELECT `GROUP BY` FINAL")
def group_by_final(self, name, final_modifier_available):
    """Select `GROUP BY` query step with `FINAL` without force final."""
    group_by_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=True,
        final_force=0,
    )


@TestStep
@Name("SELECT `GROUP BY` force final")
def group_by_ffinal(self, name, final_modifier_available):
    """Select `GROUP BY` query step without `FINAL` with force final."""

    group_by_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=False,
        final_force=1,
    )


@TestStep
@Name("SELECT `GROUP BY` FINAL force final")
def group_by_final_ffinal(self, name, final_modifier_available):
    """Select `GROUP BY` query step with `FINAL` with force final."""

    group_by_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=True,
        final_force=1,
    )


@TestStep
@Name("`GROUP BY` result check")
def group_by_result_check(self, name, final_modifier_available):
    """Compare results between c`GROUP BY` query with `FINAL`,without force final and query without `FINAL`,
    with force final."""

    group_by_query(
        name=name,
        final_manual=False,
        final_force=1,
        check_results=True,
        final_modifier_available=final_modifier_available,
        final_manual_check=True,
        final_force_check=0,
        negative=False,
    )


@TestStep
@Name("`GROUP BY` negative result check")
def group_by_negative_result_check(self, name, final_modifier_available):
    """Compare results between `GROUP BY` query without `FINAL`,with force final and query without `FINAL`,
    without force final."""

    group_by_query(
        name=name,
        final_manual=False,
        final_force=1,
        check_results=True,
        final_modifier_available=final_modifier_available,
        final_manual_check=False,
        final_force_check=0,
        negative=True,
    )
