# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.221009.1165957.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_ClickHouse_ParseKeyValue = Requirement(
    name="RQ.ClickHouse.ParseKeyValue",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `parseKeyValue` string function that SHALL have the following syntax:\n"
        "\n"
        "\n"
        "```sql\n"
        "parseKeyValue(<column_name>|<constant>|<function_return_value>|<alias>)\n"
        "```\n"
        "\n"
        "For example, \n"
        "\n"
        "> Insert into the table parsed keys, values from another table\n"
        "\n"
        "```sql\n"
        "INSERT INTO table_2 SELECT parseKeyValue(x) FROM table_1;\n"
        "```\n"
        "\n"
        "The function SHALL return an `String` that SHALL contain parsed keys, values\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.1.1",
)

RQ_ClickHouse_ParseKeyValue_SupportedDataTypes = Requirement(
    name="RQ.ClickHouse.ParseKeyValue.SupportedDataTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `parseKeyValue` function for the following data types that SHALL either\n"
        "be provided as a constant or using a table column:\n"
        "\n"
        "* `String`\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.1.2",
)

RQ_ClickHouse_ParseKeyValue_UnsupportedDataTypes = Requirement(
    name="RQ.ClickHouse.ParseKeyValue.UnsupportedDataTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s `base58Encode` function SHALL return an error if input data type is not supported.\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "[KeyValue]: https://github.com/arthurpassos/KeyValuePairFileProcessor\n"
        "[ClickHouse]: https://clickhouse.tech\n"
    ),
    link=None,
    level=3,
    num="2.1.3",
)

SRS_ClickHouse_Key_Value_Function = Specification(
    name="SRS ClickHouse Key Value Function",
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
        Heading(name="Introduction", level=1, num="1"),
        Heading(name="Requirements", level=1, num="2"),
        Heading(name="Parse Key Value", level=2, num="2.1"),
        Heading(name="RQ.ClickHouse.ParseKeyValue", level=3, num="2.1.1"),
        Heading(
            name="RQ.ClickHouse.ParseKeyValue.SupportedDataTypes", level=3, num="2.1.2"
        ),
        Heading(
            name="RQ.ClickHouse.ParseKeyValue.UnsupportedDataTypes",
            level=3,
            num="2.1.3",
        ),
    ),
    requirements=(
        RQ_ClickHouse_ParseKeyValue,
        RQ_ClickHouse_ParseKeyValue_SupportedDataTypes,
        RQ_ClickHouse_ParseKeyValue_UnsupportedDataTypes,
    ),
    content="""
# SRS ClickHouse Key Value Function
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Requirements](#requirements)
  * 2.1 [Parse Key Value](#parse-key-value)
    * 2.1.1 [RQ.ClickHouse.ParseKeyValue](#rqclickhouseparsekeyvalue)
    * 2.1.2 [RQ.ClickHouse.ParseKeyValue.SupportedDataTypes](#rqclickhouseparsekeyvaluesupporteddatatypes)
    * 2.1.3 [RQ.ClickHouse.ParseKeyValue.UnsupportedDataTypes](#rqclickhouseparsekeyvalueunsupporteddatatypes)

## Introduction

This software requirements specification covers requirements related to [ClickHouse]
[KeyValue] functionality that implements parseKeyValue function.

## Requirements

### Parse Key Value

#### RQ.ClickHouse.ParseKeyValue
version: 1.0

[ClickHouse] SHALL support `parseKeyValue` string function that SHALL have the following syntax:


```sql
parseKeyValue(<column_name>|<constant>|<function_return_value>|<alias>)
```

For example, 

> Insert into the table parsed keys, values from another table

```sql
INSERT INTO table_2 SELECT parseKeyValue(x) FROM table_1;
```

The function SHALL return an `String` that SHALL contain parsed keys, values

#### RQ.ClickHouse.ParseKeyValue.SupportedDataTypes
version: 1.0

[ClickHouse] SHALL support using `parseKeyValue` function for the following data types that SHALL either
be provided as a constant or using a table column:

* `String`

#### RQ.ClickHouse.ParseKeyValue.UnsupportedDataTypes
version: 1.0

[ClickHouse]'s `base58Encode` function SHALL return an error if input data type is not supported.




[KeyValue]: https://github.com/arthurpassos/KeyValuePairFileProcessor
[ClickHouse]: https://clickhouse.tech
""",
)
