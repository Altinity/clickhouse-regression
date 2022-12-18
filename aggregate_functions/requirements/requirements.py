# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.221103.1222218.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Count = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [count] standard aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.1.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Count_DistinctImplementationSetting = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.DistinctImplementationSetting",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [count_distinct_implementation](https://clickhouse.com/docs/en/operations/settings/settings#settings-count_distinct_implementation) setting that SHALL specify\n"
        "which `uniq*` function SHALL be used to calculate `COUNT(DISTINCT expr)`. \n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.1.2",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Count_OptimizeTrivialCountQuerySetting = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.OptimizeTrivialCountQuerySetting",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [optimize_trivial_count_query]https://clickhouse.com/docs/en/operations/settings/settings#optimize-trivial-count-query setting that SHALL enable or disable\n"
        "the optimization of trivial `SELECT count() FROM table` query using metadata from [MergeTree] tables.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.1.3",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Count_OptimizeFunctionsToSubcolumnsSetting = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.OptimizeFunctionsToSubcolumnsSetting",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support optimizing `SELECT count(nullable_column) FROM table` query by enabling the\n"
        "[optimize_functions_to_subcolumns](https://clickhouse.com/docs/en/operations/settings/settings#optimize-functions-to-subcolumns) setting. With `optimize_functions_to_subcolumns=1` the function SHALL\n"
        "read only null sub-column instead of reading and processing the whole column data.\n"
        "\n"
        "The query `SELECT count(n) FROM table` SHALL be transformed to `SELECT sum(NOT n.null) FROM table`.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.1.4",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Min = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Min",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [min] standard aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.2.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Max = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Max",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [max] standard aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.3.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Sum = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Sum",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [sum] standard aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.4.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Avg = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Avg",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [avg] standard aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.5.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Any = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Any",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [any] standard aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.6.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevPop = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.StddevPop",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [stddevPop] standard aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.7.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevSamp = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.StddevSamp",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [stddevSamp] standard aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.8.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_VarPop = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.VarPop",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [varPop] standard aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.9.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_VarSamp = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.VarSamp",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [varSamp] standard aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.10.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarPop = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.CovarPop",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [covarPop] standard aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.11.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarSamp = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.CovarSamp",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [covarSamp] standard aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.1.12.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AnyHeavy = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AnyHeavy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [anyHeavy] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.1.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AnyLast = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AnyLast",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [anyLast] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.2.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMin = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ArgMin",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [argMin] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.3.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMax = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ArgMax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [argMax] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.4.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AvgWeighted = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AvgWeighted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [avgWeighted] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.5.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_TopK = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.TopK",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [topK] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.6.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_TopKWeighted = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.TopKWeighted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [topKWeighted] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.7.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArray = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupArray] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.8.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupUniqArray = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupUniqArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupUniqArray] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.9.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayInsertAt = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayInsertAt",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupArrayInsertAt] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.10.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayMovingAvg = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayMovingAvg",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupArrayMovingAvg] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.11.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayMovingSum = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayMovingSum",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupArrayMovingSum] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.12.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArraySample = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArraySample",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupArraySample] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.13.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitAnd = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitAnd",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupBitAnd] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.14.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitOr = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitOr",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupBitOr] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.15.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitXor = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitXor",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupBitXor] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.16.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmap = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmap",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupBitmap] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.17.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapAnd = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapAnd",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupBitmapAnd] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.18.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapOr = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapOr",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupBitmapOr] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.19.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapXor = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapXor",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [groupBitmapXor] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.20.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumWithOverflow = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumWithOverflow",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [sumWithOverflow] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.21.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumMap = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumMap",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [sumMap] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.22.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MinMap = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MinMap",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [minMap] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.23.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MaxMap = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MaxMap",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [maxMap] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.24.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SkewSamp = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SkewSamp",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [skewSamp] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.25.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SkewPop = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SkewPop",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [skewPop] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.26.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_KurtSamp = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KurtSamp",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [kurtSamp] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.27.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_KurtPop = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KurtPop",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [kurtPop] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.28.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Uniq = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Uniq",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [uniq] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.29.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqExact = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqExact",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [uniqExact] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.30.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqCombined = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqCombined",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [uniqCombined] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.31.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqCombined64 = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqCombined64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [uniqCombined64] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.32.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqHLL12 = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqHLL12",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [uniqHLL12] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.33.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Quantile = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Quantile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantile] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.34.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Quantiles = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Quantiles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantiles] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.35.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExactExclusive = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactExclusive",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesExactExclusive] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.36.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExactInclusive = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactInclusive",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesExactInclusive] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.37.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesDeterministic = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesDeterministic",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesDeterministic] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.38.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExact = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExact",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesExact] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.39.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExactHigh = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactHigh",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesExactHigh] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.40.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExactLow = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactLow",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesExactLow] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.41.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExactWeighted = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactWeighted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesExactWeighted] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.42.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesTDigest = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTDigest",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesTDigest] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.43.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesTDigestWeighted = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTDigestWeighted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesTDigestWeighted] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.44.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesBFloat16 = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesBFloat16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesBFloat16] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.45.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesBFloat16Weighted = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesBFloat16Weighted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesBFloat16Weighted] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.46.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesTiming = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTiming",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesTiming] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.47.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesTimingWeighted = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTimingWeighted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantilesTimingWeighted] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.48.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileExact = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExact",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantileExact] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.49.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileExactLow = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactLow",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantileExactLow] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.50.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileExactHigh = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactHigh",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantileExactHigh] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.51.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileExactWeighted = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactWeighted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantileExactWeighted] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.52.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileTiming = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTiming",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantileTiming] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.53.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileTimingWeighted = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTimingWeighted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantileTimingWeighted] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.54.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileDeterministic = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileDeterministic",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantileDeterministic] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.55.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileTDigest = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTDigest",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantileTDigest] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.56.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileTDigestWeighted = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTDigestWeighted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantileTDigestWeighted] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.57.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileBFloat16 = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileBFloat16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantileBFloat16] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.58.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileBFloat16Weighted = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileBFloat16Weighted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [quantileBFloat16Weighted] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.59.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SimpleLinearRegression = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SimpleLinearRegression",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [simpleLinearRegression] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.60.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StochasticLinearRegression = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StochasticLinearRegression",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [stochasticLinearRegression] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.61.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StochasticLogisticRgression = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StochasticLogisticRgression",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [stochasticLogisticRegression] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.62.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_CategoricalInformationValue = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.CategoricalInformationValue",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [categoricalInformationValue] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.63.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StudentTTest = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StudentTTest",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [studentTTest] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.64.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_WelchTTest = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.WelchTTest",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [welchTTest] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.65.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MannWhitneyUTest = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MannWhitneyUTest",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [mannWhitneyUTest] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.66.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Median = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Median",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [median] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.67.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_RankCorr = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.RankCorr",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [rankCorr] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.68.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Entropy = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Entropy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [entropy] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.69.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MeanZTest = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MeanZTest",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [meanZTest] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.70.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Sparkbar = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Sparkbar",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [sparkbar] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.71.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Corr = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Corr",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [corr] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.72.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_DeltaSum = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.DeltaSum",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [deltaSum] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.73.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_DeltaSumTimestamp = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.DeltaSumTimestamp",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [deltaSumTimestamp] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.74.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ExponentialMovingAverage = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ExponentialMovingAverage",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [exponentialMovingAverage] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.75.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_IntervalLengthSum = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.IntervalLengthSum",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [intervalLengthSum] specific aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.76.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumCount = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumCount",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [sumCount] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.77.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumKahan = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumKahan",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [sumKahan] specific aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.2.78.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_FirstValue = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.FirstValue",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `first_value` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.1.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LastValue = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LastValue",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `last_value` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.2.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LagInFrame = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LagInFrame",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `lagInFrame` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.3.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LeadInFrame = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LeadInFrame",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `leadInFrame` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.4.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_NthValue = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.NthValue",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `nth_value` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.5.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Rank = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Rank",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `rank` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.6.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_RowNumber = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.RowNumber",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `row_number` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.7.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SingleValueOrNull = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SingleValueOrNull",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `singleValueOrNull` aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.8.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_MaxIntersections = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxIntersections",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `maxIntersections` aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.9.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_MaxIntersectionsPosition = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxIntersectionsPosition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `maxIntersectionsPosition` aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.10.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_AggThrow = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.AggThrow",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `aggThrow` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.11.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_BoundingRatio = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.BoundingRatio",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `boundingRatio` aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.12.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Contingency = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Contingency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `contingency` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.13.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_CramersV = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.CramersV",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `cramersV` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.14.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_CramersVBiasCorrected = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.CramersVBiasCorrected",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `cramersVBiasCorrected` aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.15.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_DenseRank = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.DenseRank",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `dense_rank` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.16.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedAvg = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedAvg",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `exponentialTimeDecayedAvg` aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.17.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedCount = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedCount",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `exponentialTimeDecayedCount` aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.18.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedMax = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedMax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `exponentialTimeDecayedMax` aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.19.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedSum = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedSum",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `exponentialTimeDecayedSum` aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.20.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_UniqTheta = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.UniqTheta",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `uniqTheta` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.21.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_QuantileExactExclusive = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.QuantileExactExclusive",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `quantileExactExclusive` aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.22.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_QuantileExactInclusive = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.QuantileExactInclusive",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `quantileExactInclusive` aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.23.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SumMapFilteredWithOverflow = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMapFilteredWithOverflow",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `sumMapFilteredWithOverflow` aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.24.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SumMapWithOverflow = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMapWithOverflow",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `sumMapWithOverflow` aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.25.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SumMappedArrays = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMappedArrays",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `sumMappedArrays` aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.26.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Nothing = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Nothing",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `nothing` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.27.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_MaxMappedArrays = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxMappedArrays",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `maxMappedArrays` aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.28.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_MinMappedArrays = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MinMappedArrays",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `minMappedArrays` aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.29.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_NonNegativeDerivative = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.NonNegativeDerivative",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `nonNegativeDerivative` aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.3.30.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_TheilsU = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.TheilsU",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `theilsU` aggregate function.\n" "\n"),
    link=None,
    level=5,
    num="3.1.3.31.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_Histogram = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.Histogram",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [histogram] parameteric aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.4.1.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SequenceMatch = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceMatch",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [sequenceMatch] parameteric aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.4.2.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SequenceCount = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceCount",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [sequenceCount] parameteric aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.4.3.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_WindowFunnel = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.WindowFunnel",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [windowFunnel] parameteric aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.4.4.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_Retention = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.Retention",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [retention] parameteric aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.4.5.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_UniqUpTo = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.UniqUpTo",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [uniqUpTo] parameteric aggregate function.\n" "\n"
    ),
    link=None,
    level=5,
    num="3.1.4.6.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SumMapFiltered = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SumMapFiltered",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [sumMapFiltered] parameteric aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.4.7.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SequenceNextNode = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceNextNode",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [sequenceNextNode] parameteric aggregate function.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.1.4.8.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_If = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.If",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [-If] combinator suffix for all [aggregate function]s which\n"
        "SHALL enable the aggregate function to accept an extra argument – a condition of `Uint8` type.\n"
        "The aggregate function SHALL process only the rows that trigger the condition.\n"
        "If the condition was not triggered even once, the function SHALL return a default value.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "sumIf(column, cond)\n"
        "countIf(cond)\n"
        "avgIf(x, cond)\n"
        "quantilesTimingIf(level1, level2)(x, cond)\n"
        "argMinIf(arg, val, cond)\n"
        "...\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.1.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Array = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Array",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [-Array] combinator suffix for all [aggregate function]s which\n"
        "SHALL enable the aggregate function ti take arguments of the `Array(T)` type (arrays)\n"
        "instead of `T` type arguments.\n"
        "\n"
        "If the aggregate function accepts multiple arguments, the arrays SHALL be of equal lengths.\n"
        "When processing arrays, the aggregate function SHALL work like the original\n"
        "aggregate function across all array elements.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "sumArray(arr) -- sum all the elements of all ‘arr’ arrays\n"
        "```\n"
        "\n"
        "```sql\n"
        "uniqArray(arr) -- count the number of unique elements in all ‘arr’ arrays\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.2.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Map = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Map",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [-Map] combinator suffix for all [aggregate function]s which\n"
        "SHALL cause the aggregate function to take `Map` type as an argument,\n"
        "and SHALL aggregate values of each key of the map separately using the specified aggregate function.\n"
        "\n"
        "The result SHALL also be of a `Map` type.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "sumMap(map(1,1))\n"
        "avgMap(map('a', 1))\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.3.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [-State] combinator suffix for all [aggregate function]s which\n"
        "SHALL return an intermediate state of the aggregation that user SHALL be able to use for\n"
        "further processing or stored in a table to finish aggregation later.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.4.2",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_AggregatingMergeTree = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.AggregatingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator\n"
        "with [AggregatingMergeTree] table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.4.3",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_FinalizeAggregationFunction = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.FinalizeAggregationFunction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator\n"
        "with [finalizeAggregation] function.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.4.4",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_RunningAccumulateFunction = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.RunningAccumulateFunction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator\n"
        "with [runningAccumulate] function.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.4.5",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_Merge = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.Merge",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator\n"
        "with the corresponding [-Merge] combinator function.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.4.6",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_MergeState = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.MergeState",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator\n"
        "with the corresponding [-MergeState] combinator function.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.4.7",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_AggregateFunctionDataType = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.AggregateFunctionDataType",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator\n"
        "with [AggregateFunction] data type columns.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.4.8",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_MaterializedView = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.MaterializedView",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator\n"
        "with [Materialized View] table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.4.9",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_SimpleState = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.SimpleState",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [-SimpleState] combinator suffix for all [aggregate function]s which\n"
        "SHALL return the same result as the aggregate function but with a [SimpleAggregateFunction] data type.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "WITH anySimpleState(number) AS c SELECT toTypeName(c), c FROM numbers(1)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.5.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_SimpleState_With_AggregatingMergeTree = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.SimpleState.With.AggregatingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s SHALL support using all [aggregate function]s with [-SimpleState] combinator\n"
        "with [AggregatingMergeTree] table engine to store data in a column with [SimpleAggregateFunction] data type.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.5.2",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Merge = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Merge",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [-Merge] combinator suffix for all [aggregate function]s which\n"
        "SHALL cause the aggregate function to take the intermediate aggregation state as an argument and\n"
        "combine the states to finish aggregation and the function SHALL return the resulting value.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.6.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_MergeState = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.MergeState",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [-MergeState] combinator suffix for all [aggregate function]s which\n"
        "SHALL cause the aggregate function to merge the intermediate aggregation states in the same way as the\n"
        "[-Merge] combinator but SHALL return an intermediate aggregation state, similar to the [-State] combinator.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.7.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_ForEach = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.ForEach",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [-MergeState] combinator suffix for all [aggregate function]s which\n"
        "SHALL convert aggregate function for tables into an aggregate function for arrays\n"
        "that SHALL aggregate the corresponding array items and SHALL return an array of results.\n"
        "\n"
        "For example,\n"
        "\n"
        "> sumForEach for the arrays [1, 2], [3, 4, 5] and [6, 7] SHALL return the result [10, 13, 5]\n"
        "> after adding together the corresponding array items\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.8.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Distinct = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Distinct",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [-Distinct] combinator suffix for all [aggregate function]s which\n"
        "SHALL cause the aggregate function for every unique combination of arguments to be aggregated only once.\n"
        "\n"
        "Repeating values SHALL be ignored.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "sum(DISTINCT x)\n"
        "groupArray(DISTINCT x)\n"
        "corrStableDistinct(DISTINCT x, y)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.9.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_OrDefault = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.OrDefault",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [-Distinct] combinator suffix for all [aggregate function]s which\n"
        "SHALL change the behavior of an aggregate function.\n"
        "\n"
        "If an aggregate function does not have input values, with this combinator it SHALL return\n"
        "the default value for its return data type.\n"
        "\n"
        "This combinator SHALL apply to the aggregate functions that can take empty input data.\n"
        "\n"
        "The `-OrDefault` SHALL support to be used with other combinators which\n"
        "SHALL enable to use aggregate function which do not accept the empty input.\n"
        "\n"
        "Syntax:\n"
        "\n"
        "```sql\n"
        "[aggregate function]OrDefault(x)\n"
        "```\n"
        "\n"
        "where `x` are the aggregate function parameters.\n"
        "\n"
        "The function SHALL return the default value of an aggregate function’s return type if there is nothing to aggregate\n"
        "and the type SHALL depend on the aggregate function used.\n"
        "\n"
        "For example, \n"
        "\n"
        "```sql\n"
        "SELECT avg(number), avgOrDefault(number) FROM numbers(0)\n"
        "```\n"
        "\n"
        "SHALL produce the following output\n"
        "\n"
        "```bash\n"
        "┌─avg(number)─┬─avgOrDefault(number)─┐\n"
        "│         nan │                    0 │\n"
        "└─────────────┴──────────────────────┘\n"
        "```\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT avgOrDefaultIf(x, x > 10)\n"
        "FROM\n"
        "(\n"
        "    SELECT toDecimal32(1.23, 2) AS x\n"
        ")\n"
        "```\n"
        "\n"
        "SHALL produce the following output\n"
        "\n"
        "```bash\n"
        "┌─avgOrDefaultIf(x, greater(x, 10))─┐\n"
        "│                              0.00 │\n"
        "└───────────────────────────────────┘\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.10.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_OrNull = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.OrNull",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [-Distinct] combinator suffix for all [aggregate function]s which\n"
        "SHALL change the behavior of an aggregate function.\n"
        "\n"
        "The combinator SHALL convert a result of an aggregate function to the `Nullable` data type.\n"
        "If the aggregate function does not have values to calculate it SHALL return `NULL`.\n"
        "\n"
        "Syntax:\n"
        "\n"
        "```sql\n"
        "<aggregate function>OrNull(x)\n"
        "```\n"
        "\n"
        "where `x` is aggregate function parameters.\n"
        "\n"
        "In addition, the [-OrNull] combinator SHALL support to be used with other combinators\n"
        "which SHALL enable to use aggregate function which do not accept the empty input.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT sumOrNull(number), toTypeName(sumOrNull(number)) FROM numbers(10) WHERE number > 10\n"
        "```\n"
        "\n"
        "SHALL produce the following output\n"
        "\n"
        "```bash\n"
        "┌─sumOrNull(number)─┬─toTypeName(sumOrNull(number))─┐\n"
        "│              ᴺᵁᴸᴸ │ Nullable(UInt64)              │\n"
        "└───────────────────┴───────────────────────────────┘\n"
        "```\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT avgOrNullIf(x, x > 10)\n"
        "FROM\n"
        "(\n"
        "    SELECT toDecimal32(1.23, 2) AS x\n"
        ")\n"
        "```\n"
        "\n"
        "SHALL produce the following output\n"
        "\n"
        "```bash\n"
        "┌─avgOrNullIf(x, greater(x, 10))─┐\n"
        "│                           ᴺᵁᴸᴸ │\n"
        "└────────────────────────────────┘\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.11.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Resample = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Resample",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [-Resample] combinator suffix for all [aggregate function]s which\n"
        "SHALL cause the aggregate function to divide data into groups, and then it SHALL separately aggregate\n"
        "the data in those groups. Groups SHALL be created by splitting the values from one column into intervals.\n"
        "\n"
        "The function SHALL return an `Array` of aggregate function results for each sub-interval.\n"
        "\n"
        "Syntax:\n"
        "\n"
        "```sql\n"
        "<aggregate function>Resample(start, end, step)(<aggFunction_params>, resampling_key)\n"
        "```\n"
        "\n"
        "where arguments SHALL be the following\n"
        "\n"
        "* `start`  starting value of the whole required interval for resampling_key values\n"
        "* `stop`  ending value of the whole required interval for resampling_key values\n"
        "  The whole interval does not include the stop value [start, stop)\n"
        "* `step` step for separating the whole interval into sub-intervals.\n"
        "  The aggregate function is executed over each of those sub-intervals independently.\n"
        "* `resampling_key` column whose values are used for separating data into intervals\n"
        "* `aggFunction_params` aggregate function parameters\n"
        "\n"
        "For example, \n"
        "\n"
        "with `people` table containing\n"
        "\n"
        "```bash\n"
        "┌─name───┬─age─┬─wage─┐\n"
        "│ John   │  16 │   10 │\n"
        "│ Alice  │  30 │   15 │\n"
        "│ Mary   │  35 │    8 │\n"
        "│ Evelyn │  48 │ 11.5 │\n"
        "│ David  │  62 │  9.9 │\n"
        "│ Brian  │  60 │   16 │\n"
        "└────────┴─────┴──────┘\n"
        "```\n"
        "\n"
        "```sql\n"
        "SELECT groupArrayResample(30, 75, 30)(name, age) FROM people\n"
        "```\n"
        "\n"
        "SHALL produce the following result\n"
        "\n"
        "```bash\n"
        "┌─groupArrayResample(30, 75, 30)(name, age)─────┐\n"
        "│ [['Alice','Mary','Evelyn'],['David','Brian']] │\n"
        "└───────────────────────────────────────────────┘\n"
        "```\n"
        "\n"
        "and\n"
        "\n"
        "```sql\n"
        "SELECT\n"
        "    countResample(30, 75, 30)(name, age) AS amount,\n"
        "    avgResample(30, 75, 30)(wage, age) AS avg_wage\n"
        "FROM people\n"
        "```\n"
        "\n"
        "SHALL produce\n"
        "\n"
        "```bash\n"
        "┌─amount─┬─avg_wage──────────────────┐\n"
        "│ [3,2]  │ [11.5,12.949999809265137] │\n"
        "└────────┴───────────────────────────┘\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.12.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_DataType_SimpleAggregateFunction = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.SimpleAggregateFunction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [SimpleAggregateFunction] data type which SHALL allow to store a\n"
        "current value of the aggregate function. \n"
        "\n"
        "This function SHALL be used as optimization to [AggregateFunction] when the following property holds: \n"
        "\n"
        "> the result of applying a function f to a row set S1 UNION ALL S2 can be obtained by applying f to parts of the row set\n"
        "> separately, and then again applying f to the results: f(S1 UNION ALL S2) = f(f(S1) UNION ALL f(S2)).\n"
        "> This property guarantees that partial aggregation results are enough to compute the combined one,\n"
        "> so we do not have to store and process any extra data.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.1.1",
)

RQ_SRS_031_ClickHouse_AggregateFunctions_DataType_AggregateFunction = Requirement(
    name="RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction",
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
    level=4,
    num="3.3.2.1",
)

SRS_031_ClickHouse_Aggregate_Functions = Specification(
    name="SRS-031 ClickHouse Aggregate Functions",
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
        Heading(name="Aggregate Functions", level=2, num="3.1"),
        Heading(name="Standard Functions", level=3, num="3.1.1"),
        Heading(name="count", level=4, num="3.1.1.1"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count",
            level=5,
            num="3.1.1.1.1",
        ),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.DistinctImplementationSetting",
            level=5,
            num="3.1.1.1.2",
        ),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.OptimizeTrivialCountQuerySetting",
            level=5,
            num="3.1.1.1.3",
        ),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.OptimizeFunctionsToSubcolumnsSetting",
            level=5,
            num="3.1.1.1.4",
        ),
        Heading(name="min", level=4, num="3.1.1.2"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Min",
            level=5,
            num="3.1.1.2.1",
        ),
        Heading(name="max", level=4, num="3.1.1.3"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Max",
            level=5,
            num="3.1.1.3.1",
        ),
        Heading(name="sum", level=4, num="3.1.1.4"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Sum",
            level=5,
            num="3.1.1.4.1",
        ),
        Heading(name="avg", level=4, num="3.1.1.5"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Avg",
            level=5,
            num="3.1.1.5.1",
        ),
        Heading(name="any", level=4, num="3.1.1.6"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Any",
            level=5,
            num="3.1.1.6.1",
        ),
        Heading(name="stddevPop", level=4, num="3.1.1.7"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.StddevPop",
            level=5,
            num="3.1.1.7.1",
        ),
        Heading(name="stddevSamp", level=4, num="3.1.1.8"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.StddevSamp",
            level=5,
            num="3.1.1.8.1",
        ),
        Heading(name="varPop", level=4, num="3.1.1.9"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.VarPop",
            level=5,
            num="3.1.1.9.1",
        ),
        Heading(name="varSamp", level=4, num="3.1.1.10"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.VarSamp",
            level=5,
            num="3.1.1.10.1",
        ),
        Heading(name="covarPop", level=4, num="3.1.1.11"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.CovarPop",
            level=5,
            num="3.1.1.11.1",
        ),
        Heading(name="covarSamp", level=4, num="3.1.1.12"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.CovarSamp",
            level=5,
            num="3.1.1.12.1",
        ),
        Heading(name="Specific Functions", level=3, num="3.1.2"),
        Heading(name="anyHeavy", level=4, num="3.1.2.1"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AnyHeavy",
            level=5,
            num="3.1.2.1.1",
        ),
        Heading(name="anyLast", level=4, num="3.1.2.2"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AnyLast",
            level=5,
            num="3.1.2.2.1",
        ),
        Heading(name="argMin", level=4, num="3.1.2.3"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ArgMin",
            level=5,
            num="3.1.2.3.1",
        ),
        Heading(name="argMax", level=4, num="3.1.2.4"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ArgMax",
            level=5,
            num="3.1.2.4.1",
        ),
        Heading(name="avgWeighted", level=4, num="3.1.2.5"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AvgWeighted",
            level=5,
            num="3.1.2.5.1",
        ),
        Heading(name="topK", level=4, num="3.1.2.6"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.TopK",
            level=5,
            num="3.1.2.6.1",
        ),
        Heading(name="topKWeighted", level=4, num="3.1.2.7"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.TopKWeighted",
            level=5,
            num="3.1.2.7.1",
        ),
        Heading(name="groupArray", level=4, num="3.1.2.8"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArray",
            level=5,
            num="3.1.2.8.1",
        ),
        Heading(name="groupUniqArray", level=4, num="3.1.2.9"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupUniqArray",
            level=5,
            num="3.1.2.9.1",
        ),
        Heading(name="groupArrayInsertAt", level=4, num="3.1.2.10"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayInsertAt",
            level=5,
            num="3.1.2.10.1",
        ),
        Heading(name="groupArrayMovingAvg", level=4, num="3.1.2.11"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayMovingAvg",
            level=5,
            num="3.1.2.11.1",
        ),
        Heading(name="groupArrayMovingSum", level=4, num="3.1.2.12"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayMovingSum",
            level=5,
            num="3.1.2.12.1",
        ),
        Heading(name="groupArraySample", level=4, num="3.1.2.13"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArraySample",
            level=5,
            num="3.1.2.13.1",
        ),
        Heading(name="groupBitAnd", level=4, num="3.1.2.14"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitAnd",
            level=5,
            num="3.1.2.14.1",
        ),
        Heading(name="groupBitOr", level=4, num="3.1.2.15"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitOr",
            level=5,
            num="3.1.2.15.1",
        ),
        Heading(name="groupBitXor", level=4, num="3.1.2.16"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitXor",
            level=5,
            num="3.1.2.16.1",
        ),
        Heading(name="groupBitmap", level=4, num="3.1.2.17"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmap",
            level=5,
            num="3.1.2.17.1",
        ),
        Heading(name="groupBitmapAnd", level=4, num="3.1.2.18"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapAnd",
            level=5,
            num="3.1.2.18.1",
        ),
        Heading(name="groupBitmapOr", level=4, num="3.1.2.19"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapOr",
            level=5,
            num="3.1.2.19.1",
        ),
        Heading(name="groupBitmapXor", level=4, num="3.1.2.20"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapXor",
            level=5,
            num="3.1.2.20.1",
        ),
        Heading(name="sumWithOverflow", level=4, num="3.1.2.21"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumWithOverflow",
            level=5,
            num="3.1.2.21.1",
        ),
        Heading(name="sumMap", level=4, num="3.1.2.22"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumMap",
            level=5,
            num="3.1.2.22.1",
        ),
        Heading(name="minMap", level=4, num="3.1.2.23"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MinMap",
            level=5,
            num="3.1.2.23.1",
        ),
        Heading(name="maxMap", level=4, num="3.1.2.24"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MaxMap",
            level=5,
            num="3.1.2.24.1",
        ),
        Heading(name="skewSamp", level=4, num="3.1.2.25"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SkewSamp",
            level=5,
            num="3.1.2.25.1",
        ),
        Heading(name="skewPop", level=4, num="3.1.2.26"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SkewPop",
            level=5,
            num="3.1.2.26.1",
        ),
        Heading(name="kurtSamp", level=4, num="3.1.2.27"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KurtSamp",
            level=5,
            num="3.1.2.27.1",
        ),
        Heading(name="kurtPop", level=4, num="3.1.2.28"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KurtPop",
            level=5,
            num="3.1.2.28.1",
        ),
        Heading(name="uniq", level=4, num="3.1.2.29"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Uniq",
            level=5,
            num="3.1.2.29.1",
        ),
        Heading(name="uniqExact", level=4, num="3.1.2.30"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqExact",
            level=5,
            num="3.1.2.30.1",
        ),
        Heading(name="uniqCombined", level=4, num="3.1.2.31"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqCombined",
            level=5,
            num="3.1.2.31.1",
        ),
        Heading(name="uniqCombined64", level=4, num="3.1.2.32"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqCombined64",
            level=5,
            num="3.1.2.32.1",
        ),
        Heading(name="uniqHLL12", level=4, num="3.1.2.33"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqHLL12",
            level=5,
            num="3.1.2.33.1",
        ),
        Heading(name="quantile", level=4, num="3.1.2.34"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Quantile",
            level=5,
            num="3.1.2.34.1",
        ),
        Heading(name="quantiles", level=4, num="3.1.2.35"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Quantiles",
            level=5,
            num="3.1.2.35.1",
        ),
        Heading(name="quantilesExactExclusive", level=4, num="3.1.2.36"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactExclusive",
            level=5,
            num="3.1.2.36.1",
        ),
        Heading(name="quantilesExactInclusive", level=4, num="3.1.2.37"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactInclusive",
            level=5,
            num="3.1.2.37.1",
        ),
        Heading(name="quantilesDeterministic", level=4, num="3.1.2.38"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesDeterministic",
            level=5,
            num="3.1.2.38.1",
        ),
        Heading(name="quantilesExact", level=4, num="3.1.2.39"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExact",
            level=5,
            num="3.1.2.39.1",
        ),
        Heading(name="quantilesExactHigh", level=4, num="3.1.2.40"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactHigh",
            level=5,
            num="3.1.2.40.1",
        ),
        Heading(name="quantilesExactLow", level=4, num="3.1.2.41"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactLow",
            level=5,
            num="3.1.2.41.1",
        ),
        Heading(name="quantilesExactWeighted", level=4, num="3.1.2.42"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactWeighted",
            level=5,
            num="3.1.2.42.1",
        ),
        Heading(name="quantilesTDigest", level=4, num="3.1.2.43"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTDigest",
            level=5,
            num="3.1.2.43.1",
        ),
        Heading(name="quantilesTDigestWeighted", level=4, num="3.1.2.44"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTDigestWeighted",
            level=5,
            num="3.1.2.44.1",
        ),
        Heading(name="quantilesBFloat16", level=4, num="3.1.2.45"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesBFloat16",
            level=5,
            num="3.1.2.45.1",
        ),
        Heading(name="quantilesBFloat16Weighted", level=4, num="3.1.2.46"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesBFloat16Weighted",
            level=5,
            num="3.1.2.46.1",
        ),
        Heading(name="quantilesTiming", level=4, num="3.1.2.47"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTiming",
            level=5,
            num="3.1.2.47.1",
        ),
        Heading(name="quantilesTimingWeighted", level=4, num="3.1.2.48"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTimingWeighted",
            level=5,
            num="3.1.2.48.1",
        ),
        Heading(name="quantileExact", level=4, num="3.1.2.49"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExact",
            level=5,
            num="3.1.2.49.1",
        ),
        Heading(name="quantileExactLow", level=4, num="3.1.2.50"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactLow",
            level=5,
            num="3.1.2.50.1",
        ),
        Heading(name="quantileExactHigh", level=4, num="3.1.2.51"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactHigh",
            level=5,
            num="3.1.2.51.1",
        ),
        Heading(name="quantileExactWeighted", level=4, num="3.1.2.52"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactWeighted",
            level=5,
            num="3.1.2.52.1",
        ),
        Heading(name="quantileTiming", level=4, num="3.1.2.53"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTiming",
            level=5,
            num="3.1.2.53.1",
        ),
        Heading(name="quantileTimingWeighted", level=4, num="3.1.2.54"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTimingWeighted",
            level=5,
            num="3.1.2.54.1",
        ),
        Heading(name="quantileDeterministic", level=4, num="3.1.2.55"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileDeterministic",
            level=5,
            num="3.1.2.55.1",
        ),
        Heading(name="quantileTDigest", level=4, num="3.1.2.56"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTDigest",
            level=5,
            num="3.1.2.56.1",
        ),
        Heading(name="quantileTDigestWeighted", level=4, num="3.1.2.57"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTDigestWeighted",
            level=5,
            num="3.1.2.57.1",
        ),
        Heading(name="quantileBFloat16", level=4, num="3.1.2.58"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileBFloat16",
            level=5,
            num="3.1.2.58.1",
        ),
        Heading(name="quantileBFloat16Weighted", level=4, num="3.1.2.59"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileBFloat16Weighted",
            level=5,
            num="3.1.2.59.1",
        ),
        Heading(name="simpleLinearRegression", level=4, num="3.1.2.60"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SimpleLinearRegression",
            level=5,
            num="3.1.2.60.1",
        ),
        Heading(name="stochasticLinearRegression", level=4, num="3.1.2.61"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StochasticLinearRegression",
            level=5,
            num="3.1.2.61.1",
        ),
        Heading(name="stochasticLogisticRegression", level=4, num="3.1.2.62"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StochasticLogisticRgression",
            level=5,
            num="3.1.2.62.1",
        ),
        Heading(name="categoricalInformationValue", level=4, num="3.1.2.63"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.CategoricalInformationValue",
            level=5,
            num="3.1.2.63.1",
        ),
        Heading(name="studentTTest", level=4, num="3.1.2.64"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StudentTTest",
            level=5,
            num="3.1.2.64.1",
        ),
        Heading(name="welchTTest", level=4, num="3.1.2.65"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.WelchTTest",
            level=5,
            num="3.1.2.65.1",
        ),
        Heading(name="mannWhitneyUTest", level=4, num="3.1.2.66"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MannWhitneyUTest",
            level=5,
            num="3.1.2.66.1",
        ),
        Heading(name="median", level=4, num="3.1.2.67"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Median",
            level=5,
            num="3.1.2.67.1",
        ),
        Heading(name="rankCorr", level=4, num="3.1.2.68"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.RankCorr",
            level=5,
            num="3.1.2.68.1",
        ),
        Heading(name="entropy", level=4, num="3.1.2.69"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Entropy",
            level=5,
            num="3.1.2.69.1",
        ),
        Heading(name="meanZTest", level=4, num="3.1.2.70"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MeanZTest",
            level=5,
            num="3.1.2.70.1",
        ),
        Heading(name="sparkbar", level=4, num="3.1.2.71"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Sparkbar",
            level=5,
            num="3.1.2.71.1",
        ),
        Heading(name="corr", level=4, num="3.1.2.72"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Corr",
            level=5,
            num="3.1.2.72.1",
        ),
        Heading(name="deltaSum", level=4, num="3.1.2.73"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.DeltaSum",
            level=5,
            num="3.1.2.73.1",
        ),
        Heading(name="deltaSumTimestamp", level=4, num="3.1.2.74"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.DeltaSumTimestamp",
            level=5,
            num="3.1.2.74.1",
        ),
        Heading(name="exponentialMovingAverage", level=4, num="3.1.2.75"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ExponentialMovingAverage",
            level=5,
            num="3.1.2.75.1",
        ),
        Heading(name="intervalLengthSum", level=4, num="3.1.2.76"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.IntervalLengthSum",
            level=5,
            num="3.1.2.76.1",
        ),
        Heading(name="sumCount", level=4, num="3.1.2.77"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumCount",
            level=5,
            num="3.1.2.77.1",
        ),
        Heading(name="sumKahan", level=4, num="3.1.2.78"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumKahan",
            level=5,
            num="3.1.2.78.1",
        ),
        Heading(name="Miscellaneous Functions", level=3, num="3.1.3"),
        Heading(name="first_value", level=4, num="3.1.3.1"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.FirstValue",
            level=5,
            num="3.1.3.1.1",
        ),
        Heading(name="last_value", level=4, num="3.1.3.2"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LastValue",
            level=5,
            num="3.1.3.2.1",
        ),
        Heading(name="lagInFrame", level=4, num="3.1.3.3"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LagInFrame",
            level=5,
            num="3.1.3.3.1",
        ),
        Heading(name="leadInFrame", level=4, num="3.1.3.4"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LeadInFrame",
            level=5,
            num="3.1.3.4.1",
        ),
        Heading(name="nth_value", level=4, num="3.1.3.5"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.NthValue",
            level=5,
            num="3.1.3.5.1",
        ),
        Heading(name="rank", level=4, num="3.1.3.6"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Rank",
            level=5,
            num="3.1.3.6.1",
        ),
        Heading(name="row_number", level=4, num="3.1.3.7"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.RowNumber",
            level=5,
            num="3.1.3.7.1",
        ),
        Heading(name="singleValueOrNull", level=4, num="3.1.3.8"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SingleValueOrNull",
            level=5,
            num="3.1.3.8.1",
        ),
        Heading(name="maxIntersections", level=4, num="3.1.3.9"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxIntersections",
            level=5,
            num="3.1.3.9.1",
        ),
        Heading(name="maxIntersectionsPosition", level=4, num="3.1.3.10"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxIntersectionsPosition",
            level=5,
            num="3.1.3.10.1",
        ),
        Heading(name="aggThrow", level=4, num="3.1.3.11"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.AggThrow",
            level=5,
            num="3.1.3.11.1",
        ),
        Heading(name="boundingRatio", level=4, num="3.1.3.12"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.BoundingRatio",
            level=5,
            num="3.1.3.12.1",
        ),
        Heading(name="contingency", level=4, num="3.1.3.13"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Contingency",
            level=5,
            num="3.1.3.13.1",
        ),
        Heading(name="cramersV", level=4, num="3.1.3.14"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.CramersV",
            level=5,
            num="3.1.3.14.1",
        ),
        Heading(name="cramersVBiasCorrected", level=4, num="3.1.3.15"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.CramersVBiasCorrected",
            level=5,
            num="3.1.3.15.1",
        ),
        Heading(name="dense_rank", level=4, num="3.1.3.16"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.DenseRank",
            level=5,
            num="3.1.3.16.1",
        ),
        Heading(name="exponentialTimeDecayedAvg", level=4, num="3.1.3.17"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedAvg",
            level=5,
            num="3.1.3.17.1",
        ),
        Heading(name="exponentialTimeDecayedCount", level=4, num="3.1.3.18"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedCount",
            level=5,
            num="3.1.3.18.1",
        ),
        Heading(name="exponentialTimeDecayedMax", level=4, num="3.1.3.19"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedMax",
            level=5,
            num="3.1.3.19.1",
        ),
        Heading(name="exponentialTimeDecayedSum", level=4, num="3.1.3.20"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedSum",
            level=5,
            num="3.1.3.20.1",
        ),
        Heading(name="uniqTheta", level=4, num="3.1.3.21"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.UniqTheta",
            level=5,
            num="3.1.3.21.1",
        ),
        Heading(name="quantileExactExclusive", level=4, num="3.1.3.22"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.QuantileExactExclusive",
            level=5,
            num="3.1.3.22.1",
        ),
        Heading(name="quantileExactInclusive", level=4, num="3.1.3.23"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.QuantileExactInclusive",
            level=5,
            num="3.1.3.23.1",
        ),
        Heading(name="sumMapFilteredWithOverflow", level=4, num="3.1.3.24"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMapFilteredWithOverflow",
            level=5,
            num="3.1.3.24.1",
        ),
        Heading(name="sumMapWithOverflow", level=4, num="3.1.3.25"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMapWithOverflow",
            level=5,
            num="3.1.3.25.1",
        ),
        Heading(name="sumMappedArrays", level=4, num="3.1.3.26"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMappedArrays",
            level=5,
            num="3.1.3.26.1",
        ),
        Heading(name="nothing", level=4, num="3.1.3.27"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Nothing",
            level=5,
            num="3.1.3.27.1",
        ),
        Heading(name="maxMappedArrays", level=4, num="3.1.3.28"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxMappedArrays",
            level=5,
            num="3.1.3.28.1",
        ),
        Heading(name="minMappedArrays", level=4, num="3.1.3.29"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MinMappedArrays",
            level=5,
            num="3.1.3.29.1",
        ),
        Heading(name="nonNegativeDerivative", level=4, num="3.1.3.30"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.NonNegativeDerivative",
            level=5,
            num="3.1.3.30.1",
        ),
        Heading(name="theilsU", level=4, num="3.1.3.31"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.TheilsU",
            level=5,
            num="3.1.3.31.1",
        ),
        Heading(name="Parametric Functions", level=3, num="3.1.4"),
        Heading(name="histogram", level=4, num="3.1.4.1"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.Histogram",
            level=5,
            num="3.1.4.1.1",
        ),
        Heading(name="sequenceMatch", level=4, num="3.1.4.2"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceMatch",
            level=5,
            num="3.1.4.2.1",
        ),
        Heading(name="sequenceCount", level=4, num="3.1.4.3"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceCount",
            level=5,
            num="3.1.4.3.1",
        ),
        Heading(name="windowFunnel", level=4, num="3.1.4.4"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.WindowFunnel",
            level=5,
            num="3.1.4.4.1",
        ),
        Heading(name="retention", level=4, num="3.1.4.5"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.Retention",
            level=5,
            num="3.1.4.5.1",
        ),
        Heading(name="uniqUpTo", level=4, num="3.1.4.6"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.UniqUpTo",
            level=5,
            num="3.1.4.6.1",
        ),
        Heading(name="sumMapFiltered", level=4, num="3.1.4.7"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SumMapFiltered",
            level=5,
            num="3.1.4.7.1",
        ),
        Heading(name="sequenceNextNode", level=4, num="3.1.4.8"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceNextNode",
            level=5,
            num="3.1.4.8.1",
        ),
        Heading(name="Combinator Functions", level=2, num="3.2"),
        Heading(name="-If Suffix", level=3, num="3.2.1"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.If",
            level=4,
            num="3.2.1.1",
        ),
        Heading(name="-Array Suffix", level=3, num="3.2.2"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Array",
            level=4,
            num="3.2.2.1",
        ),
        Heading(name="-Map Suffix", level=3, num="3.2.3"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Map",
            level=4,
            num="3.2.3.1",
        ),
        Heading(name="-State Suffix", level=3, num="3.2.4"),
        Heading(name="Test Feature Diagram", level=4, num="3.2.4.1"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State",
            level=4,
            num="3.2.4.2",
        ),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.AggregatingMergeTree",
            level=4,
            num="3.2.4.3",
        ),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.FinalizeAggregationFunction",
            level=4,
            num="3.2.4.4",
        ),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.RunningAccumulateFunction",
            level=4,
            num="3.2.4.5",
        ),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.Merge",
            level=4,
            num="3.2.4.6",
        ),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.MergeState",
            level=4,
            num="3.2.4.7",
        ),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.AggregateFunctionDataType",
            level=4,
            num="3.2.4.8",
        ),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.MaterializedView",
            level=4,
            num="3.2.4.9",
        ),
        Heading(name="-SimpleState Suffix", level=3, num="3.2.5"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.SimpleState",
            level=4,
            num="3.2.5.1",
        ),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.SimpleState.With.AggregatingMergeTree",
            level=4,
            num="3.2.5.2",
        ),
        Heading(name="-Merge Suffix", level=3, num="3.2.6"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Merge",
            level=4,
            num="3.2.6.1",
        ),
        Heading(name="-MergeState Suffix", level=3, num="3.2.7"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.MergeState",
            level=4,
            num="3.2.7.1",
        ),
        Heading(name="-ForEach Suffix", level=3, num="3.2.8"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.ForEach",
            level=4,
            num="3.2.8.1",
        ),
        Heading(name="-Distinct Suffix", level=3, num="3.2.9"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Distinct",
            level=4,
            num="3.2.9.1",
        ),
        Heading(name="-OrDefault Suffix", level=3, num="3.2.10"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.OrDefault",
            level=4,
            num="3.2.10.1",
        ),
        Heading(name="-OrNull Suffix", level=3, num="3.2.11"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.OrNull",
            level=4,
            num="3.2.11.1",
        ),
        Heading(name="-Resample Suffix", level=3, num="3.2.12"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Resample",
            level=4,
            num="3.2.12.1",
        ),
        Heading(name="Data Types", level=2, num="3.3"),
        Heading(name="SimpleAggregateFunction", level=3, num="3.3.1"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.SimpleAggregateFunction",
            level=4,
            num="3.3.1.1",
        ),
        Heading(name="AggregateFunction", level=3, num="3.3.2"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction",
            level=4,
            num="3.3.2.1",
        ),
        Heading(name="Inserting Data", level=4, num="3.3.2.2"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction.Insert",
            level=5,
            num="3.3.2.2.1",
        ),
        Heading(name="Selecting Data", level=4, num="3.3.2.3"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction.Select",
            level=5,
            num="3.3.2.3.1",
        ),
        Heading(name="Grouping", level=2, num="3.4"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.Grouping",
            level=3,
            num="3.4.1",
        ),
        Heading(name="Grouping Sets", level=2, num="3.5"),
        Heading(
            name="RQ.SRS-031.ClickHouse.AggregateFunctions.GroupingSets",
            level=3,
            num="3.5.1",
        ),
        Heading(name="References", level=1, num="4"),
    ),
    requirements=(
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Count,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Count_DistinctImplementationSetting,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Count_OptimizeTrivialCountQuerySetting,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Count_OptimizeFunctionsToSubcolumnsSetting,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Min,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Max,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Sum,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Avg,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Any,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevPop,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevSamp,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_VarPop,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_VarSamp,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarPop,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarSamp,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AnyHeavy,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AnyLast,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMin,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMax,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AvgWeighted,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_TopK,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_TopKWeighted,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArray,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupUniqArray,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayInsertAt,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayMovingAvg,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayMovingSum,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArraySample,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitAnd,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitOr,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitXor,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmap,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapAnd,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapOr,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapXor,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumWithOverflow,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumMap,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MinMap,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MaxMap,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SkewSamp,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SkewPop,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_KurtSamp,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_KurtPop,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Uniq,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqExact,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqCombined,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqCombined64,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqHLL12,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Quantile,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Quantiles,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExactExclusive,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExactInclusive,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesDeterministic,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExact,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExactHigh,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExactLow,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExactWeighted,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesTDigest,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesTDigestWeighted,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesBFloat16,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesBFloat16Weighted,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesTiming,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesTimingWeighted,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileExact,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileExactLow,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileExactHigh,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileExactWeighted,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileTiming,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileTimingWeighted,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileDeterministic,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileTDigest,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileTDigestWeighted,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileBFloat16,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileBFloat16Weighted,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SimpleLinearRegression,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StochasticLinearRegression,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StochasticLogisticRgression,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_CategoricalInformationValue,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StudentTTest,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_WelchTTest,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MannWhitneyUTest,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Median,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_RankCorr,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Entropy,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MeanZTest,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Sparkbar,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Corr,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_DeltaSum,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_DeltaSumTimestamp,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ExponentialMovingAverage,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_IntervalLengthSum,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumCount,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumKahan,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_FirstValue,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LastValue,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LagInFrame,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LeadInFrame,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_NthValue,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Rank,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_RowNumber,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SingleValueOrNull,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_MaxIntersections,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_MaxIntersectionsPosition,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_AggThrow,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_BoundingRatio,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Contingency,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_CramersV,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_CramersVBiasCorrected,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_DenseRank,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedAvg,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedCount,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedMax,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedSum,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_UniqTheta,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_QuantileExactExclusive,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_QuantileExactInclusive,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SumMapFilteredWithOverflow,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SumMapWithOverflow,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SumMappedArrays,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Nothing,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_MaxMappedArrays,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_MinMappedArrays,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_NonNegativeDerivative,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_TheilsU,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_Histogram,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SequenceMatch,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SequenceCount,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_WindowFunnel,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_Retention,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_UniqUpTo,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SumMapFiltered,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SequenceNextNode,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_If,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Array,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Map,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_AggregatingMergeTree,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_FinalizeAggregationFunction,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_RunningAccumulateFunction,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_Merge,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_MergeState,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_AggregateFunctionDataType,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_MaterializedView,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_SimpleState,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_SimpleState_With_AggregatingMergeTree,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Merge,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_MergeState,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_ForEach,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Distinct,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_OrDefault,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_OrNull,
        RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Resample,
        RQ_SRS_031_ClickHouse_AggregateFunctions_DataType_SimpleAggregateFunction,
        RQ_SRS_031_ClickHouse_AggregateFunctions_DataType_AggregateFunction,
    ),
    content="""
# SRS-031 ClickHouse Aggregate Functions
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Requirements](#requirements)
  * 3.1 [Aggregate Functions](#aggregate-functions)
    * 3.1.1 [Standard Functions](#standard-functions)
      * 3.1.1.1 [count](#count)
        * 3.1.1.1.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count](#rqsrs-031clickhouseaggregatefunctionsstandardcount)
        * 3.1.1.1.2 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.DistinctImplementationSetting](#rqsrs-031clickhouseaggregatefunctionsstandardcountdistinctimplementationsetting)
        * 3.1.1.1.3 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.OptimizeTrivialCountQuerySetting](#rqsrs-031clickhouseaggregatefunctionsstandardcountoptimizetrivialcountquerysetting)
        * 3.1.1.1.4 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.OptimizeFunctionsToSubcolumnsSetting](#rqsrs-031clickhouseaggregatefunctionsstandardcountoptimizefunctionstosubcolumnssetting)
      * 3.1.1.2 [min](#min)
        * 3.1.1.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Min](#rqsrs-031clickhouseaggregatefunctionsstandardmin)
      * 3.1.1.3 [max](#max)
        * 3.1.1.3.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Max](#rqsrs-031clickhouseaggregatefunctionsstandardmax)
      * 3.1.1.4 [sum](#sum)
        * 3.1.1.4.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Sum](#rqsrs-031clickhouseaggregatefunctionsstandardsum)
      * 3.1.1.5 [avg](#avg)
        * 3.1.1.5.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Avg](#rqsrs-031clickhouseaggregatefunctionsstandardavg)
      * 3.1.1.6 [any](#any)
        * 3.1.1.6.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Any](#rqsrs-031clickhouseaggregatefunctionsstandardany)
      * 3.1.1.7 [stddevPop](#stddevpop)
        * 3.1.1.7.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.StddevPop](#rqsrs-031clickhouseaggregatefunctionsstandardstddevpop)
      * 3.1.1.8 [stddevSamp](#stddevsamp)
        * 3.1.1.8.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.StddevSamp](#rqsrs-031clickhouseaggregatefunctionsstandardstddevsamp)
      * 3.1.1.9 [varPop](#varpop)
        * 3.1.1.9.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.VarPop](#rqsrs-031clickhouseaggregatefunctionsstandardvarpop)
      * 3.1.1.10 [varSamp](#varsamp)
        * 3.1.1.10.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.VarSamp](#rqsrs-031clickhouseaggregatefunctionsstandardvarsamp)
      * 3.1.1.11 [covarPop](#covarpop)
        * 3.1.1.11.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.CovarPop](#rqsrs-031clickhouseaggregatefunctionsstandardcovarpop)
      * 3.1.1.12 [covarSamp](#covarsamp)
        * 3.1.1.12.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.CovarSamp](#rqsrs-031clickhouseaggregatefunctionsstandardcovarsamp)
    * 3.1.2 [Specific Functions](#specific-functions)
      * 3.1.2.1 [anyHeavy](#anyheavy)
        * 3.1.2.1.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AnyHeavy](#rqsrs-031clickhouseaggregatefunctionsspecificanyheavy)
      * 3.1.2.2 [anyLast](#anylast)
        * 3.1.2.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AnyLast](#rqsrs-031clickhouseaggregatefunctionsspecificanylast)
      * 3.1.2.3 [argMin](#argmin)
        * 3.1.2.3.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ArgMin](#rqsrs-031clickhouseaggregatefunctionsspecificargmin)
      * 3.1.2.4 [argMax](#argmax)
        * 3.1.2.4.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ArgMax](#rqsrs-031clickhouseaggregatefunctionsspecificargmax)
      * 3.1.2.5 [avgWeighted](#avgweighted)
        * 3.1.2.5.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AvgWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificavgweighted)
      * 3.1.2.6 [topK](#topk)
        * 3.1.2.6.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.TopK](#rqsrs-031clickhouseaggregatefunctionsspecifictopk)
      * 3.1.2.7 [topKWeighted](#topkweighted)
        * 3.1.2.7.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.TopKWeighted](#rqsrs-031clickhouseaggregatefunctionsspecifictopkweighted)
      * 3.1.2.8 [groupArray](#grouparray)
        * 3.1.2.8.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArray](#rqsrs-031clickhouseaggregatefunctionsspecificgrouparray)
      * 3.1.2.9 [groupUniqArray](#groupuniqarray)
        * 3.1.2.9.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupUniqArray](#rqsrs-031clickhouseaggregatefunctionsspecificgroupuniqarray)
      * 3.1.2.10 [groupArrayInsertAt](#grouparrayinsertat)
        * 3.1.2.10.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayInsertAt](#rqsrs-031clickhouseaggregatefunctionsspecificgrouparrayinsertat)
      * 3.1.2.11 [groupArrayMovingAvg](#grouparraymovingavg)
        * 3.1.2.11.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayMovingAvg](#rqsrs-031clickhouseaggregatefunctionsspecificgrouparraymovingavg)
      * 3.1.2.12 [groupArrayMovingSum](#grouparraymovingsum)
        * 3.1.2.12.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayMovingSum](#rqsrs-031clickhouseaggregatefunctionsspecificgrouparraymovingsum)
      * 3.1.2.13 [groupArraySample](#grouparraysample)
        * 3.1.2.13.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArraySample](#rqsrs-031clickhouseaggregatefunctionsspecificgrouparraysample)
      * 3.1.2.14 [groupBitAnd](#groupbitand)
        * 3.1.2.14.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitAnd](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitand)
      * 3.1.2.15 [groupBitOr](#groupbitor)
        * 3.1.2.15.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitOr](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitor)
      * 3.1.2.16 [groupBitXor](#groupbitxor)
        * 3.1.2.16.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitXor](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitxor)
      * 3.1.2.17 [groupBitmap](#groupbitmap)
        * 3.1.2.17.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmap](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitmap)
      * 3.1.2.18 [groupBitmapAnd](#groupbitmapand)
        * 3.1.2.18.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapAnd](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitmapand)
      * 3.1.2.19 [groupBitmapOr](#groupbitmapor)
        * 3.1.2.19.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapOr](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitmapor)
      * 3.1.2.20 [groupBitmapXor](#groupbitmapxor)
        * 3.1.2.20.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapXor](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitmapxor)
      * 3.1.2.21 [sumWithOverflow](#sumwithoverflow)
        * 3.1.2.21.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumWithOverflow](#rqsrs-031clickhouseaggregatefunctionsspecificsumwithoverflow)
      * 3.1.2.22 [sumMap](#summap)
        * 3.1.2.22.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumMap](#rqsrs-031clickhouseaggregatefunctionsspecificsummap)
      * 3.1.2.23 [minMap](#minmap)
        * 3.1.2.23.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MinMap](#rqsrs-031clickhouseaggregatefunctionsspecificminmap)
      * 3.1.2.24 [maxMap](#maxmap)
        * 3.1.2.24.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MaxMap](#rqsrs-031clickhouseaggregatefunctionsspecificmaxmap)
      * 3.1.2.25 [skewSamp](#skewsamp)
        * 3.1.2.25.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SkewSamp](#rqsrs-031clickhouseaggregatefunctionsspecificskewsamp)
      * 3.1.2.26 [skewPop](#skewpop)
        * 3.1.2.26.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SkewPop](#rqsrs-031clickhouseaggregatefunctionsspecificskewpop)
      * 3.1.2.27 [kurtSamp](#kurtsamp)
        * 3.1.2.27.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KurtSamp](#rqsrs-031clickhouseaggregatefunctionsspecifickurtsamp)
      * 3.1.2.28 [kurtPop](#kurtpop)
        * 3.1.2.28.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KurtPop](#rqsrs-031clickhouseaggregatefunctionsspecifickurtpop)
      * 3.1.2.29 [uniq](#uniq)
        * 3.1.2.29.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Uniq](#rqsrs-031clickhouseaggregatefunctionsspecificuniq)
      * 3.1.2.30 [uniqExact](#uniqexact)
        * 3.1.2.30.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqExact](#rqsrs-031clickhouseaggregatefunctionsspecificuniqexact)
      * 3.1.2.31 [uniqCombined](#uniqcombined)
        * 3.1.2.31.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqCombined](#rqsrs-031clickhouseaggregatefunctionsspecificuniqcombined)
      * 3.1.2.32 [uniqCombined64](#uniqcombined64)
        * 3.1.2.32.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqCombined64](#rqsrs-031clickhouseaggregatefunctionsspecificuniqcombined64)
      * 3.1.2.33 [uniqHLL12](#uniqhll12)
        * 3.1.2.33.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqHLL12](#rqsrs-031clickhouseaggregatefunctionsspecificuniqhll12)
      * 3.1.2.34 [quantile](#quantile)
        * 3.1.2.34.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Quantile](#rqsrs-031clickhouseaggregatefunctionsspecificquantile)
      * 3.1.2.35 [quantiles](#quantiles)
        * 3.1.2.35.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Quantiles](#rqsrs-031clickhouseaggregatefunctionsspecificquantiles)
      * 3.1.2.36 [quantilesExactExclusive](#quantilesexactexclusive)
        * 3.1.2.36.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactExclusive](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesexactexclusive)
      * 3.1.2.37 [quantilesExactInclusive](#quantilesexactinclusive)
        * 3.1.2.37.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactInclusive](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesexactinclusive)
      * 3.1.2.38 [quantilesDeterministic](#quantilesdeterministic)
        * 3.1.2.38.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesDeterministic](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesdeterministic)
      * 3.1.2.39 [quantilesExact](#quantilesexact)
        * 3.1.2.39.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExact](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesexact)
      * 3.1.2.40 [quantilesExactHigh](#quantilesexacthigh)
        * 3.1.2.40.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactHigh](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesexacthigh)
      * 3.1.2.41 [quantilesExactLow](#quantilesexactlow)
        * 3.1.2.41.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactLow](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesexactlow)
      * 3.1.2.42 [quantilesExactWeighted](#quantilesexactweighted)
        * 3.1.2.42.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesexactweighted)
      * 3.1.2.43 [quantilesTDigest](#quantilestdigest)
        * 3.1.2.43.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTDigest](#rqsrs-031clickhouseaggregatefunctionsspecificquantilestdigest)
      * 3.1.2.44 [quantilesTDigestWeighted](#quantilestdigestweighted)
        * 3.1.2.44.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTDigestWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantilestdigestweighted)
      * 3.1.2.45 [quantilesBFloat16](#quantilesbfloat16)
        * 3.1.2.45.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesBFloat16](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesbfloat16)
      * 3.1.2.46 [quantilesBFloat16Weighted](#quantilesbfloat16weighted)
        * 3.1.2.46.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesBFloat16Weighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesbfloat16weighted)
      * 3.1.2.47 [quantilesTiming](#quantilestiming)
        * 3.1.2.47.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTiming](#rqsrs-031clickhouseaggregatefunctionsspecificquantilestiming)
      * 3.1.2.48 [quantilesTimingWeighted](#quantilestimingweighted)
        * 3.1.2.48.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTimingWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantilestimingweighted)
      * 3.1.2.49 [quantileExact](#quantileexact)
        * 3.1.2.49.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExact](#rqsrs-031clickhouseaggregatefunctionsspecificquantileexact)
      * 3.1.2.50 [quantileExactLow](#quantileexactlow)
        * 3.1.2.50.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactLow](#rqsrs-031clickhouseaggregatefunctionsspecificquantileexactlow)
      * 3.1.2.51 [quantileExactHigh](#quantileexacthigh)
        * 3.1.2.51.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactHigh](#rqsrs-031clickhouseaggregatefunctionsspecificquantileexacthigh)
      * 3.1.2.52 [quantileExactWeighted](#quantileexactweighted)
        * 3.1.2.52.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantileexactweighted)
      * 3.1.2.53 [quantileTiming](#quantiletiming)
        * 3.1.2.53.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTiming](#rqsrs-031clickhouseaggregatefunctionsspecificquantiletiming)
      * 3.1.2.54 [quantileTimingWeighted](#quantiletimingweighted)
        * 3.1.2.54.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTimingWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantiletimingweighted)
      * 3.1.2.55 [quantileDeterministic](#quantiledeterministic)
        * 3.1.2.55.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileDeterministic](#rqsrs-031clickhouseaggregatefunctionsspecificquantiledeterministic)
      * 3.1.2.56 [quantileTDigest](#quantiletdigest)
        * 3.1.2.56.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTDigest](#rqsrs-031clickhouseaggregatefunctionsspecificquantiletdigest)
      * 3.1.2.57 [quantileTDigestWeighted](#quantiletdigestweighted)
        * 3.1.2.57.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTDigestWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantiletdigestweighted)
      * 3.1.2.58 [quantileBFloat16](#quantilebfloat16)
        * 3.1.2.58.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileBFloat16](#rqsrs-031clickhouseaggregatefunctionsspecificquantilebfloat16)
      * 3.1.2.59 [quantileBFloat16Weighted](#quantilebfloat16weighted)
        * 3.1.2.59.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileBFloat16Weighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantilebfloat16weighted)
      * 3.1.2.60 [simpleLinearRegression](#simplelinearregression)
        * 3.1.2.60.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SimpleLinearRegression](#rqsrs-031clickhouseaggregatefunctionsspecificsimplelinearregression)
      * 3.1.2.61 [stochasticLinearRegression](#stochasticlinearregression)
        * 3.1.2.61.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StochasticLinearRegression](#rqsrs-031clickhouseaggregatefunctionsspecificstochasticlinearregression)
      * 3.1.2.62 [stochasticLogisticRegression](#stochasticlogisticregression)
        * 3.1.2.62.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StochasticLogisticRgression](#rqsrs-031clickhouseaggregatefunctionsspecificstochasticlogisticrgression)
      * 3.1.2.63 [categoricalInformationValue](#categoricalinformationvalue)
        * 3.1.2.63.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.CategoricalInformationValue](#rqsrs-031clickhouseaggregatefunctionsspecificcategoricalinformationvalue)
      * 3.1.2.64 [studentTTest](#studentttest)
        * 3.1.2.64.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StudentTTest](#rqsrs-031clickhouseaggregatefunctionsspecificstudentttest)
      * 3.1.2.65 [welchTTest](#welchttest)
        * 3.1.2.65.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.WelchTTest](#rqsrs-031clickhouseaggregatefunctionsspecificwelchttest)
      * 3.1.2.66 [mannWhitneyUTest](#mannwhitneyutest)
        * 3.1.2.66.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MannWhitneyUTest](#rqsrs-031clickhouseaggregatefunctionsspecificmannwhitneyutest)
      * 3.1.2.67 [median](#median)
        * 3.1.2.67.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Median](#rqsrs-031clickhouseaggregatefunctionsspecificmedian)
      * 3.1.2.68 [rankCorr](#rankcorr)
        * 3.1.2.68.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.RankCorr](#rqsrs-031clickhouseaggregatefunctionsspecificrankcorr)
      * 3.1.2.69 [entropy](#entropy)
        * 3.1.2.69.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Entropy](#rqsrs-031clickhouseaggregatefunctionsspecificentropy)
      * 3.1.2.70 [meanZTest](#meanztest)
        * 3.1.2.70.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MeanZTest](#rqsrs-031clickhouseaggregatefunctionsspecificmeanztest)
      * 3.1.2.71 [sparkbar](#sparkbar)
        * 3.1.2.71.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Sparkbar](#rqsrs-031clickhouseaggregatefunctionsspecificsparkbar)
      * 3.1.2.72 [corr](#corr)
        * 3.1.2.72.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Corr](#rqsrs-031clickhouseaggregatefunctionsspecificcorr)
      * 3.1.2.73 [deltaSum](#deltasum)
        * 3.1.2.73.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.DeltaSum](#rqsrs-031clickhouseaggregatefunctionsspecificdeltasum)
      * 3.1.2.74 [deltaSumTimestamp](#deltasumtimestamp)
        * 3.1.2.74.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.DeltaSumTimestamp](#rqsrs-031clickhouseaggregatefunctionsspecificdeltasumtimestamp)
      * 3.1.2.75 [exponentialMovingAverage](#exponentialmovingaverage)
        * 3.1.2.75.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ExponentialMovingAverage](#rqsrs-031clickhouseaggregatefunctionsspecificexponentialmovingaverage)
      * 3.1.2.76 [intervalLengthSum](#intervallengthsum)
        * 3.1.2.76.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.IntervalLengthSum](#rqsrs-031clickhouseaggregatefunctionsspecificintervallengthsum)
      * 3.1.2.77 [sumCount](#sumcount)
        * 3.1.2.77.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumCount](#rqsrs-031clickhouseaggregatefunctionsspecificsumcount)
      * 3.1.2.78 [sumKahan](#sumkahan)
        * 3.1.2.78.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumKahan](#rqsrs-031clickhouseaggregatefunctionsspecificsumkahan)
    * 3.1.3 [Miscellaneous Functions](#miscellaneous-functions)
      * 3.1.3.1 [first_value](#first_value)
        * 3.1.3.1.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.FirstValue](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousfirstvalue)
      * 3.1.3.2 [last_value](#last_value)
        * 3.1.3.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LastValue](#rqsrs-031clickhouseaggregatefunctionsmiscellaneouslastvalue)
      * 3.1.3.3 [lagInFrame](#laginframe)
        * 3.1.3.3.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LagInFrame](#rqsrs-031clickhouseaggregatefunctionsmiscellaneouslaginframe)
      * 3.1.3.4 [leadInFrame](#leadinframe)
        * 3.1.3.4.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LeadInFrame](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousleadinframe)
      * 3.1.3.5 [nth_value](#nth_value)
        * 3.1.3.5.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.NthValue](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousnthvalue)
      * 3.1.3.6 [rank](#rank)
        * 3.1.3.6.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Rank](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousrank)
      * 3.1.3.7 [row_number](#row_number)
        * 3.1.3.7.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.RowNumber](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousrownumber)
      * 3.1.3.8 [singleValueOrNull](#singlevalueornull)
        * 3.1.3.8.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SingleValueOrNull](#rqsrs-031clickhouseaggregatefunctionsmiscellaneoussinglevalueornull)
      * 3.1.3.9 [maxIntersections](#maxintersections)
        * 3.1.3.9.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxIntersections](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousmaxintersections)
      * 3.1.3.10 [maxIntersectionsPosition](#maxintersectionsposition)
        * 3.1.3.10.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxIntersectionsPosition](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousmaxintersectionsposition)
      * 3.1.3.11 [aggThrow](#aggthrow)
        * 3.1.3.11.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.AggThrow](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousaggthrow)
      * 3.1.3.12 [boundingRatio](#boundingratio)
        * 3.1.3.12.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.BoundingRatio](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousboundingratio)
      * 3.1.3.13 [contingency](#contingency)
        * 3.1.3.13.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Contingency](#rqsrs-031clickhouseaggregatefunctionsmiscellaneouscontingency)
      * 3.1.3.14 [cramersV](#cramersv)
        * 3.1.3.14.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.CramersV](#rqsrs-031clickhouseaggregatefunctionsmiscellaneouscramersv)
      * 3.1.3.15 [cramersVBiasCorrected](#cramersvbiascorrected)
        * 3.1.3.15.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.CramersVBiasCorrected](#rqsrs-031clickhouseaggregatefunctionsmiscellaneouscramersvbiascorrected)
      * 3.1.3.16 [dense_rank](#dense_rank)
        * 3.1.3.16.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.DenseRank](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousdenserank)
      * 3.1.3.17 [exponentialTimeDecayedAvg](#exponentialtimedecayedavg)
        * 3.1.3.17.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedAvg](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousexponentialtimedecayedavg)
      * 3.1.3.18 [exponentialTimeDecayedCount](#exponentialtimedecayedcount)
        * 3.1.3.18.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedCount](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousexponentialtimedecayedcount)
      * 3.1.3.19 [exponentialTimeDecayedMax](#exponentialtimedecayedmax)
        * 3.1.3.19.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedMax](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousexponentialtimedecayedmax)
      * 3.1.3.20 [exponentialTimeDecayedSum](#exponentialtimedecayedsum)
        * 3.1.3.20.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedSum](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousexponentialtimedecayedsum)
      * 3.1.3.21 [uniqTheta](#uniqtheta)
        * 3.1.3.21.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.UniqTheta](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousuniqtheta)
      * 3.1.3.22 [quantileExactExclusive](#quantileexactexclusive)
        * 3.1.3.22.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.QuantileExactExclusive](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousquantileexactexclusive)
      * 3.1.3.23 [quantileExactInclusive](#quantileexactinclusive)
        * 3.1.3.23.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.QuantileExactInclusive](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousquantileexactinclusive)
      * 3.1.3.24 [sumMapFilteredWithOverflow](#summapfilteredwithoverflow)
        * 3.1.3.24.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMapFilteredWithOverflow](#rqsrs-031clickhouseaggregatefunctionsmiscellaneoussummapfilteredwithoverflow)
      * 3.1.3.25 [sumMapWithOverflow](#summapwithoverflow)
        * 3.1.3.25.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMapWithOverflow](#rqsrs-031clickhouseaggregatefunctionsmiscellaneoussummapwithoverflow)
      * 3.1.3.26 [sumMappedArrays](#summappedarrays)
        * 3.1.3.26.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMappedArrays](#rqsrs-031clickhouseaggregatefunctionsmiscellaneoussummappedarrays)
      * 3.1.3.27 [nothing](#nothing)
        * 3.1.3.27.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Nothing](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousnothing)
      * 3.1.3.28 [maxMappedArrays](#maxmappedarrays)
        * 3.1.3.28.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxMappedArrays](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousmaxmappedarrays)
      * 3.1.3.29 [minMappedArrays](#minmappedarrays)
        * 3.1.3.29.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MinMappedArrays](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousminmappedarrays)
      * 3.1.3.30 [nonNegativeDerivative](#nonnegativederivative)
        * 3.1.3.30.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.NonNegativeDerivative](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousnonnegativederivative)
      * 3.1.3.31 [theilsU](#theilsu)
        * 3.1.3.31.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.TheilsU](#rqsrs-031clickhouseaggregatefunctionsmiscellaneoustheilsu)
    * 3.1.4 [Parametric Functions](#parametric-functions)
      * 3.1.4.1 [histogram](#histogram)
        * 3.1.4.1.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.Histogram](#rqsrs-031clickhouseaggregatefunctionsparametrichistogram)
      * 3.1.4.2 [sequenceMatch](#sequencematch)
        * 3.1.4.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceMatch](#rqsrs-031clickhouseaggregatefunctionsparametricsequencematch)
      * 3.1.4.3 [sequenceCount](#sequencecount)
        * 3.1.4.3.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceCount](#rqsrs-031clickhouseaggregatefunctionsparametricsequencecount)
      * 3.1.4.4 [windowFunnel](#windowfunnel)
        * 3.1.4.4.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.WindowFunnel](#rqsrs-031clickhouseaggregatefunctionsparametricwindowfunnel)
      * 3.1.4.5 [retention](#retention)
        * 3.1.4.5.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.Retention](#rqsrs-031clickhouseaggregatefunctionsparametricretention)
      * 3.1.4.6 [uniqUpTo](#uniqupto)
        * 3.1.4.6.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.UniqUpTo](#rqsrs-031clickhouseaggregatefunctionsparametricuniqupto)
      * 3.1.4.7 [sumMapFiltered](#summapfiltered)
        * 3.1.4.7.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SumMapFiltered](#rqsrs-031clickhouseaggregatefunctionsparametricsummapfiltered)
      * 3.1.4.8 [sequenceNextNode](#sequencenextnode)
        * 3.1.4.8.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceNextNode](#rqsrs-031clickhouseaggregatefunctionsparametricsequencenextnode)
  * 3.2 [Combinator Functions](#combinator-functions)
    * 3.2.1 [-If Suffix](#-if-suffix)
      * 3.2.1.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.If](#rqsrs-031clickhouseaggregatefunctionscombinatorif)
    * 3.2.2 [-Array Suffix](#-array-suffix)
      * 3.2.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Array](#rqsrs-031clickhouseaggregatefunctionscombinatorarray)
    * 3.2.3 [-Map Suffix](#-map-suffix)
      * 3.2.3.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Map](#rqsrs-031clickhouseaggregatefunctionscombinatormap)
    * 3.2.4 [-State Suffix](#-state-suffix)
      * 3.2.4.1 [Test Feature Diagram](#test-feature-diagram)
      * 3.2.4.2 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State](#rqsrs-031clickhouseaggregatefunctionscombinatorstate)
      * 3.2.4.3 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.AggregatingMergeTree](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithaggregatingmergetree)
      * 3.2.4.4 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.FinalizeAggregationFunction](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithfinalizeaggregationfunction)
      * 3.2.4.5 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.RunningAccumulateFunction](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithrunningaccumulatefunction)
      * 3.2.4.6 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.Merge](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithmerge)
      * 3.2.4.7 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.MergeState](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithmergestate)
      * 3.2.4.8 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.AggregateFunctionDataType](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithaggregatefunctiondatatype)
      * 3.2.4.9 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.MaterializedView](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithmaterializedview)
    * 3.2.5 [-SimpleState Suffix](#-simplestate-suffix)
      * 3.2.5.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.SimpleState](#rqsrs-031clickhouseaggregatefunctionscombinatorsimplestate)
      * 3.2.5.2 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.SimpleState.With.AggregatingMergeTree](#rqsrs-031clickhouseaggregatefunctionscombinatorsimplestatewithaggregatingmergetree)
    * 3.2.6 [-Merge Suffix](#-merge-suffix)
      * 3.2.6.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Merge](#rqsrs-031clickhouseaggregatefunctionscombinatormerge)
    * 3.2.7 [-MergeState Suffix](#-mergestate-suffix)
      * 3.2.7.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.MergeState](#rqsrs-031clickhouseaggregatefunctionscombinatormergestate)
    * 3.2.8 [-ForEach Suffix](#-foreach-suffix)
      * 3.2.8.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.ForEach](#rqsrs-031clickhouseaggregatefunctionscombinatorforeach)
    * 3.2.9 [-Distinct Suffix](#-distinct-suffix)
      * 3.2.9.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Distinct](#rqsrs-031clickhouseaggregatefunctionscombinatordistinct)
    * 3.2.10 [-OrDefault Suffix](#-ordefault-suffix)
      * 3.2.10.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.OrDefault](#rqsrs-031clickhouseaggregatefunctionscombinatorordefault)
    * 3.2.11 [-OrNull Suffix](#-ornull-suffix)
      * 3.2.11.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.OrNull](#rqsrs-031clickhouseaggregatefunctionscombinatorornull)
    * 3.2.12 [-Resample Suffix](#-resample-suffix)
      * 3.2.12.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Resample](#rqsrs-031clickhouseaggregatefunctionscombinatorresample)
  * 3.3 [Data Types](#data-types)
    * 3.3.1 [SimpleAggregateFunction](#simpleaggregatefunction)
      * 3.3.1.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.SimpleAggregateFunction](#rqsrs-031clickhouseaggregatefunctionsdatatypesimpleaggregatefunction)
    * 3.3.2 [AggregateFunction](#aggregatefunction)
      * 3.3.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction](#rqsrs-031clickhouseaggregatefunctionsdatatypeaggregatefunction)
      * 3.3.2.2 [Inserting Data](#inserting-data)
        * 3.3.2.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction.Insert](#rqsrs-031clickhouseaggregatefunctionsdatatypeaggregatefunctioninsert)
      * 3.3.2.3 [Selecting Data](#selecting-data)
        * 3.3.2.3.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction.Select](#rqsrs-031clickhouseaggregatefunctionsdatatypeaggregatefunctionselect)
  * 3.4 [Grouping](#grouping)
    * 3.4.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Grouping](#rqsrs-031clickhouseaggregatefunctionsgrouping)
  * 3.5 [Grouping Sets](#grouping-sets)
    * 3.5.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.GroupingSets](#rqsrs-031clickhouseaggregatefunctionsgroupingsets)
* 4 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for [aggregate function]s and corresponding
data types in [ClickHouse].

## Requirements

### Aggregate Functions

#### Standard Functions

##### count

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count
version: 1.0

[ClickHouse] SHALL support [count] standard aggregate function.

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.DistinctImplementationSetting
version: 1.0

[ClickHouse] SHALL support [count_distinct_implementation](https://clickhouse.com/docs/en/operations/settings/settings#settings-count_distinct_implementation) setting that SHALL specify
which `uniq*` function SHALL be used to calculate `COUNT(DISTINCT expr)`. 

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.OptimizeTrivialCountQuerySetting
version: 1.0

[ClickHouse] SHALL support [optimize_trivial_count_query]https://clickhouse.com/docs/en/operations/settings/settings#optimize-trivial-count-query setting that SHALL enable or disable
the optimization of trivial `SELECT count() FROM table` query using metadata from [MergeTree] tables.


###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.OptimizeFunctionsToSubcolumnsSetting
version: 1.0

[ClickHouse] SHALL support optimizing `SELECT count(nullable_column) FROM table` query by enabling the
[optimize_functions_to_subcolumns](https://clickhouse.com/docs/en/operations/settings/settings#optimize-functions-to-subcolumns) setting. With `optimize_functions_to_subcolumns=1` the function SHALL
read only null sub-column instead of reading and processing the whole column data.

The query `SELECT count(n) FROM table` SHALL be transformed to `SELECT sum(NOT n.null) FROM table`.

##### min

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Min
version: 1.0

[ClickHouse] SHALL support [min] standard aggregate function.

##### max

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Max
version: 1.0

[ClickHouse] SHALL support [max] standard aggregate function.

##### sum

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Sum
version: 1.0

[ClickHouse] SHALL support [sum] standard aggregate function.

##### avg

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Avg
version: 1.0

[ClickHouse] SHALL support [avg] standard aggregate function.

##### any

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Any
version: 1.0

[ClickHouse] SHALL support [any] standard aggregate function.

##### stddevPop

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.StddevPop
version: 1.0

[ClickHouse] SHALL support [stddevPop] standard aggregate function.

##### stddevSamp

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.StddevSamp
version: 1.0

[ClickHouse] SHALL support [stddevSamp] standard aggregate function.

##### varPop

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.VarPop
version: 1.0

[ClickHouse] SHALL support [varPop] standard aggregate function.

##### varSamp

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.VarSamp
version: 1.0

[ClickHouse] SHALL support [varSamp] standard aggregate function.

##### covarPop

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.CovarPop
version: 1.0

[ClickHouse] SHALL support [covarPop] standard aggregate function.

##### covarSamp

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.CovarSamp
version: 1.0

[ClickHouse] SHALL support [covarSamp] standard aggregate function.

#### Specific Functions

##### anyHeavy

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AnyHeavy
version: 1.0

[ClickHouse] SHALL support [anyHeavy] specific aggregate function.

##### anyLast

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AnyLast
version: 1.0

[ClickHouse] SHALL support [anyLast] specific aggregate function.

##### argMin

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ArgMin
version: 1.0

[ClickHouse] SHALL support [argMin] specific aggregate function.

##### argMax

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ArgMax
version: 1.0

[ClickHouse] SHALL support [argMax] specific aggregate function.

##### avgWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AvgWeighted
version: 1.0

[ClickHouse] SHALL support [avgWeighted] specific aggregate function.

##### topK

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.TopK
version: 1.0

[ClickHouse] SHALL support [topK] specific aggregate function.

##### topKWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.TopKWeighted
version: 1.0

[ClickHouse] SHALL support [topKWeighted] specific aggregate function.

##### groupArray

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArray
version: 1.0

[ClickHouse] SHALL support [groupArray] specific aggregate function.

##### groupUniqArray

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupUniqArray
version: 1.0

[ClickHouse] SHALL support [groupUniqArray] specific aggregate function.

##### groupArrayInsertAt

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayInsertAt
version: 1.0

[ClickHouse] SHALL support [groupArrayInsertAt] specific aggregate function.

##### groupArrayMovingAvg

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayMovingAvg
version: 1.0

[ClickHouse] SHALL support [groupArrayMovingAvg] specific aggregate function.

##### groupArrayMovingSum

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayMovingSum
version: 1.0

[ClickHouse] SHALL support [groupArrayMovingSum] specific aggregate function.

##### groupArraySample

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArraySample
version: 1.0

[ClickHouse] SHALL support [groupArraySample] specific aggregate function.

##### groupBitAnd

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitAnd
version: 1.0

[ClickHouse] SHALL support [groupBitAnd] specific aggregate function.

##### groupBitOr

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitOr
version: 1.0

[ClickHouse] SHALL support [groupBitOr] specific aggregate function.

##### groupBitXor

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitXor
version: 1.0

[ClickHouse] SHALL support [groupBitXor] specific aggregate function.

##### groupBitmap

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmap
version: 1.0

[ClickHouse] SHALL support [groupBitmap] specific aggregate function.

##### groupBitmapAnd

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapAnd
version: 1.0

[ClickHouse] SHALL support [groupBitmapAnd] specific aggregate function.

##### groupBitmapOr

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapOr
version: 1.0

[ClickHouse] SHALL support [groupBitmapOr] specific aggregate function.

##### groupBitmapXor

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapXor
version: 1.0

[ClickHouse] SHALL support [groupBitmapXor] specific aggregate function.

##### sumWithOverflow

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumWithOverflow
version: 1.0

[ClickHouse] SHALL support [sumWithOverflow] specific aggregate function.

##### sumMap

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumMap
version: 1.0

[ClickHouse] SHALL support [sumMap] specific aggregate function.

##### minMap

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MinMap
version: 1.0

[ClickHouse] SHALL support [minMap] specific aggregate function.

##### maxMap

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MaxMap
version: 1.0

[ClickHouse] SHALL support [maxMap] specific aggregate function.

##### skewSamp

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SkewSamp
version: 1.0

[ClickHouse] SHALL support [skewSamp] specific aggregate function.

##### skewPop

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SkewPop
version: 1.0

[ClickHouse] SHALL support [skewPop] specific aggregate function.

##### kurtSamp

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KurtSamp
version: 1.0

[ClickHouse] SHALL support [kurtSamp] specific aggregate function.

##### kurtPop

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KurtPop
version: 1.0

[ClickHouse] SHALL support [kurtPop] specific aggregate function.

##### uniq

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Uniq
version: 1.0

[ClickHouse] SHALL support [uniq] specific aggregate function.

##### uniqExact

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqExact
version: 1.0

[ClickHouse] SHALL support [uniqExact] specific aggregate function.

##### uniqCombined

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqCombined
version: 1.0

[ClickHouse] SHALL support [uniqCombined] specific aggregate function.

##### uniqCombined64

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqCombined64
version: 1.0

[ClickHouse] SHALL support [uniqCombined64] specific aggregate function.

##### uniqHLL12

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqHLL12
version: 1.0

[ClickHouse] SHALL support [uniqHLL12] specific aggregate function.

##### quantile

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Quantile
version: 1.0

[ClickHouse] SHALL support [quantile] specific aggregate function.

##### quantiles

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Quantiles
version: 1.0

[ClickHouse] SHALL support [quantiles] specific aggregate function.

##### quantilesExactExclusive

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactExclusive
version: 1.0

[ClickHouse] SHALL support [quantilesExactExclusive] specific aggregate function.

##### quantilesExactInclusive

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactInclusive
version: 1.0

[ClickHouse] SHALL support [quantilesExactInclusive] specific aggregate function.

##### quantilesDeterministic

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesDeterministic
version: 1.0

[ClickHouse] SHALL support [quantilesDeterministic] specific aggregate function.

##### quantilesExact

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExact
version: 1.0

[ClickHouse] SHALL support [quantilesExact] specific aggregate function.

##### quantilesExactHigh

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactHigh
version: 1.0

[ClickHouse] SHALL support [quantilesExactHigh] specific aggregate function.

##### quantilesExactLow

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactLow
version: 1.0

[ClickHouse] SHALL support [quantilesExactLow] specific aggregate function.

##### quantilesExactWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactWeighted
version: 1.0

[ClickHouse] SHALL support [quantilesExactWeighted] specific aggregate function.

##### quantilesTDigest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTDigest
version: 1.0

[ClickHouse] SHALL support [quantilesTDigest] specific aggregate function.

##### quantilesTDigestWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTDigestWeighted
version: 1.0

[ClickHouse] SHALL support [quantilesTDigestWeighted] specific aggregate function.

##### quantilesBFloat16

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesBFloat16
version: 1.0

[ClickHouse] SHALL support [quantilesBFloat16] specific aggregate function.

##### quantilesBFloat16Weighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesBFloat16Weighted
version: 1.0

[ClickHouse] SHALL support [quantilesBFloat16Weighted] specific aggregate function.

##### quantilesTiming

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTiming
version: 1.0

[ClickHouse] SHALL support [quantilesTiming] specific aggregate function.

##### quantilesTimingWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTimingWeighted
version: 1.0

[ClickHouse] SHALL support [quantilesTimingWeighted] specific aggregate function.

##### quantileExact

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExact
version: 1.0

[ClickHouse] SHALL support [quantileExact] specific aggregate function.

##### quantileExactLow

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactLow
version: 1.0

[ClickHouse] SHALL support [quantileExactLow] specific aggregate function.

##### quantileExactHigh

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactHigh
version: 1.0

[ClickHouse] SHALL support [quantileExactHigh] specific aggregate function.

##### quantileExactWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactWeighted
version: 1.0

[ClickHouse] SHALL support [quantileExactWeighted] specific aggregate function.

##### quantileTiming

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTiming
version: 1.0

[ClickHouse] SHALL support [quantileTiming] specific aggregate function.

##### quantileTimingWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTimingWeighted
version: 1.0

[ClickHouse] SHALL support [quantileTimingWeighted] specific aggregate function.

##### quantileDeterministic

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileDeterministic
version: 1.0

[ClickHouse] SHALL support [quantileDeterministic] specific aggregate function.

##### quantileTDigest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTDigest
version: 1.0

[ClickHouse] SHALL support [quantileTDigest] specific aggregate function.

##### quantileTDigestWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTDigestWeighted
version: 1.0

[ClickHouse] SHALL support [quantileTDigestWeighted] specific aggregate function.

##### quantileBFloat16

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileBFloat16
version: 1.0

[ClickHouse] SHALL support [quantileBFloat16] specific aggregate function.

##### quantileBFloat16Weighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileBFloat16Weighted
version: 1.0

[ClickHouse] SHALL support [quantileBFloat16Weighted] specific aggregate function.

##### simpleLinearRegression

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SimpleLinearRegression
version: 1.0

[ClickHouse] SHALL support [simpleLinearRegression] specific aggregate function.

##### stochasticLinearRegression

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StochasticLinearRegression
version: 1.0

[ClickHouse] SHALL support [stochasticLinearRegression] specific aggregate function.

##### stochasticLogisticRegression

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StochasticLogisticRgression
version: 1.0

[ClickHouse] SHALL support [stochasticLogisticRegression] specific aggregate function.

##### categoricalInformationValue

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.CategoricalInformationValue
version: 1.0

[ClickHouse] SHALL support [categoricalInformationValue] specific aggregate function.

##### studentTTest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StudentTTest
version: 1.0

[ClickHouse] SHALL support [studentTTest] specific aggregate function.

##### welchTTest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.WelchTTest
version: 1.0

[ClickHouse] SHALL support [welchTTest] specific aggregate function.

##### mannWhitneyUTest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MannWhitneyUTest
version: 1.0

[ClickHouse] SHALL support [mannWhitneyUTest] specific aggregate function.

##### median

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Median
version: 1.0

[ClickHouse] SHALL support [median] specific aggregate function.

##### rankCorr

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.RankCorr
version: 1.0

[ClickHouse] SHALL support [rankCorr] specific aggregate function.

##### entropy

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Entropy
version: 1.0

[ClickHouse] SHALL support [entropy] specific aggregate function.

##### meanZTest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MeanZTest
version: 1.0

[ClickHouse] SHALL support [meanZTest] specific aggregate function.

##### sparkbar

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Sparkbar
version: 1.0

[ClickHouse] SHALL support [sparkbar] specific aggregate function.

##### corr

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Corr
version: 1.0

[ClickHouse] SHALL support [corr] specific aggregate function.

##### deltaSum

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.DeltaSum
version: 1.0

[ClickHouse] SHALL support [deltaSum] specific aggregate function.

##### deltaSumTimestamp

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.DeltaSumTimestamp
version: 1.0

[ClickHouse] SHALL support [deltaSumTimestamp] specific aggregate function.

##### exponentialMovingAverage

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ExponentialMovingAverage
version: 1.0

[ClickHouse] SHALL support [exponentialMovingAverage] specific aggregate function.

##### intervalLengthSum

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.IntervalLengthSum
version: 1.0

[ClickHouse] SHALL support [intervalLengthSum] specific aggregate function.

##### sumCount

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumCount
version: 1.0

[ClickHouse] SHALL support [sumCount] specific aggregate function.

##### sumKahan

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumKahan
version: 1.0

[ClickHouse] SHALL support [sumKahan] specific aggregate function.

#### Miscellaneous Functions

##### first_value

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.FirstValue
version: 1.0

[ClickHouse] SHALL support `first_value` aggregate function.

##### last_value

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LastValue
version: 1.0

[ClickHouse] SHALL support `last_value` aggregate function.

##### lagInFrame

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LagInFrame
version: 1.0

[ClickHouse] SHALL support `lagInFrame` aggregate function.

##### leadInFrame

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LeadInFrame
version: 1.0

[ClickHouse] SHALL support `leadInFrame` aggregate function.

##### nth_value

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.NthValue
version: 1.0

[ClickHouse] SHALL support `nth_value` aggregate function.

##### rank

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Rank
version: 1.0

[ClickHouse] SHALL support `rank` aggregate function.

##### row_number

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.RowNumber
version: 1.0

[ClickHouse] SHALL support `row_number` aggregate function.

##### singleValueOrNull

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SingleValueOrNull
version: 1.0

[ClickHouse] SHALL support `singleValueOrNull` aggregate function.

##### maxIntersections

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxIntersections
version: 1.0

[ClickHouse] SHALL support `maxIntersections` aggregate function.

##### maxIntersectionsPosition

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxIntersectionsPosition
version: 1.0

[ClickHouse] SHALL support `maxIntersectionsPosition` aggregate function.

##### aggThrow

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.AggThrow
version: 1.0

[ClickHouse] SHALL support `aggThrow` aggregate function.

##### boundingRatio

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.BoundingRatio
version: 1.0

[ClickHouse] SHALL support `boundingRatio` aggregate function.

##### contingency

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Contingency
version: 1.0

[ClickHouse] SHALL support `contingency` aggregate function.

##### cramersV

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.CramersV
version: 1.0

[ClickHouse] SHALL support `cramersV` aggregate function.

##### cramersVBiasCorrected

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.CramersVBiasCorrected
version: 1.0

[ClickHouse] SHALL support `cramersVBiasCorrected` aggregate function.

##### dense_rank

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.DenseRank
version: 1.0

[ClickHouse] SHALL support `dense_rank` aggregate function.

##### exponentialTimeDecayedAvg

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedAvg
version: 1.0

[ClickHouse] SHALL support `exponentialTimeDecayedAvg` aggregate function.

##### exponentialTimeDecayedCount

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedCount
version: 1.0

[ClickHouse] SHALL support `exponentialTimeDecayedCount` aggregate function.

##### exponentialTimeDecayedMax

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedMax
version: 1.0

[ClickHouse] SHALL support `exponentialTimeDecayedMax` aggregate function.

##### exponentialTimeDecayedSum

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedSum
version: 1.0

[ClickHouse] SHALL support `exponentialTimeDecayedSum` aggregate function.

##### uniqTheta

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.UniqTheta
version: 1.0

[ClickHouse] SHALL support `uniqTheta` aggregate function.

##### quantileExactExclusive

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.QuantileExactExclusive
version: 1.0

[ClickHouse] SHALL support `quantileExactExclusive` aggregate function.

##### quantileExactInclusive

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.QuantileExactInclusive
version: 1.0

[ClickHouse] SHALL support `quantileExactInclusive` aggregate function.

##### sumMapFilteredWithOverflow

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMapFilteredWithOverflow
version: 1.0

[ClickHouse] SHALL support `sumMapFilteredWithOverflow` aggregate function.

##### sumMapWithOverflow

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMapWithOverflow
version: 1.0

[ClickHouse] SHALL support `sumMapWithOverflow` aggregate function.

##### sumMappedArrays

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMappedArrays
version: 1.0

[ClickHouse] SHALL support `sumMappedArrays` aggregate function.

##### nothing

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Nothing
version: 1.0

[ClickHouse] SHALL support `nothing` aggregate function.

##### maxMappedArrays

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxMappedArrays
version: 1.0

[ClickHouse] SHALL support `maxMappedArrays` aggregate function.

##### minMappedArrays

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MinMappedArrays
version: 1.0

[ClickHouse] SHALL support `minMappedArrays` aggregate function.

##### nonNegativeDerivative

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.NonNegativeDerivative
version: 1.0

[ClickHouse] SHALL support `nonNegativeDerivative` aggregate function.

##### theilsU

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.TheilsU
version: 1.0

[ClickHouse] SHALL support `theilsU` aggregate function.

#### Parametric Functions

##### histogram

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.Histogram
version: 1.0

[ClickHouse] SHALL support [histogram] parameteric aggregate function.

##### sequenceMatch

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceMatch
version: 1.0

[ClickHouse] SHALL support [sequenceMatch] parameteric aggregate function.

##### sequenceCount

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceCount
version: 1.0

[ClickHouse] SHALL support [sequenceCount] parameteric aggregate function.

##### windowFunnel

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.WindowFunnel
version: 1.0

[ClickHouse] SHALL support [windowFunnel] parameteric aggregate function.

##### retention

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.Retention
version: 1.0

[ClickHouse] SHALL support [retention] parameteric aggregate function.

##### uniqUpTo

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.UniqUpTo
version: 1.0

[ClickHouse] SHALL support [uniqUpTo] parameteric aggregate function.

##### sumMapFiltered

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SumMapFiltered
version: 1.0

[ClickHouse] SHALL support [sumMapFiltered] parameteric aggregate function.

##### sequenceNextNode

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceNextNode
version: 1.0

[ClickHouse] SHALL support [sequenceNextNode] parameteric aggregate function.

### Combinator Functions

#### -If Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.If
version: 1.0

[ClickHouse] SHALL support [-If] combinator suffix for all [aggregate function]s which
SHALL enable the aggregate function to accept an extra argument – a condition of `Uint8` type.
The aggregate function SHALL process only the rows that trigger the condition.
If the condition was not triggered even once, the function SHALL return a default value.

For example,

```sql
sumIf(column, cond)
countIf(cond)
avgIf(x, cond)
quantilesTimingIf(level1, level2)(x, cond)
argMinIf(arg, val, cond)
...
```

#### -Array Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Array
version: 1.0

[ClickHouse] SHALL support [-Array] combinator suffix for all [aggregate function]s which
SHALL enable the aggregate function ti take arguments of the `Array(T)` type (arrays)
instead of `T` type arguments.

If the aggregate function accepts multiple arguments, the arrays SHALL be of equal lengths.
When processing arrays, the aggregate function SHALL work like the original
aggregate function across all array elements.

For example,

```sql
sumArray(arr) -- sum all the elements of all ‘arr’ arrays
```

```sql
uniqArray(arr) -- count the number of unique elements in all ‘arr’ arrays
```

#### -Map Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Map
version: 1.0

[ClickHouse] SHALL support [-Map] combinator suffix for all [aggregate function]s which
SHALL cause the aggregate function to take `Map` type as an argument,
and SHALL aggregate values of each key of the map separately using the specified aggregate function.

The result SHALL also be of a `Map` type.

For example,

```sql
sumMap(map(1,1))
avgMap(map('a', 1))
```

#### -State Suffix

##### Test Feature Diagram

```mermaid
flowchart LR
  subgraph -State
    direction TB
    subgraph A[Aggregate Functions]
        direction LR
        A1["all aggregate functions"]
        A2["all argument data types"]
    end
    subgraph B[Compatibility]
      direction LR
      B1["AggregatingMergeTree table engine"]
      B2["finalizeAggregation() function"]
      B3["runningAccumulate() function"]
      B4["-Merge functions"]
      B5["-MergeState functions"]
      B6["ArregateFunction data type"]
      B6["SimpleArregateFunction data type ?"]
      B7["Materialized View"]
    end
    subgraph CM[Output/Input]
      subgraph C[Output Formats]
      end
      subgraph D[Input Formats]
      end
    end
    subgraph E[ClickHouse versions]
      direction LR
      E1[Upgrade]
      E2[Downgrade]
    end
    subgraph F[Backups]
      direction LR
      F1[clickhouse-backup utility]
      F2[BACKUP TABLE .. TO statement] 
    end
  end
```

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State
version: 1.0

[ClickHouse] SHALL support [-State] combinator suffix for all [aggregate function]s which
SHALL return an intermediate state of the aggregation that user SHALL be able to use for
further processing or stored in a table to finish aggregation later.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.AggregatingMergeTree
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with [AggregatingMergeTree] table engine.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.FinalizeAggregationFunction
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with [finalizeAggregation] function.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.RunningAccumulateFunction
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with [runningAccumulate] function.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.Merge
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with the corresponding [-Merge] combinator function.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.MergeState
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with the corresponding [-MergeState] combinator function.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.AggregateFunctionDataType
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with [AggregateFunction] data type columns.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.MaterializedView
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with [Materialized View] table engine.

#### -SimpleState Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.SimpleState
version: 1.0

[ClickHouse] SHALL support [-SimpleState] combinator suffix for all [aggregate function]s which
SHALL return the same result as the aggregate function but with a [SimpleAggregateFunction] data type.

For example,

```sql
WITH anySimpleState(number) AS c SELECT toTypeName(c), c FROM numbers(1)
```

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.SimpleState.With.AggregatingMergeTree
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-SimpleState] combinator
with [AggregatingMergeTree] table engine to store data in a column with [SimpleAggregateFunction] data type.

#### -Merge Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Merge
version: 1.0

[ClickHouse] SHALL support [-Merge] combinator suffix for all [aggregate function]s which
SHALL cause the aggregate function to take the intermediate aggregation state as an argument and
combine the states to finish aggregation and the function SHALL return the resulting value.

#### -MergeState Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.MergeState
version: 1.0

[ClickHouse] SHALL support [-MergeState] combinator suffix for all [aggregate function]s which
SHALL cause the aggregate function to merge the intermediate aggregation states in the same way as the
[-Merge] combinator but SHALL return an intermediate aggregation state, similar to the [-State] combinator.

#### -ForEach Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.ForEach
version: 1.0

[ClickHouse] SHALL support [-MergeState] combinator suffix for all [aggregate function]s which
SHALL convert aggregate function for tables into an aggregate function for arrays
that SHALL aggregate the corresponding array items and SHALL return an array of results.

For example,

> sumForEach for the arrays [1, 2], [3, 4, 5] and [6, 7] SHALL return the result [10, 13, 5]
> after adding together the corresponding array items

#### -Distinct Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Distinct
version: 1.0

[ClickHouse] SHALL support [-Distinct] combinator suffix for all [aggregate function]s which
SHALL cause the aggregate function for every unique combination of arguments to be aggregated only once.

Repeating values SHALL be ignored.

For example,

```sql
sum(DISTINCT x)
groupArray(DISTINCT x)
corrStableDistinct(DISTINCT x, y)
```

#### -OrDefault Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.OrDefault
version: 1.0

[ClickHouse] SHALL support [-Distinct] combinator suffix for all [aggregate function]s which
SHALL change the behavior of an aggregate function.

If an aggregate function does not have input values, with this combinator it SHALL return
the default value for its return data type.

This combinator SHALL apply to the aggregate functions that can take empty input data.

The `-OrDefault` SHALL support to be used with other combinators which
SHALL enable to use aggregate function which do not accept the empty input.

Syntax:

```sql
[aggregate function]OrDefault(x)
```

where `x` are the aggregate function parameters.

The function SHALL return the default value of an aggregate function’s return type if there is nothing to aggregate
and the type SHALL depend on the aggregate function used.

For example, 

```sql
SELECT avg(number), avgOrDefault(number) FROM numbers(0)
```

SHALL produce the following output

```bash
┌─avg(number)─┬─avgOrDefault(number)─┐
│         nan │                    0 │
└─────────────┴──────────────────────┘
```

For example,

```sql
SELECT avgOrDefaultIf(x, x > 10)
FROM
(
    SELECT toDecimal32(1.23, 2) AS x
)
```

SHALL produce the following output

```bash
┌─avgOrDefaultIf(x, greater(x, 10))─┐
│                              0.00 │
└───────────────────────────────────┘
```

#### -OrNull Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.OrNull
version: 1.0

[ClickHouse] SHALL support [-Distinct] combinator suffix for all [aggregate function]s which
SHALL change the behavior of an aggregate function.

The combinator SHALL convert a result of an aggregate function to the `Nullable` data type.
If the aggregate function does not have values to calculate it SHALL return `NULL`.

Syntax:

```sql
<aggregate function>OrNull(x)
```

where `x` is aggregate function parameters.

In addition, the [-OrNull] combinator SHALL support to be used with other combinators
which SHALL enable to use aggregate function which do not accept the empty input.

For example,

```sql
SELECT sumOrNull(number), toTypeName(sumOrNull(number)) FROM numbers(10) WHERE number > 10
```

SHALL produce the following output

```bash
┌─sumOrNull(number)─┬─toTypeName(sumOrNull(number))─┐
│              ᴺᵁᴸᴸ │ Nullable(UInt64)              │
└───────────────────┴───────────────────────────────┘
```

For example,

```sql
SELECT avgOrNullIf(x, x > 10)
FROM
(
    SELECT toDecimal32(1.23, 2) AS x
)
```

SHALL produce the following output

```bash
┌─avgOrNullIf(x, greater(x, 10))─┐
│                           ᴺᵁᴸᴸ │
└────────────────────────────────┘
```

#### -Resample Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Resample
version: 1.0

[ClickHouse] SHALL support [-Resample] combinator suffix for all [aggregate function]s which
SHALL cause the aggregate function to divide data into groups, and then it SHALL separately aggregate
the data in those groups. Groups SHALL be created by splitting the values from one column into intervals.

The function SHALL return an `Array` of aggregate function results for each sub-interval.

Syntax:

```sql
<aggregate function>Resample(start, end, step)(<aggFunction_params>, resampling_key)
```

where arguments SHALL be the following

* `start`  starting value of the whole required interval for resampling_key values
* `stop`  ending value of the whole required interval for resampling_key values
  The whole interval does not include the stop value [start, stop)
* `step` step for separating the whole interval into sub-intervals.
  The aggregate function is executed over each of those sub-intervals independently.
* `resampling_key` column whose values are used for separating data into intervals
* `aggFunction_params` aggregate function parameters

For example, 

with `people` table containing

```bash
┌─name───┬─age─┬─wage─┐
│ John   │  16 │   10 │
│ Alice  │  30 │   15 │
│ Mary   │  35 │    8 │
│ Evelyn │  48 │ 11.5 │
│ David  │  62 │  9.9 │
│ Brian  │  60 │   16 │
└────────┴─────┴──────┘
```

```sql
SELECT groupArrayResample(30, 75, 30)(name, age) FROM people
```

SHALL produce the following result

```bash
┌─groupArrayResample(30, 75, 30)(name, age)─────┐
│ [['Alice','Mary','Evelyn'],['David','Brian']] │
└───────────────────────────────────────────────┘
```

and

```sql
SELECT
    countResample(30, 75, 30)(name, age) AS amount,
    avgResample(30, 75, 30)(wage, age) AS avg_wage
FROM people
```

SHALL produce

```bash
┌─amount─┬─avg_wage──────────────────┐
│ [3,2]  │ [11.5,12.949999809265137] │
└────────┴───────────────────────────┘
```

### Data Types

#### SimpleAggregateFunction

##### RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.SimpleAggregateFunction
version: 1.0

[ClickHouse] SHALL support [SimpleAggregateFunction] data type which SHALL allow to store a
current value of the aggregate function. 

This function SHALL be used as optimization to [AggregateFunction] when the following property holds: 

> the result of applying a function f to a row set S1 UNION ALL S2 can be obtained by applying f to parts of the row set
> separately, and then again applying f to the results: f(S1 UNION ALL S2) = f(f(S1) UNION ALL f(S2)).
> This property guarantees that partial aggregation results are enough to compute the combined one,
> so we do not have to store and process any extra data.

#### AggregateFunction

##### RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction
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

##### Inserting Data

###### RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction.Insert

[ClickHouse] SHALL support inserting data into [AggregateFunction] data type column 
using a value returned by calling the [aggregate function] with the `-State` suffix in
`INSERT SELECT` statement.

For example,

```sql
INSERT INTO table SELECT uniqState(UserID), quantilesState(0.5, 0.9)(SendTiming)
```

##### Selecting Data

###### RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction.Select

[ClickHouse] SHALL support selecting final result of aggregation from [AggregateFunction] data type column
by using the same [aggregate function] with the `-Merge` suffix.

For example,

```sql
SELECT uniqMerge(state) FROM (SELECT uniqState(UserID) AS state FROM table GROUP BY RegionID)
```

### Grouping

#### RQ.SRS-031.ClickHouse.AggregateFunctions.Grouping

[ClickHouse] SHALL support `GROUPING` function which SHALL take multiple columns as an argument and SHALL
return a bitmask where bits SHALL indicate the following

* `1` that a row returned by a `ROLLUP` or `CUBE` modifier to `GROUP BY` is a subtotal
* `0` that a row returned by a `ROLLUP` or `CUBE` is a row that is not a subtotal

### Grouping Sets

#### RQ.SRS-031.ClickHouse.AggregateFunctions.GroupingSets

[ClickHouse] SHALL support `GROUPING SETS` which SHALL allow user to specify the specific combinations to calculate
as by default, the `CUBE` modifier calculates subtotals for all possible combinations of the columns passed to
`CUBE`.

For example,

```sql
SELECT
    datacenter,
    distro, 
    SUM (quantity) qty
FROM
    servers
GROUP BY
    GROUPING SETS(
        (datacenter,distro),
        (datacenter),
        (distro),
        ()
    )
```

## References

* [ClickHouse]
* [GitHub Repository]
* [Revision History]
* [Git]

[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/
[Materialized View]: https://clickhouse.com/docs/en/sql-reference/statements/create/view#materialized-view
[-MergeState]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-mergestate
[-Merge]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-merge
[-SimpleState]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-simplestate
[-State]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-state
[runningAccumulate]: https://clickhouse.com/docs/en/sql-reference/functions/other-functions#function-finalizeaggregation
[finalizeAggregation]: https://clickhouse.com/docs/en/sql-reference/functions/other-functions#function-finalizeaggregation
[AggregatingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/aggregatingmergetree
[aggregate function]: #aggregate-functions
[SimpleAggregateFunction]: https://clickhouse.com/docs/en/sql-reference/data-types/simpleaggregatefunction
[AggregateFunction]: https://clickhouse.com/docs/en/sql-reference/data-types/aggregatefunction
[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/aggregate_functions/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/aggregate_functions/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
[count]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/count/
[min]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/min/
[max]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/max/
[sum]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/sum/
[avg]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/avg/
[any]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/any/
[stddevPop]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/stddevpop/
[stddevSamp]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/stddevsamp/
[varPop]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/varpop/
[varSamp]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/varsamp/
[covarPop]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/covarpop/
[covarSamp]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/covarsamp/
[anyHeavy]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/anyheavy/
[anyLast]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/anylast/
[argMin]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/argmin/
[argMax]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/argmax/
[avgWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/avgweighted/
[corr]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/corr/
[topK]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/topk/
[topKWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/topkweighted/
[groupArray]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/grouparray/
[groupUniqArray]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupuniqarray/
[groupArrayInsertAt]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/grouparrayinsertat/
[groupArrayMovingSum]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/grouparraymovingsum/
[groupArrayMovingAvg]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/grouparraymovingavg/
[groupArraySample]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/grouparraysample/
[groupBitAnd]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitand/
[groupBitOr]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitor/
[groupBitXor]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitxor/
[groupBitmap]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitmap/
[groupBitmapAnd]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitmapand/
[groupBitmapOr]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitmapor/
[groupBitmapXor]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitmapxor/
[sumWithOverflow]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/sumwithoverflow/
[deltaSum]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/deltasum/
[deltaSumTimestamp]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/deltasumtimestamp
[sumMap]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/summap/
[minMap]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/minmap/
[maxMap]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/maxmap/
[initializeAggregation]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/initializeAggregation/
[skewPop]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/skewpop/
[skewSamp]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/skewsamp/
[kurtPop]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/kurtpop/
[kurtSamp]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/kurtsamp/
[uniq]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/uniq/
[uniqExact]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/uniqexact/
[uniqCombined]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/uniqcombined/
[uniqCombined64]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/uniqcombined64/
[uniqHLL12]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/uniqhll12/
[quantile]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantile/
[quantiles]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesExactExclusive]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles#quantilesexactexclusive
[quantilesExactInclusive]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles#quantilesexactinclusive
[quantilesDeterministic]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesExact]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesExactHigh]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesExactLow]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesExactWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesTDigest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesTDigestWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesBFloat16]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesBFloat16Weigted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesTiming]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesTimingWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantileExact]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantileexact/
[quantileExactWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantileexactweighted/
[quantileTiming]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiletiming/
[quantileTimingWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiletimingweighted/
[quantileDeterministic]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiledeterministic/
[quantileTDigest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiletdigest/
[quantileTDigestWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiletdigestweighted/
[quantileBFloat16]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantilebfloat16
[quantileBFloat16Weighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantilebfloat16
[simpleLinearRegression]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/simplelinearregression/
[stochasticLinearRegression]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/stochasticlinearregression/
[stochasticLogisticRegression]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/stochasticlogisticregression/
[categoricalInformationValue]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/stochasticlogisticregression/
[studentTTest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/studentttest/
[welchTTest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/welchttest/
[mannWhitneyUTest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/mannwhitneyutest/
[median]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/median/
[rankCorr]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/rankCorr/
[histogram]:https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#histogram
[sequenceMatch]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#function-sequencematch
[sequenceCount]:https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#function-sequencecount
[windowFunnel]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#windowfunnel
[retention]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#retention
[uniqUpTo]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#uniquptonx
[sumMapFiltered]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#summapfilteredkeys-to-keepkeys-values
[sequenceNextNode]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions#sequencenextnode
[entropy]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/entropy
[meanZTest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/meanztest
[sparkbar]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/sparkbar
[exponentialMovingAverage]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/exponentialmovingaverage
[intervalLengthSum]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/intervalLengthSum
[sumCount]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/sumcount
[sumKahan]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/sumkahan
""",
)
