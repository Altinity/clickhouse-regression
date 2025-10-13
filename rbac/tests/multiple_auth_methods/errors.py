from testflows.core import current
from helpers.common import check_clickhouse_version


def syntax_error():
    exitcode, message = 62, "Exception: Syntax error: failed at position"
    return exitcode, message


def no_password_cannot_coexist_with_others():
    exitcode, message = (
        36,
        "DB::Exception: Authentication method 'no_password' cannot co-exist with other authentication methods.",
    )
    return exitcode, message


def no_user(user_name):
    def return_exitcode_and_message():
        exitcode, message = (
            192,
            f"DB::Exception: There is no user `{user_name}` in user directories. (UNKNOWN_USER)",
        )

        if check_clickhouse_version(">=25.6")(current()):
            message = (
                f"DB::Exception: There is no user `{user_name}` in `user directories`"
            )

        return exitcode, message

    return return_exitcode_and_message


def user_can_not_be_created_updated():
    exitcode, message = (
        36,
        "DB::Exception: User can not be created/updated because it exceeds the allowed quantity of authentication methods per user.",
    )
    return exitcode, message


def no_user_with_such_name(user_name):
    def return_exitcode_and_message():
        exitcode, message = (
            4,
            f"DB::Exception: {user_name}: Authentication failed: password is incorrect, or there is no user with such name.",
        )
        return exitcode, message

    return return_exitcode_and_message


def wrong_password(user_name):
    def return_exitcode_and_message():
        exitcode, message = (
            4,
            f"DB::Exception: {user_name}: Authentication failed: password is incorrect, or there is no user with such name.",
        )
        return exitcode, message

    return return_exitcode_and_message


def create_user_query_is_not_allowed_to_have_add():
    exitcode, message = (
        36,
        "DB::Exception: Create user query is not allowed to have ADD IDENTIFIED, remove the ADD keyword.",
    )
    return exitcode, message


def unexpected_date(date=""):
    def return_exitcode_and_message():
        exitcode, message = (
            41,
            f"DB::Exception: Cannot read DateTime: unexpected date: {date}",
        )
        return exitcode, message

    return return_exitcode_and_message


def unexpected_symbol():
    def return_exitcode_and_message():
        exitcode, message = (41, "DB::Exception: Cannot read DateTime:")
        return exitcode, message

    return return_exitcode_and_message
