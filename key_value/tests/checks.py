from key_value.tests.steps import *


@TestCheck
def noise_before(self, scenario):
    """Check noise characters before key value pair are ignored."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains noise before key value pair",
            f"'{parsed_noise} {ascii_alpha}{ascii_num}:{ascii_num}'",
        )
        output = define(
            "expected output", "{" + f"'{ascii_alpha}{ascii_num}':'{ascii_num}'" + "}"
        )
        params = define("function parameters", f"'\\\\\\\\', ':', ',', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def noise_after(self, scenario):
    """Check noise characters after key value pair are ignored."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains noise after key value pair",
            f"'{ascii_alpha}{ascii_num}:{ascii_num} {parsed_noise}'",
        )
        output = define(
            "expected output", "{" + f"'{ascii_alpha}{ascii_num}':'{ascii_num}'" + "}"
        )
        params = define("function parameters", f"'\\\\\\\\', ':', ',', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def noise_between(self, scenario):
    """Check noise characters between key value pairs are ignored."""
    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains noise between key value pair",
            f"'{ascii_alpha}{ascii_num}:{ascii_num} {parsed_noise}, {parsed_noise} {ascii_alpha}:{ascii_num}'",
        )
        output = define(
            "expected output",
            "{"
            + f"'{ascii_alpha}{ascii_num}':'{ascii_num}','{ascii_alpha}':'{ascii_num}'"
            + "}",
        )
        params = define("function parameters", f"'\\\\\\\\', ':', ',', '\\\"'")

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
            f'\'"{ascii_alpha}{ascii_num}{parsed_noise_without_quotation_mark}":'
            f"{ascii_num}, {ascii_alpha}{ascii_num}\\::{ascii_num}'",
        )
        output = define(
            "expected output",
            "{"
            + f"'{ascii_alpha}{ascii_num}{noise_without_quotation_mark}':'{ascii_num}',"
            f"'{ascii_alpha}{ascii_num}:':'{ascii_num}'" + "}",
        )
        params = define("function parameters", f"'\\\\\\\\', ':', ',', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def key_first_symbol(self, scenario):
    """Check that the key is not recognized if it starts with non-alphabet symbol."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string with key, that starts with number",
            f"'{ascii_num}{ascii_alpha}:{ascii_num}'",
        )
        output = define("expected output", "{}")
        params = define("function parameters", f"'\\\\\\\\', ':', ',', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def key_symbols(self, scenario):
    """Check that the key is recognized only if it contains alphabet symbols, underscores and numbers."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string with key, that contains punctuation marks",
            f"'{ascii_alpha}{parsed_noise}{ascii_alpha}:{ascii_num}'",
        )
        output = define("expected output", "{}")
        params = define("function parameters", f"'\\\\\\\\', ':', ',', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def key_empty_string(self, scenario):
    """Check that the key is not recognized if it is an empty string."""

    with Given("I specify input, expected output and parameters"):
        input = define("input string, that contains empty key", f"':{ascii_num}'")
        output = define("expected output", "{}")
        params = define("function parameters", f"'\\\\\\\\', ':', ',', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestFeature
@Name("key format")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Key_Format("1.0"))
def key_format_checks(self, scenario):
    """Check that valid keys are recognized, and invalid are not."""

    properly_defined_key(scenario=scenario)
    key_first_symbol(scenario=scenario)
    key_symbols(scenario=scenario)
    key_empty_string(scenario=scenario)


@TestCheck
def properly_defined_value(self, scenario):
    """Check that the value is recognized if it is defined properly."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains properly defined value",
            f'\'{ascii_alpha}{ascii_num}:"{ascii_num}{parsed_noise_without_quotation_mark}",'
            f" {ascii_alpha}:{ascii_num}\\:'",
        )
        output = define(
            "expected output",
            "{"
            + f"'{ascii_alpha}{ascii_num}':'{ascii_num}{noise_without_quotation_mark}',"
            f"'{ascii_alpha}':'{ascii_num}:'" + "}",
        )
        params = define("function parameters", f"'\\\\\\\\', ':', ',', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def value_symbols(self, scenario):
    """Check that the value is recognized only if it contains alphabet symbols, underscores and numbers."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string with value that contains punctuation marks",
            f"'{ascii_alpha}:{ascii_num}{parsed_noise}{ascii_alpha}'",
        )
        output = define("expected output", "{}")
        params = define("function parameters", f"'\\\\\\\\', ':', ',', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def value_empty_string(self, scenario):
    """Check that the value is recognized if it is an empty string."""

    with Given("I specify input, expected output and parameters"):
        input = define("input string with empty value", f"'{ascii_alpha}:'")
        output = define("expected output", "{" + f"'{ascii_alpha}':''" + "}")
        params = define("function parameters", f"'\\\\\\\\', ':', ',', '\\\"'")

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
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_ValueSpecialCharactersAllowList(
        "1.0"
    )
)
def specifying_value_special_characters_allow_list(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying value special characters allow list."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains symbols from value_special_characters_allow_list",
            f"'{ascii_alpha}:.{ascii_alpha}.]['",
        )
        output = define(
            "expected output", "{" + f"'{ascii_alpha}':'.{ascii_alpha}.]['" + "}"
        )
        params = define("function parameters", "'\\\\', ':', ',', '\\\"', '.][q'")

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_EnclosingCharacter(
        "1.0"
    )
)
def specifying_enclosing_character_non_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying enclosing character
    using a non-alphabet symbol."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains `-`",
            f"'{ascii_alpha}:-{ascii_alpha}{parsed_noise.replace('-', '')}-'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha}':'{ascii_alpha}{noise.replace('-', '')}" + "}",
        )
        params = define(
            "function parameters with enclosing character as `-`",
            "'\\\\', ':', ',', '-'",
        )

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_EnclosingCharacter(
        "1.0"
    )
)
def specifying_enclosing_character_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying enclosing character
    using an alphabet symbol."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains `q`", f"'{ascii_alpha}:q{parsed_noise}q'"
        )
        output = define(
            "expected output", "{" + f"'{ascii_alpha}':'{parsed_noise}" + "}"
        )
        params = define(
            "function parameters with enclosing character as `q`",
            "'\\\\', ':', ',', 'q'",
        )

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_ItemDelimiter("1.0")
)
def specifying_item_delimiter_non_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying item delimiter
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
        params = define(
            "function parameters with item delimiter as `-`", "'\\\\', ':', '-'"
        )

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_ItemDelimiter("1.0")
)
def specifying_item_delimiter_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying item delimiter
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
        params = define(
            "function parameters with item delimiter as `q`", "'\\\\', ':', 'q'"
        )

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
            "function parameters with key value pair delimiter as `-`", "'\\\\', '-'"
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
            "function parameters with key value pair delimiter as `q`", "'\\\\', 'q'"
        )

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_EscapeCharacter(
        "1.0"
    )
)
def specifying_escape_character_non_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying escape character
    using a non-alphabet symbol."""

    with Given("I specify input, expected output and parameters"):
        input = define("input string, that contains `-`", f"'{ascii_alpha},-)'")
        output = define("expected output", "{" + f"'{ascii_alpha}':')'" + "}")
        params = define("function parameters with escape character as `-`", "'-'")

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_EscapeCharacter(
        "1.0"
    )
)
def specifying_escape_character_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying escape character
    using an alphabet symbol."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains `q`", f"'{ascii_alpha.replace('q', '')},q)'"
        )
        output = define(
            "expected output", "{" + f"'{ascii_alpha.replace('q', '')}':')'" + "}"
        )
        params = define("function parameters with escape character as `-`", "'q'")

    scenario(input=input, output=output, params=params)


@TestFeature
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying("1.0"))
@Name("specifying special symbols")
def custom_special_symbols_checks(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying following parameters:
    `escape_character`, `key_value_pair_delimiter`, `item_delimiter`, `enclosing_character`,
     `value_special_characters_allow_list`."""

    specifying_value_special_characters_allow_list(scenario=scenario)
    specifying_enclosing_character_non_alpha(scenario=scenario)
    specifying_enclosing_character_alpha(scenario=scenario)
    specifying_item_delimiter_non_alpha(scenario=scenario)
    specifying_item_delimiter_alpha(scenario=scenario)
    specifying_key_value_pair_delimiter_non_alpha(scenario=scenario)
    specifying_key_value_pair_delimiter_alpha(scenario=scenario)
    specifying_escape_character_non_alpha(scenario=scenario)
    specifying_escape_character_alpha(scenario=scenario)


@TestCheck
@Name("special characters default values")
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_ValueSpecialCharactersAllowList(
        "1.0"
    )
)
def value_special_characters_allow_list_default_value(self, scenario):
    """Check that default value for value_special_characters_allow_list is empty string."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string that contains all ascii symbols",
            f"'{ascii_alpha}:{parsed_noise}{ascii_num}'",
        )
        output = define("expected output", "{" + f"'{ascii_alpha}':''" + "}")
        params = define("function parameters", "")

    scenario(input=input, output=output, params=params)


@TestCheck
@Name("enclosing character default value")
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_EnclosingCharacter("1.0")
)
def enclosing_character_default_value(self, scenario):
    """Check that default value for enclosing_character is `"`."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            'input string that contains `"`',
            f"'{ascii_alpha}:\"{parsed_noise_without_quotation_mark}{ascii_num}\"'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha}':'{noise_without_quotation_mark}{ascii_num}'" + "}",
        )
        params = define("function parameters", "")

    scenario(input=input, output=output, params=params)


@TestCheck
@Name("item delimiter default value")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_ItemDelimiter("1.0"))
def item_delimiter_default_value(self, scenario):
    """Check that default value for item_delimiter is `:`."""

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
    """Check that default value for key_value_pair_delimiter is `,`."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string that contains `,`",
            f"'{ascii_alpha}:{ascii_alpha}, {ascii_alpha}{ascii_num}:{ascii_alpha}'",
        )
        output = define(
            "expected output",
            "{"
            + f"'{ascii_alpha}':'{ascii_alpha}','{ascii_alpha}{ascii_num}':'{ascii_alpha}'"
            + "}",
        )
        params = define("function parameters", "")

    scenario(input=input, output=output, params=params)


@TestCheck
@Name("escape character default value")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_EscapeCharacter("1.0"))
def escape_character_default_value(self, scenario):
    """Check that default value for escape_character is `\\`."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string that contains `\\`", f"'{ascii_alpha}\\::{ascii_alpha}'"
        )
        output = define(
            "expected output", "{" + f"'{ascii_alpha}:':'{ascii_alpha}'" + "}"
        )
        params = define("function parameters", "")

    scenario(input=input, output=output, params=params)


@TestFeature
@Name("default parameters values")
def default_parameters_values_checks(self, scenario):
    """Check that clickhouse extractKeyValuePairs default values for special symbols are
    `\\` - for escape_character, `:` - for key_value_pair_delimiter, `,` for item_delimeter
    `"` for enclosing_character, empty string for value_special_characters_allow_list."""

    value_special_characters_allow_list_default_value(scenario=scenario)
    enclosing_character_default_value(scenario=scenario)
    item_delimiter_default_value(scenario=scenario)
    key_value_pair_delimiter_default_value(scenario=scenario)
    escape_character_default_value(scenario=scenario)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Input("1.0"))
def input_format(self, scenario):
    """Check that extractKeyValuePairs function can accept any string as input."""

    with When("I specify input string using string that contains all ascii symbols"):
        input = define(
            "input string that contains all ascii symbols",
            f"'{ascii_alpha}{ascii_num}{parsed_noise}'",
        )
        output = define("expected output", "{}")
        params = define("function parameters", f"'\\\\\\\\', ':', ',', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Input("1.0"))
def input_format_checks(self, scenario):
    """Check that extractKeyValuePairs function can accept any string as input."""

    input_format(scenario=scenario)


checks = [
    noise_checks,
    key_format_checks,
    value_format_checks,
    default_parameters_values_checks,
    input_format_checks,
    custom_special_symbols_checks,
]
