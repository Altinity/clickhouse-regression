from selects.tests.steps.main_steps import *


@TestOutline(When)
@Name("SELECT ... LIMIT")
def limit_query(
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
    """Outline to check all `SELECT LIMIT` combinations with/without, final/force_final and compare results."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT ... {'FINAL' if final_manual else ''} LIMIT...` "
        f"{'with enabled force select final modifier' if final_force == 1 else ''} from table {name}"
    ):
        result1 = node.query(
            f"SELECT * FROM  {name} {'FINAL' if final_manual and final_modifier_available else ''}"
            f" LIMIT 1 FORMAT JSONEachRow;",
            settings=[("final", final_force)],
        ).output.strip()

        if check_results:
            with Then(
                f"I compare previous query result with check query result "
                f"`SELECT ... {'FINAL' if final_manual_check else ''} LIMIT ...` "
                f"{'with enabled force select final modifier' if final_force_check == 1 else ''} from table {name}"
            ):
                result2 = node.query(
                    f"SELECT * FROM  {name} {'FINAL' if final_manual_check and final_modifier_available else ''} "
                    f"LIMIT 1 FORMAT JSONEachRow;",
                    settings=[("final", final_force_check)],
                ).output.strip()

                if negative:
                    with Then("I check that compare results are different"):
                        if (
                            final_modifier_available
                            and node.query(
                                f"SELECT * FROM {name}" f" LIMIT 1 FORMAT JSONEachRow"
                            ).output.strip()
                            != node.query(
                                f"SELECT * FROM {name}"
                                f" FINAL LIMIT 1 FORMAT JSONEachRow"
                            ).output.strip()
                        ):
                            assert result1 != result2
                        else:
                            xfail("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2


@TestStep
@Name("SELECT `LIMIT`")
def limit(self, name, final_modifier_available):
    """Select `LIMIT` query step without `FINAL` without force final."""

    limit_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=False,
        final_force=0,
    )


@TestStep
@Name("SELECT `LIMIT` FINAL")
def limit_final(self, name, final_modifier_available):
    """Select `LIMIT` query step with `FINAL` without force final."""

    limit_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=True,
        final_force=0,
    )


@TestStep
@Name("SELECT `LIMIT` force final")
def limit_ffinal(self, name, final_modifier_available):
    """Select `LIMIT` query step without `FINAL` with force final."""

    limit_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=False,
        final_force=1,
    )


@TestStep
@Name("SELECT `LIMIT` FINAL force final")
def limit_final_ffinal(self, name, final_modifier_available):
    """Select `LIMIT` query step with `FINAL` with force final."""

    limit_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=True,
        final_force=1,
    )


@TestStep
@Name("`LIMIT` result check")
def limit_result_check(self, name, final_modifier_available):
    """Compare results between `LIMIT` query with `FINAL`,without force final and query without `FINAL`,
    with force final."""
    limit_query(
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
@Name("`LIMIT` negative result check")
def limit_negative_result_check(self, name, final_modifier_available):
    """Compare results between `LIMIT` query without `FINAL`,with force final and query without `FINAL`,
    without force final."""

    limit_query(
        name=name,
        final_manual=False,
        final_force=1,
        check_results=True,
        final_modifier_available=final_modifier_available,
        final_manual_check=False,
        final_force_check=0,
        negative=True,
    )
