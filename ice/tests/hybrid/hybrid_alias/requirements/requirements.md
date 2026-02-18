# SRS Hybrid Table ALIAS Columns
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Settings](#settings)
    * 2.1 [RQ.Ice.HybridAlias.Settings.AsteriskIncludeAliasColumns](#rqicehybridaliassettingsasteriskincludealiascolumns)
* 3 [ALIAS Column Types](#alias-column-types)
    * 3.1 [Simple Arithmetic Aliases](#simple-arithmetic-aliases)
        * 3.1.1 [RQ.Ice.HybridAlias.AliasTypes.SimpleArithmetic](#rqicehybridaliasaliastypessimplearithmetic)
        * 3.1.2 [RQ.Ice.HybridAlias.AliasTypes.SimpleArithmetic.Division](#rqicehybridaliasaliastypessimplearithmeticdivision)
        * 3.1.3 [RQ.Ice.HybridAlias.AliasTypes.SimpleArithmetic.FloatTypes](#rqicehybridaliasaliastypessimplearithmeticfloattypes)
    * 3.2 [Constant Aliases](#constant-aliases)
        * 3.2.1 [RQ.Ice.HybridAlias.AliasTypes.Constant](#rqicehybridaliasaliastypesconstant)
        * 3.2.2 [RQ.Ice.HybridAlias.AliasTypes.Constant.StringDate](#rqicehybridaliasaliastypesconstantstringdate)
        * 3.2.3 [RQ.Ice.HybridAlias.AliasTypes.Constant.Null](#rqicehybridaliasaliastypesconstantnull)
    * 3.3 [Boolean Logical Aliases](#boolean-logical-aliases)
        * 3.3.1 [RQ.Ice.HybridAlias.AliasTypes.BooleanLogical](#rqicehybridaliasaliastypesbooleanlogical)
        * 3.3.2 [RQ.Ice.HybridAlias.AliasTypes.BooleanLogical.ComplexExpressions](#rqicehybridaliasaliastypesbooleanlogicalcomplexexpressions)
        * 3.3.3 [RQ.Ice.HybridAlias.AliasTypes.BooleanLogical.NullHandling](#rqicehybridaliasaliastypesbooleanlogicalnullhandling)
    * 3.4 [Date Time Function Aliases](#date-time-function-aliases)
        * 3.4.1 [RQ.Ice.HybridAlias.AliasTypes.DateTimeFunction](#rqicehybridaliasaliastypesdatetimefunction)
        * 3.4.2 [RQ.Ice.HybridAlias.AliasTypes.DateTimeFunction.Arithmetic](#rqicehybridaliasaliastypesdatetimefunctionarithmetic)
        * 3.4.3 [RQ.Ice.HybridAlias.AliasTypes.DateTimeFunction.UnixTimestamp](#rqicehybridaliasaliastypesdatetimefunctionunixtimestamp)
    * 3.5 [String Function Aliases](#string-function-aliases)
        * 3.5.1 [RQ.Ice.HybridAlias.AliasTypes.StringFunction](#rqicehybridaliasaliastypesstringfunction)
        * 3.5.2 [RQ.Ice.HybridAlias.AliasTypes.StringFunction.Concatenation](#rqicehybridaliasaliastypesstringfunctionconcatenation)
        * 3.5.3 [RQ.Ice.HybridAlias.AliasTypes.StringFunction.NullHandling](#rqicehybridaliasaliastypesstringfunctionnullhandling)
    * 3.6 [Type Conversion Aliases](#type-conversion-aliases)
        * 3.6.1 [RQ.Ice.HybridAlias.AliasTypes.TypeConversion](#rqicehybridaliasaliastypestypeconversion)
        * 3.6.2 [RQ.Ice.HybridAlias.AliasTypes.TypeConversion.DateConversions](#rqicehybridaliasaliastypestypeconversiondateconversions)
        * 3.6.3 [RQ.Ice.HybridAlias.AliasTypes.TypeConversion.InvalidConversion](#rqicehybridaliasaliastypestypeconversioninvalidconversion)
    * 3.7 [Conditional Aliases](#conditional-aliases)
        * 3.7.1 [RQ.Ice.HybridAlias.AliasTypes.Conditional](#rqicehybridaliasaliastypesconditional)
        * 3.7.2 [RQ.Ice.HybridAlias.AliasTypes.Conditional.MultiIf](#rqicehybridaliasaliastypesconditionalmultiif)
        * 3.7.3 [RQ.Ice.HybridAlias.AliasTypes.Conditional.Coalesce](#rqicehybridaliasaliastypesconditionalcoalesce)
    * 3.8 [Nested Dependent Aliases](#nested-dependent-aliases)
        * 3.8.1 [RQ.Ice.HybridAlias.AliasTypes.NestedDependent](#rqicehybridaliasaliastypesnesteddependent)
        * 3.8.2 [RQ.Ice.HybridAlias.AliasTypes.NestedDependent.MultiLevel](#rqicehybridaliasaliastypesnesteddependentmultilevel)
        * 3.8.3 [RQ.Ice.HybridAlias.AliasTypes.NestedDependent.MultipleDependencies](#rqicehybridaliasaliastypesnesteddependentmultipledependencies)
        * 3.8.4 [RQ.Ice.HybridAlias.AliasTypes.NestedDependent.CircularDependency](#rqicehybridaliasaliastypesnesteddependentcirculardependency)
    * 3.9 [Complex Expression Aliases](#complex-expression-aliases)
        * 3.9.1 [RQ.Ice.HybridAlias.AliasTypes.ComplexExpression](#rqicehybridaliasaliastypescomplexexpression)
* 4 [Watermark and Predicate Types](#watermark-and-predicate-types)
    * 4.1 [Direct Column Predicates](#direct-column-predicates)
        * 4.1.1 [RQ.Ice.HybridAlias.Predicates.DirectColumn](#rqicehybridaliaspredicatesdirectcolumn)
    * 4.2 [Alias Column Predicates](#alias-column-predicates)
        * 4.2.1 [RQ.Ice.HybridAlias.Predicates.AliasColumn](#rqicehybridaliaspredicatesaliascolumn)
    * 4.3 [Predicates on Columns That Aliases Depend On](#predicates-on-columns-that-aliases-depend-on)
        * 4.3.1 [RQ.Ice.HybridAlias.Predicates.BaseDependentColumn](#rqicehybridaliaspredicatesbasedependentcolumn)
    * 4.4 [Predicates on Columns That Aliases Do Not Depend On](#predicates-on-columns-that-aliases-do-not-depend-on)
        * 4.4.1 [RQ.Ice.HybridAlias.Predicates.BaseIndependentColumn](#rqicehybridaliaspredicatesbaseindependentcolumn)
    * 4.5 [Complex Predicates with Aliases](#complex-predicates-with-aliases)
        * 4.5.1 [RQ.Ice.HybridAlias.Predicates.Complex](#rqicehybridaliaspredicatescomplex)
    * 4.6 [Date Based Predicates](#date-based-predicates)
        * 4.6.1 [RQ.Ice.HybridAlias.Predicates.DateBased](#rqicehybridaliaspredicatesdatebased)
    * 4.7 [Numeric Range Predicates](#numeric-range-predicates)
        * 4.7.1 [RQ.Ice.HybridAlias.Predicates.NumericRange](#rqicehybridaliaspredicatesnumericrange)
    * 4.8 [String Predicates](#string-predicates)
        * 4.8.1 [RQ.Ice.HybridAlias.Predicates.String](#rqicehybridaliaspredicatesstring)
* 5 [Query Context](#query-context)
    * 5.1 [SELECT Clause](#select-clause)
        * 5.1.1 [RQ.Ice.HybridAlias.QueryContext.Select](#rqicehybridaliasquerycontextselect)
    * 5.2 [WHERE Clause](#where-clause)
        * 5.2.1 [RQ.Ice.HybridAlias.QueryContext.Where](#rqicehybridaliasquerycontextwhere)
    * 5.3 [GROUP BY Clause](#group-by-clause)
        * 5.3.1 [RQ.Ice.HybridAlias.QueryContext.GroupBy](#rqicehybridaliasquerycontextgroupby)
    * 5.4 [ORDER BY Clause](#order-by-clause)
        * 5.4.1 [RQ.Ice.HybridAlias.QueryContext.OrderBy](#rqicehybridaliasquerycontextorderby)
    * 5.5 [HAVING Clause](#having-clause)
        * 5.5.1 [RQ.Ice.HybridAlias.QueryContext.Having](#rqicehybridaliasquerycontexthaving)
    * 5.6 [JOIN Operations](#join-operations)
        * 5.6.1 [RQ.Ice.HybridAlias.QueryContext.Join](#rqicehybridaliasquerycontextjoin)
    * 5.7 [Subqueries](#subqueries)
        * 5.7.1 [RQ.Ice.HybridAlias.QueryContext.Subquery](#rqicehybridaliasquerycontextsubquery)
* 6 [Segment Behavior](#segment-behavior)
    * 6.1 [Left Alias Right Normal](#left-alias-right-normal)
        * 6.1.1 [RQ.Ice.HybridAlias.Segments.LeftAliasRightNormal](#rqicehybridaliassegmentsleftaliasrightnormal)
    * 6.2 [Left Normal Right Alias](#left-normal-right-alias)
        * 6.2.1 [RQ.Ice.HybridAlias.Segments.LeftNormalRightAlias](#rqicehybridaliassegmentsleftnormalrightalias)
    * 6.3 [Both Segments Alias](#both-segments-alias)
        * 6.3.1 [RQ.Ice.HybridAlias.Segments.BothAlias](#rqicehybridaliassegmentsbothalias)
    * 6.4 [Segment Type Mismatch](#segment-type-mismatch)
        * 6.4.1 [RQ.Ice.HybridAlias.Segments.TypeMismatch](#rqicehybridaliassegmentstypemismatch)
* 7 [Type Compatibility](#type-compatibility)
    * 7.1 [Type Alignment](#type-alignment)
        * 7.1.1 [RQ.Ice.HybridAlias.TypeCompatibility.Alignment](#rqicehybridaliastypecompatibilityalignment)
    * 7.2 [Automatic Type Casting](#automatic-type-casting)
        * 7.2.1 [RQ.Ice.HybridAlias.TypeCompatibility.AutoCast](#rqicehybridaliastypecompatibilityautocast)
* 8 [Edge Cases and Error Scenarios](#edge-cases-and-error-scenarios)
    * 8.1 [Missing Dependencies](#missing-dependencies)
        * 8.1.1 [RQ.Ice.HybridAlias.EdgeCases.MissingDependencies](#rqicehybridaliasedgecasesmissingdependencies)
    * 8.2 [NULL Handling](#null-handling)
        * 8.2.1 [RQ.Ice.HybridAlias.EdgeCases.NullHandling](#rqicehybridaliasedgecasesnullhandling)
    * 8.3 [Division by Zero](#division-by-zero)
        * 8.3.1 [RQ.Ice.HybridAlias.EdgeCases.DivisionByZero](#rqicehybridaliasedgecasesdivisionbyzero)
    * 8.4 [Segment Mismatches](#segment-mismatches)
        * 8.4.1 [RQ.Ice.HybridAlias.EdgeCases.SegmentMismatch](#rqicehybridaliasedgecasessegmentmismatch)

## Introduction

This software requirements specification covers requirements for ALIAS columns
in [ClickHouse] Hybrid table engine segments. ALIAS columns are computed columns
whose values are calculated on-the-fly from expressions referencing base columns
or other alias columns. When used with the Hybrid table engine, ALIAS columns
must be handled consistently across segments (left and right) and correctly
evaluated through watermark predicates.

The Hybrid table engine unions multiple data sources behind per-segment
predicates so queries behave like a single table while data is migrated or
tiered. ALIAS columns add a layer of computed values that must be transparent
to this routing mechanism.

## Settings

### RQ.Ice.HybridAlias.Settings.AsteriskIncludeAliasColumns
version: 1.0

[ClickHouse] SHALL support the `asterisk_include_alias_columns` setting which
controls whether `SELECT *` includes ALIAS columns in the result set for Hybrid
tables. When set to `1`, alias columns SHALL be included in `SELECT *` output
alongside base columns.

```sql
SET asterisk_include_alias_columns = 1;
SELECT * FROM hybrid_table ORDER BY id;
```

## ALIAS Column Types

### Simple Arithmetic Aliases

#### RQ.Ice.HybridAlias.AliasTypes.SimpleArithmetic
version: 1.0

[ClickHouse] SHALL support ALIAS columns that perform basic arithmetic
operations (`+`, `-`, `*`, `/`, `%`) on base columns in Hybrid table segments.
The alias expression SHALL be evaluated on-the-fly and return correct results
across both segments.

Supported numeric base column types SHALL include:
Int8, Int16, Int32, Int64, UInt8, UInt16, UInt32, UInt64, Float32, Float64.

For example:

```sql
CREATE TABLE left_table (
    id Int32,
    value Int32,
    date_col Date,
    computed ALIAS value * 2,
    sum_alias ALIAS id + value
) ENGINE = MergeTree ORDER BY (date_col, id);
```

#### RQ.Ice.HybridAlias.AliasTypes.SimpleArithmetic.Division
version: 1.0

[ClickHouse] SHALL correctly evaluate ALIAS columns that use division operations
in Hybrid table segments. The result type SHALL match the expected numeric type
of the division (integer division for integer types, floating-point for float types).

For example:

```sql
quotient ALIAS value1 / value2
modulo ALIAS value % 3
```

#### RQ.Ice.HybridAlias.AliasTypes.SimpleArithmetic.FloatTypes
version: 1.0

[ClickHouse] SHALL correctly evaluate ALIAS columns that operate on Float32
and Float64 base columns in Hybrid table segments. Arithmetic operations
on floating-point types SHALL preserve floating-point precision semantics.

### Constant Aliases

#### RQ.Ice.HybridAlias.AliasTypes.Constant
version: 1.0

[ClickHouse] SHALL support ALIAS columns that evaluate to constant values in
Hybrid table segments. The constant SHALL be returned for every row regardless
of the base column values.

Supported constant types SHALL include numeric constants (integers, floats),
string constants, and boolean constants (`true`, `false`, `1`, `0`).

For example:

```sql
threshold ALIAS 50
max_value ALIAS 1000
```

#### RQ.Ice.HybridAlias.AliasTypes.Constant.StringDate
version: 1.0

[ClickHouse] SHALL support ALIAS columns that evaluate to string constants
and date constants in Hybrid table segments.

For example:

```sql
default_date ALIAS toDate('2025-01-01')
label ALIAS 'constant_string'
```

#### RQ.Ice.HybridAlias.AliasTypes.Constant.Null
version: 1.0

[ClickHouse] SHALL support ALIAS columns that evaluate to NULL constants in
Hybrid table segments. The NULL value SHALL be returned for every row.

### Boolean Logical Aliases

#### RQ.Ice.HybridAlias.AliasTypes.BooleanLogical
version: 1.0

[ClickHouse] SHALL support ALIAS columns that evaluate to boolean values
(UInt8 0/1) using comparison operators (`=`, `!=`, `<`, `<=`, `>`, `>=`) in
Hybrid table segments.

For example:

```sql
is_even ALIAS value % 2 = 0
is_recent ALIAS date_col >= '2025-01-15'
```

#### RQ.Ice.HybridAlias.AliasTypes.BooleanLogical.ComplexExpressions
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use logical operators (`AND`,
`OR`, `NOT`) to combine multiple boolean conditions in Hybrid table segments.

For example:

```sql
is_valid ALIAS value > 0 AND value < 100
is_active ALIAS status = 'active' OR status = 'pending'
```

#### RQ.Ice.HybridAlias.AliasTypes.BooleanLogical.NullHandling
version: 1.0

[ClickHouse] SHALL handle NULL values correctly in boolean ALIAS column
comparisons within Hybrid table segments. Comparisons involving NULL SHALL follow
standard SQL three-valued logic.

### Date Time Function Aliases

#### RQ.Ice.HybridAlias.AliasTypes.DateTimeFunction
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use date and time functions
in Hybrid table segments. Supported functions SHALL include `toYear`, `toMonth`,
`toDayOfWeek`, `toDayOfMonth`, `toYYYYMM`, and `toString` applied to date columns.

For example:

```sql
year_month ALIAS toYYYYMM(date_col)
year ALIAS toYear(date_col)
day_of_week ALIAS toDayOfWeek(date_col)
date_string ALIAS toString(date_col)
```

#### RQ.Ice.HybridAlias.AliasTypes.DateTimeFunction.Arithmetic
version: 1.0

[ClickHouse] SHALL support ALIAS columns that perform date arithmetic using
interval additions and subtractions in Hybrid table segments.

For example:

```sql
next_day ALIAS date_col + INTERVAL 1 DAY
prev_month ALIAS date_col - INTERVAL 1 MONTH
```

#### RQ.Ice.HybridAlias.AliasTypes.DateTimeFunction.UnixTimestamp
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use `toUnixTimestamp` and
time zone conversion functions in Hybrid table segments.

For example:

```sql
timestamp ALIAS toUnixTimestamp(date_col)
```

### String Function Aliases

#### RQ.Ice.HybridAlias.AliasTypes.StringFunction
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use string manipulation functions
in Hybrid table segments. Supported functions SHALL include `upper`, `lower`,
`length`, `substring`, and `reverse`.

For example:

```sql
upper_name ALIAS upper(name)
lower_name ALIAS lower(name)
name_length ALIAS length(name)
substring_name ALIAS substring(name, 1, 5)
```

#### RQ.Ice.HybridAlias.AliasTypes.StringFunction.Concatenation
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use string concatenation functions
(`concat`, `concat_ws`) in Hybrid table segments.

For example:

```sql
full_name ALIAS concat(first_name, ' ', last_name)
```

#### RQ.Ice.HybridAlias.AliasTypes.StringFunction.NullHandling
version: 1.0

[ClickHouse] SHALL handle NULL string values correctly in string function ALIAS
columns within Hybrid table segments.

### Type Conversion Aliases

#### RQ.Ice.HybridAlias.AliasTypes.TypeConversion
version: 1.0

[ClickHouse] SHALL support ALIAS columns that perform explicit type conversions
in Hybrid table segments. Supported conversion functions SHALL include:

* Numeric: `toInt8`, `toInt16`, `toInt32`, `toInt64`, `toUInt8`, `toUInt16`, `toUInt32`, `toUInt64`, `toFloat32`, `toFloat64`
* String: `toString`

For example:

```sql
value_str ALIAS toString(value)
value_float ALIAS toFloat64(value)
```

#### RQ.Ice.HybridAlias.AliasTypes.TypeConversion.DateConversions
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use date conversion functions
(`toDate`, `toDateTime`) in Hybrid table segments.

For example:

```sql
value_date ALIAS toDate(date_string)
value_datetime ALIAS toDateTime(timestamp_string)
```

#### RQ.Ice.HybridAlias.AliasTypes.TypeConversion.InvalidConversion
version: 1.0

[ClickHouse] SHALL return an error or handle gracefully when an ALIAS column
expression performs an invalid type conversion in Hybrid table segments.

### Conditional Aliases

#### RQ.Ice.HybridAlias.AliasTypes.Conditional
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use `if` conditional expressions
in Hybrid table segments.

For example:

```sql
category ALIAS if(value > 50, 'high', 'low')
```

#### RQ.Ice.HybridAlias.AliasTypes.Conditional.MultiIf
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use `multiIf` expressions with
multiple conditions in Hybrid table segments.

For example:

```sql
status ALIAS multiIf(value < 10, 'low', value < 50, 'medium', 'high')
```

#### RQ.Ice.HybridAlias.AliasTypes.Conditional.Coalesce
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use `coalesce` to provide
fallback values for NULL base column values in Hybrid table segments.

For example:

```sql
coalesced ALIAS coalesce(value1, value2, 0)
```

### Nested Dependent Aliases

#### RQ.Ice.HybridAlias.AliasTypes.NestedDependent
version: 1.0

[ClickHouse] SHALL support ALIAS columns that depend on other ALIAS columns
(single-level dependency) in Hybrid table segments.

For example:

```sql
computed ALIAS value * 2
computed_2 ALIAS computed + 10
```

#### RQ.Ice.HybridAlias.AliasTypes.NestedDependent.MultiLevel
version: 1.0

[ClickHouse] SHALL support multi-level alias dependency chains (3 or more
levels deep) in Hybrid table segments. The engine SHALL correctly resolve
the dependency chain and evaluate each alias in the correct order.

For example:

```sql
doubled ALIAS value * 2
quadrupled ALIAS doubled * 2
octupled ALIAS quadrupled * 2
```

#### RQ.Ice.HybridAlias.AliasTypes.NestedDependent.MultipleDependencies
version: 1.0

[ClickHouse] SHALL support ALIAS columns that depend on multiple other ALIAS
columns simultaneously in Hybrid table segments.

For example:

```sql
doubled ALIAS value * 2
quadrupled ALIAS doubled * 2
sum_all ALIAS id + value + doubled + quadrupled
```

#### RQ.Ice.HybridAlias.AliasTypes.NestedDependent.CircularDependency
version: 1.0

[ClickHouse] SHALL detect and reject circular alias dependencies when creating
tables that are used in Hybrid table segments. An error SHALL be returned
if alias A depends on alias B and alias B depends on alias A.

### Complex Expression Aliases

#### RQ.Ice.HybridAlias.AliasTypes.ComplexExpression
version: 1.0

[ClickHouse] SHALL support ALIAS columns with complex expressions that combine
multiple functions and operations in Hybrid table segments. Nested function
calls, multiple operations, and correct operator precedence SHALL be handled.

For example:

```sql
score ALIAS (value * 2) + (id % 10) - length(name)
formatted_date ALIAS concat(toString(toYear(date_col)), '-', toString(toMonth(date_col)))
```

## Watermark and Predicate Types

### Direct Column Predicates

#### RQ.Ice.HybridAlias.Predicates.DirectColumn
version: 1.0

[ClickHouse] SHALL support using base columns directly in watermark predicates
for Hybrid tables that contain ALIAS columns. The predicates SHALL correctly
route data between segments without affecting alias evaluation.

For example:

```sql
ENGINE = Hybrid(
    remote(..., left_table), date_col >= '2025-01-15',
    remote(..., right_table), date_col < '2025-01-15'
)
```

Supported predicate types SHALL include date column predicates, numeric column
predicates, string column predicates, and range predicates (`BETWEEN`).

### Alias Column Predicates

#### RQ.Ice.HybridAlias.Predicates.AliasColumn
version: 1.0

[ClickHouse] SHALL support or explicitly handle ALIAS columns used directly in
watermark predicates for Hybrid tables. If supported, the alias expression
SHALL be correctly evaluated during predicate routing. If not supported, a clear
error message SHALL be returned.

For example:

```sql
ENGINE = Hybrid(
    remote(..., left_table), computed >= 20,
    remote(..., right_table), computed < 20
)
```

Where `computed` is defined as `computed ALIAS value * 2`.

### Predicates on Columns That Aliases Depend On

#### RQ.Ice.HybridAlias.Predicates.BaseDependentColumn
version: 1.0

[ClickHouse] SHALL correctly handle watermark predicates that reference base
columns upon which ALIAS columns depend in Hybrid tables. The predicate SHALL
control data routing between segments, and the alias expression SHALL be
independently evaluated on the routed data.

For example, given `computed ALIAS value * 2`, a watermark predicate
`value >= 50` SHALL route rows based on the `value` column while `computed`
remains correctly evaluated as `value * 2` on each segment's data.

### Predicates on Columns That Aliases Do Not Depend On

#### RQ.Ice.HybridAlias.Predicates.BaseIndependentColumn
version: 1.0

[ClickHouse] SHALL correctly handle watermark predicates that reference base
columns unrelated to any ALIAS column definitions in Hybrid tables. Alias
column evaluation SHALL not be affected by predicates on independent columns.

For example, given `computed ALIAS value * 2`, a watermark predicate
`date_col >= '2025-01-15'` SHALL route data by date while `computed` is
evaluated independently.

### Complex Predicates with Aliases

#### RQ.Ice.HybridAlias.Predicates.Complex
version: 1.0

[ClickHouse] SHALL support complex watermark predicates that combine base
columns and alias columns using logical operators (`AND`, `OR`) in Hybrid tables.

For example:

```sql
ENGINE = Hybrid(
    remote(..., left_table), date_col >= '2025-01-15' AND value > 100,
    remote(..., right_table), date_col < '2025-01-15' OR value <= 100
)
```

### Date Based Predicates

#### RQ.Ice.HybridAlias.Predicates.DateBased
version: 1.0

[ClickHouse] SHALL support date-based watermark predicates in Hybrid tables
with ALIAS columns. Both direct date column comparisons and date function
predicates SHALL be supported.

For example:

```sql
-- Direct date comparison
date_col >= '2025-01-15'
date_col < '2025-01-15'

-- Date function predicate
toYYYYMM(date_col) >= 202501
toYear(date_col) = 2025
```

### Numeric Range Predicates

#### RQ.Ice.HybridAlias.Predicates.NumericRange
version: 1.0

[ClickHouse] SHALL support numeric range watermark predicates in Hybrid tables
with ALIAS columns. `BETWEEN`, range predicates with `AND`, and `IN` predicates
SHALL be supported.

For example:

```sql
-- BETWEEN predicate
id BETWEEN 10 AND 15

-- Range with AND
value >= 1 AND value <= 1000

-- IN predicate
value IN (10, 20, 30)
```

### String Predicates

#### RQ.Ice.HybridAlias.Predicates.String
version: 1.0

[ClickHouse] SHALL support string-based watermark predicates in Hybrid tables
with ALIAS columns. Equality predicates, `IN` predicates with strings, and
`LIKE` predicates SHALL be supported.

For example:

```sql
name = 'test'
status IN ('active', 'pending')
name LIKE 'test%'
```

## Query Context

### SELECT Clause

#### RQ.Ice.HybridAlias.QueryContext.Select
version: 1.0

[ClickHouse] SHALL support selecting ALIAS columns in the `SELECT` clause of
queries on Hybrid tables. The following patterns SHALL be supported:

* Selecting only alias columns
* Selecting a mix of base and alias columns
* Selecting nested/dependent aliases
* Selecting aliases within expressions (e.g., `computed + 10`)

For example:

```sql
SELECT computed, sum_alias FROM hybrid_table ORDER BY id;
SELECT id, value, computed FROM hybrid_table ORDER BY id;
```

### WHERE Clause

#### RQ.Ice.HybridAlias.QueryContext.Where
version: 1.0

[ClickHouse] SHALL support using ALIAS columns in the `WHERE` clause of queries
on Hybrid tables. Filtering by alias columns, filtering by base columns when
aliases are in `SELECT`, and complex `WHERE` conditions with aliases SHALL all
be supported.

For example:

```sql
SELECT id, computed FROM hybrid_table WHERE computed > 100 ORDER BY id;
SELECT id, value, computed FROM hybrid_table WHERE value > 5000 ORDER BY id;
```

### GROUP BY Clause

#### RQ.Ice.HybridAlias.QueryContext.GroupBy
version: 1.0

[ClickHouse] SHALL support using ALIAS columns in the `GROUP BY` clause of
queries on Hybrid tables. Grouping by alias columns, grouping by date function
aliases, and multiple alias columns in `GROUP BY` SHALL be supported.

For example:

```sql
SELECT date_col, sum(computed) AS total FROM hybrid_table GROUP BY date_col ORDER BY date_col;
SELECT year_month, count() FROM hybrid_table GROUP BY year_month ORDER BY year_month;
```

### ORDER BY Clause

#### RQ.Ice.HybridAlias.QueryContext.OrderBy
version: 1.0

[ClickHouse] SHALL support using ALIAS columns in the `ORDER BY` clause of
queries on Hybrid tables. Both `ASC` and `DESC` ordering by alias columns and
multiple alias columns in `ORDER BY` SHALL be supported.

For example:

```sql
SELECT id, computed FROM hybrid_table ORDER BY computed ASC;
SELECT id, computed, sum_alias FROM hybrid_table ORDER BY computed DESC, sum_alias ASC;
```

### HAVING Clause

#### RQ.Ice.HybridAlias.QueryContext.Having
version: 1.0

[ClickHouse] SHALL support using ALIAS columns in the `HAVING` clause of
queries on Hybrid tables. Filtering grouped results based on aggregations of
alias columns SHALL be supported.

For example:

```sql
SELECT date_col, sum(computed) AS total
FROM hybrid_table
GROUP BY date_col
HAVING total > 100
ORDER BY date_col;
```

### JOIN Operations

#### RQ.Ice.HybridAlias.QueryContext.Join
version: 1.0

[ClickHouse] SHALL support ALIAS columns in `JOIN` operations involving Hybrid
tables. ALIAS columns SHALL be accessible in JOIN conditions, and alias columns
from both sides of a JOIN SHALL be available in the result set.

### Subqueries

#### RQ.Ice.HybridAlias.QueryContext.Subquery
version: 1.0

[ClickHouse] SHALL support ALIAS columns in subqueries involving Hybrid tables.
ALIAS columns SHALL be accessible in subquery `SELECT` and `WHERE` clauses.

For example:

```sql
SELECT * FROM (SELECT id, computed FROM hybrid_table WHERE computed > 50) sub ORDER BY id;
```

## Segment Behavior

### Left Alias Right Normal

#### RQ.Ice.HybridAlias.Segments.LeftAliasRightNormal
version: 1.0

[ClickHouse] SHALL support Hybrid tables where the left segment defines a
column as an ALIAS and the right segment defines the same column as a regular
(non-alias) column. The Hybrid table SHALL correctly return values from both
segments regardless of how the underlying column is defined.

For example:

```sql
-- Left table: computed is an ALIAS
computed ALIAS value * 2

-- Right table: computed is a regular column
computed Int64
```

### Left Normal Right Alias

#### RQ.Ice.HybridAlias.Segments.LeftNormalRightAlias
version: 1.0

[ClickHouse] SHALL support Hybrid tables where the left segment defines a
column as a regular (non-alias) column and the right segment defines the same
column as an ALIAS. The Hybrid table SHALL correctly return values from both
segments.

### Both Segments Alias

#### RQ.Ice.HybridAlias.Segments.BothAlias
version: 1.0

[ClickHouse] SHALL support Hybrid tables where both segments define the same
column as an ALIAS. The alias expression SHALL be independently evaluated on
each segment's data.

### Segment Type Mismatch

#### RQ.Ice.HybridAlias.Segments.TypeMismatch
version: 1.0

[ClickHouse] SHALL handle type mismatches between segment alias columns and
the Hybrid table column definitions. When `hybrid_table_auto_cast_columns = 1`
is enabled, automatic type casting SHALL be applied. When disabled, type
mismatches SHALL produce appropriate errors.

For example, if an alias returns `Int16` but the Hybrid table defines the
column as `Int32`, automatic casting SHALL widen the type when enabled.

## Type Compatibility

### Type Alignment

#### RQ.Ice.HybridAlias.TypeCompatibility.Alignment
version: 1.0

[ClickHouse] SHALL support explicit type alignment between ALIAS column return
types and Hybrid table column definitions. The ALIAS expression return type
SHALL be compatible with or castable to the Hybrid table's column type.

For example:

* Alias returns `Int32`, Hybrid table expects `Int64` — SHALL work
* Alias returns `String`, Hybrid table expects `Int32` — SHALL produce an error

### Automatic Type Casting

#### RQ.Ice.HybridAlias.TypeCompatibility.AutoCast
version: 1.0

[ClickHouse] SHALL support automatic type casting for ALIAS columns across
Hybrid table segments when `hybrid_table_auto_cast_columns = 1` is enabled.
The automatic casting SHALL handle widening numeric conversions without data
loss.

## Edge Cases and Error Scenarios

### Missing Dependencies

#### RQ.Ice.HybridAlias.EdgeCases.MissingDependencies
version: 1.0

[ClickHouse] SHALL return an error when an ALIAS column references a
non-existent or dropped base column in a table used as a Hybrid table segment.

### NULL Handling

#### RQ.Ice.HybridAlias.EdgeCases.NullHandling
version: 1.0

[ClickHouse] SHALL correctly handle NULL values in ALIAS column evaluation
within Hybrid table segments. When a base column value is NULL, the alias
expression SHALL evaluate according to [ClickHouse] NULL propagation rules.

Aliases that produce NULL values SHALL return NULL in the Hybrid table query
results. NULL values in alias predicates SHALL follow standard SQL three-valued
logic.

### Division by Zero

#### RQ.Ice.HybridAlias.EdgeCases.DivisionByZero
version: 1.0

[ClickHouse] SHALL handle division by zero in ALIAS column expressions within
Hybrid table segments according to standard [ClickHouse] behavior (returning
`inf`, `-inf`, or `nan` for floating-point types, or 0 for integer types).

### Segment Mismatches

#### RQ.Ice.HybridAlias.EdgeCases.SegmentMismatch
version: 1.0

[ClickHouse] SHALL handle mismatches between segments in Hybrid tables where
alias definitions differ. The following mismatch scenarios SHALL be handled:

* Different alias expressions in left and right segments for the same column name
* An alias present in one segment but missing in the other segment
* Incompatible return types between segment alias expressions

[ClickHouse]: https://clickhouse.com
