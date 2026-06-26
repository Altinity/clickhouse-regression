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
