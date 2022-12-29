import json

from helpers.common import *
from key_value.requirements.requirements import *


askii_alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
askii_num = "0123456789"
askii_punctuation_marks = "!\"#$%&'()*+,-./:;>=<?@[\\]^_`{|}~"

noise = askii_punctuation_marks + askii_num

parsed_noise = askii_punctuation_marks.replace("\\", "\\\\").replace('"', '\\"'). \
    replace("!", "\\!").replace("`", "\\`").replace("'", "\\'")

noise_without_quotation_mark = noise.replace('"', '')

parsed_noise_without_quotation_mark = noise_without_quotation_mark.replace("\\", "\\\\").replace('"', '\\"'). \
    replace("!", "\\!").replace("`", "\\`").replace("'", "\\'")


@TestStep(Given)
def create_partitioned_table(
    self,
    table_name,
    extra_table_col="",
    cluster="",
    engine="MergeTree",
    partition="PARTITION BY x",
    order="ORDER BY x",
    settings="",
    node=None,
    options="",
    column_type="String",
):
    """Create a partitioned table."""
    if node is None:
        node = self.context.node

    try:
        with Given(f"I have a table {table_name}"):
            node.query(
                f"CREATE TABLE {table_name} {cluster} (x {column_type}{extra_table_col})"
                f" Engine = {engine} {partition} {order} {options} {settings}"
            )
        yield

    finally:
        with Finally("I remove the table", flags=TE):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestStep(When)
def insert(self, table_name, x, y, node=None, use_file=True):
    """Insert data into the table"""
    if node is None:
        node = self.context.node

    node.query(f"INSERT INTO {table_name} VALUES ({x}, '{y}')", use_file=use_file)


@TestStep(When)
def optimize_table(self, table_name, final=True, node=None):
    """Force merging of some (final=False) or all parts (final=True)
    by calling OPTIMIZE TABLE.
    """
    if node is None:
        node = self.context.node

    query = f"OPTIMIZE TABLE {table_name}"
    if final:
        query += " FINAL"

    return node.query(query)


@TestStep(Then)
def check_constant_input(self, input, output=None, params='', exitcode=0, node=None):
    """Check that clickhouse parseKeyValue function support constant input."""

    if node is None:
        node = self.context.node
    if params != '':
        params = ', '+params
    with Then("I check parseKeyValue function returns correct value"):
        if exitcode != 0:
            node.query(f"SELECT extractKeyValuePairs({input}{params})", use_file=True, exitcode=exitcode)
        else:
            r = node.query(f"SELECT extractKeyValuePairs({input}{params})", use_file=True)
            print(input)
            print(r.output)
            print(output)
            assert r.output == output, error()


@TestCheck
def noise_before(self, scenario):
    """Check noise characters before key value pair are ignored.
    """

    with When("I specify input string with noise before key value pair, "
              "output map and parameters for extractKeyValuePairs function"):
        input = f"'{parsed_noise} {askii_alpha}{askii_num}:{askii_num}'"
        output = "{" + f"'{askii_alpha}{askii_num}':'{askii_num}'"+"}"
        params = f"'\\\\\\\\', ':', ',', '\\\"'"

    scenario(input=input, output=output, params=params)


@TestCheck
def noise_after(self, scenario):
    """Check noise characters after key value pair are ignored.
    """

    with When("I specify input string with noise after key value pair, "
              "output map and parameters for extractKeyValuePairs function"):
        input = f"'{askii_alpha}{askii_num}:{askii_num} {parsed_noise}'"
        output = "{" + f"'{askii_alpha}{askii_num}':'{askii_num}'"+"}"
        params = f"'\\\\\\\\', ':', ',', '\\\"'"

    scenario(input=input, output=output, params=params)


@TestCheck
def noise_between(self, scenario):
    """Check noise characters between key value pairs are ignored.
    """
    with When("I specify input string with noise between key value pairs, "
              "output map and parameters for extractKeyValuePairs function"):
        input = f"'{askii_alpha}{askii_num}:{askii_num} {parsed_noise}, {parsed_noise} {askii_alpha}:{askii_num}'"
        output = "{" + f"'{askii_alpha}{askii_num}':'{askii_num}','{askii_alpha}':'{askii_num}'"+"}"
        params = f"'\\\\\\\\', ':', ',', '\\\"'"

    scenario(input=input, output=output, params=params)


@TestFeature
@Name("noise")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_Noise("1.0"))
def noise_feature(self, scenario):
    """Check noise characters in input string are ignored."""

    noise_before(scenario=scenario)
    noise_after(scenario=scenario)
    noise_between(scenario=scenario)


@TestCheck
def properly_defined_key(self, scenario):
    """Check that the key is recognized if it is defined properly.
    """
    with When("I specify input string with key that defined properly, "
              "output map and parameters for extractKeyValuePairs function"):
        input = f"'\"{askii_alpha}{askii_num}{parsed_noise_without_quotation_mark}\":" \
                f"{askii_num}, {askii_alpha}{askii_num}\\::{askii_num}'"
        output = "{" + f"'{askii_alpha}{askii_num}{noise_without_quotation_mark}':'{askii_num}'," \
                       f"'{askii_alpha}{askii_num}:':'{askii_num}'"+"}"
        params = f"'\\\\\\\\', ':', ',', '\\\"'"

    scenario(input=input, output=output, params=params)


@TestCheck
def key_first_symbol(self, scenario):
    """Check that the key is not recognized if it starts with non-alphabet symbol.
    """

    with When("I specify input string with key starting with alphabet symbol and key starting with number, "
              "empty output map and parameters for extractKeyValuePairs function"):
        input = f"'{askii_num}{askii_alpha}:{askii_num}'"
        output = "{}"
        params = f"'\\\\\\\\', ':', ',', '\\\"'"

    scenario(input=input, output=output, params=params)


@TestCheck
def key_symbols(self, scenario):
    """Check that the key is recognized only if it contains alphabet symbols, underscores and numbers.
    """

    with When("I specify input string with key that contains punctuation marks, "
              "empty output map and parameters for extractKeyValuePairs function"):
        input = f"'{askii_alpha}{parsed_noise}{askii_alpha}:{askii_num}'"
        output = "{}"
        params = f"'\\\\\\\\', ':', ',', '\\\"'"

    scenario(input=input, output=output, params=params)


@TestCheck
def key_empty_string(self, scenario):
    """Check that the key is not recognized if it is an empty string.
    """

    with When("I specify input string with empty key, empty output map "
              "and parameters for extractKeyValuePairs function"):
        input = f"':{askii_num}'"
        output = "{}"
        params = f"'\\\\\\\\', ':', ',', '\\\"'"

    scenario(input=input, output=output, params=params)


@TestFeature
@Name("key format")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Key_Format("1.0"))
def key_format_feature(self, scenario):
    """Check that valid keys are recognized, and invalid are not."""

    properly_defined_key(scenario=scenario)
    key_first_symbol(scenario=scenario)
    key_symbols(scenario=scenario)
    key_empty_string(scenario=scenario)


@TestCheck
def properly_defined_value(self, scenario):
    """Check that the value is recognized if it is defined properly. """

    with When("I specify input string with value that defined properly, "
              "output map and parameters for extractKeyValuePairs function"):
        input = f"'{askii_alpha}{askii_num}:\"{askii_num}{parsed_noise_without_quotation_mark}\", {askii_alpha}:{askii_num}\\:'"
        output = "{" + f"'{askii_alpha}{askii_num}':'{askii_num}{noise_without_quotation_mark}','{askii_alpha}':'{askii_num}:'"+"}"
        params = f"'\\\\\\\\', ':', ',', '\\\"'"
        print(input)
    scenario(input=input, output=output, params=params)


@TestCheck
def value_symbols(self, scenario):
    """Check that the value is recognized only if it contains alphabet symbols, underscores and numbers.
    """

    with When("I specify input string with key that contains punctuation marks, "
              "empty output map and parameters for extractKeyValuePairs function"):
        input = f"'{askii_alpha}:{askii_num}{parsed_noise}{askii_alpha}'"
        output = "{}"
        params = f"'\\\\\\\\', ':', ',', '\\\"'"

    scenario(input=input, output=output, params=params)


@TestCheck
def value_empty_string(self, scenario):
    """Check that the value is recognized if it is an empty string.
    """

    with When("I specify input string with empty value, output map "
              "and parameters for extractKeyValuePairs function"):
        input = f"'{askii_alpha}:'"
        output = "{"+f"'{askii_alpha}':''"+"}"
        params = f"'\\\\\\\\', ':', ',', '\\\"'"

    scenario(input=input, output=output, params=params)


@TestFeature
@Name("value format")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Value_Format("1.0"))
def value_format_feature(self, scenario):
    """Check that valid values are recognized, and invalid are not."""

    properly_defined_value(scenario=scenario)
    value_symbols(scenario=scenario)
    value_empty_string(scenario=scenario)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ValueSpecialCharactersAllowList("1.0"))
def specifying_value_special_characters_allow_list(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying value special characters allow list."""

    with When("I specify input string, output map and define value_special_characters_allow_list "
              "parameter for extractKeyValuePairs function"):
        input = f"'{askii_alpha}:.{askii_alpha}.]['"
        output = "{" + f"'{askii_alpha}':'.{askii_alpha}.]['" + "}"
        params = "'\\\\', ':', ',', '\\\"', '.][q'"

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EnclosingCharacter("1.0"))
def specifying_enclosing_character_non_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying enclosing character
    as non-alphabet symbol."""

    with When("I specify input string, output map and define enclosing character "
              "parameter as '-' for extractKeyValuePairs function"):
        input = f"'{askii_alpha}:-{askii_alpha}{parsed_noise.replace('-', '')}-'"
        output = "{" + f"'{askii_alpha}':'{askii_alpha}{noise.replace('-', '')}" + "}"
        params = "'\\\\', ':', ',', '-'"

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EnclosingCharacter("1.0"))
def specifying_enclosing_character_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying enclosing character
    as alphabet symbol."""

    with When("I specify input string, output map and define enclosing character "
              "parameter as 'q' for extractKeyValuePairs function"):
        input = f"'{askii_alpha}:q{parsed_noise}q'"
        output = "{" + f"'{askii_alpha}':'{parsed_noise}" + "}"
        params = "'\\\\', ':', ',', 'q'"

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ItemDelimiter("1.0"))
def specifying_item_delimiter_non_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying item delimiter
    as non-alphabet symbol."""

    with When("I specify input string, output map and define item delimiter "
              "parameter as '-' for extractKeyValuePairs function"):
        input = f"'{askii_alpha}:{askii_alpha}-{askii_alpha}{askii_num}:{askii_alpha}'"
        output = "{" + f"'{askii_alpha}':'{askii_alpha}','{askii_alpha}{askii_num}':'{askii_alpha}'" + "}"
        params = "'\\\\', ':', '-'"

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ItemDelimiter("1.0"))
def specifying_item_delimiter_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying item delimiter
    as alphabet symbol."""

    with When("I specify input string, output map and define item delimiter "
              "parameter as 'q' for extractKeyValuePairs function"):
        input = f"'{askii_alpha.replace('q', '')}:" \
                f"{askii_num}q{askii_alpha.replace('q', '')}{askii_num}:{askii_num}'"
        output = "{" + f"'{askii_alpha.replace('q', '')}':" \
                       f"'{askii_num}','{askii_alpha.replace('q', '')}{askii_num}':'{askii_num}'" + "}"
        params = "'\\\\', ':', 'q'"

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_KeyValuePairDelimiter("1.0"))
def specifying_key_value_pair_delimiter_non_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying key value pair delimiter
    as non-alphabet symbol."""

    with When("I specify input string, output map and define key value pair delimiter "
              "parameter as '-' for extractKeyValuePairs function"):
        input = f"'{askii_alpha}-{askii_alpha}'"
        output = "{" + f"'{askii_alpha}':'{askii_alpha}'" + "}"
        params = "'\\\\', '-'"

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_KeyValuePairDelimiter("1.0"))
def specifying_key_value_pair_delimiter_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying key value pair delimiter
    as alphabet symbol."""

    with When("I specify input string, output map and define key value pair delimiter "
              "parameter as 'q' for extractKeyValuePairs function"):
        input = f"'{askii_alpha.replace('q','')}q{askii_num}'"
        output = "{" + f"'{askii_alpha.replace('q','')}':'{askii_num}'" + "}"
        params = "'\\\\', 'q'"

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EscapeCharacter("1.0"))
def specifying_escape_character_non_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying escape character
    as non-alphabet symbol."""

    with When("I specify input string, output map and define escape character "
              "parameter as '-' for extractKeyValuePairs function"):
        input = f"'{askii_alpha},-)'"
        output = "{" + f"'{askii_alpha}':')'" + "}"
        params = "'-'"

    scenario(input=input, output=output, params=params)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EscapeCharacter("1.0"))
def specifying_escape_character_alpha(self, scenario):
    """Check that clickhouse extractKeyValuePairs function support specifying escape character
    as alphabet symbol."""

    with When("I specify input string, output map and define escape character "
              "parameter as 'q' for extractKeyValuePairs function"):
        input = f"'{askii_alpha.replace('q', '')},q)'"
        output = "{" + f"'{askii_alpha.replace('q', '')}':')'" + "}"
        params = "'q'"

    scenario(input=input, output=output, params=params)


@TestFeature
@Name("specifying special symbols")
def specifying_special_symbols(self, scenario):
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


# @TestCheck
# @Name("value special characters allow list default value")
# @Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ValueSpecialCharactersAllowList("1.0"))
# def value_special_characters_allow_list_default_value(self, scenario):
#     """Check that default value for value_special_characters_allow_list is empty string"""
#
#     with When("I specify input as string with  , output map and define escape character "
#               "parameter as 'q' for extractKeyValuePairs function"):
#         input = f"'{askii_alpha}:{noise}{askii_num}'"
#         output = f"{askii_alpha}:''"
#         params = ""
#
#     scenario(input=input, output=output, params=params)
#
#
#
# @TestFeature
# @Name("default parameters values")
# def default_parameters_values(self):
#     """Check that clickhouse extractKeyValuePairs default values for special symbols are
#     `\` - for escape_character, `:` - for key_value_pair_delimiter, `,` for item_delimeter
#     `"` for enclosing_character, empty string for value_special_characters_allow_list."""
#
#     value_special_characters_allow_list_default_value(scenario=scenario)
#     enclosing_character_default_value(scenario=scenario)
#     item_delimiter_default_value(scenario=scenario)
#     key_value_pair_delimiter_default_value(scenario=scenario)
#     escape_character_default_value(scenario=scenario)


@TestCheck
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Input("1.0"))
def input_format(self, scenario):
    """Check that extractKeyValuePairs function can accept any string as input.
    """

    with When("I specify input string as string that contains all askii symbols"):
        input = f"'{askii_alpha}{askii_num}{parsed_noise}'"
        output = "{}"
        params = f"'\\\\\\\\', ':', ',', '\\\"'"

    scenario(input=input, output=output, params=params)
