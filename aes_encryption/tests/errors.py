from helpers.common import check_clickhouse_version, current, is_with_analyzer


def forgot_quotes():
    if check_clickhouse_version(">=24.9")(current()):
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
