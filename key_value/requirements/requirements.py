# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230315.1003122.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Function = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `extractKeyValuePairs` function that SHALL have the following syntax:\n'
        '\n'
        '\n'
        '```sql\n'
        'extractKeyValuePairs(<column_name>|<constant>|<function_return_value>|<alias>[, key_value_pair_delimiter[, pair_delimiters[, quoting_character[, escape_sequences_support]]]]])\n'
        '```\n'
        '\n'
        'For example, \n'
        '\n'
        '> Insert into the table parsed key-values from another table\n'
        '\n'
        '```sql\n'
        'INSERT INTO table_2 SELECT extractKeyValuePairs(x) FROM table_1;\n'
        '```\n'
        '\n'
        'The function SHALL return a `map` object containing all recognized parsed keys and values. \n'
        '\n'
        "`{'key': 'value', ...}`\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.1.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Function_SupportedDataTypes = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.SupportedDataTypes',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support using the [extractKeyValuePairs] function with the following data types:\n'
        '\n'
        '* [String]\n'
        '* [LowCardinality]\n'
        '* [FixedString]\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.1.2'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Function_UnsupportedDataTypes = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.UnsupportedDataTypes',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if input data type is not supported. \n"
        'Nullable types are not supported.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.1.3'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Constant = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Constant',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as a string constant.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.2.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Column = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Column',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as a string column.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.2.2'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Array = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Array',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as the value \n"
        'returned from the array.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.2.3'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Map = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Map',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as \n"
        'value that returned from the map.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.2.4'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Alias = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Alias',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as alias expression.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.2.5'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_Noise = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.Noise',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL remove all noise that is not related to the key or value.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.3.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_IdenticalKeys = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.IdenticalKeys',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL return the last key value pair \n"
        'for all key value pairs with the same key.\n'
        '\n'
        'For example:\n'
        '\n'
        "`SELECT extractKeyValuePairs('a:a, a:b')`\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.3.2'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Input = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Input',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL accept any string as input.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.4.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Key_Format = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Key.Format',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL recognize the key in the input string\n"
        'if it satisfies the following conditions:\n'
        '\n'
        '* Key starts with the alphabet symbol.\n'
        '* Only alphabet symbols, numbers, and underscore are used in the key.\n'
        "* Key can't be an empty string.\n"
        '* If escape_sequences_support is ON, key can contain any non-control symbols.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.5.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Value_Format = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Value.Format',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL recognize the value in the input string\n"
        'if it satisfies the following conditions:\n'
        '\n'
        '* Value starts with any non-space symbol.\n'
        '* Only symbols, numbers, and underscore are used in the value.\n'
        '* Value can be an empty string.\n'
        '* If a value is enclosed, value can contain any non-control symbols.\n'
        '* If escape_sequences_support is ON, value can contain any non-control symbols.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.6.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying following parameters:\n"
        '`key_value_pair_delimiter`, `pair_delimiters`, `quoting_character`, `escape_sequences_support`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.7.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_KeyValuePairDelimiter = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.KeyValuePairDelimiter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `key_value_pair_delimiter`\n"
        'which SHALL divide key value pairs among themselves.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='3.7.2.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_KeyValuePairDelimiter_Format = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.KeyValuePairDelimiter.Format',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if `key_value_pair_delimiter` \n"
        'parameter specified with non-string value or string value with more than one symbol.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='3.7.2.2'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_PairDelimiter = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.PairDelimiter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `pair_delimiters`\n"
        'which SHALL divide key value pairs in input string.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='3.7.3.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_PairDelimiter_Format = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.PairDelimiter.Format',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if `pair_delimiters` \n"
        'parameter specified with non-string value.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='3.7.3.2'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_QuotingCharacter = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.QuotingCharacter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `quoting_character`\n"
        'which SHALL enclose symbols which allows you to use unsupported characters in a key or value.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='3.7.4.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_QuotingCharacter_Format = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.QuotingCharacter.Format',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if `quoting_character` \n"
        'parameter specified with non-string value or string value with more than one symbol.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='3.7.4.2'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_EscapeSequencesSupport = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.EscapeSequencesSupport',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying \n"
        '`escape_sequences_support` which SHALL allow using non-control symbols in keys and values\n'
        'and allow specifying symbols in hexadecimal format.\n'
        '\n'
        'For example:\n'
        '\n'
        '`SELECT extractKeyValuePairs(\'a:\\\\x0A\', \':\', \',\', \'"\', \'1\')`\n'
        '\n'
        'SHALL return\n'
        '\n'
        "`{'a':'\\n'}`\n"
        '\n'
    ),
    link=None,
    level=4,
    num='3.7.5.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_EscapeSequencesSupport_extractKeyValuePairsWithEscaping = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.EscapeSequencesSupport.extractKeyValuePairsWithEscaping',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `extractKeyValuePairsWithEscaping` function that SHALL return the same result as \n'
        '`extractKeyValuePairs` function with `escape_sequences_support` enabled.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='3.7.5.2'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_EscapeSequencesSupport_Format = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.EscapeSequencesSupport.Format',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if `escape_sequences_support` \n"
        'parameter specified with non-boolean value.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='3.7.5.3'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_SpecialCharactersConflict = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.SpecialCharactersConflict',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if any of the following \n"
        'parameters are specified with the same symbol: `key_value_pair_delimiter`, `pair_delimiters`,\n'
        '`quoting_character`.\n'
        '\n'
        'For example:\n'
        '\n'
        "`SELECT extractKeyValuePairs('a=a', '=', '=', '=')`\n"
        '\n'
    ),
    link=None,
    level=4,
    num='3.7.6.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_KeyValuePairDelimiter = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.KeyValuePairDelimiter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "By default, [ClickHouse]'s [extractKeyValuePairs] function SHALL \n"
        "specify `key_value_pair_delimiter` using `':'`.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.8.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_PairDelimiters = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.PairDelimiters',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "By default, [ClickHouse]'s [extractKeyValuePairs] function SHALL \n"
        "specify `pair_delimiters` using `' ,;'`.\n"
        '\n'
    ),
    link=None,
    level=2,
    num='3.9'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_QuotingCharacter = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.QuotingCharacter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "By default, [ClickHouse]'s [extractKeyValuePairs] function SHALL\n"
        'specify `quoting_character` using `\'"\'`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.9.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_EscapeSequencesSupport = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.EscapeSequencesSupport',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "By default, [ClickHouse]'s [extractKeyValuePairs] function SHALL\n"
        'specify `escape_sequences_support` using `OFF`.\n'
        '\n'
        '[String]: https://clickhouse.com/docs/en/sql-reference/data-types/string\n'
        '[FixedString]: https://clickhouse.com/docs/en/sql-reference/data-types/fixedstring\n'
        '[LowCardinality]: https://clickhouse.com/docs/en/sql-reference/data-types/lowcardinality\n'
        '[extractKeyValuePairs]: https://github.com/arthurpassos/KeyValuePairFileProcessor\n'
        '[ClickHouse]: https://clickhouse.tech\n'
    ),
    link=None,
    level=3,
    num='3.9.2'
)

SRS033_ClickHouse_Key_Value_Function = Specification(
    name='SRS033 ClickHouse Key Value Function',
    description=None,
    author=None,
    date=None,
    status=None,
    approved_by=None,
    approved_date=None,
    approved_version=None,
    version=None,
    group=None,
    type=None,
    link=None,
    uid=None,
    parent=None,
    children=None,
    headings=(
        Heading(name='Introduction', level=1, num='1'),
        Heading(name='Test Feature Diagram', level=1, num='2'),
        Heading(name='Requirements', level=1, num='3'),
        Heading(name='extractKeyValuePairs Function', level=2, num='3.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function', level=3, num='3.1.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.SupportedDataTypes', level=3, num='3.1.2'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.UnsupportedDataTypes', level=3, num='3.1.3'),
        Heading(name='Input Data Source', level=2, num='3.2'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Constant', level=3, num='3.2.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Column', level=3, num='3.2.2'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Array', level=3, num='3.2.3'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Map', level=3, num='3.2.4'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Alias', level=3, num='3.2.5'),
        Heading(name='Parsing', level=2, num='3.3'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.Noise', level=3, num='3.3.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.IdenticalKeys', level=3, num='3.3.2'),
        Heading(name='Format', level=2, num='3.4'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Input', level=3, num='3.4.1'),
        Heading(name='Key', level=2, num='3.5'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Key.Format', level=3, num='3.5.1'),
        Heading(name='Value', level=2, num='3.6'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Value.Format', level=3, num='3.6.1'),
        Heading(name='Parameters', level=2, num='3.7'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters', level=3, num='3.7.1'),
        Heading(name='Key Value Pair Delimiter', level=3, num='3.7.2'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.KeyValuePairDelimiter', level=4, num='3.7.2.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.KeyValuePairDelimiter.Format', level=4, num='3.7.2.2'),
        Heading(name='Pair Delimiter', level=3, num='3.7.3'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.PairDelimiter', level=4, num='3.7.3.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.PairDelimiter.Format', level=4, num='3.7.3.2'),
        Heading(name='Quoting Character', level=3, num='3.7.4'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.QuotingCharacter', level=4, num='3.7.4.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.QuotingCharacter.Format', level=4, num='3.7.4.2'),
        Heading(name='Escape Sequences Support', level=3, num='3.7.5'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.EscapeSequencesSupport', level=4, num='3.7.5.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.EscapeSequencesSupport.extractKeyValuePairsWithEscaping', level=4, num='3.7.5.2'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.EscapeSequencesSupport.Format', level=4, num='3.7.5.3'),
        Heading(name='Special Characters Conflict', level=3, num='3.7.6'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.SpecialCharactersConflict', level=4, num='3.7.6.1'),
        Heading(name='Default Parameters Values', level=2, num='3.8'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.KeyValuePairDelimiter', level=3, num='3.8.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.PairDelimiters', level=2, num='3.9'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.QuotingCharacter', level=3, num='3.9.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.EscapeSequencesSupport', level=3, num='3.9.2'),
        ),
    requirements=(
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Function,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Function_SupportedDataTypes,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Function_UnsupportedDataTypes,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Constant,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Column,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Array,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Map,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Alias,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_Noise,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_IdenticalKeys,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Input,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Key_Format,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Value_Format,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_KeyValuePairDelimiter,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_KeyValuePairDelimiter_Format,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_PairDelimiter,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_PairDelimiter_Format,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_QuotingCharacter,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_QuotingCharacter_Format,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_EscapeSequencesSupport,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_EscapeSequencesSupport_extractKeyValuePairsWithEscaping,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_EscapeSequencesSupport_Format,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parameters_SpecialCharactersConflict,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_KeyValuePairDelimiter,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_PairDelimiters,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_QuotingCharacter,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Default_EscapeSequencesSupport,
        ),
    content='''
# SRS033 ClickHouse Key Value Function
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Test Feature Diagram](#test-feature-diagram)
* 3 [Requirements](#requirements)
  * 3.1 [extractKeyValuePairs Function](#extractkeyvaluepairs-function)
    * 3.1.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function](#rqsrs-033clickhouseextractkeyvaluepairsfunction)
    * 3.1.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.SupportedDataTypes](#rqsrs-033clickhouseextractkeyvaluepairsfunctionsupporteddatatypes)
    * 3.1.3 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.UnsupportedDataTypes](#rqsrs-033clickhouseextractkeyvaluepairsfunctionunsupporteddatatypes)
  * 3.2 [Input Data Source](#input-data-source)
    * 3.2.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Constant](#rqsrs-033clickhouseextractkeyvaluepairsinputdatasourceconstant)
    * 3.2.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Column](#rqsrs-033clickhouseextractkeyvaluepairsinputdatasourcecolumn)
    * 3.2.3 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Array](#rqsrs-033clickhouseextractkeyvaluepairsinputdatasourcearray)
    * 3.2.4 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Map](#rqsrs-033clickhouseextractkeyvaluepairsinputdatasourcemap)
    * 3.2.5 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Alias](#rqsrs-033clickhouseextractkeyvaluepairsinputdatasourcealias)
  * 3.3 [Parsing](#parsing)
    * 3.3.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.Noise](#rqsrs-033clickhouseextractkeyvaluepairsparsingnoise)
    * 3.3.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.IdenticalKeys](#rqsrs-033clickhouseextractkeyvaluepairsparsingidenticalkeys)
  * 3.4 [Format](#format)
    * 3.4.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Input](#rqsrs-033clickhouseextractkeyvaluepairsformatinput)
  * 3.5 [Key](#key)
    * 3.5.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Key.Format](#rqsrs-033clickhouseextractkeyvaluepairskeyformat)
  * 3.6 [Value](#value)
    * 3.6.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Value.Format](#rqsrs-033clickhouseextractkeyvaluepairsvalueformat)
  * 3.7 [Parameters](#parameters)
    * 3.7.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters](#rqsrs-033clickhouseextractkeyvaluepairsparameters)
    * 3.7.2 [Key Value Pair Delimiter](#key-value-pair-delimiter)
      * 3.7.2.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.KeyValuePairDelimiter](#rqsrs-033clickhouseextractkeyvaluepairsparameterskeyvaluepairdelimiter)
      * 3.7.2.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.KeyValuePairDelimiter.Format](#rqsrs-033clickhouseextractkeyvaluepairsparameterskeyvaluepairdelimiterformat)
    * 3.7.3 [Pair Delimiter](#pair-delimiter)
      * 3.7.3.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.PairDelimiter](#rqsrs-033clickhouseextractkeyvaluepairsparameterspairdelimiter)
      * 3.7.3.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.PairDelimiter.Format](#rqsrs-033clickhouseextractkeyvaluepairsparameterspairdelimiterformat)
    * 3.7.4 [Quoting Character](#quoting-character)
      * 3.7.4.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.QuotingCharacter](#rqsrs-033clickhouseextractkeyvaluepairsparametersquotingcharacter)
      * 3.7.4.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.QuotingCharacter.Format](#rqsrs-033clickhouseextractkeyvaluepairsparametersquotingcharacterformat)
    * 3.7.5 [Escape Sequences Support](#escape-sequences-support)
      * 3.7.5.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.EscapeSequencesSupport](#rqsrs-033clickhouseextractkeyvaluepairsparametersescapesequencessupport)
      * 3.7.5.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.EscapeSequencesSupport.extractKeyValuePairsWithEscaping](#rqsrs-033clickhouseextractkeyvaluepairsparametersescapesequencessupportextractkeyvaluepairswithescaping)
      * 3.7.5.3 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.EscapeSequencesSupport.Format](#rqsrs-033clickhouseextractkeyvaluepairsparametersescapesequencessupportformat)
    * 3.7.6 [Special Characters Conflict](#special-characters-conflict)
      * 3.7.6.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.SpecialCharactersConflict](#rqsrs-033clickhouseextractkeyvaluepairsparametersspecialcharactersconflict)
  * 3.8 [Default Parameters Values](#default-parameters-values)
    * 3.8.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.KeyValuePairDelimiter](#rqsrs-033clickhouseextractkeyvaluepairsdefaultkeyvaluepairdelimiter)
  * 3.9 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.PairDelimiters](#rqsrs-033clickhouseextractkeyvaluepairsdefaultpairdelimiters)
    * 3.9.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.QuotingCharacter](#rqsrs-033clickhouseextractkeyvaluepairsdefaultquotingcharacter)
    * 3.9.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.EscapeSequencesSupport](#rqsrs-033clickhouseextractkeyvaluepairsdefaultescapesequencessupport)
## Introduction

This software requirements specification covers requirements related to [ClickHouse]
[extractKeyValuePairs] function.

## Test Feature Diagram

```mermaid
flowchart LR
  subgraph Key Value
    direction LR
    subgraph A[extractKeyValuePairs]
        A1[remove all noise not related to the key or value]
        A2[output any values that are recognized as a key-value pair]
    end
    subgraph E[Format]
        direction TB
        subgraph E1[input format]
            direction LR
            E11[Any string]
            E12["extractKeyValuePairs(string[, key_value_pair_delimiter[, pair_delimiters[, quoting_character[, escape_sequences_support]]]]])"]
        end
        subgraph E2[output format]
            direction LR 
            E21["String in format {'key': 'value', ...}"]
        end
    end  
    subgraph Z[Separator]
        direction TB
        subgraph Z1[Key]
            direction LR
            Z12[can't contain control symbols]
            Z13[can't be an empty string]
            Z14[it accepts anything if it is between the enclosing character]
        end
        subgraph Z2[Value]
            direction LR
            Z21[can start with any non-space character or escape_sequences_support is ON]
            Z22[can be empty]
            Z23[can't contain control symbols]
            Z24[it accepts anything if it is between the enclosing character or escape_sequences_support is ON]
        end
    end
    subgraph Q[Parameters]
        direction TB
        Q1[key_value_pair_delimiter, default ':']
        Q2[pair_delimiters, default ' ,;']
        Q3[quoting_character, default '\"']
        Q5[escape_sequences_support, default OFF]
    end
  end
```

## Requirements

### extractKeyValuePairs Function

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function
version: 1.0

[ClickHouse] SHALL support `extractKeyValuePairs` function that SHALL have the following syntax:


```sql
extractKeyValuePairs(<column_name>|<constant>|<function_return_value>|<alias>[, key_value_pair_delimiter[, pair_delimiters[, quoting_character[, escape_sequences_support]]]]])
```

For example, 

> Insert into the table parsed key-values from another table

```sql
INSERT INTO table_2 SELECT extractKeyValuePairs(x) FROM table_1;
```

The function SHALL return a `map` object containing all recognized parsed keys and values. 

`{'key': 'value', ...}`

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.SupportedDataTypes
version: 1.0

[ClickHouse] SHALL support using the [extractKeyValuePairs] function with the following data types:

* [String]
* [LowCardinality]
* [FixedString]

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.UnsupportedDataTypes
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if input data type is not supported. 
Nullable types are not supported.

### Input Data Source

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Constant
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as a string constant.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Column
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as a string column.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Array
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as the value 
returned from the array.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Map
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as 
value that returned from the map.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Alias
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as alias expression.

### Parsing

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.Noise
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL remove all noise that is not related to the key or value.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.IdenticalKeys
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return the last key value pair 
for all key value pairs with the same key.

For example:

`SELECT extractKeyValuePairs('a:a, a:b')`

### Format

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Input
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept any string as input.

### Key

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Key.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL recognize the key in the input string
if it satisfies the following conditions:

* Key starts with the alphabet symbol.
* Only alphabet symbols, numbers, and underscore are used in the key.
* Key can't be an empty string.
* If escape_sequences_support is ON, key can contain any non-control symbols.

### Value

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Value.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL recognize the value in the input string
if it satisfies the following conditions:

* Value starts with any non-space symbol.
* Only symbols, numbers, and underscore are used in the value.
* Value can be an empty string.
* If a value is enclosed, value can contain any non-control symbols.
* If escape_sequences_support is ON, value can contain any non-control symbols.

### Parameters

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying following parameters:
`key_value_pair_delimiter`, `pair_delimiters`, `quoting_character`, `escape_sequences_support`.

#### Key Value Pair Delimiter

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.KeyValuePairDelimiter
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `key_value_pair_delimiter`
which SHALL divide key value pairs among themselves.

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.KeyValuePairDelimiter.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if `key_value_pair_delimiter` 
parameter specified with non-string value or string value with more than one symbol.

#### Pair Delimiter

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.PairDelimiter
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `pair_delimiters`
which SHALL divide key value pairs in input string.

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.PairDelimiter.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if `pair_delimiters` 
parameter specified with non-string value.

#### Quoting Character

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.QuotingCharacter
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `quoting_character`
which SHALL enclose symbols which allows you to use unsupported characters in a key or value.

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.QuotingCharacter.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if `quoting_character` 
parameter specified with non-string value or string value with more than one symbol.

#### Escape Sequences Support

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.EscapeSequencesSupport
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying 
`escape_sequences_support` which SHALL allow using non-control symbols in keys and values
and allow specifying symbols in hexadecimal format.

For example:

`SELECT extractKeyValuePairs('a:\\x0A', ':', ',', '"', '1')`

SHALL return

`{'a':'\n'}`

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.EscapeSequencesSupport.extractKeyValuePairsWithEscaping
version: 1.0

[ClickHouse] SHALL support `extractKeyValuePairsWithEscaping` function that SHALL return the same result as 
`extractKeyValuePairs` function with `escape_sequences_support` enabled.

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.EscapeSequencesSupport.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if `escape_sequences_support` 
parameter specified with non-boolean value.

#### Special Characters Conflict

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.SpecialCharactersConflict
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if any of the following 
parameters are specified with the same symbol: `key_value_pair_delimiter`, `pair_delimiters`,
`quoting_character`.

For example:

`SELECT extractKeyValuePairs('a=a', '=', '=', '=')`

### Default Parameters Values

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.KeyValuePairDelimiter
version: 1.0

By default, [ClickHouse]'s [extractKeyValuePairs] function SHALL 
specify `key_value_pair_delimiter` using `':'`.

### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.PairDelimiters
version: 1.0

By default, [ClickHouse]'s [extractKeyValuePairs] function SHALL 
specify `pair_delimiters` using `' ,;'`.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.QuotingCharacter
version: 1.0

By default, [ClickHouse]'s [extractKeyValuePairs] function SHALL
specify `quoting_character` using `'"'`.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.EscapeSequencesSupport
version: 1.0

By default, [ClickHouse]'s [extractKeyValuePairs] function SHALL
specify `escape_sequences_support` using `OFF`.

[String]: https://clickhouse.com/docs/en/sql-reference/data-types/string
[FixedString]: https://clickhouse.com/docs/en/sql-reference/data-types/fixedstring
[LowCardinality]: https://clickhouse.com/docs/en/sql-reference/data-types/lowcardinality
[extractKeyValuePairs]: https://github.com/arthurpassos/KeyValuePairFileProcessor
[ClickHouse]: https://clickhouse.tech
'''
)
