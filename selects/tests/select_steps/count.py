from selects.tests.steps import *

# FIXME: remove outline 
@TestOutline(When)
def query(
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
    """Outline to check all `SELECT count()` combinations:
    
    * with FINAL clause included in the query
    * without FINAL clause included in the query
    * with --final setting enabled
    * without --final setting enabled
    """

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
    """Execute select count() query without `FINAL` clause and without force final."""
    query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=False,
        final_force=0,
    )


@TestStep
@Name("SELECT count() with FINAL")
def count_with_final_clause(self, name, final_modifier_available):
    """Execute select count() query step with `FINAL` clause but without force final."""
    query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=True,
        final_force=0,
    )


@TestStep
@Name("SELECT count() with --final")
def count_with_force_final(self, name, final_modifier_available):
    """Execute count() query step without `FINAL` clause but with force final enabled."""
    query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=False,
        final_force=1,
    )


@TestStep
@Name("SELECT count() with FINAL and --final")
def count_with_final_clause_and_force_final(self, name, final_modifier_available):
    """Select count() query step with `FINAL` clause and with force final enabled."""
    count_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=True,
        final_force=1,
    )


@TestStep
@Name("count() result check")
def count_result_check(self, name, final_modifier_available):
    """Compare results between count() query with `FINAL` and count() query with --final setting enabled."""
    query(
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
    """Compare results between count() query with --final and count() query without `FINAL` and without --final.

    The expectation is that query results should be different when collapsed rows are present but FINAL modifier is not applied
    either explicitly using FINAL clause or using --final query setting."""
    query(
        name=name,
        final_manual=False,
        final_force=1,
        check_results=True,
        final_modifier_available=final_modifier_available,
        final_manual_check=False,
        final_force_check=0,
        negative=True,
    )


@TestStep
def count_all_combinations(self, name, final_modifier_available):
    """...."""
    ...
