from helpers.common import (
    check_clickhouse_version,
    check_if_altinity_build,
    check_if_not_antalya_build,
    current,
    is_with_analyzer,
)


def forgot_quotes():
    if check_clickhouse_version(">=26.9")(current()):
        return (
            47,
            "DB::Exception: Unknown expression or function identifier `aes`. In scope SELECT",
        )
    elif check_clickhouse_version(">=24.9")(current()):
        return (
            47,
            "DB::Exception: Unknown expression or function identifier `aes` in scope SELECT",
        )
    elif is_with_analyzer(node=current().context.node):
        return (
            47,
            "DB::Exception: Unknown expression or function identifier 'aes' in scope SELECT",
        )
    else:
        return (
            47,
            "DB::Exception: Missing columns: 'ecb' 'aes' while processing query",
        )


def _signature_exception(function, detail):
    """26.11 exception text, including ``DB::Exception:``.

    ``Node.query`` treats a message without ``Exception:`` as a successful
    result and fails when the server output still contains an exception.
    """
    if function.endswith("_mysql"):
        arguments = (
            "const mode StringOrFixedString, input StringOrFixedString, "
            "key StringOrFixedString, [IV StringOrFixedString]"
        )
    else:
        arguments = (
            "const mode StringOrFixedString, input StringOrFixedString, "
            "key StringOrFixedString, [IV StringOrFixedString], "
            "[AAD StringOrFixedString]"
        )
    return (
        f"DB::Exception: Arguments of function {function} do not match its signature "
        f"(({arguments}) -> String): {detail}"
    )


def argument_count_error(function, count, before_24_7, since_24_7):
    """Exception text for an encrypt or decrypt call with the wrong arity.

    ClickHouse 26.11 matches arguments against a declarative signature and
    reports ``too few arguments (N)`` or ``too many arguments (N)``.
    """
    if check_clickhouse_version(">=26.11")(current()):
        if count < 3:
            detail = f"too few arguments ({count}), must be at least 3"
        else:
            detail = f"too many arguments ({count})"
        return _signature_exception(function, detail)
    if check_clickhouse_version("<24.7")(current()):
        return before_24_7
    return since_24_7


def argument_type_error(
    function,
    ordinal,
    name,
    before_24_7,
    since_24_7,
    got_type=None,
    since_24_7_before_26_8=None,
):
    """Exception text when an encrypt or decrypt argument has the wrong type.

    ``ordinal`` is the 26.11 signature position (``1st``, ``2nd``, ...).
    ``since_24_7_before_26_8`` is the 24.7 through 26.7 text, where optional
    arguments were numbered one place earlier.
    """
    if check_clickhouse_version(">=26.11")(current()):
        detail = f"value provided as {ordinal} argument '{name}'"
        if got_type is not None:
            detail += f" has type {got_type} that is not StringOrFixedString"
        return _signature_exception(function, detail)
    if check_clickhouse_version("<24.7")(current()):
        return before_24_7
    if since_24_7_before_26_8 is not None and check_clickhouse_version("<26.8")(
        current()
    ):
        return since_24_7_before_26_8
    return since_24_7


def decrypt_final_failed():
    test = current()

    if check_clickhouse_version("<25.4")(test):
        return "DB::Exception: Failed to decrypt"

    if check_clickhouse_version(">26.6")(test) or (
        check_if_altinity_build(test)
        and check_if_not_antalya_build(test)
        and check_clickhouse_version("~26.3")(test)
    ):
        return "DB::Exception: Cannot decrypt: invalid PKCS#7 padding"

    return "DB::Exception: EVP_DecryptFinal_ex failed"
