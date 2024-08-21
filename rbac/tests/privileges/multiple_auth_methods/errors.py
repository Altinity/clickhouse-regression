def syntax_error():
    exitcode, message = 62, "Exception: Syntax error: failed at position"
    return exitcode, message


def no_password_cannot_coexist_with_others():
    exitcode, message = (
        36,
        "DB::Exception: Authentication method 'no_password' cannot co-exist with other authentication methods.",
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
