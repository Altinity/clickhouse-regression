# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230315.1003122.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_032_ClickHouse_Alter_ReplacePartition = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.ReplacePartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `REPLACE PARTITION`.\n" "\n"
    ),
    link=None,
    level=3,
    num="3.1.1",
)

RQ_SRS_032_ClickHouse_Alter_ReplacePartition_ReplaceData = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.ReplacePartition.ReplaceData",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the ability to add a new partition to a table, replacing an existing one.\n"
        "\n"
        "For example,\n"
        "\n"
        "This query copies the data partition from the `table1` to `table2` and replaces existing partition in the `table2`.\n"
        "\n"
        "```sql\n"
        "ALTER TABLE table2 [ON CLUSTER cluster] REPLACE PARTITION partition_expr FROM table1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.2",
)

RQ_SRS_032_ClickHouse_Alter_ReplacePartition_AddNewPartition_NewData = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.NewData",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support replace an existing partition with new data.\n"
        "\n"
        "For example,\n"
        "```sql\n"
        "ALTER TABLE my_table REPLACE PARTITION 202301 WITH ATTACH 'path_to_new_data';\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.3",
)

RQ_SRS_032_ClickHouse_Alter_ReplacePartition_AddNewPartition_KeepTable = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.KeepTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL keep the data of the table from which the partition is copied from.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.4",
)

RQ_SRS_032_ClickHouse_Alter_ReplacePartition_AddNewPartition_TemporaryTable = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.TemporaryTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support copying the data partition from the temporary table.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.5",
)

RQ_SRS_032_ClickHouse_Alter_ReplacePartition_AddNewPartition_Conditions = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.Conditions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `REPLACE PARTITION` when,\n"
        "\n"
        "* Both Table have the same structure.\n"
        "* Both tables have the same partition key, the same `ORDER BY` key and the same primary key.\n"
        "* Both tables must have the same storage policy.\n"
        "\n"
        "\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/alter/requirements/requirements.md\n"
        "[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/alter/requirements/requirements.md\n"
        "[Git]: https://git-scm.com/\n"
        "[GitHub]: https://github.com\n"
    ),
    link=None,
    level=3,
    num="3.1.6",
)

SRS032_ClickHouse_Alter_statement = Specification(
    name="SRS032 ClickHouse Alter statement",
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
        Heading(name="Working with ALTER statement", level=1, num="3"),
        Heading(name="REPLACE PARTITION", level=2, num="3.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.ReplacePartition", level=3, num="3.1.1"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.ReplacePartition.ReplaceData",
            level=3,
            num="3.1.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.NewData",
            level=3,
            num="3.1.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.KeepTable",
            level=3,
            num="3.1.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.TemporaryTable",
            level=3,
            num="3.1.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.Conditions",
            level=3,
            num="3.1.6",
        ),
    ),
    requirements=(
        RQ_SRS_032_ClickHouse_Alter_ReplacePartition,
        RQ_SRS_032_ClickHouse_Alter_ReplacePartition_ReplaceData,
        RQ_SRS_032_ClickHouse_Alter_ReplacePartition_AddNewPartition_NewData,
        RQ_SRS_032_ClickHouse_Alter_ReplacePartition_AddNewPartition_KeepTable,
        RQ_SRS_032_ClickHouse_Alter_ReplacePartition_AddNewPartition_TemporaryTable,
        RQ_SRS_032_ClickHouse_Alter_ReplacePartition_AddNewPartition_Conditions,
    ),
    content="""
# SRS032 ClickHouse Alter statement
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Working with ALTER statement](#working-with-alter-statement)
  * 3.1 [REPLACE PARTITION](#replace-partition)
    * 3.1.1 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition](#rqsrs-032clickhousealterreplacepartition)
    * 3.1.2 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.ReplaceData](#rqsrs-032clickhousealterreplacepartitionreplacedata)
    * 3.1.3 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.NewData](#rqsrs-032clickhousealterreplacepartitionaddnewpartitionnewdata)
    * 3.1.4 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.KeepTable](#rqsrs-032clickhousealterreplacepartitionaddnewpartitionkeeptable)
    * 3.1.5 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.TemporaryTable](#rqsrs-032clickhousealterreplacepartitionaddnewpartitiontemporarytable)
    * 3.1.6 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.Conditions](#rqsrs-032clickhousealterreplacepartitionaddnewpartitionconditions)


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `ALTER` statement in [ClickHouse].

The documentation used:
- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#replace-partition

## Working with ALTER statement

[ClickHouse] SHALL support the usage of the `ALTER` statement.

### REPLACE PARTITION

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION`.

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.ReplaceData
version: 1.0

[ClickHouse] SHALL support the ability to add a new partition to a table, replacing an existing one.

For example,

This query copies the data partition from the `table1` to `table2` and replaces existing partition in the `table2`.

```sql
ALTER TABLE table2 [ON CLUSTER cluster] REPLACE PARTITION partition_expr FROM table1
```

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.NewData
version: 1.0

[ClickHouse] SHALL support replace an existing partition with new data.

For example,
```sql
ALTER TABLE my_table REPLACE PARTITION 202301 WITH ATTACH 'path_to_new_data';
```

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.KeepTable
version: 1.0

[ClickHouse] SHALL keep the data of the table from which the partition is copied from.

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.TemporaryTable
version: 1.0

[ClickHouse] SHALL support copying the data partition from the temporary table.

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.Conditions
version: 1.0

[ClickHouse] SHALL support the usage of `REPLACE PARTITION` when,

* Both Table have the same structure.
* Both tables have the same partition key, the same `ORDER BY` key and the same primary key.
* Both tables must have the same storage policy.



[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/alter/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/alter/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
""",
)
