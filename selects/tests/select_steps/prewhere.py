from selects.tests.steps import *


@TestOutline(When)
@Name("SELECT ... PREWHERE")
def prewhere_query(
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
    """Select with `PREWHERE` query step."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT ... {'FINAL' if final_manual else ''} PREWHERE ... ` "
        f"{'with enabled force select final modifier' if final_force == 1 else ''} from table {name}"
    ):
        result1 = node.query(
            f"SELECT * FROM {name} {'FINAL' if final_manual and final_modifier_available else ''}"
            f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", final_force)],
        ).output.strip()

        if check_results:
            with Then(
                f"I compare previous query result with check query result "
                f"`SELECT ... {'FINAL' if final_manual_check else ''} PREWHERE ...` "
                f"{'with enabled force select final modifier' if final_force_check == 1 else ''} from table {name}"
            ):
                result2 = node.query(
                    f"SELECT * FROM {name} {'FINAL' if final_manual_check and final_modifier_available else ''}"
                    f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                    settings=[("final", final_force_check)],
                ).output.strip()

                if negative:
                    with Then("I check that compare results are different"):
                        if (
                            final_modifier_available
                            and node.query(
                                f"SELECT * FROM {name}"
                                f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
                            ).output.strip()
                            != node.query(
                                f"SELECT * FROM {name} FINAL"
                                f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
                            ).output.strip()
                        ):
                            assert result1 != result2
                        else:
                            xfail("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2


@TestStep
@Name("SELECT `PREWHERE`")
def prewhere(self, name,  final_modifier_available):
    prewhere_query(name=name,  final_modifier_available=final_modifier_available, final_manual=False, final_force=0)


@TestStep
@Name("SELECT `PREWHERE` FINAL")
def prewhere_final(self, name,  final_modifier_available):
    prewhere_query(name=name,  final_modifier_available=final_modifier_available, final_manual=True, final_force=0)


@TestStep
@Name("SELECT `PREWHERE` force final")
def prewhere_ffinal(self, name, final_modifier_available):
    prewhere_query(name=name,  final_modifier_available=final_modifier_available, final_manual=False, final_force=1)


@TestStep
@Name("SELECT `PREWHERE` FINAL force final")
def prewhere_final_ffinal(self, name,  final_modifier_available):
    prewhere_query(name=name,  final_modifier_available=final_modifier_available, final_manual=True, final_force=1)


@TestStep
@Name("`PREWHERE` result check")
def prewhere_result_check(self, name,  final_modifier_available):
    prewhere_query(
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
@Name("`PREWHERE` negative result check")
def prewhere_negative_result_check(self, name, final_modifier_available):
    prewhere_query(
        name=name,
        final_manual=False,
        final_force=1,
        check_results=True,
        final_modifier_available=final_modifier_available,
        final_manual_check=False,
        final_force_check=0,
        negative=True,
    )