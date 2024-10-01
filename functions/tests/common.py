from testflows.core import *
from testflows.asserts import values, error, snapshot

import json

math_functions_list = [
    "e",
    "pi",
    "exp",
    "ln",
    "log",
    "exp2",
    "intExp2",
    "log2",
    "exp10",
    "intExp10",
    "log10",
    "sqrt",
    "cbrt",
    "erf",
    "erfc",
    "lgamma",
    "tgamma",
    "sin",
    "cos",
    "tan",
    "asin",
    "acos",
    "atan",
    "pow",
    "power",
    "cosh",
    "acosh",
    "sinh",
    "asinh",
    "tanh",
    "atanh",
    "atan2",
    "hypot",
    "log1p",
    "sign",
    "sigmoid",
    "degrees",
    "radians",
    "factorial",
    "width_bucket",
    "WIDTH_BUCKET",
    "proportionsZTest",
]


one_parameter_functions = [
    "exp",
    "log",
    "exp2",
    "intExp2",
    "log2",
    "exp10",
    "intExp10",
    "log10",
    "sqrt",
    "cbrt",
    "erf",
    "erfc",
    "lgamma",
    "tgamma",
    "sin",
    "cos",
    "tan",
    "asin",
    "acos",
    "atan",
    "cosh",
    "acosh",
    "sinh",
    "asinh",
    "tanh",
    "atanh",
    "log1p",
    "sign",
    "sigmoid",
    "degrees",
    "radians",
]


def execute_query(
    sql,
    expected=None,
    exitcode=None,
    message=None,
    no_checks=False,
    snapshot_name=None,
    format="JSONEachRow",
    use_file=False,
    hash_output=False,
    timeout=None,
    settings=None,
    use_result_in_snapshot_name=None,
):
    """Execute SQL query and compare the output to the snapshot."""
    if settings is None:
        settings = [("allow_suspicious_low_cardinality_types", 1)]

    if snapshot_name is None:
        snapshot_name = current().name

    if message is None and exitcode is None:
        assert (
            "snapshot_id" in current().context
        ), "test must set self.context.snapshot_id"

    with When("I execute query", description=sql):
        note(sql)
        if format and not "FORMAT" in sql:
            sql += " FORMAT " + format

        r = current().context.node.query(
            sql,
            exitcode=exitcode,
            message=message,
            no_checks=no_checks,
            use_file=use_file,
            hash_output=hash_output,
            timeout=timeout,
            settings=settings,
        )
        if no_checks:
            return r

    if use_result_in_snapshot_name:
        result = json.loads(r.output)
        result_value = list(result.values())[0]
        snapshot_name += f"_{result_value}"

    if message is None:
        if expected is not None:
            with Then("I check output against expected"):
                assert r.output.strip() == expected, error()
        else:
            with Then("I check output against snapshot"):
                with values() as that:
                    assert that(
                        snapshot(
                            "\n" + r.output.strip() + "\n",
                            id=current().context.snapshot_id,
                            name=snapshot_name,
                            encoder=str,
                            mode=snapshot.CHECK,  # snapshot.REWRITE | snapshot.CHECK | snapshot.UPDATE
                        )
                    ), error()
