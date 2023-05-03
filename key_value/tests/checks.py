from key_value.tests.steps import *
from testflows.core import *
from key_value.tests.constant import *


@TestCheck
def noise_before(self, scenario):
    """Check noise characters before key value pair are ignored for {scenario.name}."""

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
    """Check noise characters after key value pair are ignored for {scenario.name}."""

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
    """Check noise characters between key value pairs are ignored for {scenario.name}."""

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

    Check(test=noise_before, format_description=True)(scenario=scenario)
    Check(test=noise_after, format_description=True)(scenario=scenario)
    Check(test=noise_between, format_description=True)(scenario=scenario)


@TestCheck
def properly_defined_key(self, scenario):
    """Check that the key is recognized if it is defined properly for {scenario.name}."""

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


@TestCheck
def key_first_symbol(self, scenario):
    """Check that the key can starts with escaped symbol for {scenario.name}."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string with key, that starts with number",
            f"'\\\\nn:\\\\nn'",
        )
        output = define("expected output", "{" + f"'\\\\nn':'\\\\nn'" + "}")
        params = define("function parameters", f"':', ' ,', '\\\"'")

    scenario(input=input, output=output, params=params)


@TestCheck
def key_symbols(self, scenario):
    """Check that the key is recognized only if it symbols not defined in parameters for {scenario.name}."""

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
    """Check that the key is not recognized if it is an empty string for {scenario.name}."""

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

    Check(test=properly_defined_key, format_description=True)(scenario=scenario)
    Check(test=key_first_symbol, format_description=True)(scenario=scenario)
    Check(test=key_symbols, format_description=True)(scenario=scenario)
    Check(test=key_empty_string, format_description=True)(scenario=scenario)


@TestCheck
def properly_defined_value(self, scenario):
    """Check that the value is recognized if it is defined properly for {scenario.name}."""

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
    """Check that the value is recognized only if it contains symbols not defined in parameters  for {scenario.name}."""

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
    """Check that the value is recognized if it is an empty string for {scenario.name}."""

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

    Check(test=properly_defined_value, format_description=True)(scenario=scenario)
    Check(test=value_symbols, format_description=True)(scenario=scenario)
    Check(test=value_empty_string, format_description=True)(scenario=scenario)


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_ExtractKeyValuePairsWithEscaping(
        "1.0"
    )
)
def extract_key_value_with_escaping(self, scenario):
    """Check that ClickHouse's extractKeyValuePairs function support extractKeyValuePairsWithEscaping function  for {scenario.name}."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string, that contains non-alphabet non-numeric symbols",
            f"'{ascii_alpha}:{ascii_alpha}{noise}\\x0A'",
        )
        output = define(
            "expected output",
            "{" + f"'{ascii_alpha}':'{ascii_alpha}{out_noise}\\n'" + "}",
        )
        params = define("function parameters", "':', ' ,', '\\\"'")

    scenario(
        input=input,
        output=output,
        params=params,
        function="extractKeyValuePairsWithEscaping",
    )


@TestCheck
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_QuotingCharacter("1.0")
)
def specifying_quoting_character_non_alpha(self, scenario):
    """Check that ClickHouse's extractKeyValuePairs function support specifying quoting character
    using a non-alphabet symbol for {scenario.name}."""

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
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_QuotingCharacter("1.0")
)
def specifying_quoting_character_alpha(self, scenario):
    """Check that ClickHouse's extractKeyValuePairs function support specifying quoting character
    using an alphabet symbol for {scenario.name}."""

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
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_PairDelimiters("1.0")
)
def specifying_pair_delimiter_non_alpha(self, scenario):
    """Check that ClickHouse's extractKeyValuePairs function support specifying pair delimiter
    using a non-alphabet symbol for {scenario.name}."""

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
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_PairDelimiters("1.0")
)
def specifying_pair_delimiter_alpha(self, scenario):
    """Check that ClickHouse's extractKeyValuePairs function support specifying pair delimiter
    using an alphabet symbol for {scenario.name}."""

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
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_KeyValuePairDelimiter("1.0")
)
def specifying_key_value_pair_delimiter_non_alpha(self, scenario):
    """Check that ClickHouse's extractKeyValuePairs function support specifying key value pair delimiter
    using a non-alphabet symbol for {scenario.name}."""

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
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_KeyValuePairDelimiter("1.0")
)
def specifying_key_value_pair_delimiter_alpha(self, scenario):
    """Check that ClickHouse's extractKeyValuePairs function support specifying key value pair delimiter
    using an alphabet symbol for {scenario.name}."""

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


@TestFeature
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters("1.0"))
@Name("specifying special symbols")
def custom_special_symbols_checks(self, scenario):
    """Check that ClickHouse's extractKeyValuePairs function support specifying following parameters:
    ``key_value_pair_delimiter`, `pair_delimiters`, `quoting_character`."""

    Check(test=extract_key_value_with_escaping, format_description=True)(
        scenario=scenario
    )
    Check(test=specifying_quoting_character_non_alpha, format_description=True)(
        scenario=scenario
    )
    Check(test=specifying_quoting_character_alpha, format_description=True)(
        scenario=scenario
    )
    Check(test=specifying_pair_delimiter_non_alpha, format_description=True)(
        scenario=scenario
    )
    Check(test=specifying_pair_delimiter_alpha, format_description=True)(
        scenario=scenario
    )
    Check(test=specifying_key_value_pair_delimiter_non_alpha, format_description=True)(
        scenario=scenario
    )
    Check(test=specifying_key_value_pair_delimiter_alpha, format_description=True)(
        scenario=scenario
    )


@TestCheck
@Name("quoting character default value")
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_QuotingCharacter("1.0")
)
def quoting_character_default_value(self, scenario):
    """Check that default value for quoting_character is `"` for {scenario.name}."""

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
    """Check that default value for pair_delimiter is `:` for {scenario.name}."""

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
    """Check that default value for key_value_pair_delimiter is ` ,;` for {scenario.name}."""

    with Given("I specify input, expected output and parameters"):
        input = define(
            "input string that contains ` ,;`",
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


@TestFeature
@Name("default parameters values")
def default_parameters_values_checks(self, scenario):
    """Check that ClickHouse's extractKeyValuePairs default values for special symbols are
    `:` - for key_value_pair_delimiter, ` ,;` for pair_delimiter,
    `"` for quoting_character."""

    Check(test=quoting_character_default_value, format_description=True)(
        scenario=scenario
    )
    Check(test=pair_delimiter_default_value, format_description=True)(scenario=scenario)
    Check(test=key_value_pair_delimiter_default_value, format_description=True)(
        scenario=scenario
    )


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Input("1.0"))
def input_format(self, scenario):
    """Check that ClickHouse's extractKeyValuePairs function can accept any string as input for {scenario.name}."""

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
    """Check that ClickHouse's extractKeyValuePairs function can accept any string as input."""

    Check(test=input_format, format_description=True)(scenario=scenario)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_IdenticalKeys("1.0"))
def same_key_with_different_values(self, scenario):
    """Check that ClickHouse's extractKeyValuePairs function returns every key value pair even
    if the keys for different pairs are the same for {scenario.name}."""

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

    Check(test=same_key_with_different_values, format_description=True)(
        scenario=scenario
    )


checks = [
    noise_checks,
    key_format_checks,
    value_format_checks,
    default_parameters_values_checks,
    input_format_checks,
    custom_special_symbols_checks,
    key_value_pairs_order,
]
