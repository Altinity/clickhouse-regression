from selects.tests.steps import *


@TestOutline(When)
@Name("SELECT as")
def as_query(
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
    """Outline to check all `SELECT as` combinations with/without, final/force_final and compare results."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT as ... {'FINAL' if final_manual else ''} ...` "
        f"{'with enabled force select final modifier' if final_force == 1 else ''} from table {name}"
    ):
        result1 = node.query(
            f"SELECT id as new_id FROM {name} {'FINAL' if final_manual and final_modifier_available else ''}"
            f" ORDER BY (id) FORMAT JSONEachRow;",
            settings=[("final", final_force)],
        ).output.strip()

        if check_results:
            with Then(
                f"I compare previous query result with check query result "
                f"I make `SELECT as ... {'FINAL' if final_manual else ''} ...` "
                f"{'with enabled force select final modifier' if final_force_check == 1 else ''} from table {name}"
            ):
                result2 = node.query(
                    f"SELECT id as new_id FROM {name} {'FINAL' if final_manual_check and final_modifier_available else ''}"
                    f" ORDER BY (id) FORMAT JSONEachRow;",
                    settings=[("final", final_force_check)],
                ).output.strip()

                if negative:
                    with Then("I check that compare results are different"):
                        if (
                            final_modifier_available
                            and node.query(
                                f"SELECT id as new_id FROM {name}"
                                f" ORDER BY (id) FORMAT JSONEachRow;"
                            ).output.strip()
                            != node.query(
                                f"SELECT id as new_id FROM {name} FINAL"
                                f" ORDER BY (id) FORMAT JSONEachRow;"
                            ).output.strip()
                        ):
                            assert result1 != result2
                        else:
                            xfail("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2


@TestStep
@Name("SELECT `as`")
def as_statement(self, name, final_modifier_available):
    """Select with `as` query step without `FINAL` without force final."""
    as_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=False,
        final_force=0,
    )


@TestStep
@Name("SELECT `as` FINAL")
def as_final(self, name, final_modifier_available):
    """Select with `as` query step with `FINAL` without force final."""

    as_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=True,
        final_force=0,
    )


@TestStep
@Name("SELECT `as` force final")
def as_ffinal(self, name, final_modifier_available):
    """Select with `as` query step without `FINAL` with force final."""

    as_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=False,
        final_force=1,
    )


@TestStep
@Name("SELECT `as` FINAL force final")
def as_final_ffinal(self, name, final_modifier_available):
    """Select with `as` query step with `FINAL` with force final."""

    as_query(
        name=name,
        final_modifier_available=final_modifier_available,
        final_manual=True,
        final_force=1,
    )


@TestStep
@Name("`as` result check")
def as_result_check(self, name, final_modifier_available):
    """Compare results between `SELECT as` query with `FINAL`,without force final and query without `FINAL`,
    with force final."""

    as_query(
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
@Name("`as` negative result check")
def as_negative_result_check(self, name, final_modifier_available):
    """Compare results between `SELECT as` query without `FINAL`,with force final and query without `FINAL`,
    without force final."""

    as_query(
        name=name,
        final_manual=False,
        final_force=1,
        check_results=True,
        final_modifier_available=final_modifier_available,
        final_manual_check=False,
        final_force_check=0,
        negative=True,
    )
