from selects.tests.steps import *


@TestOutline(When)
@Name("SELECT ... LIMIT BY")
def limit_by_query(
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
    """Select with `LIMIT BY` query step."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT ... {'FINAL' if final_manual else ''} LIMIT BY ... ` "
        f"{'with enabled force select final modifier' if final_force == 1 else ''} from table {name}"
    ):
        result1 = node.query(
            f"SELECT * FROM  {name} {'FINAL' if final_manual and final_modifier_available else ''}"
            f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;",
            settings=[("final", final_force)],
        ).output.strip()

        if check_results:
            with Then(
                f"I compare previous query result with check query result "
                f"`SELECT ... {'FINAL' if final_manual_check else ''} LIMIT BY...` "
                f"{'with enabled force select final modifier' if final_force_check == 1 else ''} from table {name}"
            ):
                result2 = node.query(
                    f"SELECT * FROM  {name} {'FINAL' if final_manual_check and final_modifier_available else ''}"
                    f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;",
                    settings=[("final", final_force_check)],
                ).output.strip()

                if negative:
                    with Then("I check that compare results are different"):
                        if (
                            final_modifier_available
                            and node.query(
                                f"SELECT * FROM {name}"
                                f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;"
                            ).output.strip()
                            != node.query(
                                f"SELECT * FROM {name} FINAL"
                                f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;"
                            ).output.strip()
                        ):
                            assert result1 != result2
                        else:
                            xfail("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2


@TestStep
@Name("SELECT `LIMIT BY`")
def limit_by(self, name,  final_modifier_available):
    limit_by_query(name=name,  final_modifier_available=final_modifier_available, final_manual=False, final_force=0)


@TestStep
@Name("SELECT `LIMIT BY` FINAL")
def limit_by_final(self, name,  final_modifier_available):
    limit_by_query(name=name,  final_modifier_available=final_modifier_available, final_manual=True, final_force=0)


@TestStep
@Name("SELECT `LIMIT BY` force final")
def limit_by_ffinal(self, name, final_modifier_available):
    limit_by_query(name=name,  final_modifier_available=final_modifier_available, final_manual=False, final_force=1)


@TestStep
@Name("SELECT `LIMIT BY` FINAL force final")
def limit_by_final_ffinal(self, name,  final_modifier_available):
    limit_by_query(name=name,  final_modifier_available=final_modifier_available, final_manual=True, final_force=1)


@TestStep
@Name("`LIMIT BY` result check")
def limit_by_result_check(self, name,  final_modifier_available):
    limit_by_query(
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
@Name("`LIMIT BY` negative result check")
def limit_by_negative_result_check(self, name, final_modifier_available):
    limit_by_query(
        name=name,
        final_manual=False,
        final_force=1,
        check_results=True,
        final_modifier_available=final_modifier_available,
        final_manual_check=False,
        final_force_check=0,
        negative=True,
    )