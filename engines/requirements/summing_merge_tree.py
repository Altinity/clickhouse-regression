# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_046_ClickHouse_SummingMergeTree_ZeroRowDeletion_Update = Requirement(
    name='RQ.SRS-046.ClickHouse.SummingMergeTree.ZeroRowDeletion.Update',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[SummingMergeTree] SHALL delete a row whose summing columns have been set to zero\n'
        'via `ALTER TABLE ... UPDATE` after `OPTIMIZE TABLE ... FINAL`.\n'
        '\n'
    ),
    link=None,
    level=2,
    num='4.1'
)

RQ_SRS_046_ClickHouse_SummingMergeTree_ZeroRowDeletion_ClearColumn = Requirement(
    name='RQ.SRS-046.ClickHouse.SummingMergeTree.ZeroRowDeletion.ClearColumn',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[SummingMergeTree] SHALL delete a row whose summing columns have been zeroed via\n'
        '`ALTER TABLE ... CLEAR COLUMN ... IN PARTITION ...` after `OPTIMIZE TABLE ... FINAL`,\n'
        'equivalently to the row being zeroed via `ALTER TABLE ... UPDATE`.\n'
        '\n'
    ),
    link=None,
    level=2,
    num='4.2'
)

RQ_SRS_046_ClickHouse_SummingMergeTree_ClearColumn_Consistency = Requirement(
    name='RQ.SRS-046.ClickHouse.SummingMergeTree.ClearColumn.Consistency',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[SummingMergeTree] SHALL apply the same `ALTER TABLE ... CLEAR COLUMN ... IN\n'
        'PARTITION ...` validation regardless of whether `columns_to_sum` was declared\n'
        'explicitly (`SummingMergeTree(c)`) or auto-detected (`SummingMergeTree`).\n'
        '\n'
        '\n'
    ),
    link=None,
    level=2,
    num='4.3'
)

SRS_046_ClickHouse_SummingMergeTree = Specification(
    name='SRS-046 ClickHouse SummingMergeTree',
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
        Heading(name='Related Resources', level=1, num='2'),
        Heading(name='Terminology', level=1, num='3'),
        Heading(name='SRS', level=3, num='3.0.1'),
        Heading(name='Requirements', level=1, num='4'),
        Heading(name='RQ.SRS-046.ClickHouse.SummingMergeTree.ZeroRowDeletion.Update', level=2, num='4.1'),
        Heading(name='RQ.SRS-046.ClickHouse.SummingMergeTree.ZeroRowDeletion.ClearColumn', level=2, num='4.2'),
        Heading(name='RQ.SRS-046.ClickHouse.SummingMergeTree.ClearColumn.Consistency', level=2, num='4.3'),
        Heading(name='References', level=1, num='5'),
        ),
    requirements=(
        RQ_SRS_046_ClickHouse_SummingMergeTree_ZeroRowDeletion_Update,
        RQ_SRS_046_ClickHouse_SummingMergeTree_ZeroRowDeletion_ClearColumn,
        RQ_SRS_046_ClickHouse_SummingMergeTree_ClearColumn_Consistency,
        ),
    content=r'''
# SRS-046 ClickHouse SummingMergeTree
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Related Resources](#related-resources)
* 3 [Terminology](#terminology)
* 4 [Requirements](#requirements)
  * 4.1 [RQ.SRS-046.ClickHouse.SummingMergeTree.ZeroRowDeletion.Update](#rqsrs-046clickhousesummingmergetreezerorowdeletionupdate)
  * 4.2 [RQ.SRS-046.ClickHouse.SummingMergeTree.ZeroRowDeletion.ClearColumn](#rqsrs-046clickhousesummingmergetreezerorowdeletionclearcolumn)
  * 4.3 [RQ.SRS-046.ClickHouse.SummingMergeTree.ClearColumn.Consistency](#rqsrs-046clickhousesummingmergetreeclearcolumnconsistency)


## Introduction

This software requirements specification covers requirements related to the
[ClickHouse] [SummingMergeTree] engine, specifically zero-row deletion after merges
and the consistency of `ALTER TABLE ... CLEAR COLUMN` validation between explicit
and auto-detected `columns_to_sum`.


## Related Resources

* https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/summingmergetree
* https://github.com/ClickHouse/ClickHouse/issues/101953
* https://github.com/ClickHouse/ClickHouse/pull/83892


## Terminology

#### SRS

Software Requirements Specification


## Requirements

### RQ.SRS-046.ClickHouse.SummingMergeTree.ZeroRowDeletion.Update
version: 1.0

[SummingMergeTree] SHALL delete a row whose summing columns have been set to zero
via `ALTER TABLE ... UPDATE` after `OPTIMIZE TABLE ... FINAL`.

### RQ.SRS-046.ClickHouse.SummingMergeTree.ZeroRowDeletion.ClearColumn
version: 1.0

[SummingMergeTree] SHALL delete a row whose summing columns have been zeroed via
`ALTER TABLE ... CLEAR COLUMN ... IN PARTITION ...` after `OPTIMIZE TABLE ... FINAL`,
equivalently to the row being zeroed via `ALTER TABLE ... UPDATE`.

### RQ.SRS-046.ClickHouse.SummingMergeTree.ClearColumn.Consistency
version: 1.0

[SummingMergeTree] SHALL apply the same `ALTER TABLE ... CLEAR COLUMN ... IN
PARTITION ...` validation regardless of whether `columns_to_sum` was declared
explicitly (`SummingMergeTree(c)`) or auto-detected (`SummingMergeTree`).


## References

[SRS]: #srs
[ClickHouse]: https://clickhouse.com
[SummingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/summingmergetree/
'''
)
