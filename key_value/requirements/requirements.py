# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.221009.1165957.
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
        'extractKeyValuePairs(<column_name>|<constant>|<function_return_value>|<alias>[, escape_character[, key_value_pair_delimiter[, item_delimiter[, enclosing_character[, value_special_characters_allow_list]]]]])\n'
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
        'The function SHALL return a `String` object containing parsed keys and values. \n'
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
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if input data type is not supported.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.1.3'
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
    num='3.2.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_RecognizedKeyValuePairs = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.RecognizedKeyValuePairs',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL output all values that are recognized as a key-value pair.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.2.2'
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
    num='3.3.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Output = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Output',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL return a string in the following format:\n"
        '\n'
        "`{'key': 'value', ...}`\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.3.2'
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
        '* Key starts with the alfabet symbol.\n'
        '* Only alfabet symbols, numbers, and underscore are used in the key.\n'
        "* Key can't be an empty string.\n"
        '* If not supported symbols are escaped or a value is enclosed, the key can be any string. \n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.4.1'
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
        '* Key starts with any non-space symbol.\n'
        '* Only symbols, numbers, and underscore are used in the value.\n'
        '* Value can be an empty string.\n'
        '* If not supported symbols are escaped or a value is enclosed, value can be any string. \n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.5.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ItemDelimiter = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.ItemDelimiter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `item_delimeter`\n"
        'which SHALL divide key value pairs in input string.\n'
        '\n'
        'By default, the function SHALL specify `item_delimeter` as `,`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.6.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_KeyValueDelimiter = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.KeyValueDelimiter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `key_value_delimiter`\n"
        'which SHALL divide key value pairs among themselves.\n'
        '\n'
        'By default, the function SHALL specify `key_value_delimiter` as `:`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.7.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EscapeCharacter = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.EscapeCharacter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `escape_character`\n"
        'which SHALL escape symbols which allows you to use unsupported characters in a key or value.\n'
        '\n'
        'By default, the function SHALL specify `escape_character` as `\\`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.8.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EnclosingCharacter = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.EnclosingCharacter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `enclosing_character`\n"
        'which SHALL enclose symbols which allows you to use unsupported characters in a key or value.\n'
        '\n'
        'By default, the function SHALL specify `enclosing_character` as `"`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.9.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_SpecialCharactersConflict = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.SpecialCharactersConflict',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if any \n"
        'specified special symbols match.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.10.1'
)

RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ValueSpecialCharactersAllowList = Requirement(
    name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.ValueSpecialCharactersAllowList',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `Value Special Characters Allow List`\n"
        'which SHALL specify symbols, that can be used in key and value without escaping or enclosing.\n'
        '\n'
        'By default, the function SHALL specify `enclosing_character` as `"`.\n'
        '\n'
        '[String]: https://clickhouse.com/docs/en/sql-reference/data-types/string\n'
        '[FixedString]: https://clickhouse.com/docs/en/sql-reference/data-types/fixedstring\n'
        '[extractKeyValuePairs]: https://github.com/arthurpassos/KeyValuePairFileProcessor\n'
        '[ClickHouse]: https://clickhouse.tech\n'
    ),
    link=None,
    level=3,
    num='3.11.1'
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
        Heading(name='Parsing', level=2, num='3.2'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.Noise', level=3, num='3.2.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.RecognizedKeyValuePairs', level=3, num='3.2.2'),
        Heading(name='Format', level=2, num='3.3'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Input', level=3, num='3.3.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Output', level=3, num='3.3.2'),
        Heading(name='Key', level=2, num='3.4'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Key.Format', level=3, num='3.4.1'),
        Heading(name='Value', level=2, num='3.5'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Value.Format', level=3, num='3.5.1'),
        Heading(name='Item Delimiter', level=2, num='3.6'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.ItemDelimiter', level=3, num='3.6.1'),
        Heading(name='Key Value Delimiter', level=2, num='3.7'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.KeyValueDelimiter', level=3, num='3.7.1'),
        Heading(name='Escape Character', level=2, num='3.8'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.EscapeCharacter', level=3, num='3.8.1'),
        Heading(name='Enclosing Character', level=2, num='3.9'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.EnclosingCharacter', level=3, num='3.9.1'),
        Heading(name='Special Characters Conflict', level=2, num='3.10'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.SpecialCharactersConflict', level=3, num='3.10.1'),
        Heading(name='Value Special Characters Allow List', level=2, num='3.11'),
        Heading(name='RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.ValueSpecialCharactersAllowList', level=3, num='3.11.1'),
        ),
    requirements=(
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Function,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Function_SupportedDataTypes,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Function_UnsupportedDataTypes,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_Noise,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_RecognizedKeyValuePairs,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Input,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Output,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Key_Format,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Value_Format,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ItemDelimiter,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_KeyValueDelimiter,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EscapeCharacter,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EnclosingCharacter,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_SpecialCharactersConflict,
        RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ValueSpecialCharactersAllowList,
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
  * 3.2 [Parsing](#parsing)
    * 3.2.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.Noise](#rqsrs-033clickhouseextractkeyvaluepairsparsingnoise)
    * 3.2.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.RecognizedKeyValuePairs](#rqsrs-033clickhouseextractkeyvaluepairsparsingrecognizedkeyvaluepairs)
  * 3.3 [Format](#format)
    * 3.3.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Input](#rqsrs-033clickhouseextractkeyvaluepairsformatinput)
    * 3.3.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Output](#rqsrs-033clickhouseextractkeyvaluepairsformatoutput)
  * 3.4 [Key](#key)
    * 3.4.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Key.Format](#rqsrs-033clickhouseextractkeyvaluepairskeyformat)
  * 3.5 [Value](#value)
    * 3.5.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Value.Format](#rqsrs-033clickhouseextractkeyvaluepairsvalueformat)
  * 3.6 [Item Delimiter](#item-delimiter)
    * 3.6.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.ItemDelimiter](#rqsrs-033clickhouseextractkeyvaluepairsitemdelimiter)
  * 3.7 [Key Value Delimiter](#key-value-delimiter)
    * 3.7.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.KeyValueDelimiter](#rqsrs-033clickhouseextractkeyvaluepairskeyvaluedelimiter)
  * 3.8 [Escape Character](#escape-character)
    * 3.8.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.EscapeCharacter](#rqsrs-033clickhouseextractkeyvaluepairsescapecharacter)
  * 3.9 [Enclosing Character](#enclosing-character)
    * 3.9.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.EnclosingCharacter](#rqsrs-033clickhouseextractkeyvaluepairsenclosingcharacter)
  * 3.10 [Special Characters Conflict](#special-characters-conflict)
    * 3.10.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.SpecialCharactersConflict](#rqsrs-033clickhouseextractkeyvaluepairsspecialcharactersconflict)
  * 3.11 [Value Special Characters Allow List](#value-special-characters-allow-list)
    * 3.11.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.ValueSpecialCharactersAllowList](#rqsrs-033clickhouseextractkeyvaluepairsvaluespecialcharactersallowlist)

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
            E12["extractKeyValuePairs(string[, escape_character[, key_value_pair_delimiter[, item_delimiter[, enclosing_character[, value_special_characters_allow_list]]]]])"]
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
            Z11[must start with the symbol]
            Z12[contain only letters, numbers, and underscores]
            Z13[can't be an empty string]
            Z14[it accepts anything if it is between the enclosing character]
        end
        subgraph Z2[Value]
            direction LR
            Z21[can start with any non-space character]
            Z22[can be empty]
            Z23[contain only letters, numbers, and underscores]
            Z24[it accepts anything if it is between the enclosing character]
        end
    end
    subgraph Q[Сontrol сharacters]
        direction TB
        Q1[item_delimiter, default ',']
        Q2[key_value_delimiter, default ':']
        Q3[escape_character, default '\']
        Q4[enclosing_character, default '']
        Q5[value_special_characters_allow_list, default '']
    end
  end
```

## Requirements

### extractKeyValuePairs Function

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function
version: 1.0

[ClickHouse] SHALL support `extractKeyValuePairs` function that SHALL have the following syntax:


```sql
extractKeyValuePairs(<column_name>|<constant>|<function_return_value>|<alias>[, escape_character[, key_value_pair_delimiter[, item_delimiter[, enclosing_character[, value_special_characters_allow_list]]]]])
```

For example, 

> Insert into the table parsed key-values from another table

```sql
INSERT INTO table_2 SELECT extractKeyValuePairs(x) FROM table_1;
```

The function SHALL return a `String` object containing parsed keys and values. 

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.SupportedDataTypes
version: 1.0

[ClickHouse] SHALL support using the [extractKeyValuePairs] function with the following data types:

* [String]
* [FixedString]

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.UnsupportedDataTypes
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if input data type is not supported.

### Parsing

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.Noise
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL remove all noise that is not related to the key or value.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.RecognizedKeyValuePairs
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL output all values that are recognized as a key-value pair.

### Format

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Input
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept any string as input.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Output
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return a string in the following format:

`{'key': 'value', ...}`

### Key

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Key.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL recognize the key in the input string
if it satisfies the following conditions:

* Key starts with the alfabet symbol.
* Only alfabet symbols, numbers, and underscore are used in the key.
* Key can't be an empty string.
* If not supported symbols are escaped or a value is enclosed, the key can be any string. 

### Value

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Value.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL recognize the value in the input string
if it satisfies the following conditions:

* Key starts with any non-space symbol.
* Only symbols, numbers, and underscore are used in the value.
* Value can be an empty string.
* If not supported symbols are escaped or a value is enclosed, value can be any string. 

### Item Delimiter

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.ItemDelimiter
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `item_delimeter`
which SHALL divide key value pairs in input string.

By default, the function SHALL specify `item_delimeter` as `,`.

### Key Value Delimiter

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.KeyValueDelimiter
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `key_value_delimiter`
which SHALL divide key value pairs among themselves.

By default, the function SHALL specify `key_value_delimiter` as `:`.

### Escape Character

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.EscapeCharacter
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `escape_character`
which SHALL escape symbols which allows you to use unsupported characters in a key or value.

By default, the function SHALL specify `escape_character` as `\`.

### Enclosing Character

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.EnclosingCharacter
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `enclosing_character`
which SHALL enclose symbols which allows you to use unsupported characters in a key or value.

By default, the function SHALL specify `enclosing_character` as `"`.

### Special Characters Conflict

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.SpecialCharactersConflict
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if any 
specified special symbols match.

### Value Special Characters Allow List

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.ValueSpecialCharactersAllowList
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `Value Special Characters Allow List`
which SHALL specify symbols, that can be used in key and value without escaping or enclosing.

By default, the function SHALL specify `enclosing_character` as `"`.

[String]: https://clickhouse.com/docs/en/sql-reference/data-types/string
[FixedString]: https://clickhouse.com/docs/en/sql-reference/data-types/fixedstring
[extractKeyValuePairs]: https://github.com/arthurpassos/KeyValuePairFileProcessor
[ClickHouse]: https://clickhouse.tech
'''
)
