from key_value.tests.steps import *


@TestCheck
def noise_before(self, scenario):
    """Check noise characters before key value pair are ignored."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains noise before key value pair",
            f"'{noise} {ascii_alpha}{ascii_num}:{ascii_num}'",
        )
        output = define(
            "expected output", "{" + f"'{ascii_alpha}{ascii_num}':'{ascii_num}'" + "}"
        )
        params = define("function parameters", f"':', ' ,', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def noise_after(self, scenario):
    """Check noise characters after key value pair are ignored."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains noise after key value pair",
            f"'{ascii_alpha}{ascii_num}:{ascii_num} {noise}'",
        )
        output = define(
            "expected output", "{" + f"'{ascii_alpha}{ascii_num}':'{ascii_num}'" + "}"
        )
        params = define("function parameters", f"':', ' ,', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def noise_between(self, scenario):
    """Check noise characters between key value pairs are ignored."""
    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains noise between key value pair",
            f"'{ascii_alpha}{ascii_num}:{ascii_num} {noise}, {noise} {ascii_alpha}:{ascii_num}'",
        )
        output = define(
            "expected output",
            "{"
            + f"'{ascii_alpha}{ascii_num}':'{ascii_num}','{ascii_alpha}':'{ascii_num}'"
            + "}",
        )
        params = define("function parameters", f"':', ' ,', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestFeature
@Name("noise")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_Noise("1.0"))
def noise_checks(self, scenario):
    """Check noise characters in input string are ignored."""

    noise_before(scenario=scenario)
    noise_after(scenario=scenario)
    noise_between(scenario=scenario)


@TestCheck
def properly_defined_key(self, scenario):
    """Check that the key is recognized if it is defined properly."""
    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains properly defined key",
            f"'\"{ascii_alpha}{ascii_num}\\n\":{ascii_num}'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha}{ascii_num}\\n':'{ascii_num}'" + "}",
        )
        params = define("function parameters", f"':', ' ,', '\\\"'")

    scenario(input=input, output=output, params=params)


# @TestCheck
# def key_first_symbol(self, scenario):
#     """Check that the key is recognized only if it starts with alphabet symbol."""
#
#     with Given("I specify input, expected output and parameters"):
#         input = define(
#             "input string with key, that starts with number",
#             f"'{ascii_num}{ascii_alpha}:{ascii_num}'",
#         )
#         output = define("expected output", "{" + f"'{ascii_alpha}':'{ascii_num}'" + "}")
#         params = define("function parameters", f"':', ' ,', '\\\"'")
#
#     scenario(input=input, output=output, params=params)


@TestCheck
def key_symbols(self, scenario):
    """Check that the key is recognized only if it contains non-control symbols."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string with key, that contains control symbols",
            f"'{ascii_alpha}{noise}{ascii_alpha}:{ascii_num}'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha}{out_noise}{ascii_alpha}':'{ascii_num}'" + "}",
        )
        params = define("function parameters", f"':', ' ,', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def key_empty_string(self, scenario):
    """Check that the key is not recognized if it is an empty string."""

    with Given("I specify input, expected output and parameters"):
        input = define("input string, that contains empty key", f"':{ascii_num}'")
        output = define("expected output", "{}")
        params = define("function parameters", f"':', ' ,', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestFeature
@Name("key format")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Key_Format("1.0"))
def key_format_checks(self, scenario):
    """Check that valid keys are recognized, and invalid are not."""

    properly_defined_key(scenario=scenario)
    # key_first_symbol(scenario=scenario)
    key_symbols(scenario=scenario)
    key_empty_string(scenario=scenario)


@TestCheck
def properly_defined_value(self, scenario):
    """Check that the value is recognized if it is defined properly."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains properly defined value",
            f'\'{ascii_alpha}{ascii_num}:"{ascii_num}{parsed_noise}",'
            + f"{ascii_alpha}:{ascii_num}'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha}{ascii_num}':'{ascii_num}{parsed_noise}',"
            f"'{ascii_alpha}':'{ascii_num}'" + "}",
        )
        params = define("function parameters", f"':', ' ,', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def value_symbols(self, scenario):
    """Check that the value is recognized only if it contains non-control symbols."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string with value that contains punctuation marks",
            f"'{ascii_alpha}:{ascii_num}{parsed_noise}{ascii_alpha}'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha}':'{ascii_num}{parsed_noise}{ascii_alpha}'" + "}",
        )
        params = define("function parameters", f"':', ' ,', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def value_empty_string(self, scenario):
    """Check that the value is recognized if it is an empty string."""

    with Given("I specify input, expected output and parameters"):
        input = define("input string with empty value", f"'{ascii_alpha}:'")
        output = define("expected output", "{" + f"'{ascii_alpha}':''" + "}")
        params = define("function parameters", f"':', ' ,', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestFeature
@Name("value format")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Value_Format("1.0"))
def value_format_checks(self, scenario):
    """Check that valid values are recognized, and invalid are not."""

    properly_defined_value(scenario=scenario)
    value_symbols(scenario=scenario)
    value_empty_string(scenario=scenario)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_EscapeSequencesSupport(
        "1.0"
    )
)
def specifying_escape_sequences_support(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying escape sequences support."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains non-alphabet non-numeric symbols",
            f"'{ascii_alpha}:{ascii_alpha}{noise}\\x0A'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha}':'{ascii_alpha}{out_noise}\\n'" + "}",
        )
        params = define("function parameters", "':', ' ,', '\\\"', 1")

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_QuotingCharacter(
        "1.0"
    )
)
def specifying_enclosing_character_non_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying enclosing character
    using a non-alphabet symbol."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains `-`",
            f"'{ascii_alpha}:-{ascii_alpha}{parsed_noise}-'",
        )
        output = define(
            "expected output",
            "{"
            + f"'{ascii_alpha}':'{ascii_alpha}{parsed_noise.replace('-', '')}'"
            + "}",
        )
        params = define(
            "function parameters with enclosing character as `-`",
            "':', ' ,', '-'",
        )

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_QuotingCharacter(
        "1.0"
    )
)
def specifying_enclosing_character_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying enclosing character
    using an alphabet symbol."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains `q`",
            f"'{ascii_alpha.replace('q', '')}:q{parsed_noise}:,q'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha.replace('q', '')}':'{parsed_noise}:,'" + "}",
        )
        params = define(
            "function parameters with enclosing character as `q`",
            "':', ' ,', 'q'",
        )

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_PairDelimiter("1.0")
)
def specifying_pair_delimiter_non_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying pair delimiter
    using a non-alphabet symbol."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains `-`",
            f"'{ascii_alpha}:{ascii_alpha}-{ascii_alpha}{ascii_num}:{ascii_alpha}'",
        )
        output = define(
            "expected output",
            "{"
            + f"'{ascii_alpha}':'{ascii_alpha}','{ascii_alpha}{ascii_num}':'{ascii_alpha}'"
            + "}",
        )
        params = define("function parameters with item delimiter as `-`", "':', '-'")

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_PairDelimiter("1.0")
)
def specifying_pair_delimiter_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying pair delimiter
    using an alphabet symbol."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains `q`",
            f"'{ascii_alpha.replace('q', '')}:"
            f"{ascii_num}q{ascii_alpha.replace('q', '')}{ascii_num}:{ascii_num}'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha.replace('q', '')}':"
            f"'{ascii_num}','{ascii_alpha.replace('q', '')}{ascii_num}':'{ascii_num}'"
            + "}",
        )
        params = define("function parameters with item delimiter as `q`", "':', 'q'")

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_KeyValuePairDelimiter(
        "1.0"
    )
)
def specifying_key_value_pair_delimiter_non_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying key value pair delimiter
    using a non-alphabet symbol."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains `-`", f"'{ascii_alpha}-{ascii_alpha}'"
        )
        output = define(
            "expected output", "{" + f"'{ascii_alpha}':'{ascii_alpha}'" + "}"
        )
        params = define(
            "function parameters with key value pair delimiter as `-`", "'-'"
        )

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_KeyValuePairDelimiter(
        "1.0"
    )
)
def specifying_key_value_pair_delimiter_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying key value pair delimiter
    using an alphabet symbol."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains `q`",
            f"'{ascii_alpha.replace('q', '')}q{ascii_num}'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha.replace('q', '')}':'{ascii_num}'" + "}",
        )
        params = define(
            "function parameters with key value pair delimiter as `q`", "'q'"
        )

    scenario(input=input, output=output, params=params)


# @TestCheck
# @Requirements(
#     RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_EscapeCharacter(
#         "1.0"
#     )
# )
# def specifying_escape_character_non_alpha(self, scenario):
#     """Check that clickhouse extractKeyValuePairs function support specifying escape character
#     using a non-alphabet symbol."""
#
#     with Given("I specify input, expected output and parameters"):
#         input = define("input string, that contains `-`", f"'{ascii_alpha},-)'")
#         output = define("expected output", "{" + f"'{ascii_alpha}':')'" + "}")
#         params = define("function parameters with escape character as `-`", "'-'")
#
#     scenario(input=input, output=output, params=params)
#
#
# @TestCheck
# @Requirements(
#     RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_EscapeCharacter(
#         "1.0"
#     )
# )
# def specifying_escape_character_alpha(self, scenario):
#     """Check that clickhouse extractKeyValuePairs function support specifying escape character
#     using an alphabet symbol."""
#
#     with Given("I specify input, expected output and parameters"):
#         input = define(
#             "input string, that contains `q`", f"'{ascii_alpha.replace('q', '')},q)'"
#         )
#         output = define(
#             "expected output", "{" + f"'{ascii_alpha.replace('q', '')}':')'" + "}"
#         )
#         params = define("function parameters with escape character as `q`", "'q'")
#
#     scenario(input=input, output=output, params=params)


@TestFeature
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying("1.0"))
@Name("specifying special symbols")
def custom_special_symbols_checks(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying following parameters:
    ``key_value_pair_delimiter`, `pair_delimiters`, `quoting_character`, `escape_sequences_support`."""

    specifying_escape_sequences_support(scenario=scenario)
    specifying_enclosing_character_non_alpha(scenario=scenario)
    specifying_enclosing_character_alpha(scenario=scenario)
    specifying_pair_delimiter_non_alpha(scenario=scenario)
    specifying_pair_delimiter_alpha(scenario=scenario)
    specifying_key_value_pair_delimiter_non_alpha(scenario=scenario)
    specifying_key_value_pair_delimiter_alpha(scenario=scenario)
    # specifying_escape_character_non_alpha(scenario=scenario)
    # specifying_escape_character_alpha(scenario=scenario)


@TestCheck
@Name("escape sequences support")
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_EscapeSequencesSupport("1.0")
)
def escape_sequences_support_default_value(self, scenario):
    """Check that default value for escape_sequences_support is OFF."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string that contains all ascii symbols",
            f"'{ascii_alpha}:{parsed_noise}{ascii_num}'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha}':'{parsed_noise}{ascii_num}'" + "}",
        )
        params = define("function parameters", "")

    scenario(input=input, output=output, params=params)


@TestCheck
@Name("quoting character default value")
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_QuotingCharacter("1.0")
)
def quoting_character_default_value(self, scenario):
    """Check that default value for quoting_character is `"`."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            'input string that contains `"`',
            f"'{ascii_alpha}:\"{parsed_noise}\"'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha}':'{parsed_noise}'" + "}",
        )
        params = define("function parameters", "")

    scenario(input=input, output=output, params=params)


@TestCheck
@Name("pair delimiter default value")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_PairDelimiters("1.0"))
def pair_delimiter_default_value(self, scenario):
    """Check that default value for pair_delimiter is `:`."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string that contains `:`", f"'{ascii_alpha}:{ascii_alpha}'"
        )
        output = define(
            "expected output", "{" + f"'{ascii_alpha}':'{ascii_alpha}'" + "}"
        )
        params = define("function parameters", "")

    scenario(input=input, output=output, params=params)


@TestCheck
@Name("key value pair delimiter default value")
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_KeyValuePairDelimiter("1.0")
)
def key_value_pair_delimiter_default_value(self, scenario):
    """Check that default value for key_value_pair_delimiter is `,;`."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string that contains `,`",
            f"'{ascii_alpha}:{ascii_alpha}, {ascii_alpha}{ascii_num}:{ascii_alpha};"
            + f"{ascii_alpha}:{ascii_alpha} {ascii_alpha}:{ascii_alpha}'",
        )
        output = define(
            "expected output",
            "{"
            + f"'{ascii_alpha}':'{ascii_alpha}','{ascii_alpha}{ascii_num}':'{ascii_alpha}',"
            f"'{ascii_alpha}':'{ascii_alpha}','{ascii_alpha}':'{ascii_alpha}'" + "}",
        )
        params = define("function parameters", "")

    scenario(input=input, output=output, params=params)


#
# @TestCheck
# @Name("escape character default value")
# @Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_EscapeCharacter("1.0"))
# def escape_character_default_value(self, scenario):
#     """Check that default value for escape_character is `\\`."""
#
#     with Given("I specify input, expected output and parameters"):
#         input = define(
#             "input string that contains `\\`", f"'{ascii_alpha}\\::{ascii_alpha}'"
#         )
#         output = define(
#             "expected output", "{" + f"'{ascii_alpha}:':'{ascii_alpha}'" + "}"
#         )
#         params = define("function parameters", "")
#
#     scenario(input=input, output=output, params=params)


@TestFeature
@Name("default parameters values")
def default_parameters_values_checks(self, scenario):
    """Check that clickhouse extractKeyValuePairs default values for special symbols are
    `:` - for key_value_pair_delimiter, `,;` for pair_delimeter
    `"` for quoting_character, OFF for escape_sequences_support."""

    escape_sequences_support_default_value(scenario=scenario)
    quoting_character_default_value(scenario=scenario)
    pair_delimiter_default_value(scenario=scenario)
    key_value_pair_delimiter_default_value(scenario=scenario)
    # escape_character_default_value(scenario=scenario)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Input("1.0"))
def input_format(self, scenario):
    """Check that extractKeyValuePairs function can accept any string as input."""

    with When("I specify input, expected output and parameters"):
        input = define(
            "input string that contains all ascii symbols",
            f"'{ascii_alpha}{ascii_num}{parsed_noise}'",
        )
        output = define("expected output", "{}")
        params = define("function parameters", f"':', ' ,', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestFeature
def input_format_checks(self, scenario):
    """Check that extractKeyValuePairs function can accept any string as input."""

    input_format(scenario=scenario)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_IdenticalKeys("1.0"))
def same_key_with_different_values(self, scenario):
    """Check that extractKeyValuePairs function returns every key value pair even
    if key for different pairs are the same."""

    with When("I specify input, expected output and parameters"):
        input = define(
            "input string key value pairs with the same key",
            f"'{ascii_alpha}:{ascii_alpha},{ascii_alpha}:{ascii_num}'",
        )
        output = define(
            "expected output",
            "{"
            + f"'{ascii_alpha}':'{ascii_alpha}',"
            + f"'{ascii_alpha}':'{ascii_num}'"
            + "}",
        )
        params = define("function parameters", f"':', ' ,', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestFeature
def key_value_pairs_order(self, scenario):
    """Check that order of key value pairs affect result properly."""

    same_key_with_different_values(scenario=scenario)


checks = [
    noise_checks,
    key_format_checks,
    value_format_checks,
    default_parameters_values_checks,
    input_format_checks,
    custom_special_symbols_checks,
    key_value_pairs_order,
]
