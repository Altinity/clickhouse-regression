# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.221103.1222218.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_031_ClickHouse_AggregateFunction_DataType = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunction.DataType",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [AggregateFunction] data type which SHALL allow to store as a table column\n"
        "implementation-defined intermediate state of the specified [aggregate function].\n"
        "\n"
        "The data type SHALL be defined using the following syntax:\n"
        "\n"
        "```sql\n"
        "AggregateFunction(name, types_of_arguments…).\n"
        "```\n"
        "\n"
        "where parameters\n"
        "\n"
        "* `name` SHALL specify the aggregate function and if the function is parametric the parameters SHALL be specified as well\n"
        "* `types_of_arguments` SHALL specify types of the aggregate function arguments.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "CREATE TABLE t\n"
        "(\n"
        "    column1 AggregateFunction(uniq, UInt64),\n"
        "    column2 AggregateFunction(anyIf, String, UInt8),\n"
        "    column3 AggregateFunction(quantiles(0.5, 0.9), UInt64)\n"
        ") ENGINE = ...\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.1",
)

SRS031_ClickHouse_AggregateFunction_Data_Type = Specification(
    name="SRS031 ClickHouse AggregateFunction Data Type",
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
        Heading(name="Revision History", level=1, num="1"),
        Heading(name="Introduction", level=1, num="2"),
        Heading(name="Requirements", level=1, num="3"),
        Heading(name="General", level=2, num="3.1"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunction.DataType",
            level=3,
            num="3.1.1",
        ),
        Heading(name="Inserting Data", level=2, num="3.2"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunction.DataType.Insert",
            level=3,
            num="3.2.1",
        ),
        Heading(name="Selecting Data", level=2, num="3.3"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunction.DataType.Select",
            level=3,
            num="3.3.1",
        ),
        Heading(name="References", level=1, num="4"),
    ),
    requirements=(RQ_SRS_031_ClickHouse_AggregateFunction_DataType,),
    content="""
# SRS031 ClickHouse AggregateFunction Data Type
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Requirements](#requirements)
  * 3.1 [General](#general)
    * 3.1.1 [RQ.SRS-031.ClickHouse.AggregateFunction.DataType](#rqsrs-031clickhouseaggregatefunctiondatatype)
  * 3.2 [Inserting Data](#inserting-data)
    * 3.2.1 [RQ.SRS-031.ClickHouse.AggregateFunction.DataType.Insert](#rqsrs-031clickhouseaggregatefunctiondatatypeinsert)
  * 3.3 [Selecting Data](#selecting-data)
    * 3.3.1 [RQ.SRS-031.ClickHouse.AggregateFunction.DataType.Select](#rqsrs-031clickhouseaggregatefunctiondatatypeselect)
* 4 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for supporting [AggregateFunction] data type in [ClickHouse].

## Requirements

### General

#### RQ.SRS-031.ClickHouse.AggregateFunction.DataType
version: 1.0

[ClickHouse] SHALL support [AggregateFunction] data type which SHALL allow to store as a table column
implementation-defined intermediate state of the specified [aggregate function].

The data type SHALL be defined using the following syntax:

```sql
AggregateFunction(name, types_of_arguments…).
```

where parameters

* `name` SHALL specify the aggregate function and if the function is parametric the parameters SHALL be specified as well
* `types_of_arguments` SHALL specify types of the aggregate function arguments.

For example,

```sql
CREATE TABLE t
(
    column1 AggregateFunction(uniq, UInt64),
    column2 AggregateFunction(anyIf, String, UInt8),
    column3 AggregateFunction(quantiles(0.5, 0.9), UInt64)
) ENGINE = ...
```

### Inserting Data

#### RQ.SRS-031.ClickHouse.AggregateFunction.DataType.Insert

[ClickHouse] SHALL support inserting data into [AggregateFunction] data type column 
using a value returned by calling the [aggregate function] with the `-State` suffix in
`INSERT SELECT` statement.

For example,

```sql
INSERT INTO table SELECT uniqState(UserID), quantilesState(0.5, 0.9)(SendTiming)
```

### Selecting Data

#### RQ.SRS-031.ClickHouse.AggregateFunction.DataType.Select

[ClickHouse] SHALL support selecting final result of aggregation from [AggregateFunction] data type column
by using the same [aggregate function] with the `-Merge` suffix.

For example,

```sql
SELECT uniqMerge(state) FROM (SELECT uniqState(UserID) AS state FROM table GROUP BY RegionID)
```

## References

* [ClickHouse]
* [GitHub Repository]
* [Revision History]
* [Git]

[aggregate function]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/ 
[AggregateFunction]: https://clickhouse.com/docs/en/sql-reference/data-types/aggregatefunction
[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/aggregate_function_type/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/aggregate_function_type/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
""",
)
