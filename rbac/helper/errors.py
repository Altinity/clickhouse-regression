from helpers.common import check_clickhouse_version, current

## Syntax

# Errors: not found

not_found = "Exception: There is no {type} `{name}`"


def user_not_found_in_disk(name):
    return (192, not_found.format(type="user", name=name))


def role_not_found_in_disk(name):
    return (255, not_found.format(type="role", name=name))


def settings_profile_not_found_in_disk(name):
    return (180, not_found.format(type="settings profile", name=name))


def quota_not_found_in_disk(name):
    return (199, not_found.format(type="quota", name=name))


def row_policy_not_found_in_disk(name):
    return (11, not_found.format(type="row policy", name=name))


def table_does_not_exist(name):
    return (60, "Exception: Table {name} doesn't exist".format(name=name))


# Errors: cannot_rename

cannot_rename = "Exception: {type} `{name}`: cannot rename to `{name_new}` because {type} `{name_new}` already exists"
cannot_rename_exitcode = 237


def cannot_rename_user(name, name_new):
    return (
        cannot_rename_exitcode,
        cannot_rename.format(type="user", name=name, name_new=name_new),
    )


def cannot_rename_role(name, name_new):
    return (
        cannot_rename_exitcode,
        cannot_rename.format(type="role", name=name, name_new=name_new),
    )


def cannot_rename_settings_profile(name, name_new):
    return (
        cannot_rename_exitcode,
        cannot_rename.format(type="settings profile", name=name, name_new=name_new),
    )


def cannot_rename_quota(name, name_new):
    return (
        cannot_rename_exitcode,
        cannot_rename.format(type="quota", name=name, name_new=name_new),
    )


def cannot_rename_row_policy(name, name_new):
    return (
        cannot_rename_exitcode,
        cannot_rename.format(type="row policy", name=name, name_new=name_new),
    )


# Errors: cannot insert

cannot_insert = (
    "Exception: {type} `{name}`: cannot insert because {type} `{name}` already exists"
)
cannot_insert_exitcode = 237


def cannot_insert_user(name):
    return (cannot_insert_exitcode, cannot_insert.format(type="user", name=name))


def cannot_insert_role(name):
    return (cannot_insert_exitcode, cannot_insert.format(type="role", name=name))


def cannot_insert_settings_profile(name):
    return (
        cannot_insert_exitcode,
        cannot_insert.format(type="settings profile", name=name),
    )


def cannot_insert_quota(name):
    return (cannot_insert_exitcode, cannot_insert.format(type="quota", name=name))


def cannot_insert_row_policy(name):
    return (cannot_insert_exitcode, cannot_insert.format(type="row policy", name=name))


# Error: default is readonly

cannot_remove_default = "Exception: Cannot remove {type} `default` from users.xml because this storage is readonly"
cannot_remove_default_exitcode = 239


def cannot_update_default(self):
    if check_clickhouse_version(">=26.2")(self):
        # PR #88139 changed storage initialization order, causing SET_NON_GRANTED_ROLE (512)
        # PR #96841 fixed exit codes to return 255 for server errors
        return (
            255,
            "Exception: Role should be granted to set default",
        )
    elif check_clickhouse_version(">=25.11")(self):
        # PR #88139 changed storage initialization order, causing SET_NON_GRANTED_ROLE (512)
        # to be raised before ACCESS_STORAGE_READONLY (495) when access_control_path is set
        return (
            0,  # 512 % 256 = 0 (broken exit code before PR #96841)
            "Exception: Role should be granted to set default",
        )
    elif check_clickhouse_version("<23.8")(self):
        message = "Exception: Cannot update user `default` in users.xml because this storage is readonly"
    else:
        message = "Exception: Cannot update user `default` in users_xml because this storage is readonly"

    return (
        cannot_remove_default_exitcode,
        message,
    )


def cannot_remove_user_default(self):
    message = cannot_remove_default.format(type="user")
    if check_clickhouse_version(">=23.8")(self):
        message = message.replace(".", "_")

    return (cannot_remove_default_exitcode, message)


def cannot_remove_settings_profile_default(self):
    message = cannot_remove_default.format(type="settings profile")
    if check_clickhouse_version(">=23.8")(self):
        message = message.replace(".", "_")

    return (cannot_remove_default_exitcode, message)


def cannot_remove_quota_default(self):
    message = cannot_remove_default.format(type="quota")
    if check_clickhouse_version(">=23.8")(self):
        message = message.replace(".", "_")

    return (cannot_remove_default_exitcode, message)


# Other syntax errors


def unknown_setting(self, setting):
    if check_clickhouse_version(">=24.3")(self):
        return (115, f"Exception: Unknown setting '{setting}'.")
    return (115, f"Exception: Unknown setting {setting}.")


def cluster_not_found(self, cluster):
    if check_clickhouse_version("<23.8")(self):
        return (170, f"Exception: Requested cluster '{cluster}' not found.")
    else:
        return (189, f"Exception: Requested cluster '{cluster}' not found.")


## Privileges


def not_enough_privileges(name):
    return (241, f"Exception: {name}: Not enough privileges.")


def cannot_parse_string_as_float(string):
    return (6, f"Exception: Cannot parse string '{string}' as Float64")


def missing_columns(name):
    return (47, f"Exception: Missing columns: '{name}' while processing")


def missing_columns_analyzer(name):
    if check_clickhouse_version("<24.9")(current()):
        return (47, f"Exception: Unknown expression identifier '{name}' in scope")
    else:
        return (47, f"Exception: Unknown expression identifier `{name}` in scope")


# Errors: wrong name

wrong_name = "Exception: Wrong {type} name. Cannot find {type} `{name}` to drop"


def wrong_column_name(name):
    return (10, wrong_name.format(type="column", name=name))


def wrong_index_name(name):
    return (36, wrong_name.format(type="index", name=name))


def wrong_constraint_name(name):
    return (36, wrong_name.format(type="constraint", name=name))


# Errors: cannot add

cannot_add = "Exception: Cannot add index {name}: index with this name already exists"
cannot_add_exitcode = 44


def cannot_add_index(name):
    return (cannot_add_exitcode, cannot_add.format(name=name))


def cannot_add_constraint(name):
    return (cannot_add_exitcode, cannot_add.format(name=name))


# Errors: special


def aggregate_function_throw(name=None):
    return (
        247,
        f"DB::Exception: Aggregate function aggThrow has thrown exception successfully",
    )


def invoker_not_allowed():
    return (
        141,
        "DB::Exception: SQL SECURITY INVOKER can't be specified for MATERIALIZED VIEW.",
    )
