# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.221009.1165957.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_033_ClickHouse_ParseKeyValue_Function = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.Function',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `parseKeyValue` string function that SHALL have the following syntax:\n'
        '\n'
        '\n'
        '```sql\n'
        'parseKeyValue(<column_name>|<constant>|<function_return_value>|<alias>[, item_delimiter[, key_value_delimiter[, escape_character[, enclosing_character]]]])\n'
        '```\n'
        '\n'
        'For example, \n'
        '\n'
        '> Insert into the table parsed keys, values from another table\n'
        '\n'
        '```sql\n'
        'INSERT INTO table_2 SELECT parseKeyValue(x) FROM table_1;\n'
        '```\n'
        '\n'
        'The function SHALL return a `String` object containing parsed keys and values. \n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.1.1'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_Function_SupportedDataTypes = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.Function.SupportedDataTypes',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support using the "parseKeyValue" function with the following data types:\n'
        '\n'
        '* `String`\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.1.2'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_Function_UnsupportedDataTypes = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.Function.UnsupportedDataTypes',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL return an error if input data type is not supported.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.1.3'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_Parsing_Noise = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.Parsing.Noise',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL remove all noise that is not related to the key or value.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.2.1'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_Parsing_RecognizedKeyValuePairs = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.Parsing.RecognizedKeyValuePairs',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL output any values that are recognized as a key-value pair.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.2.2'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_Format_Input = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.Format.Input',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL accept any string as input.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.3.1'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_Format_Output = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.Format.Output',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL return a string in the following format:\n"
        '\n'
        "`{'key': 'value', ...}`\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.3.2'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_Key_Format = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.Key.Format',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL recognize the key in the input string\n"
        'if it satisfies the following conditions:\n'
        '\n'
        '* Key starts with the symbol.\n'
        '* Only symbols, numbers, and underscore are used in the key.\n'
        "* Key can't be an empty string.\n"
        '* If not supported symbols are escaped or a value is enclosed, the key can be any string. \n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.4.1'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_Value_Format = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.Value.Format',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL recognize the value in the input string\n"
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

RQ_SRS_033_ClickHouse_ParseKeyValue_ItemDelimiter = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.ItemDelimiter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL support specifying `item_delimeter`\n"
        'which SHALL divide key value pairs in input string.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.6.1'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_ItemDelimiter_default = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.ItemDelimiter.default',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL specify `item_delimeter` as `,` by default.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.6.2'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_KeyValueDelimiter = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.KeyValueDelimiter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL support specifying `key_value_delimiter`\n"
        'which SHALL divide key value pairs among themselves.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.7.1'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_KeyValueDelimiter_default = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.KeyValueDelimiter.default',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL specify `key_value_delimiter` as `:` by default.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.7.2'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_EscapeCharacter = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.EscapeCharacter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL support specifying `escape_character`\n"
        'which SHALL escape symbols which allows you to use unsupported characters in a key or value.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.8.1'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_EscapeCharacter_default = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.EscapeCharacter.default',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL specify `escape_character` as `\\` by default.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='3.8.2'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_EnclosingCharacter = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.EnclosingCharacter',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `parseKeyValue` function SHALL support specifying `enclosing_character`\n"
        'which SHALL enclose symbols which allows you to use unsupported characters in a key or value.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='3.9.1'
)

RQ_SRS_033_ClickHouse_ParseKeyValue_EnclosingCharacter_default = Requirement(
    name='RQ.SRS-033.ClickHouse.ParseKeyValue.EnclosingCharacter.default',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse]\'s `parseKeyValue` function SHALL specify `enclosing_character` as `"` by default.\n'
        '\n'
        '\n'
        '[KeyValue]: https://github.com/arthurpassos/KeyValuePairFileProcessor\n'
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
        Heading(name='Parse Key Value Function', level=2, num='3.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.Function', level=3, num='3.1.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.Function.SupportedDataTypes', level=3, num='3.1.2'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.Function.UnsupportedDataTypes', level=3, num='3.1.3'),
        Heading(name='Parsing', level=2, num='3.2'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.Parsing.Noise', level=3, num='3.2.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.Parsing.RecognizedKeyValuePairs', level=3, num='3.2.2'),
        Heading(name='Format', level=2, num='3.3'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.Format.Input', level=3, num='3.3.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.Format.Output', level=3, num='3.3.2'),
        Heading(name='Key', level=2, num='3.4'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.Key.Format', level=3, num='3.4.1'),
        Heading(name='Value', level=2, num='3.5'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.Value.Format', level=3, num='3.5.1'),
        Heading(name='Item Delimiter', level=2, num='3.6'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.ItemDelimiter', level=3, num='3.6.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.ItemDelimiter.default', level=3, num='3.6.2'),
        Heading(name='Key Value Delimiter', level=2, num='3.7'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.KeyValueDelimiter', level=3, num='3.7.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.KeyValueDelimiter.default', level=3, num='3.7.2'),
        Heading(name='Escape Character', level=2, num='3.8'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.EscapeCharacter', level=3, num='3.8.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.EscapeCharacter.default', level=3, num='3.8.2'),
        Heading(name='Enclosing Character', level=2, num='3.9'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.EnclosingCharacter', level=3, num='3.9.1'),
        Heading(name='RQ.SRS-033.ClickHouse.ParseKeyValue.EnclosingCharacter.default', level=3, num='3.9.2'),
        ),
    requirements=(
        RQ_SRS_033_ClickHouse_ParseKeyValue_Function,
        RQ_SRS_033_ClickHouse_ParseKeyValue_Function_SupportedDataTypes,
        RQ_SRS_033_ClickHouse_ParseKeyValue_Function_UnsupportedDataTypes,
        RQ_SRS_033_ClickHouse_ParseKeyValue_Parsing_Noise,
        RQ_SRS_033_ClickHouse_ParseKeyValue_Parsing_RecognizedKeyValuePairs,
        RQ_SRS_033_ClickHouse_ParseKeyValue_Format_Input,
        RQ_SRS_033_ClickHouse_ParseKeyValue_Format_Output,
        RQ_SRS_033_ClickHouse_ParseKeyValue_Key_Format,
        RQ_SRS_033_ClickHouse_ParseKeyValue_Value_Format,
        RQ_SRS_033_ClickHouse_ParseKeyValue_ItemDelimiter,
        RQ_SRS_033_ClickHouse_ParseKeyValue_ItemDelimiter_default,
        RQ_SRS_033_ClickHouse_ParseKeyValue_KeyValueDelimiter,
        RQ_SRS_033_ClickHouse_ParseKeyValue_KeyValueDelimiter_default,
        RQ_SRS_033_ClickHouse_ParseKeyValue_EscapeCharacter,
        RQ_SRS_033_ClickHouse_ParseKeyValue_EscapeCharacter_default,
        RQ_SRS_033_ClickHouse_ParseKeyValue_EnclosingCharacter,
        RQ_SRS_033_ClickHouse_ParseKeyValue_EnclosingCharacter_default,
        ),
    content='''
# SRS033 ClickHouse Key Value Function
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Test Feature Diagram](#test-feature-diagram)
* 3 [Requirements](#requirements)
  * 3.1 [Parse Key Value Function](#parse-key-value-function)
    * 3.1.1 [RQ.SRS-033.ClickHouse.ParseKeyValue.Function](#rqsrs-033clickhouseparsekeyvaluefunction)
    * 3.1.2 [RQ.SRS-033.ClickHouse.ParseKeyValue.Function.SupportedDataTypes](#rqsrs-033clickhouseparsekeyvaluefunctionsupporteddatatypes)
    * 3.1.3 [RQ.SRS-033.ClickHouse.ParseKeyValue.Function.UnsupportedDataTypes](#rqsrs-033clickhouseparsekeyvaluefunctionunsupporteddatatypes)
  * 3.2 [Parsing](#parsing)
    * 3.2.1 [RQ.SRS-033.ClickHouse.ParseKeyValue.Parsing.Noise](#rqsrs-033clickhouseparsekeyvalueparsingnoise)
    * 3.2.2 [RQ.SRS-033.ClickHouse.ParseKeyValue.Parsing.RecognizedKeyValuePairs](#rqsrs-033clickhouseparsekeyvalueparsingrecognizedkeyvaluepairs)
  * 3.3 [Format](#format)
    * 3.3.1 [RQ.SRS-033.ClickHouse.ParseKeyValue.Format.Input](#rqsrs-033clickhouseparsekeyvalueformatinput)
    * 3.3.2 [RQ.SRS-033.ClickHouse.ParseKeyValue.Format.Output](#rqsrs-033clickhouseparsekeyvalueformatoutput)
  * 3.4 [Key](#key)
    * 3.4.1 [RQ.SRS-033.ClickHouse.ParseKeyValue.Key.Format](#rqsrs-033clickhouseparsekeyvaluekeyformat)
  * 3.5 [Value](#value)
    * 3.5.1 [RQ.SRS-033.ClickHouse.ParseKeyValue.Value.Format](#rqsrs-033clickhouseparsekeyvaluevalueformat)
  * 3.6 [Item Delimiter](#item-delimiter)
    * 3.6.1 [RQ.SRS-033.ClickHouse.ParseKeyValue.ItemDelimiter](#rqsrs-033clickhouseparsekeyvalueitemdelimiter)
    * 3.6.2 [RQ.SRS-033.ClickHouse.ParseKeyValue.ItemDelimiter.default](#rqsrs-033clickhouseparsekeyvalueitemdelimiterdefault)
  * 3.7 [Key Value Delimiter](#key-value-delimiter)
    * 3.7.1 [RQ.SRS-033.ClickHouse.ParseKeyValue.KeyValueDelimiter](#rqsrs-033clickhouseparsekeyvaluekeyvaluedelimiter)
    * 3.7.2 [RQ.SRS-033.ClickHouse.ParseKeyValue.KeyValueDelimiter.default](#rqsrs-033clickhouseparsekeyvaluekeyvaluedelimiterdefault)
  * 3.8 [Escape Character](#escape-character)
    * 3.8.1 [RQ.SRS-033.ClickHouse.ParseKeyValue.EscapeCharacter](#rqsrs-033clickhouseparsekeyvalueescapecharacter)
    * 3.8.2 [RQ.SRS-033.ClickHouse.ParseKeyValue.EscapeCharacter.default](#rqsrs-033clickhouseparsekeyvalueescapecharacterdefault)
  * 3.9 [Enclosing Character](#enclosing-character)
    * 3.9.1 [RQ.SRS-033.ClickHouse.ParseKeyValue.EnclosingCharacter](#rqsrs-033clickhouseparsekeyvalueenclosingcharacter)
    * 3.9.2 [RQ.SRS-033.ClickHouse.ParseKeyValue.EnclosingCharacter.default](#rqsrs-033clickhouseparsekeyvalueenclosingcharacterdefault)

## Introduction

This software requirements specification covers requirements related to [ClickHouse]
[KeyValue] functionality that implements the parseKeyValue function.

## Test Feature Diagram

```mermaid
flowchart LR
  subgraph Key Value
    direction LR
    subgraph A[parseKeyValue]
        A1[remove all noise not related to the key or value]
        A2[output any values that are recognized as a key-value pair]
    end
    subgraph E[Format]
        direction TB
        subgraph E1[input format]
            direction LR
            E11[Any string]
            E12["parseKeyValue(string[, item_delimiter[, key_value_delimiter[, escape_character[, enclosing_character]]]])"]
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
    end
  end
```

## Requirements

### Parse Key Value Function

#### RQ.SRS-033.ClickHouse.ParseKeyValue.Function
version: 1.0

[ClickHouse] SHALL support `parseKeyValue` string function that SHALL have the following syntax:


```sql
parseKeyValue(<column_name>|<constant>|<function_return_value>|<alias>[, item_delimiter[, key_value_delimiter[, escape_character[, enclosing_character]]]])
```

For example, 

> Insert into the table parsed keys, values from another table

```sql
INSERT INTO table_2 SELECT parseKeyValue(x) FROM table_1;
```

The function SHALL return a `String` object containing parsed keys and values. 

#### RQ.SRS-033.ClickHouse.ParseKeyValue.Function.SupportedDataTypes
version: 1.0

[ClickHouse] SHALL support using the "parseKeyValue" function with the following data types:

* `String`

#### RQ.SRS-033.ClickHouse.ParseKeyValue.Function.UnsupportedDataTypes
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL return an error if input data type is not supported.

### Parsing

#### RQ.SRS-033.ClickHouse.ParseKeyValue.Parsing.Noise
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL remove all noise that is not related to the key or value.

#### RQ.SRS-033.ClickHouse.ParseKeyValue.Parsing.RecognizedKeyValuePairs
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL output any values that are recognized as a key-value pair.

### Format

#### RQ.SRS-033.ClickHouse.ParseKeyValue.Format.Input
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL accept any string as input.

#### RQ.SRS-033.ClickHouse.ParseKeyValue.Format.Output
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL return a string in the following format:

`{'key': 'value', ...}`

### Key

#### RQ.SRS-033.ClickHouse.ParseKeyValue.Key.Format
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL recognize the key in the input string
if it satisfies the following conditions:

* Key starts with the symbol.
* Only symbols, numbers, and underscore are used in the key.
* Key can't be an empty string.
* If not supported symbols are escaped or a value is enclosed, the key can be any string. 

### Value

#### RQ.SRS-033.ClickHouse.ParseKeyValue.Value.Format
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL recognize the value in the input string
if it satisfies the following conditions:

* Key starts with any non-space symbol.
* Only symbols, numbers, and underscore are used in the value.
* Value can be an empty string.
* If not supported symbols are escaped or a value is enclosed, value can be any string. 

### Item Delimiter

#### RQ.SRS-033.ClickHouse.ParseKeyValue.ItemDelimiter
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL support specifying `item_delimeter`
which SHALL divide key value pairs in input string.

#### RQ.SRS-033.ClickHouse.ParseKeyValue.ItemDelimiter.default
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL specify `item_delimeter` as `,` by default.

### Key Value Delimiter

#### RQ.SRS-033.ClickHouse.ParseKeyValue.KeyValueDelimiter
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL support specifying `key_value_delimiter`
which SHALL divide key value pairs among themselves.

#### RQ.SRS-033.ClickHouse.ParseKeyValue.KeyValueDelimiter.default
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL specify `key_value_delimiter` as `:` by default.

### Escape Character

#### RQ.SRS-033.ClickHouse.ParseKeyValue.EscapeCharacter
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL support specifying `escape_character`
which SHALL escape symbols which allows you to use unsupported characters in a key or value.

#### RQ.SRS-033.ClickHouse.ParseKeyValue.EscapeCharacter.default
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL specify `escape_character` as `\` by default.

### Enclosing Character

#### RQ.SRS-033.ClickHouse.ParseKeyValue.EnclosingCharacter
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL support specifying `enclosing_character`
which SHALL enclose symbols which allows you to use unsupported characters in a key or value.

#### RQ.SRS-033.ClickHouse.ParseKeyValue.EnclosingCharacter.default
version: 1.0

[ClickHouse]'s `parseKeyValue` function SHALL specify `enclosing_character` as `"` by default.


[KeyValue]: https://github.com/arthurpassos/KeyValuePairFileProcessor
[ClickHouse]: https://clickhouse.tech
'''
)
