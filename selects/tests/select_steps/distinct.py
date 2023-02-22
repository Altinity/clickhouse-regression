from selects.tests.steps import *


@TestOutline(When)
@Name("SELECT ... DISTINCT")
def distinct_query(
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
    """Select with `DISTINCT` query outline."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT DISTINCT ... {'FINAL' if final_manual else ''} ...` "
        f"{'with enabled force select final modifier' if final_force == 1 else ''} from table {name}"
    ):
        result1 = node.query(
            f"SELECT DISTINCT * FROM {name} {'FINAL' if final_manual and final_modifier_available else ''}"
            f" ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", final_force)],
        ).output.strip()

        if check_results:
            with Then(
                f"I compare previous query result with check query result "
                f"I make `SELECT DISTINCT ... {'FINAL' if final_manual else ''} ...` "
                f"{'with enabled force select final modifier' if final_force_check == 1 else ''} from table {name}"
            ):
                result2 = node.query(
                    f"SELECT DISTINCT * FROM {name} {'FINAL' if final_manual_check and final_modifier_available else ''}"
                    f" ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                    settings=[("final", final_force_check)],
                ).output.strip()

                if negative:
                    with Then("I check that compare results are different"):
                        if (
                            final_modifier_available
                            and node.query(
                                f"SELECT DISTINCT * FROM {name}"
                                f" ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
                            ).output.strip()
                            != node.query(
                                f"SELECT DISTINCT * FROM {name} FINAL"
                                f" ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
                            ).output.strip()
                        ):
                            assert result1 != result2
                        else:
                            xfail("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2


@TestStep
@Name("SELECT `DISTINCT`")
def distinct(self, name, final_modifier_available):
    distinct_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=False,
        final_force=0,
    )


@TestStep
@Name("SELECT `DISTINCT` FINAL")
def distinct_final(self, name, final_modifier_available):
    distinct_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=True,
        final_force=0,
    )


@TestStep
@Name("SELECT `DISTINCT` force final")
def distinct_ffinal(self, name, final_modifier_available):
    distinct_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=False,
        final_force=1,
    )


@TestStep
@Name("SELECT `DISTINCT` FINAL force final")
def distinct_final_ffinal(self, name, final_modifier_available):
    distinct_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=True,
        final_force=1,
    )


@TestStep
@Name("`DISTINCT` result check")
def distinct_result_check(self, name, final_modifier_available):
    distinct_query(
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
@Name("`DISTINCT` negative result check")
def distinct_negative_result_check(self, name, final_modifier_available):
    distinct_query(
        name=name,
        final_manual=False,
        final_force=1,
        check_results=True,
        final_modifier_available=final_modifier_available,
        final_manual_check=False,
        final_force_check=0,
        negative=True,
    )
