from selects.tests.steps import *


# @TestStep(Then)
# @Name("check results")
# def check_results(
#         self,
#         name,
#         select,
#         final_manual=False,
#         final_force=1,
#         final_modifier_available=True,
#         check_results=False,
#         final_manual_check=True,
#         final_force_check=0,
#         node=None,
# ):
#     result1 = By(select.name, test=select, parallel=False)(
#         self,
#         name,
#         final_manual=final_manual,
#         final_force=final_force,
#         final_modifier_available=final_modifier_available)
#
#     with Then("I compare previous query result with check query result "):
#         By(select.name, test=select, parallel=False)(
#             self,
#             name,
#             final_manual=final_manual_check,
#             final_force=final_force_check,
#             final_modifier_available=final_modifier_available)


@TestStep(When)
@Name("SELECT count()")
def select_count_query(
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
    """Select count() query step."""

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
                            and node.query(f"SELECT count() FROM {name}").output.strip() !=
                            node.query(f"SELECT count() FROM {name} FINAL").output.strip()
                    ):
                        assert result1 != result2
                    else:
                        exception("not enough data for negative check")
            else:
                with Then("I check that compare results are the same"):
                    assert result1 == result2


@TestStep(When)
@Name("SELECT ... LIMIT")
def select_limit_query(
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
    """Select with `LIMIT` query step."""

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
                    f"LIMIT 1 FORMAT JFORMAT JSONEachRow;",
                    settings=[("final", final_force_check)],
                ).output.strip()

                if negative:
                    with Then("I check that compare results are different"):
                        if (
                                final_modifier_available
                                and node.query(f"SELECT * FROM {name}"
                                               f" LIMIT 1 FORMAT JFORMAT JSONEachRow").output.strip() !=
                                node.query(f"SELECT * FROM {name}"
                                           f" FINAL LIMIT 1 FORMAT JFORMAT JSONEachRow").output.strip()
                        ):
                            assert result1 != result2
                        else:
                            exception("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2


@TestStep(When)
@Name("SELECT ... LIMIT BY")
def select_limit_by_query(
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
                                and node.query(f"SELECT * FROM {name}"
                                               f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;").output.strip() !=
                                node.query(f"SELECT * FROM {name} FINAL"
                                           f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;").output.strip()
                        ):
                            assert result1 != result2
                        else:
                            exception("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2


@TestStep(When)
@Name("SELECT ... GROUP BY")
def select_group_by_query(
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
    """Select with `GROUP BY` query step."""

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
                    f"SELECT * FROM  {name} {'FINAL' if final_manual_check and final_modifier_available else ''}"
                    f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
                    settings=[("final", final_force_check)],
                ).output.strip()

                if negative:
                    with Then("I check that compare results are different"):
                        if (
                                final_modifier_available
                                and node.query(f"SELECT * FROM {name}"
                                               f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;").output.strip() !=
                                node.query(f"SELECT * FROM {name} FINAL"
                                           f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;").output.strip()
                        ):
                            assert result1 != result2
                        else:
                            exception("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2


@TestStep(When)
@Name("SELECT ... DISTINCT")
def select_distinct_query(
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
    """Select with `DISTINCT` query step."""

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
                                and node.query(f"SELECT DISTINCT * FROM {name}"
                                               f" ORDER BY (id, x, someCol) FORMAT JSONEachRow;").output.strip() !=
                                node.query(f"SELECT DISTINCT * FROM {name} FINAL"
                                           f" ORDER BY (id, x, someCol) FORMAT JSONEachRow;").output.strip()
                        ):
                            assert result1 != result2
                        else:
                            exception("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2


@TestStep(When)
@Name("SELECT ... PREWHERE")
def select_prewhere_query(
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
                                and node.query(f"SELECT * FROM {name}"
                                               f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;").output.strip() !=
                                node.query(f"SELECT * FROM {name} FINAL"
                                           f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;").output.strip()
                        ):
                            assert result1 != result2
                        else:
                            exception("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2


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
                                and node.query(f"SELECT * FROM {name}"
                                               f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;").output.strip() !=
                                node.query(f"SELECT * FROM {name} FINAL"
                                           f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;").output.strip()
                        ):
                            assert result1 != result2
                        else:
                            exception("not enough data for negative check")
                else:
                    with Then("I check that compare results are the same"):
                        assert result1 == result2

