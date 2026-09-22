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
