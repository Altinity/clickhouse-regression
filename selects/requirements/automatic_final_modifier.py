# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230125.1024636.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_032_ClickHouse_AutomaticFinalModifier = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support adding [FINAL modifier] clause automatically to all [SELECT] queries\n'
        'for all table engines that support [FINAL modifier] and return the same result as if [FINAL modifier] clause\n'
        'was specified in the [SELECT] query explicitly.\n'
        '\n'
    ),
    link=None,
    level=2,
    num='5.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableSchema_Alias = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableSchema.Alias',
    version='1.0',
    priority='1.0',
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for tables with ALIAS.\n'
        '\n'
        'For example,\n'
        '\n'
        '```sql\n'
        'CREATE TABLE IF NOT EXISTS \n'
        'table1(id Int32, x Int32, s Int32 ALIAS id + x)\n'
        'ENGINE = MergeTree ORDER BY tuple()\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.2.1.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_CreateStatement = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.CreateStatement',
    version='1.0',
    priority='1.0',
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `force_select_final` table engine setting to enable automatic [FINAL modifier]\n'
        'on all [SELECT] queries when the setting is value is set to `1`.\n'
        '\n'
        'For example,\n'
        '\n'
        '```sql\n'
        'CREATE TABLE table (...)\n'
        'Engine=ReplacingMergeTree\n'
        'SETTTING force_select_final=1\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.3.1.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_IgnoreOnNotSupportedTableEngines = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.IgnoreOnNotSupportedTableEngines',
    version='1.0',
    priority='1.0',
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL silently ignore `force_select_final` table engine setting for any table\n'
        "engine that doesn't support [FINAL modifier] clause.\n"
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.3.2.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_MergeTree = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for the following [MergeTree] table engines variants:\n'
        '\n'
        '* [ReplacingMergeTree]\n'
        '* ReplacingMergeTree(version)\n'
        '* [CollapsingMergeTree(sign)]\n'
        '* AggregatingMergeTree\n'
        '* SummingMergeTree\n'
        '* [VersionedCollapsingMergeTree(sign,version)]\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.4.1.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_ReplicatedMergeTree = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for the following replicated \n'
        '[ReplicatedMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replication) \n'
        'table engines variants:\n'
        '\n'
        '* ReplicatedReplacingMergeTree\n'
        '* ReplicatedReplacingMergeTree(version)\n'
        '* ReplicatedCollapsingMergeTree(sign)\n'
        '* ReplicatedAggregatingMergeTree\n'
        '* ReplicatedSummingMergeTree\n'
        '* ReplicatedVersionedCollapsingMergeTree(sign,version)\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.4.2.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_EnginesOverOtherEngines = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the following table engines over tables that have automatic [FINAL modifier] clause enabled:\n'
        '\n'
        '* [View](https://clickhouse.com/docs/en/engines/table-engines/special/view)\n'
        '* [Distributed](https://clickhouse.com/docs/en/engines/table-engines/special/distributed)\n'
        '* [MaterializedView](https://clickhouse.com/docs/en/engines/table-engines/special/materializedview)\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.4.3.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for any type of [SELECT] queries.\n'
        '\n'
        '```sql\n'
        '[WITH expr_list|(subquery)]\n'
        'SELECT [DISTINCT [ON (column1, column2, ...)]] expr_list\n'
        '[FROM [db.]table | (subquery) | table_function] [FINAL]\n'
        '[SAMPLE sample_coeff]\n'
        '[ARRAY JOIN ...]\n'
        '[GLOBAL] [ANY|ALL|ASOF] [INNER|LEFT|RIGHT|FULL|CROSS] [OUTER|SEMI|ANTI] JOIN (subquery)|table (ON <expr_list>)|(USING <column_list>)\n'
        '[PREWHERE expr]\n'
        '[WHERE expr]\n'
        '[GROUP BY expr_list] [WITH ROLLUP|WITH CUBE] [WITH TOTALS]\n'
        '[HAVING expr]\n'
        '[ORDER BY expr_list] [WITH FILL] [FROM expr] [TO expr] [STEP expr] [INTERPOLATE [(expr_list)]]\n'
        '[LIMIT [offset_value, ]n BY columns]\n'
        '[LIMIT [n, ]m] [WITH TIES]\n'
        '[SETTINGS ...]\n'
        '[UNION  ...]\n'
        '[INTO OUTFILE filename [COMPRESSION type [LEVEL level]] ]\n'
        '[FORMAT format]\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=3,
    num='5.5.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Select = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Select',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [SELECT] clause.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.2.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_As = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.As',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with columns changed with `as` clause.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.3.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Distinct = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Distinct',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [DISTINCT] clause.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.4.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Prewhere = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Prewhere',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [PREWHERE] clause.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.5.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Where = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Where',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [WHERE] clause.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.6.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_GroupBy = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.GroupBy',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [GROUP BY] clause.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.7.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_LimitBy = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.LimitBy',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [LIMIT BY] clause.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.8.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Limit = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Limit',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [LIMIT] clause.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.9.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_ArrayJoin = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.ArrayJoin',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [ARRAY JOIN] clause.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.10.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] in any subquery that reads from a table that\n'
        'has automatic [FINAL modifier] enabled.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.11.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_Nested = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.Nested',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] in any nested subquery that reads from a table that\n'
        'has automatic [FINAL modifier] enabled.\n'
        '\n'
    ),
    link=None,
    level=5,
    num='5.5.11.1.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_ExpressionInWhere = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.ExpressionInWhere',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] in any subquery as expression in `WHERE` clause that reads from a table that\n'
        'has automatic [FINAL modifier] enabled.\n'
        '\n'
    ),
    link=None,
    level=5,
    num='5.5.11.1.2'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_ExpressionInPrewhere = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.ExpressionInPrewhere',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] in any subquery as expression in `PREWHERE` clause that reads from a table that\n'
        'has automatic [FINAL modifier] enabled.\n'
        '\n'
    ),
    link=None,
    level=5,
    num='5.5.11.1.3'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_ExpressionInArrayJoin = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.ExpressionInArrayJoin',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] in any subquery as expression in `ARRAY JOIN` clause that reads from a table that\n'
        'has automatic [FINAL modifier] enabled.\n'
        '\n'
    ),
    link=None,
    level=5,
    num='5.5.11.1.4'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_INPrewhere = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.INPrewhere',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] in any subquery with `IN` clause in `PREWHERE` that reads from a table that\n'
        'has automatic [FINAL modifier] enabled.\n'
        '\n'
    ),
    link=None,
    level=5,
    num='5.5.11.1.5'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_INWhere = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.INWhere',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] in any subquery with `IN` clause in `WHERE` that reads from a table that\n'
        'has automatic [FINAL modifier] enabled.\n'
        '\n'
    ),
    link=None,
    level=5,
    num='5.5.11.1.6'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] for any table in [JOIN] clause for which\n'
        'the automatic [FINAL modifier] is enabled.\n'
        '\n'
        '* INNER JOIN\n'
        '* LEFT OUTER JOIN\n'
        '* RIGHT OUTER JOIN\n'
        '* FULL OUTER JOIN\n'
        '* CROSS JOIN\n'
        '* LEFT SEMI JOIN and RIGHT SEMI JOIN\n'
        '* LEFT ANTI JOIN and RIGHT ANTI JOIN\n'
        '* LEFT ANY JOIN, RIGHT ANY JOIN and INNER ANY JOIN\n'
        '* ASOF JOIN and LEFT ASOF JOIN\n'
        '\n'
        'For example,\n'
        '```sql\n'
        'select count() from lhs inner join rhs on lhs.x = rhs.x;\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.12.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join_Select = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join.Select',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] for any table in [JOIN] clause with [SELECT] subquery for which\n'
        'the automatic [FINAL modifier] is enabled.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.12.2'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join_Multiple = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join.Multiple',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] for any table in multiple [JOIN] clause for which\n'
        'the automatic [FINAL modifier] is enabled.\n'
        '\n'
    ),
    link=None,
    level=5,
    num='5.5.12.2.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join_Nested = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join.Nested',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] for any table in nested [JOIN] clause for which\n'
        'the automatic [FINAL modifier] is enabled.\n'
        '\n'
    ),
    link=None,
    level=5,
    num='5.5.12.2.2'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Union = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Union',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] for any table in [UNION] clause for which\n'
        'the automatic [FINAL modifier] is enabled.\n'
        '\n'
        'For example,\n'
        '```sql\n'
        'SELECT id, count(*)\n'
        '    FROM test1 FINAL\n'
        '    GROUP BY id\n'
        '\n'
        'UNION ALL\n'
        '\n'
        'SELECT id, count(*)\n'
        '    FROM test2 FINAL\n'
        '    GROUP BY id\n'
        '\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.13.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Intersect = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Intersect',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] for any table in [INTERSECT] clause for which\n'
        'the automatic [FINAL modifier] is enabled.\n'
        '\n'
        'For example,\n'
        '```sql\n'
        'SELECT id, count(*)\n'
        '    FROM test1 FINAL\n'
        '    GROUP BY id\n'
        '\n'
        'INTERSECT\n'
        '\n'
        'SELECT id, count(*)\n'
        '    FROM test2 FINAL\n'
        '    GROUP BY id\n'
        '\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.14.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Except = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Except',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] for any table in [EXCEPT] clause for which\n'
        'the automatic [FINAL modifier] is enabled.\n'
        '\n'
        'For example,\n'
        '```sql\n'
        'SELECT id, count(*)\n'
        '    FROM test1 FINAL\n'
        '    GROUP BY id\n'
        '\n'
        'EXCEPT\n'
        '\n'
        'SELECT id, count(*)\n'
        '    FROM test2 FINAL\n'
        '    GROUP BY id\n'
        '\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.15.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_With = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.With',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] for any table in subquery inside the [WITH] clause for which\n'
        'the automatic [FINAL modifier] is enabled.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.16.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Parallel = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Parallel',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for parallel [SELECT] queries with all clauses, inserts, updates \n'
        'and deletes.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.17.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_UserRights = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.UserRights',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] when user has enough privileges for query and show exception when\n'
        'user has not enough privileges.\n'
        '\n'
        '\n'
        '[SRS]: #srs\n'
        '[SELECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/\n'
        '[DISTINCT]: https://clickhouse.com/docs/en/sql-reference/statements/select/distinct\n'
        '[GROUP BY]: https://clickhouse.com/docs/en/sql-reference/statements/select/group-by\n'
        '[LIMIT BY]: https://clickhouse.com/docs/en/sql-reference/statements/select/limit-by\n'
        '[LIMIT]: https://clickhouse.com/docs/en/sql-reference/statements/select/limit\n'
        '[WHERE]: https://clickhouse.com/docs/en/sql-reference/statements/select/where\n'
        '[PREWHERE]: https://clickhouse.com/docs/en/sql-reference/statements/select/prewhere\n'
        '[JOIN]: https://clickhouse.com/docs/en/sql-reference/statements/select/join\n'
        '[UNION]: https://clickhouse.com/docs/en/sql-reference/statements/select/union\n'
        '[INTERSECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/intersect\n'
        '[EXCEPT]: https://clickhouse.com/docs/en/sql-reference/statements/select/except\n'
        '[ARRAY JOIN]: https://clickhouse.com/docs/en/sql-reference/statements/select/array-join\n'
        '[WITH]: https://clickhouse.com/docs/en/sql-reference/statements/select/with\n'
        '[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/\n'
        '[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree\n'
        '[CollapsingMergeTree(sign)]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree\n'
        '[VersionedCollapsingMergeTree(sign,version)]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/versionedcollapsingmergetree\n'
        '[FINAL modifier]: https://clickhouse.com/docs/en/sql-reference/statements/select/from/#final-modifier\n'
        '[ClickHouse]: https://clickhouse.com\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.6.17.1'
)

SRS032_ClickHouse_Automatic_Final_Modifier_For_Select_Queries = Specification(
    name='SRS032 ClickHouse Automatic Final Modifier For Select Queries',
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
        Heading(name='Feature Diagram', level=1, num='2'),
        Heading(name='Related Resources', level=1, num='3'),
        Heading(name='Terminology', level=1, num='4'),
        Heading(name='SRS', level=2, num='4.1'),
        Heading(name='Requirements', level=1, num='5'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier', level=2, num='5.1'),
        Heading(name='Table Schema', level=2, num='5.2'),
        Heading(name='Alias', level=3, num='5.2.1'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableSchema.Alias', level=4, num='5.2.1.1'),
        Heading(name='Table Engine Setting', level=2, num='5.3'),
        Heading(name='Create Statement', level=3, num='5.3.1'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.CreateStatement', level=4, num='5.3.1.1'),
        Heading(name='Not Supported Table Engines', level=3, num='5.3.2'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.IgnoreOnNotSupportedTableEngines', level=4, num='5.3.2.1'),
        Heading(name='Supported Table Engines', level=2, num='5.4'),
        Heading(name='MergeTree', level=3, num='5.4.1'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree', level=4, num='5.4.1.1'),
        Heading(name='ReplicatedMergeTree', level=3, num='5.4.2'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree', level=4, num='5.4.2.1'),
        Heading(name='EnginesOverOtherEngines', level=3, num='5.4.3'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines', level=4, num='5.4.3.1'),
        Heading(name='Select Queries', level=2, num='5.5'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries', level=3, num='5.5.1'),
        Heading(name='Select', level=3, num='5.5.2'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Select', level=4, num='5.5.2.1'),
        Heading(name='AS', level=3, num='5.5.3'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.As', level=4, num='5.5.3.1'),
        Heading(name='Distinct', level=3, num='5.5.4'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Distinct', level=4, num='5.5.4.1'),
        Heading(name='Prewhere', level=3, num='5.5.5'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Prewhere', level=4, num='5.5.5.1'),
        Heading(name='Where', level=3, num='5.5.6'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Where', level=4, num='5.5.6.1'),
        Heading(name='Group By', level=3, num='5.5.7'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.GroupBy', level=4, num='5.5.7.1'),
        Heading(name='Limit By', level=3, num='5.5.8'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.LimitBy', level=4, num='5.5.8.1'),
        Heading(name='Limit', level=3, num='5.5.9'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Limit', level=4, num='5.5.9.1'),
        Heading(name='Array Join', level=3, num='5.5.10'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.ArrayJoin', level=4, num='5.5.10.1'),
        Heading(name='Subquery', level=3, num='5.5.11'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery', level=4, num='5.5.11.1'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.Nested', level=5, num='5.5.11.1.1'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.ExpressionInWhere', level=5, num='5.5.11.1.2'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.ExpressionInPrewhere', level=5, num='5.5.11.1.3'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.ExpressionInArrayJoin', level=5, num='5.5.11.1.4'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.INPrewhere', level=5, num='5.5.11.1.5'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.INWhere', level=5, num='5.5.11.1.6'),
        Heading(name='JOIN', level=3, num='5.5.12'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join', level=4, num='5.5.12.1'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join.Select', level=4, num='5.5.12.2'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join.Multiple', level=5, num='5.5.12.2.1'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join.Nested', level=5, num='5.5.12.2.2'),
        Heading(name='UNION', level=3, num='5.5.13'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Union', level=4, num='5.5.13.1'),
        Heading(name='INTERSECT', level=3, num='5.5.14'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Intersect', level=4, num='5.5.14.1'),
        Heading(name='EXCEPT', level=3, num='5.5.15'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Except', level=4, num='5.5.15.1'),
        Heading(name='WITH ', level=3, num='5.5.16'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.With', level=4, num='5.5.16.1'),
        Heading(name='Parallel', level=3, num='5.5.17'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Parallel', level=4, num='5.5.17.1'),
        Heading(name='User Rights', level=2, num='5.6'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.UserRights', level=4, num='5.6.17.1'),
        ),
    requirements=(
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableSchema_Alias,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_CreateStatement,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_IgnoreOnNotSupportedTableEngines,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_MergeTree,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_ReplicatedMergeTree,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_EnginesOverOtherEngines,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Select,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_As,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Distinct,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Prewhere,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Where,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_GroupBy,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_LimitBy,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Limit,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_ArrayJoin,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_Nested,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_ExpressionInWhere,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_ExpressionInPrewhere,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_ExpressionInArrayJoin,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_INPrewhere,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_INWhere,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join_Select,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join_Multiple,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join_Nested,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Union,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Intersect,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Except,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_With,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Parallel,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_UserRights,
        ),
    content='''
# SRS032 ClickHouse Automatic Final Modifier For Select Queries
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Feature Diagram](#feature-diagram)
* 3 [Related Resources](#related-resources)
* 4 [Terminology](#terminology)
  * 4.1 [SRS](#srs)
* 5 [Requirements](#requirements)
  * 5.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier](#rqsrs-032clickhouseautomaticfinalmodifier)
  * 5.2 [Table Schema](#table-schema)
    * 5.2.1 [Alias](#alias)
      * 5.2.1.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableSchema.Alias](#rqsrs-032clickhouseautomaticfinalmodifiertableschemaalias)
  * 5.3 [Table Engine Setting](#table-engine-setting)
    * 5.3.1 [Create Statement](#create-statement)
      * 5.3.1.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.CreateStatement](#rqsrs-032clickhouseautomaticfinalmodifiertableenginesettingcreatestatement)
    * 5.3.2 [Not Supported Table Engines](#not-supported-table-engines)
      * 5.3.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.IgnoreOnNotSupportedTableEngines](#rqsrs-032clickhouseautomaticfinalmodifiertableenginesettingignoreonnotsupportedtableengines)
  * 5.4 [Supported Table Engines](#supported-table-engines)
    * 5.4.1 [MergeTree](#mergetree)
      * 5.4.1.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree](#rqsrs-032clickhouseautomaticfinalmodifiersupportedtableenginesmergetree)
    * 5.4.2 [ReplicatedMergeTree](#replicatedmergetree)
      * 5.4.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree](#rqsrs-032clickhouseautomaticfinalmodifiersupportedtableenginesreplicatedmergetree)
    * 5.4.3 [EnginesOverOtherEngines](#enginesoverotherengines)
      * 5.4.3.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines](#rqsrs-032clickhouseautomaticfinalmodifiersupportedtableenginesenginesoverotherengines)
  * 5.5 [Select Queries](#select-queries)
    * 5.5.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries](#rqsrs-032clickhouseautomaticfinalmodifierselectqueries)
    * 5.5.2 [Select](#select)
      * 5.5.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Select](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesselect)
    * 5.5.3 [AS](#as)
      * 5.5.3.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.As](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesas)
    * 5.5.4 [Distinct](#distinct)
      * 5.5.4.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Distinct](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesdistinct)
    * 5.5.5 [Prewhere](#prewhere)
      * 5.5.5.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Prewhere](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesprewhere)
    * 5.5.6 [Where](#where)
      * 5.5.6.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Where](#rqsrs-032clickhouseautomaticfinalmodifierselectquerieswhere)
    * 5.5.7 [Group By](#group-by)
      * 5.5.7.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.GroupBy](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesgroupby)
    * 5.5.8 [Limit By](#limit-by)
      * 5.5.8.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.LimitBy](#rqsrs-032clickhouseautomaticfinalmodifierselectquerieslimitby)
    * 5.5.9 [Limit](#limit)
      * 5.5.9.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Limit](#rqsrs-032clickhouseautomaticfinalmodifierselectquerieslimit)
    * 5.5.10 [Array Join](#array-join)
      * 5.5.10.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.ArrayJoin](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesarrayjoin)
    * 5.5.11 [Subquery](#subquery)
      * 5.5.11.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriessubquery)
        * 5.5.11.1.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.Nested](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriessubquerynested)
        * 5.5.11.1.2 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.ExpressionInWhere](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriessubqueryexpressioninwhere)
        * 5.5.11.1.3 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.ExpressionInPrewhere](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriessubqueryexpressioninprewhere)
        * 5.5.11.1.4 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.ExpressionInArrayJoin](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriessubqueryexpressioninarrayjoin)
        * 5.5.11.1.5 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.INPrewhere](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriessubqueryinprewhere)
        * 5.5.11.1.6 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.INWhere](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriessubqueryinwhere)
    * 5.5.12 [JOIN](#join)
      * 5.5.12.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesjoin)
      * 5.5.12.2 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join.Select](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesjoinselect)
        * 5.5.12.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join.Multiple](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesjoinmultiple)
        * 5.5.12.2.2 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join.Nested](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesjoinnested)
    * 5.5.13 [UNION](#union)
      * 5.5.13.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Union](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesunion)
    * 5.5.14 [INTERSECT](#intersect)
      * 5.5.14.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Intersect](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesintersect)
    * 5.5.15 [EXCEPT](#except)
      * 5.5.15.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Except](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesexcept)
    * 5.5.16 [WITH ](#with-)
      * 5.5.16.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.With](#rqsrs-032clickhouseautomaticfinalmodifierselectquerieswith)
    * 5.5.17 [Parallel](#parallel)
      * 5.5.17.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Parallel](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesparallel)
  * 5.6 [User Rights](#user-rights)
      * 5.6.17.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.UserRights](#rqsrs-032clickhouseautomaticfinalmodifieruserrights)

## Introduction

This software requirements specification covers requirements related to [ClickHouse] support for automatically
adding [FINAL modifier] to all [SELECT] queries for a given table.

## Feature Diagram

Test feature diagram.

```mermaid
flowchart TB;

  classDef yellow fill:#ffff32,stroke:#323,stroke-width:4px,color:black;
  classDef yellow2 fill:#ffff32,stroke:#323,stroke-width:4px,color:red;
  classDef green fill:#00ff32,stroke:#323,stroke-width:4px,color:black;
  classDef red fill:red,stroke:#323,stroke-width:4px,color:black;
  classDef blue fill:blue,stroke:#323,stroke-width:4px,color:white;
  
  subgraph O["'Select ... Final' Test Feature Diagram"]
  A-->C-->K-->D--"JOIN"-->F
  A-->E-->K

  1A---2A---3A
  2A---4A
  1D---2D---3D
  2D---4D
  1C---2C---3C---4C
  1E---2E---3E---4E
  1K---2K---3K
  1F---2F---3F---4F
  
    subgraph A["Create table section"]

        1A["CREATE"]:::green
        2A["force_select_final"]:::yellow
        3A["1"]:::blue
        4A["0"]:::blue
    end
    
    subgraph D["SELECT"]
        1D["SELECT"]:::green
        2D["ignore_force_select_final"]:::yellow
        3D["1"]:::blue
        4D["0"]:::blue
    end
    
    subgraph C["Table ENGINES"]
        1C["MergeTree"]:::blue
        2C["ReplacingMergeTree"]:::blue
        3C["CollapsingMergeTree"]:::blue
        4C["VersionedCollapsingMergeTree"]:::blue
    end
    
    subgraph E["Replicated Table ENGINES"]
        1E["ReplicatedMergeTree"]:::blue
        2E["ReplicatedReplacingMergeTree"]:::blue
        3E["ReplicatedCollapsingMergeTree"]:::blue
        4E["ReplicatedVersionedCollapsingMergeTree"]:::blue
    end
      
    subgraph F["Some table"]
        1F["INNER"]:::green
        2F["LEFT"]:::green
        3F["RIGHT"]:::green
        4F["FULL"]:::green
    end
    
    subgraph K["Engines that operate over other engines"]
        1K["View"]:::yellow
        2K["Distributed"]:::yellow
        3K["MaterializedView"]:::yellow
    end

    

  end
```

## Related Resources

**Pull Requests**

* https://github.com/ClickHouse/ClickHouse/pull/40945

## Terminology

### SRS

Software Requirements Specification

## Requirements

### RQ.SRS-032.ClickHouse.AutomaticFinalModifier
version: 1.0

[ClickHouse] SHALL support adding [FINAL modifier] clause automatically to all [SELECT] queries
for all table engines that support [FINAL modifier] and return the same result as if [FINAL modifier] clause
was specified in the [SELECT] query explicitly.

### Table Schema

#### Alias

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableSchema.Alias
version: 1.0 priority: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for tables with ALIAS.

For example,

```sql
CREATE TABLE IF NOT EXISTS 
table1(id Int32, x Int32, s Int32 ALIAS id + x)
ENGINE = MergeTree ORDER BY tuple()
```

### Table Engine Setting

#### Create Statement

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.CreateStatement
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `force_select_final` table engine setting to enable automatic [FINAL modifier]
on all [SELECT] queries when the setting is value is set to `1`.

For example,

```sql
CREATE TABLE table (...)
Engine=ReplacingMergeTree
SETTTING force_select_final=1
```

#### Not Supported Table Engines

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.IgnoreOnNotSupportedTableEngines
version: 1.0 priority: 1.0

[ClickHouse] SHALL silently ignore `force_select_final` table engine setting for any table
engine that doesn't support [FINAL modifier] clause.


### Supported Table Engines

#### MergeTree

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for the following [MergeTree] table engines variants:

* [ReplacingMergeTree]
* ReplacingMergeTree(version)
* [CollapsingMergeTree(sign)]
* AggregatingMergeTree
* SummingMergeTree
* [VersionedCollapsingMergeTree(sign,version)]


#### ReplicatedMergeTree

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for the following replicated 
[ReplicatedMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replication) 
table engines variants:

* ReplicatedReplacingMergeTree
* ReplicatedReplacingMergeTree(version)
* ReplicatedCollapsingMergeTree(sign)
* ReplicatedAggregatingMergeTree
* ReplicatedSummingMergeTree
* ReplicatedVersionedCollapsingMergeTree(sign,version)

#### EnginesOverOtherEngines

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines
version: 1.0

[ClickHouse] SHALL support the following table engines over tables that have automatic [FINAL modifier] clause enabled:

* [View](https://clickhouse.com/docs/en/engines/table-engines/special/view)
* [Distributed](https://clickhouse.com/docs/en/engines/table-engines/special/distributed)
* [MaterializedView](https://clickhouse.com/docs/en/engines/table-engines/special/materializedview)


### Select Queries

#### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for any type of [SELECT] queries.

```sql
[WITH expr_list|(subquery)]
SELECT [DISTINCT [ON (column1, column2, ...)]] expr_list
[FROM [db.]table | (subquery) | table_function] [FINAL]
[SAMPLE sample_coeff]
[ARRAY JOIN ...]
[GLOBAL] [ANY|ALL|ASOF] [INNER|LEFT|RIGHT|FULL|CROSS] [OUTER|SEMI|ANTI] JOIN (subquery)|table (ON <expr_list>)|(USING <column_list>)
[PREWHERE expr]
[WHERE expr]
[GROUP BY expr_list] [WITH ROLLUP|WITH CUBE] [WITH TOTALS]
[HAVING expr]
[ORDER BY expr_list] [WITH FILL] [FROM expr] [TO expr] [STEP expr] [INTERPOLATE [(expr_list)]]
[LIMIT [offset_value, ]n BY columns]
[LIMIT [n, ]m] [WITH TIES]
[SETTINGS ...]
[UNION  ...]
[INTO OUTFILE filename [COMPRESSION type [LEVEL level]] ]
[FORMAT format]
```

#### Select

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Select
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [SELECT] clause.

#### AS

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.As
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with columns changed with `as` clause.

#### Distinct

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Distinct
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [DISTINCT] clause.

#### Prewhere

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Prewhere
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [PREWHERE] clause.

#### Where

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Where
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [WHERE] clause.

#### Group By

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.GroupBy
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [GROUP BY] clause.

#### Limit By

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.LimitBy
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [LIMIT BY] clause.

#### Limit

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Limit
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [LIMIT] clause.

#### Array Join

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.ArrayJoin
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [ARRAY JOIN] clause.

#### Subquery

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] in any subquery that reads from a table that
has automatic [FINAL modifier] enabled.

###### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.Nested
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] in any nested subquery that reads from a table that
has automatic [FINAL modifier] enabled.

###### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.ExpressionInWhere
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] in any subquery as expression in `WHERE` clause that reads from a table that
has automatic [FINAL modifier] enabled.

###### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.ExpressionInPrewhere
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] in any subquery as expression in `PREWHERE` clause that reads from a table that
has automatic [FINAL modifier] enabled.

###### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.ExpressionInArrayJoin
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] in any subquery as expression in `ARRAY JOIN` clause that reads from a table that
has automatic [FINAL modifier] enabled.

###### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.INPrewhere
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] in any subquery with `IN` clause in `PREWHERE` that reads from a table that
has automatic [FINAL modifier] enabled.

###### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery.INWhere
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] in any subquery with `IN` clause in `WHERE` that reads from a table that
has automatic [FINAL modifier] enabled.

#### JOIN

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] for any table in [JOIN] clause for which
the automatic [FINAL modifier] is enabled.

* INNER JOIN
* LEFT OUTER JOIN
* RIGHT OUTER JOIN
* FULL OUTER JOIN
* CROSS JOIN
* LEFT SEMI JOIN and RIGHT SEMI JOIN
* LEFT ANTI JOIN and RIGHT ANTI JOIN
* LEFT ANY JOIN, RIGHT ANY JOIN and INNER ANY JOIN
* ASOF JOIN and LEFT ASOF JOIN

For example,
```sql
select count() from lhs inner join rhs on lhs.x = rhs.x;
```

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join.Select
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] for any table in [JOIN] clause with [SELECT] subquery for which
the automatic [FINAL modifier] is enabled.

###### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join.Multiple
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] for any table in multiple [JOIN] clause for which
the automatic [FINAL modifier] is enabled.

###### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join.Nested
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] for any table in nested [JOIN] clause for which
the automatic [FINAL modifier] is enabled.

#### UNION

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Union
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] for any table in [UNION] clause for which
the automatic [FINAL modifier] is enabled.

For example,
```sql
SELECT id, count(*)
    FROM test1 FINAL
    GROUP BY id

UNION ALL

SELECT id, count(*)
    FROM test2 FINAL
    GROUP BY id

```

#### INTERSECT

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Intersect
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] for any table in [INTERSECT] clause for which
the automatic [FINAL modifier] is enabled.

For example,
```sql
SELECT id, count(*)
    FROM test1 FINAL
    GROUP BY id

INTERSECT

SELECT id, count(*)
    FROM test2 FINAL
    GROUP BY id

```

#### EXCEPT

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Except
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] for any table in [EXCEPT] clause for which
the automatic [FINAL modifier] is enabled.

For example,
```sql
SELECT id, count(*)
    FROM test1 FINAL
    GROUP BY id

EXCEPT

SELECT id, count(*)
    FROM test2 FINAL
    GROUP BY id

```

#### WITH 

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.With
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] for any table in subquery inside the [WITH] clause for which
the automatic [FINAL modifier] is enabled.

#### Parallel

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Parallel
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for parallel [SELECT] queries with all clauses, inserts, updates 
and deletes.

### User Rights

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.UserRights
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] when user has enough privileges for query and show exception when
user has not enough privileges.


[SRS]: #srs
[SELECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/
[DISTINCT]: https://clickhouse.com/docs/en/sql-reference/statements/select/distinct
[GROUP BY]: https://clickhouse.com/docs/en/sql-reference/statements/select/group-by
[LIMIT BY]: https://clickhouse.com/docs/en/sql-reference/statements/select/limit-by
[LIMIT]: https://clickhouse.com/docs/en/sql-reference/statements/select/limit
[WHERE]: https://clickhouse.com/docs/en/sql-reference/statements/select/where
[PREWHERE]: https://clickhouse.com/docs/en/sql-reference/statements/select/prewhere
[JOIN]: https://clickhouse.com/docs/en/sql-reference/statements/select/join
[UNION]: https://clickhouse.com/docs/en/sql-reference/statements/select/union
[INTERSECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/intersect
[EXCEPT]: https://clickhouse.com/docs/en/sql-reference/statements/select/except
[ARRAY JOIN]: https://clickhouse.com/docs/en/sql-reference/statements/select/array-join
[WITH]: https://clickhouse.com/docs/en/sql-reference/statements/select/with
[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/
[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree
[CollapsingMergeTree(sign)]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree
[VersionedCollapsingMergeTree(sign,version)]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/versionedcollapsingmergetree
[FINAL modifier]: https://clickhouse.com/docs/en/sql-reference/statements/select/from/#final-modifier
[ClickHouse]: https://clickhouse.com
'''
)
