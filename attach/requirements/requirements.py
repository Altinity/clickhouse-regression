# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.240111.1210833.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_039_ClickHouse_Attach_AttachExistingTable = Requirement(
    name="RQ.SRS-039.ClickHouse.Attach.AttachExistingTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [ATTACH TABLE] statement to attach an existing table.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.1.1",
)

RQ_SRS_039_ClickHouse_Attach_CreateNewTableAndAttach_DataWithUUID = Requirement(
    name="RQ.SRS-039.ClickHouse.Attach.CreateNewTableAndAttach.DataWithUUID",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [ATTACH TABLE UUID] statement to create a new table and attach data with specified table UUID.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.2.1",
)

RQ_SRS_039_ClickHouse_Attach_AttachExistingDictionary = Requirement(
    name="RQ.SRS-039.ClickHouse.Attach.AttachExistingDictionary",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [ATTACH DICTIONARY] statement to attach an existing dictionary.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.1",
)

RQ_SRS_039_ClickHouse_Attach_AttachExistingDatabase = Requirement(
    name="RQ.SRS-039.ClickHouse.Attach.AttachExistingDatabase",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [ATTACH DATABASE] statement to attach previously detached database.[]\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.4.1",
)

SRS_039_ClickHouse_Attach_Statement = Specification(
    name="SRS-039 ClickHouse Attach Statement",
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
        Heading(name="Attach Existing Table", level=2, num="3.1"),
        Heading(
            name="RQ.SRS-039.ClickHouse.Attach.AttachExistingTable",
            level=3,
            num="3.1.1",
        ),
        Heading(name="Create New Table And Attach Data", level=2, num="3.2"),
        Heading(name="With Specified Path to Table Data", level=3, num="3.2.1"),
        Heading(
            name="SR.SRS-039.ClickHouse.Attach.CreateNewTableAndAttach.DataWithPath",
            level=4,
            num="3.2.1.1",
        ),
        Heading(name="With Specified Table UUID", level=3, num="3.2.2"),
        Heading(
            name="RQ.SRS-039.ClickHouse.Attach.CreateNewTableAndAttach.DataWithUUID",
            level=4,
            num="3.2.2.1",
        ),
        Heading(name="Attach Existing Dictionary", level=2, num="3.3"),
        Heading(
            name="RQ.SRS-039.ClickHouse.Attach.AttachExistingDictionary",
            level=3,
            num="3.3.1",
        ),
        Heading(name="Attach Existing Database", level=2, num="3.4"),
        Heading(
            name="RQ.SRS-039.ClickHouse.Attach.AttachExistingDatabase",
            level=3,
            num="3.4.1",
        ),
        Heading(name="Attach Replicated Tables", level=2, num="3.5"),
        Heading(
            name="RQ.SRS-039.ClickHouse.ReplicaPath.AttachTable", level=2, num="3.6"
        ),
        Heading(name="References", level=1, num="4"),
    ),
    requirements=(
        RQ_SRS_039_ClickHouse_Attach_AttachExistingTable,
        RQ_SRS_039_ClickHouse_Attach_CreateNewTableAndAttach_DataWithUUID,
        RQ_SRS_039_ClickHouse_Attach_AttachExistingDictionary,
        RQ_SRS_039_ClickHouse_Attach_AttachExistingDatabase,
    ),
    content="""
# SRS-039 ClickHouse Attach Statement
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Requirements](#requirements)
    * 3.1 [Attach Existing Table](#attach-existing-table)
        * 3.1.1 [RQ.SRS-039.ClickHouse.Attach.AttachExistingTable](#rqsrs-039clickhouseattachattachexistingtable)
    * 3.2 [Create New Table And Attach Data](#create-new-table-and-attach-data)
        * 3.2.1 [With Specified Path to Table Data](#with-specified-path-to-table-data)
            * 3.2.1.1 [SR.SRS-039.ClickHouse.Attach.CreateNewTableAndAttach.DataWithPath](#srsrs-039clickhouseattachcreatenewtableandattachdatawithpath)
        * 3.2.2 [With Specified Table UUID](#with-specified-table-uuid)
            * 3.2.2.1 [RQ.SRS-039.ClickHouse.Attach.CreateNewTableAndAttach.DataWithUUID](#rqsrs-039clickhouseattachcreatenewtableandattachdatawithuuid)
    * 3.3 [Attach Existing Dictionary](#attach-existing-dictionary)
        * 3.3.1 [RQ.SRS-039.ClickHouse.Attach.AttachExistingDictionary](#rqsrs-039clickhouseattachattachexistingdictionary)
    * 3.4 [Attach Existing Database](#attach-existing-database)
        * 3.4.1 [RQ.SRS-039.ClickHouse.Attach.AttachExistingDatabase](#rqsrs-039clickhouseattachattachexistingdatabase)
    * 3.5 [Attach Replicated Tables](#attach-replicated-tables)
    * 3.6 [RQ.SRS-039.ClickHouse.ReplicaPath.AttachTable](#rqsrs-039clickhousereplicapathattachtable)
* 4 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for [attach] statement in [ClickHouse].

**ATTACH Statement** attaches a table or a dictionary, for example, when moving a database to another server.

**Syntax:**  
```sql
ATTACH TABLE|DICTIONARY|DATABASE [IF NOT EXISTS] [db.]name [ON CLUSTER cluster] ...
``` 
The query does not create data on the disk, but assumes that data is already in the appropriate places, and just adds information about the specified table, dictionary or database to the server. After executing the ATTACH query, the server will know about the existence of the table, dictionary or database.

If a table was previously detached (DETACH query), meaning that its structure is known, you can use shorthand without defining the structure.

## Requirements

### Attach Existing Table

**Syntax:**  
```sql
ATTACH TABLE [IF NOT EXISTS] [db.]name [ON CLUSTER cluster]
```

This query is used when starting the server. The server stores table metadata as files with ATTACH queries, which it simply runs at launch (with the exception of some system tables, which are explicitly created on the server).

If the table was detached permanently, it won't be reattached at the server start, so you need to use ATTACH query explicitly.

#### RQ.SRS-039.ClickHouse.Attach.AttachExistingTable
version: 1.0

[ClickHouse] SHALL support [ATTACH TABLE] statement to attach an existing table.

### Create New Table And Attach Data

#### With Specified Path to Table Data

The query creates a new table with provided structure and attaches table data from the provided directory in `user_files`.

**Syntax:**
```sql
ATTACH TABLE name FROM 'path/to/data/' (col1 Type1, ...)
```

Example:  
```sql
DROP TABLE IF EXISTS test;
INSERT INTO TABLE FUNCTION file('01188_attach/test/data.TSV', 'TSV', 's String, n UInt8') VALUES ('test', 42);
ATTACH TABLE test FROM '01188_attach/test' (s String, n UInt8) ENGINE = File(TSV);
SELECT * FROM test;
```
Result:  
```
┌─s────┬──n─┐
│ test │ 42 │
└──────┴────┘
```

##### SR.SRS-039.ClickHouse.Attach.CreateNewTableAndAttach.DataWithPath
version: 1.0

[ClickHouse] SHALL support [ATTACH TABLE FROM] statement to create a new table and attach data with specified path to table data.

#### With Specified Table UUID

This query creates a new table with provided structure and attaches data from the table with the specified UUID. It is supported by the Atomic database engine.

**Syntax:**
```sql
ATTACH TABLE name UUID '<uuid>' (col1 Type1, ...)
```

##### RQ.SRS-039.ClickHouse.Attach.CreateNewTableAndAttach.DataWithUUID
version: 1.0

[ClickHouse] SHALL support [ATTACH TABLE UUID] statement to create a new table and attach data with specified table UUID.

### Attach Existing Dictionary
Attaches a previously detached dictionary.

**Syntax:**  
```sql
ATTACH DICTIONARY [IF NOT EXISTS] [db.]name [ON CLUSTER cluster]
```

#### RQ.SRS-039.ClickHouse.Attach.AttachExistingDictionary
version: 1.0
[ClickHouse] SHALL support [ATTACH DICTIONARY] statement to attach an existing dictionary.

### Attach Existing Database
Attaches a previously detached database.  
**Syntax:**  
```sql
ATTACH DATABASE [IF NOT EXISTS] name [ENGINE=<database engine>] [ON CLUSTER cluster]
```

#### RQ.SRS-039.ClickHouse.Attach.AttachExistingDatabase
version: 1.0
[ClickHouse] SHALL support [ATTACH DATABASE] statement to attach previously detached database.[]

### Attach Replicated Tables

Possible table engines:
- ReplicatedMergeTree
- ReplicatedReplacingMergeTree
- ReplicatedAggregatingMergeTree
- ReplicatedGraphiteMergeTree
- ReplicatedSummingMergeTree
- ReplicatedCollapsingMergeTree
- ReplicatedVersionedCollapsingMergeTree

### RQ.SRS-039.ClickHouse.ReplicaPath.AttachTable
version 1.0  

[ClickHouse] SHALL not allow attach table with path that is already active.

## References

* [Git]
* [GitHub Repository]
* [Revision History]
* [attach]
* [ClickHouse]


[Git]: https://git-scm.com/
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/attach/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/attach/requirements/requirements.md
[attach]: https://clickhouse.com/docs/en/sql-reference/statements/attach/
[ClickHouse]: https://clickhouse.com
""",
)
