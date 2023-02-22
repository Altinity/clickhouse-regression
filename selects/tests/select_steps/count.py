from selects.tests.steps import *


@TestOutline(When)
def count_query(
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
    """Select count() query outline."""


    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT count() ... {'FINAL' if final_manual else ''}` "
        f"{'with enabled force select final modifier' if final_force == 1 else ''} from table {name}"
    ):
        result1 = node.query(
            f"SELECT count() FROM {name} {'FINAL' if final_manual and final_modifier_available else ''} FORMAT JSONEachRow;",
            settings=[("final", final_force)],
        ).output.strip()

        if check_results:
            with Then(
                f"I compare previous query result with check query result "
                f"`SELECT count() ... {'FINAL' if final_manual_check else ''}` "
                f"{'with enabled force select final modifier' if final_force_check == 1 else ''} from table {name}"
            ):
                result2 = node.query(
                    f"SELECT count() FROM {name} {'FINAL' if final_manual_check and final_modifier_available else ''} FORMAT JSONEachRow;",
                    settings=[("final", final_force_check)],
                ).output.strip()

            if negative:
                with Then("I check that compare results are different"):
                    if (
                        final_modifier_available
                        and node.query(f"SELECT count() FROM {name}").output.strip()
                        != node.query(
                            f"SELECT count() FROM {name} FINAL"
                        ).output.strip()
                    ):
                        assert result1 != result2
                    else:
                        xfail("not enough data for negative check")
            else:
                with Then("I check that compare results are the same"):
                    assert result1 == result2


@TestStep
@Name("SELECT count()")
def count(self, name, final_modifier_available):
    """Select count() query step without `FINAL` without force final."""

    count_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=False,
        final_force=0,
    )


@TestStep
@Name("SELECT count() FINAL")
def count_final(self, name, final_modifier_available):
    """Select count() query step with `FINAL` without force final."""

    count_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=True,
        final_force=0,
    )


@TestStep
@Name("SELECT count() force final")
def count_ffinal(self, name, final_modifier_available):
    """Select count() query step without `FINAL` with force final."""

    count_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=False,
        final_force=1,
    )


@TestStep
@Name("SELECT count() FINAL force final")
def count_final_ffinal(self, name, final_modifier_available):
    """Select count() query step with `FINAL` with force final."""

    count_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=True,
        final_force=1,
    )


@TestStep
@Name("count() result check")
def count_result_check(self, name, final_modifier_available):
    """Compare results between count() queries with `FINAL` without force final and without `FINAL`
    and with force final."""

    count_query(
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
@Name("count() negative result check")
def count_negative_result_check(self, name, final_modifier_available):
    """Compare results between count() queries without `FINAL` with force final and without `FINAL`
    and without force final."""

    count_query(
        name=name,
        final_manual=False,
        final_force=1,
        check_results=True,
        final_modifier_available=final_modifier_available,
        final_manual_check=False,
        final_force_check=0,
        negative=True,
    )
