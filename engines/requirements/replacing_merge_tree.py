# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230125.1024636.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_035_ClickHouse_ReplacingMergeTree = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support [ReplacingMergeTree] engine which allows insertion of duplicates by adding an extra\n'
        'is_deleted column (possible values: 0 / 1) to the ReplacingMergeTree. The is_deleted column is optional, but if enabled, the version \n'
        'column becomes mandatory. \n'
        '\n'
    ),
    link=None,
    level=2,
    num='4.1'
)

RQ_SRS_035_ClickHouse_ReplicatedReplacingMergeTree = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplicatedReplacingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support [ReplicatedReplacingMergeTree] engine which allows same functions as new [ReplacingMergeTree]\n'
        'but on cluster environment. \n'
        '\n'
    ),
    link=None,
    level=2,
    num='4.2'
)

RQ_SRS_035_ClickHouse_ReplicatedReplacingMergeTree_Distributed = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplicatedReplacingMergeTree.Distributed',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support connection of [Distributed] engine table to new [ReplicatedReplacingMergeTree],\n'
        '\n'
    ),
    link=None,
    level=2,
    num='4.3'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_OldReplacingMergeTree = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.OldReplacingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] new engine version SHALL support all old [ReplacingMergeTree] possibilities.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_General = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.General',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support [ReplacingMergeTree] engine which allows to  remove duplicate entries with the same sorting \n'
        'key value (`ORDER BY` table section, not `PRIMARY KEY`) during a merge process. The deduplication occurs only during a \n'
        'merge, which occurs in the background at an unknown time, and the system cannot be planned for. \n'
        'However, the `OPTIMIZE` query can be used to run an unscheduled merge.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.2'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_VersionColumn = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionColumn',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL support a version column with a type of UInt*, Date, DateTime, or DateTime64.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.6'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_SelectionOfRows = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionOfRows',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL support merging, the engine must leave only one row from all the rows with the same \n'
        'sorting key. \n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.7'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_SelectionRules = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionRules',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL support selection rules: if a version column is specified, the engine must select the \n'
        'row with the maximum version. If no version column is specified, the engine must select the last row in the selection.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.8'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_TableCreation = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.TableCreation',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL support same clauses as when creating a MergeTree table, with the addition of the \n'
        'ver column.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.9'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_CollapsingMergeTree = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.CollapsingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] new engine version SHALL support all [CollapsingMergeTree] possibilities.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_DuplicateInsertions = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.DuplicateInsertions',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL allow duplicate insertions of rows.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_Update = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Update',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL allow updating a row by inserting a row with (arbitrary) greater version. \n'
        'The replacing merge algorithm collapses all rows with the same key into one row with the greatest version.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_Update_Distributed = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Update.Distributed',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL allow updating a row by inserting a row with (arbitrary) greater version for \n'
        '[Distributed] table on it. The replacing merge algorithm collapses all rows with the same key into one row with the greatest version.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.6.1.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_Delete = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Delete',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL allow deleting a row by inserting a row with (arbitrary) greater version and\n'
        '0 is_deleted parameter. The replacing merge algorithm leaves only one row with is_deleted = 0, and then it is filtered\n'
        'out.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.7.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_DeleteDisabled = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.DeleteDisabled',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL not allow deleting a row if `is_deleted` parameter is not provided.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.7.2'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_UpdateKeyColumns = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.UpdateKeyColumns',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL allow updating key columns by deleting a row and inserting a new one.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.8.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_RemoveDuplicates = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.RemoveDuplicates',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL allow removing duplicates by using the "Replacing" merge algorithm.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.9.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_BackwardCompatibility = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.BackwardCompatibility',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL allow backward compatible with previous versions of the [ReplacingMergeTree].\n'
        'This means that it should be an option when creating a table.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.10.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_VersionNumber = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionNumber',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL increase version no matter what the operation on the data was made. If two \n'
        'inserted rows have the same version number, the last inserted one is the one kept.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.11.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_Settings_CleanDeletedRows = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Settings.CleanDeletedRows',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ReplacingMergeTree] engine SHALL support `clean_deleted_rows` (possible values: 'Never' / 'Always') which allows \n"
        'to apply deletes without `FINAL` after merge operation (manually: `OPTIMIZE TABLE tble_name FINAL`) to all `SELECT` \n'
        'queries.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.12.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_Settings_CleanDeletedRowsDisabled = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Settings.CleanDeletedRowsDisabled',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL not support `clean_deleted_rows` if `is_deleted` parameter is not provided.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.12.2'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_HandlingDeletedData = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.HandlingDeletedData',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL allow filter out deleted data when queried but not remove it from disk.\n'
        'The information of deleted data is needed for KPIs.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.13.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_Errors_WrongDataType = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Errors.WrongDataType',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL provide exception:\n'
        '\n'
        '```CMD\n'
        'Code: 169. DB::Exception: Received from localhost:9000. DB::Exception: is_deleted column (is_deleted) for \n'
        'storage ReplacingMergeTree must have type UInt8. Provided column of type String.. (BAD_TYPE_OF_FIELD)\n'
        '```\n'
        '\n'
        'when wrong data type was used for `is_deleted` column.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.14.1'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_Errors_WrongDataValue = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Errors.WrongDataValue',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL provide exception:\n'
        '\n'
        '```CMD\n'
        'Code: 117. DB::Exception: Received from localhost:9000. DB::Exception: Incorrect data: is_deleted = 6 (must be 1 or 0)..\n'
        ' (INCORRECT_DATA)\n'
        '```\n'
        '\n'
        'when other than 0 or 1 value was used in `is_deleted` column.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.14.2'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_NonFunctionalRequirements_Performance = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Performance',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL allow handle large volumes of data efficiently.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.15.2.2'
)

RQ_SRS_035_ClickHouse_ReplacingMergeTree_NonFunctionalRequirements_Reliability = Requirement(
    name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Reliability',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL be reliable and not lose any data.\n'
        '\n'
        '\n'
        '\n'
        '[SRS]: #srs\n'
        '[ClickHouse]: https://clickhouse.com\n'
        '[Distributed]: https://clickhouse.com/docs/en/engines/table-engines/special/distributed\n'
        '[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree/\n'
        '[ReplicatedReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replication\n'
        '[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.15.2.4'
)

SRS035_ClickHouse_ReplacingMergeTree = Specification(
    name='SRS035 ClickHouse ReplacingMergeTree',
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
        Heading(name='Requirements', level=1, num='4'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree', level=2, num='4.1'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplicatedReplacingMergeTree', level=2, num='4.2'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplicatedReplacingMergeTree.Distributed', level=2, num='4.3'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.OldReplacingMergeTree', level=3, num='4.3.1'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.General', level=3, num='4.3.2'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.DataDeduplication', level=3, num='4.3.3'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.OptimizeMerge', level=3, num='4.3.4'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.UniquenessOfRows', level=3, num='4.3.5'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionColumn', level=3, num='4.3.6'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionOfRows', level=3, num='4.3.7'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionRules', level=3, num='4.3.8'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.TableCreation', level=3, num='4.3.9'),
        Heading(name='CollapsingMergeTree', level=2, num='4.4'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.CollapsingMergeTree', level=3, num='4.4.1'),
        Heading(name='Duplicate Insertions', level=2, num='4.5'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.DuplicateInsertions', level=3, num='4.5.1'),
        Heading(name='Update', level=2, num='4.6'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Update', level=3, num='4.6.1'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Update.Distributed', level=4, num='4.6.1.1'),
        Heading(name='Delete', level=2, num='4.7'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Delete', level=3, num='4.7.1'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.DeleteDisabled', level=3, num='4.7.2'),
        Heading(name='Update Key Columns', level=2, num='4.8'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.UpdateKeyColumns', level=3, num='4.8.1'),
        Heading(name='Remove Duplicates', level=2, num='4.9'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.RemoveDuplicates', level=3, num='4.9.1'),
        Heading(name='Backward Compatibility', level=2, num='4.10'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.BackwardCompatibility', level=3, num='4.10.1'),
        Heading(name='Version Number', level=2, num='4.11'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionNumber', level=3, num='4.11.1'),
        Heading(name='Settings', level=2, num='4.12'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Settings.CleanDeletedRows', level=3, num='4.12.1'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Settings.CleanDeletedRowsDisabled', level=3, num='4.12.2'),
        Heading(name='Handling Deleted Data', level=2, num='4.13'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.HandlingDeletedData', level=3, num='4.13.1'),
        Heading(name='Errors', level=2, num='4.14'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Errors.WrongDataType', level=3, num='4.14.1'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.Errors.WrongDataValue', level=3, num='4.14.2'),
        Heading(name='Non-Functional Requirements', level=2, num='4.15'),
        Heading(name='Performance', level=4, num='4.15.2.1'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Performance', level=4, num='4.15.2.2'),
        Heading(name='Reliability', level=4, num='4.15.2.3'),
        Heading(name='RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Reliability', level=4, num='4.15.2.4'),
        ),
    requirements=(
        RQ_SRS_035_ClickHouse_ReplacingMergeTree,
        RQ_SRS_035_ClickHouse_ReplicatedReplacingMergeTree,
        RQ_SRS_035_ClickHouse_ReplicatedReplacingMergeTree_Distributed,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_OldReplacingMergeTree,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_General,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_VersionColumn,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_SelectionOfRows,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_SelectionRules,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_TableCreation,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_CollapsingMergeTree,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_DuplicateInsertions,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_Update,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_Update_Distributed,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_Delete,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_DeleteDisabled,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_UpdateKeyColumns,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_RemoveDuplicates,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_BackwardCompatibility,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_VersionNumber,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_Settings_CleanDeletedRows,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_Settings_CleanDeletedRowsDisabled,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_HandlingDeletedData,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_Errors_WrongDataType,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_Errors_WrongDataValue,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_NonFunctionalRequirements_Performance,
        RQ_SRS_035_ClickHouse_ReplacingMergeTree_NonFunctionalRequirements_Reliability,
        ),
    content='''
# SRS035 ClickHouse ReplacingMergeTree
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Related Resources](#related-resources)
* 3 [Terminology](#terminology)
* 4 [Requirements](#requirements)
  * 4.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree](#rqsrs-035clickhousereplacingmergetree)
  * 4.2 [RQ.SRS-035.ClickHouse.ReplicatedReplacingMergeTree](#rqsrs-035clickhousereplicatedreplacingmergetree)
  * 4.3 [RQ.SRS-035.ClickHouse.ReplicatedReplacingMergeTree.Distributed](#rqsrs-035clickhousereplicatedreplacingmergetreedistributed)
    * 4.3.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.OldReplacingMergeTree](#rqsrs-035clickhousereplacingmergetreeoldreplacingmergetree)
    * 4.3.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.General](#rqsrs-035clickhousereplacingmergetreegeneral)
    * 4.3.3 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.DataDeduplication](#rqsrs-035clickhousereplacingmergetreedatadeduplication)
    * 4.3.4 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.OptimizeMerge](#rqsrs-035clickhousereplacingmergetreeoptimizemerge)
    * 4.3.5 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.UniquenessOfRows](#rqsrs-035clickhousereplacingmergetreeuniquenessofrows)
    * 4.3.6 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionColumn](#rqsrs-035clickhousereplacingmergetreeversioncolumn)
    * 4.3.7 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionOfRows](#rqsrs-035clickhousereplacingmergetreeselectionofrows)
    * 4.3.8 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionRules](#rqsrs-035clickhousereplacingmergetreeselectionrules)
    * 4.3.9 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.TableCreation](#rqsrs-035clickhousereplacingmergetreetablecreation)
  * 4.4 [CollapsingMergeTree](#collapsingmergetree)
    * 4.4.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.CollapsingMergeTree](#rqsrs-035clickhousereplacingmergetreecollapsingmergetree)
  * 4.5 [Duplicate Insertions](#duplicate-insertions)
    * 4.5.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.DuplicateInsertions](#rqsrs-035clickhousereplacingmergetreeduplicateinsertions)
  * 4.6 [Update](#update)
    * 4.6.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Update](#rqsrs-035clickhousereplacingmergetreeupdate)
      * 4.6.1.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Update.Distributed](#rqsrs-035clickhousereplacingmergetreeupdatedistributed)
  * 4.7 [Delete](#delete)
    * 4.7.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Delete](#rqsrs-035clickhousereplacingmergetreedelete)
    * 4.7.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.DeleteDisabled](#rqsrs-035clickhousereplacingmergetreedeletedisabled)
  * 4.8 [Update Key Columns](#update-key-columns)
    * 4.8.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.UpdateKeyColumns](#rqsrs-035clickhousereplacingmergetreeupdatekeycolumns)
  * 4.9 [Remove Duplicates](#remove-duplicates)
    * 4.9.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.RemoveDuplicates](#rqsrs-035clickhousereplacingmergetreeremoveduplicates)
  * 4.10 [Backward Compatibility](#backward-compatibility)
    * 4.10.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.BackwardCompatibility](#rqsrs-035clickhousereplacingmergetreebackwardcompatibility)
  * 4.11 [Version Number](#version-number)
    * 4.11.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionNumber](#rqsrs-035clickhousereplacingmergetreeversionnumber)
  * 4.12 [Settings](#settings)
    * 4.12.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Settings.CleanDeletedRows](#rqsrs-035clickhousereplacingmergetreesettingscleandeletedrows)
    * 4.12.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Settings.CleanDeletedRowsDisabled](#rqsrs-035clickhousereplacingmergetreesettingscleandeletedrowsdisabled)
  * 4.13 [Handling Deleted Data](#handling-deleted-data)
    * 4.13.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.HandlingDeletedData](#rqsrs-035clickhousereplacingmergetreehandlingdeleteddata)
  * 4.14 [Errors](#errors)
    * 4.14.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Errors.WrongDataType](#rqsrs-035clickhousereplacingmergetreeerrorswrongdatatype)
    * 4.14.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Errors.WrongDataValue](#rqsrs-035clickhousereplacingmergetreeerrorswrongdatavalue)
  * 4.15 [Non-Functional Requirements](#non-functional-requirements)
      * 4.15.2.1 [Performance](#performance)
      * 4.15.2.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Performance](#rqsrs-035clickhousereplacingmergetreenonfunctionalrequirementsperformance)
      * 4.15.2.3 [Reliability](#reliability)
      * 4.15.2.4 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Reliability](#rqsrs-035clickhousereplacingmergetreenonfunctionalrequirementsreliability)


## Introduction

This software requirements specification covers requirements related to [ClickHouse] support from 23.2 new
[ReplacingMergeTree] which allows for duplicate insertions and combines the capabilities of 
[ReplacingMergeTree] and [CollapsingMergeTree].

[ReplacingMergeTree] is designed to remove duplicate entries with the same sorting key value (ORDER BY table section,
not PRIMARY KEY) and is suitable for clearing out duplicate data in the background in order to save space. 
However, it does not guarantee the absence of duplicates.


## Related Resources

**Pull Requests**

* https://github.com/ClickHouse/ClickHouse/pull/41005
* https://kb.altinity.com/engines/mergetree-table-engine-family/replacingmergetree/

## Terminology

####SRS

Software Requirements Specification

## Requirements

### RQ.SRS-035.ClickHouse.ReplacingMergeTree
version: 1.0

[ClickHouse] SHALL support [ReplacingMergeTree] engine which allows insertion of duplicates by adding an extra
is_deleted column (possible values: 0 / 1) to the ReplacingMergeTree. The is_deleted column is optional, but if enabled, the version 
column becomes mandatory. 

### RQ.SRS-035.ClickHouse.ReplicatedReplacingMergeTree
version: 1.0

[ClickHouse] SHALL support [ReplicatedReplacingMergeTree] engine which allows same functions as new [ReplacingMergeTree]
but on cluster environment. 

### RQ.SRS-035.ClickHouse.ReplicatedReplacingMergeTree.Distributed
version: 1.0

[ClickHouse] SHALL support connection of [Distributed] engine table to new [ReplicatedReplacingMergeTree],

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.OldReplacingMergeTree
version: 1.0

[ReplacingMergeTree] new engine version SHALL support all old [ReplacingMergeTree] possibilities.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.General
version: 1.0

[ClickHouse] SHALL support [ReplacingMergeTree] engine which allows to  remove duplicate entries with the same sorting 
key value (`ORDER BY` table section, not `PRIMARY KEY`) during a merge process. The deduplication occurs only during a 
merge, which occurs in the background at an unknown time, and the system cannot be planned for. 
However, the `OPTIMIZE` query can be used to run an unscheduled merge.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.DataDeduplication

[ReplacingMergeTree] engine SHALL support remove duplicate entries with the same sorting key value during a 
merge process.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.OptimizeMerge

[ReplacingMergeTree] engine SHALL support `OPTIMIZE` query which can be used to run an unscheduled merge as merge process 
must occur in the background at an unknown time, and the system cannot be planned for.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.UniquenessOfRows

[ReplacingMergeTree] engine SHALL support uniqueness of rows determined by the `ORDER BY` table section, 
not PRIMARY KEY.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionColumn
version: 1.0

[ReplacingMergeTree] engine SHALL support a version column with a type of UInt*, Date, DateTime, or DateTime64.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionOfRows
version: 1.0

[ReplacingMergeTree] engine SHALL support merging, the engine must leave only one row from all the rows with the same 
sorting key. 

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionRules
version: 1.0

[ReplacingMergeTree] engine SHALL support selection rules: if a version column is specified, the engine must select the 
row with the maximum version. If no version column is specified, the engine must select the last row in the selection.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.TableCreation
version: 1.0

[ReplacingMergeTree] engine SHALL support same clauses as when creating a MergeTree table, with the addition of the 
ver column.

### CollapsingMergeTree

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.CollapsingMergeTree
version: 1.0

[ReplacingMergeTree] new engine version SHALL support all [CollapsingMergeTree] possibilities.

### Duplicate Insertions

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.DuplicateInsertions
version: 1.0

[ReplacingMergeTree] engine SHALL allow duplicate insertions of rows.

### Update

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Update
version: 1.0

[ReplacingMergeTree] engine SHALL allow updating a row by inserting a row with (arbitrary) greater version. 
The replacing merge algorithm collapses all rows with the same key into one row with the greatest version.


##### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Update.Distributed
version: 1.0

[ReplacingMergeTree] engine SHALL allow updating a row by inserting a row with (arbitrary) greater version for 
[Distributed] table on it. The replacing merge algorithm collapses all rows with the same key into one row with the greatest version.

### Delete

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Delete
version: 1.0

[ReplacingMergeTree] engine SHALL allow deleting a row by inserting a row with (arbitrary) greater version and
0 is_deleted parameter. The replacing merge algorithm leaves only one row with is_deleted = 0, and then it is filtered
out.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.DeleteDisabled
version: 1.0

[ReplacingMergeTree] engine SHALL not allow deleting a row if `is_deleted` parameter is not provided.

### Update Key Columns

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.UpdateKeyColumns
version: 1.0

[ReplacingMergeTree] engine SHALL allow updating key columns by deleting a row and inserting a new one.

### Remove Duplicates

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.RemoveDuplicates
version: 1.0

[ReplacingMergeTree] engine SHALL allow removing duplicates by using the "Replacing" merge algorithm.

### Backward Compatibility

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.BackwardCompatibility
version: 1.0

[ReplacingMergeTree] engine SHALL allow backward compatible with previous versions of the [ReplacingMergeTree].
This means that it should be an option when creating a table.

### Version Number

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionNumber
version: 1.0

[ReplacingMergeTree] engine SHALL increase version no matter what the operation on the data was made. If two 
inserted rows have the same version number, the last inserted one is the one kept.

### Settings

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Settings.CleanDeletedRows
version: 1.0

[ReplacingMergeTree] engine SHALL support `clean_deleted_rows` (possible values: 'Never' / 'Always') which allows 
to apply deletes without `FINAL` after merge operation (manually: `OPTIMIZE TABLE tble_name FINAL`) to all `SELECT` 
queries.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Settings.CleanDeletedRowsDisabled
version: 1.0

[ReplacingMergeTree] engine SHALL not support `clean_deleted_rows` if `is_deleted` parameter is not provided.


### Handling Deleted Data

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.HandlingDeletedData
version: 1.0

[ReplacingMergeTree] engine SHALL allow filter out deleted data when queried but not remove it from disk.
The information of deleted data is needed for KPIs.

### Errors

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Errors.WrongDataType
version: 1.0

[ReplacingMergeTree] engine SHALL provide exception:

```CMD
Code: 169. DB::Exception: Received from localhost:9000. DB::Exception: is_deleted column (is_deleted) for 
storage ReplacingMergeTree must have type UInt8. Provided column of type String.. (BAD_TYPE_OF_FIELD)
```

when wrong data type was used for `is_deleted` column.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Errors.WrongDataValue
version: 1.0

[ReplacingMergeTree] engine SHALL provide exception:

```CMD
Code: 117. DB::Exception: Received from localhost:9000. DB::Exception: Incorrect data: is_deleted = 6 (must be 1 or 0)..
 (INCORRECT_DATA)
```

when other than 0 or 1 value was used in `is_deleted` column.

### Non-Functional Requirements

##### Performance

##### RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Performance
version: 1.0

[ReplacingMergeTree] engine SHALL allow handle large volumes of data efficiently.

##### Reliability

##### RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Reliability
version: 1.0

[ReplacingMergeTree] engine SHALL be reliable and not lose any data.



[SRS]: #srs
[ClickHouse]: https://clickhouse.com
[Distributed]: https://clickhouse.com/docs/en/engines/table-engines/special/distributed
[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree/
[ReplicatedReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replication
[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/
'''
)
