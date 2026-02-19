# SRS Hybrid Table ALIAS Columns
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Settings](#settings)
    * 2.1 [RQ.Ice.HybridAlias.Settings.AsteriskIncludeAliasColumns](#rqicehybridaliassettingsasteriskincludealiascolumns)
* 3 [ALIAS Column Types](#alias-column-types)
    * 3.1 [RQ.Ice.HybridAlias.Arithmetic](#rqicehybridaliasarithmetic)
    * 3.2 [RQ.Ice.HybridAlias.Constants](#rqicehybridaliasconstants)
    * 3.3 [RQ.Ice.HybridAlias.BooleanLogical](#rqicehybridaliasbooleanlogical)
    * 3.4 [RQ.Ice.HybridAlias.DateTimeFunction](#rqicehybridaliasdatetimefunction)
    * 3.5 [RQ.Ice.HybridAlias.StringFunction](#rqicehybridaliasstringfunction)
    * 3.6 [RQ.Ice.HybridAlias.TypeConversion](#rqicehybridaliastypeconversion)
    * 3.7 [RQ.Ice.HybridAlias.Conditional](#rqicehybridaliasconditional)
    * 3.8 [RQ.Ice.HybridAlias.NestedDependent](#rqicehybridaliasnesteddependent)
    * 3.9 [RQ.Ice.HybridAlias.ComplexExpression](#rqicehybridaliascomplexexpression)
    * 3.10 [RQ.Ice.HybridAlias.MathFunction](#rqicehybridaliasmathfunction)
    * 3.11 [RQ.Ice.HybridAlias.RoundingFunction](#rqicehybridaliasroundingfunction)
    * 3.12 [RQ.Ice.HybridAlias.ArrayFunction](#rqicehybridaliasarrayfunction)
    * 3.13 [RQ.Ice.HybridAlias.TupleFunction](#rqicehybridaliastuplefunction)
    * 3.14 [RQ.Ice.HybridAlias.MapFunction](#rqicehybridaliasmapfunction)
    * 3.15 [RQ.Ice.HybridAlias.JsonFunction](#rqicehybridaliasjsonfunction)
    * 3.16 [RQ.Ice.HybridAlias.HashEncodingFunction](#rqicehybridaliashashencodingfunction)
    * 3.17 [RQ.Ice.HybridAlias.UtilityFunction](#rqicehybridaliasutilityfunction)
* 4 [Query Context](#query-context)
    * 4.1 [RQ.Ice.HybridAlias.QueryContext](#rqicehybridaliasquerycontext)
* 5 [Top-Level Tests](#top-level-tests)
    * 5.1 [RQ.Ice.HybridAlias.SimpleArithmeticAlias](#rqicehybridaliassimplearithmeticalias)
    * 5.2 [RQ.Ice.HybridAlias.AliasColumnInPredicate](#rqicehybridaliasaliascolumninpredicate)
    * 5.3 [RQ.Ice.HybridAlias.LeftAliasRightNormal](#rqicehybridaliasLeftaliasrightnormal)
    * 5.4 [RQ.Ice.HybridAlias.LeftAliasRightNormalTypeMismatch](#rqicehybridaliasLeftaliasrightnormaltypemismatch)
    * 5.5 [RQ.Ice.HybridAlias.LeftNormalRightAlias](#rqicehybridaliasleftnormalrightalias)
    * 5.6 [RQ.Ice.HybridAlias.LeftNormalRightAliasTypeMismatch](#rqicehybridaliasleftnormalrightaliastypemismatch)
    * 5.7 [RQ.Ice.HybridAlias.DifferentAliasExpressions](#rqicehybridaliasdifferentaliasexpressions)
    * 5.8 [RQ.Ice.HybridAlias.AliasMissingInSegment](#rqicehybridaliasaliasmissinginsegment)

## Introduction

This software requirements specification covers requirements for ALIAS columns
in [ClickHouse] Hybrid table engine segments. Each requirement corresponds to
a test folder or a top-level test file under `hybrid_alias/tests/`.

Every test creates left and right segment tables, a Hybrid table, and a
reference MergeTree table to compare results. Each test file contains two
scenarios: one with a date-based watermark predicate on a base column, and one
with the alias column used directly in the watermark predicate.

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

### RQ.Ice.HybridAlias.Arithmetic
version: 1.0

[ClickHouse] SHALL support ALIAS columns that perform arithmetic operations
on base columns in Hybrid table segments. The alias expression SHALL be
evaluated on-the-fly and return correct results across both segments.

The following cases SHALL be covered:

* `computed ALIAS value * 2` — multiplication
* `sum_alias ALIAS id + value` — addition
* `difference ALIAS value1 - value2` — subtraction
* `product ALIAS value1 * value2` — multiplication of two columns
* `quotient ALIAS value1 / value2` — division
* `modulo ALIAS value % 3` — modulo
* `intdiv ALIAS intDiv(value, 2)` — integer division
* `negative ALIAS abs(value) - abs(value * 2)` — negative result values
* `multiple ALIAS (value1 * value2 - value3) % (value2 + 1)` — complex multi-operand
* `scaled ALIAS price * 1.5` — Float32 base column arithmetic
* `total ALIAS amount1 + amount2` — Float64 base column addition
* `ratio ALIAS amount1 / amount2` — Float64 base column division
* `div_by_zero ALIAS value / 0` — division by zero edge case

### RQ.Ice.HybridAlias.Constants
version: 1.0

[ClickHouse] SHALL support ALIAS columns that evaluate to constant values in
Hybrid table segments. The constant SHALL be returned for every row regardless
of the base column values.

The following constant types SHALL be covered:

* `default_int8 ALIAS -50` (Int8)
* `default_int32 ALIAS toInt32(50000)` (Int32)
* `default_int64 ALIAS toInt64(1000000000)` (Int64)
* `default_int128 ALIAS toInt128(...)` (Int128)
* `default_int256 ALIAS toInt256(...)` (Int256)
* `default_uint256 ALIAS toUInt256(...)` (UInt256)
* `default_float32 ALIAS toFloat32(3.14159)` (Float32)
* `default_float64 ALIAS 2.718281828459045` (Float64)
* `default_decimal32 ALIAS toDecimal32(4.2, 8)` (Decimal32)
* `default_string ALIAS 'hello world'` (String)
* `default_date ALIAS toDate('2025-01-01')` (Date)
* `default_datetime ALIAS toDateTime('2025-01-01 12:00:00')` (DateTime)
* `default_datetime64 ALIAS toDateTime64('2025-01-01 12:00:00', 0)` (DateTime64)
* `default_bool ALIAS true` (Bool)
* `default_bool_false ALIAS false` (Bool)
* `default_array ALIAS array(1, 2, 3)` (Array(UInt8))
* `default_array_string ALIAS array('a', 'b', 'c')` (Array(String))
* `default_tuple ALIAS tuple(1, 'hello', 3.14)` (Tuple)
* `default_nested_tuple ALIAS tuple(1, tuple(2, 3), 4)` (nested Tuple)
* `default_map ALIAS map('key1', 'value1', 'key2', 'value2')` (Map)
* `default_json ALIAS '...'::JSON` (JSON)

### RQ.Ice.HybridAlias.BooleanLogical
version: 1.0

[ClickHouse] SHALL support ALIAS columns that evaluate to boolean values
(UInt8 0/1) in Hybrid table segments.

The following cases SHALL be covered:

* `is_equal ALIAS value = 42` — equality
* `is_not_equal ALIAS value != 42` — inequality
* `is_less ALIAS value < 100` — less than
* `is_less_equal ALIAS value <= 100` — less or equal
* `is_greater ALIAS value > 0` — greater than
* `is_greater_equal ALIAS value >= 0` — greater or equal
* `is_even ALIAS value % 2 = 0` — arithmetic with comparison
* `is_recent ALIAS date_col >= '2025-01-15'` — date comparison
* `is_active ALIAS status = 'active'` — string comparison
* `is_valid ALIAS value > 0 AND value < 100` — AND
* `is_or_condition ALIAS value < 10 OR value > 90` — OR
* `is_not_condition ALIAS NOT (value = 0)` — NOT
* `is_complex_logic ALIAS (value > 0 AND value < 100) OR (value > 200 AND value < 300)` — complex AND/OR
* `is_xor_condition ALIAS xor(value > 50, value < 100)` — XOR
* `is_in_range ALIAS value BETWEEN 10 AND 100` — BETWEEN
* `is_not_in_range ALIAS value NOT BETWEEN 10 AND 100` — NOT BETWEEN
* `is_in_set ALIAS value IN (1, 2, 3, 4, 5)` — IN
* `is_not_in_set ALIAS value NOT IN (1, 2, 3, 4, 5)` — NOT IN
* `is_like ALIAS name LIKE '%test%'` — LIKE
* `is_not_like ALIAS name NOT LIKE '%test%'` — NOT LIKE
* `is_ilike ALIAS name ILIKE '%TEST%'` — ILIKE
* `is_null_check ALIAS isNull(value)` — NULL check
* `is_not_null_check ALIAS isNotNull(value)` — NOT NULL check

### RQ.Ice.HybridAlias.DateTimeFunction
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use date and time functions
in Hybrid table segments.

The following cases SHALL be covered:

* `year ALIAS toYear(date_col)` — year extraction
* `month ALIAS toMonth(date_col)` — month extraction
* `day_of_week ALIAS toDayOfWeek(date_col)` — day of week
* `day_of_month ALIAS toDayOfMonth(date_col)` — day of month
* `quarter ALIAS toQuarter(date_col)` — quarter
* `year_month ALIAS toYYYYMM(date_col)` — YYYYMM format
* `year_month_day ALIAS toYYYYMMDD(date_col)` — YYYYMMDD format
* `hour ALIAS toHour(datetime_col)` — hour extraction
* `minute ALIAS toMinute(datetime_col)` — minute extraction
* `second ALIAS toSecond(datetime_col)` — second extraction
* `start_of_day ALIAS toStartOfDay(datetime_col)` — truncate to day
* `start_of_hour ALIAS toStartOfHour(datetime_col)` — truncate to hour
* `start_of_month ALIAS toStartOfMonth(datetime_col)` — truncate to month
* `start_of_quarter ALIAS toStartOfQuarter(datetime_col)` — truncate to quarter
* `start_of_week ALIAS toStartOfWeek(datetime_col)` — truncate to week
* `start_of_year ALIAS toStartOfYear(datetime_col)` — truncate to year
* `date_string ALIAS toString(date_col)` — date to string
* `datetime_string ALIAS toString(datetime_col)` — datetime to string
* `tz_converted ALIAS toTimeZone(datetime_col, 'America/New_York')` — timezone conversion
* `timestamp ALIAS toUnixTimestamp(date_col)` — unix timestamp
* `date_plus_days ALIAS addDays(date_col, 7)` — add days
* `date_plus_months ALIAS addMonths(date_col, 1)` — add months
* `date_plus_years ALIAS addYears(date_col, 1)` — add years
* `date_minus_days ALIAS subtractDays(date_col, 7)` — subtract days
* `date_minus_months ALIAS subtractMonths(date_col, 1)` — subtract months
* `date_minus_years ALIAS subtractYears(date_col, 1)` — subtract years
* `date_plus_interval ALIAS date_col + INTERVAL 7 DAY` — interval addition
* `date_minus_interval ALIAS date_col - INTERVAL 1 MONTH` — interval subtraction
* `datetime_plus_interval ALIAS datetime_col + INTERVAL 1 HOUR` — datetime interval

### RQ.Ice.HybridAlias.StringFunction
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use string manipulation functions
in Hybrid table segments.

The following cases SHALL be covered:

* `upper_name ALIAS upper(name)` — uppercase
* `lower_name ALIAS lower(name)` — lowercase
* `name_length ALIAS length(name)` — length
* `name_length_utf8 ALIAS lengthUTF8(name)` — UTF-8 length
* `substring_name ALIAS substring(name, 1, 5)` — substring with length
* `substring_from ALIAS substring(name, 3)` — substring from position
* `reversed_name ALIAS reverse(name)` — reverse
* `concatenated ALIAS concat(first_name, ' ', last_name)` — concat
* `concat_ws ALIAS concatWithSeparator(' ', first_name, last_name)` — concat with separator
* `array_concat ALIAS arrayStringConcat([first, second], ' ')` — array string concat
* `replaced_all ALIAS replaceAll(name, 'old', 'new')` — replace all
* `replaced_one ALIAS replaceOne(name, 'old', 'new')` — replace one
* `replaced_regexp ALIAS replaceRegexpOne(name, '\\d+', 'X')` — regex replace
* `repeated_name ALIAS repeat(name, 3)` — repeat
* `left_padded ALIAS leftPad(name, 10, '0')` — left pad
* `right_padded ALIAS rightPad(name, 10, '0')` — right pad
* `trimmed_name ALIAS trimBoth(name, 'a')` — trim both
* `trimmed_left ALIAS trimLeft(name, 'a')` — trim left
* `trimmed_right ALIAS trimRight(name, 'a')` — trim right
* `position_sub ALIAS position(name, 'test')` — position
* `position_ci ALIAS positionCaseInsensitive(name, 'TEST')` — case-insensitive position
* `starts_with ALIAS startsWith(name, 'prefix')` — starts with
* `ends_with ALIAS endsWith(name, 'suffix')` — ends with
* `is_empty ALIAS empty(name)` — empty check
* `is_not_empty ALIAS notEmpty(name)` — not empty check
* `ascii_code ALIAS ascii(name)` — ascii code
* `split_by_char ALIAS splitByChar(',', name)` — split by char
* `split_by_string ALIAS splitByString('::', name)` — split by string
* `formatted ALIAS format('Hello {1}, you are {0} years old', age, name)` — format
* `extract_groups ALIAS extractAllGroups(name, '(\\w+)=(\\w+)')` — regex extraction

### RQ.Ice.HybridAlias.TypeConversion
version: 1.0

[ClickHouse] SHALL support ALIAS columns that perform explicit type conversions
in Hybrid table segments, including narrowing conversions from larger to smaller types.

The following cases SHALL be covered:

* `toInt8(value)` — Int32 to Int8
* `toInt8(small_value)` — Int16 to Int8 (narrowing)
* `toInt16(value)` — Int32 to Int16
* `toInt16(value)` — Int32 to Int16 (narrowing)
* `toInt32(value)` — identity conversion
* `toInt32(big_value)` — Int64 to Int32 (narrowing)
* `toInt64(value)` — Int32 to Int64 (widening)
* `toUInt8(value)` — to UInt8
* `toUInt8(small_value)` — UInt16 to UInt8 (narrowing)
* `toUInt16(value)` — to UInt16
* `toUInt16(value)` — UInt32 to UInt16 (narrowing)
* `toUInt32(value)` — to UInt32
* `toUInt32(big_value)` — UInt64 to UInt32 (narrowing)
* `toUInt64(value)` — to UInt64
* `toFloat32(value)` — to Float32
* `toFloat32(big_float)` — Float64 to Float32 (narrowing)
* `toFloat64(value)` — to Float64
* `toString(value)` — to String
* `toDate(toString(date_col))` — to Date
* `toDateTime(toString(date_col))` — to DateTime

### RQ.Ice.HybridAlias.Conditional
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use conditional expressions
in Hybrid table segments.

The following cases SHALL be covered:

* `category ALIAS if(value > 50, 'high', 'low')` — if expression
* `case_when ALIAS CASE WHEN value > 50 THEN 'high' ELSE 'low' END` — CASE WHEN
* `case_expr ALIAS CASE value WHEN 1 THEN 'one' WHEN 2 THEN 'two' ELSE 'other' END` — CASE value WHEN
* `status ALIAS multiIf(value < 10, 'low', value < 50, 'medium', 'high')` — multiIf
* `grade ALIAS multiIf(score >= 90, 'A', score >= 80, 'B', score >= 70, 'C', 'F')` — multiIf grading
* `coalesced ALIAS coalesce(value1, value2, 0)` — coalesce
* `null_if_result ALIAS nullIf(value, 0)` — nullIf
* `if_null_result ALIAS ifNull(value, 0)` — ifNull
* `nullable_value ALIAS toNullable(value)` — toNullable
* `assumed_not_null ALIAS assumeNotNull(nullable_value)` — assumeNotNull
* `transform_result ALIAS transform(value, [...], [...], 'default')` — transform

### RQ.Ice.HybridAlias.NestedDependent
version: 1.0

[ClickHouse] SHALL support ALIAS columns that depend on other ALIAS columns
in Hybrid table segments, including multi-level dependency chains.

The following cases SHALL be covered:

* `computed + 10` depending on `computed ALIAS value * 2` — single-level dependency
* `doubled → quadrupled` chain — two-level dependency
* `doubled → quadrupled → octupled` chain — three-level dependency
* `doubled → quadrupled → octupled → hexadecupled` chain — four-level dependency
* `sum_all ALIAS id + value + doubled + quadrupled` — depends on multiple aliases
* `product_all ALIAS doubled * quadrupled` — product of two aliases
* `percentage ALIAS (doubled * 100) / (value + doubled)` — percentage calculation
* `nested_math ALIAS (doubled + quadrupled) * 2` — complex arithmetic with aliases
* `conditional_result ALIAS if(doubled > 100, quadrupled, doubled)` — conditional referencing aliases
* `string_combined ALIAS concat(toString(doubled), '-', toString(quadrupled))` — string ops on aliases

### RQ.Ice.HybridAlias.ComplexExpression
version: 1.0

[ClickHouse] SHALL support ALIAS columns with complex expressions that combine
multiple functions and operations in Hybrid table segments.

The following cases SHALL be covered:

* `score ALIAS (value * 2) + (id % 10) - length(name)` — arithmetic + string
* `formatted_date ALIAS concat(toString(toYear(date_col)), '-', toString(toMonth(date_col)))` — nested date/string
* `normalized_value ALIAS (value - min_value) / (max_value - min_value)` — normalization formula
* `weighted_sum ALIAS (value1 * 0.3) + (value2 * 0.5) + (value3 * 0.2)` — weighted sum
* `complex_math ALIAS sqrt(pow(value, 2) + pow(id, 2))` — Pythagorean calculation
* `complex_round ALIAS round((value * 1.5) / 3.0, 2)` — arithmetic with rounding
* `conditional_math ALIAS if(value > 0, sqrt(value), abs(value))` — conditional with math
* `nested_conditional ALIAS multiIf(value < 10, value * 2, value < 50, value * 3, value * 4)` — nested conditional
* `string_transform ALIAS concat(upper(substring(name, 1, 1)), lower(substring(name, 2)))` — string chain
* `string_math ALIAS length(concat(toString(value), '_', toString(id)))` — cross-domain

### RQ.Ice.HybridAlias.MathFunction
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use mathematical functions
in Hybrid table segments.

The following functions SHALL be covered:
abs, sqrt, cbrt, pow, power, exp, exp2, exp10, ln, log, log2, log10, log1p,
sin, cos, tan, asin, acos, atan, atan2, sinh, cosh, tanh, asinh, acosh, atanh,
erf, erfc, lgamma, tgamma, sign.

### RQ.Ice.HybridAlias.RoundingFunction
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use rounding functions
in Hybrid table segments.

The following functions SHALL be covered:
round (with and without precision), ceil (with and without precision), ceiling,
floor (with and without precision), trunc (with and without precision), truncate,
roundBankers (with and without precision), roundDown, roundAge, roundDuration.

### RQ.Ice.HybridAlias.ArrayFunction
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use array manipulation functions
in Hybrid table segments.

The following cases SHALL be covered:

* `arrayElement(array_col, 1)` — first element
* `arrayElement(array_col, length(array_col))` — last element
* `length(array_col)` — array length
* `arraySum(array_col)` — array sum
* `arrayProduct(array_col)` — array product
* `arraySort(array_col)` — sort
* `arrayReverse(array_col)` — reverse
* `arrayDistinct(array_col)` — deduplicate
* `arraySlice(array_col, 1, 3)` — slice
* `arrayConcat(array1, array2)` — concatenation

### RQ.Ice.HybridAlias.TupleFunction
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use tuple element access
functions in Hybrid table segments.

The following cases SHALL be covered:

* `tupleElement(tuple_col, 1)` — first element
* `tupleElement(tuple_col, 2)` — second element

### RQ.Ice.HybridAlias.MapFunction
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use map manipulation functions
in Hybrid table segments.

The following cases SHALL be covered:

* `map_col['key']` — element access by key
* `mapKeys(map_col)` — key extraction
* `mapValues(map_col)` — value extraction
* `length(map_col)` — map size

### RQ.Ice.HybridAlias.JsonFunction
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use JSON extraction functions
in Hybrid table segments.

The following cases SHALL be covered:

* `JSONExtractInt(toString(json_col), 'key')` — integer extraction
* `JSONExtractFloat(toString(json_col), 'key')` — float extraction
* `JSONExtractString(toString(json_col), 'key')` — string extraction
* `JSONHas(toString(json_col), 'key')` — key existence check

### RQ.Ice.HybridAlias.HashEncodingFunction
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use hashing and encoding
functions in Hybrid table segments.

The following cases SHALL be covered:

* `hex(string_col)` — hex encoding
* `base64Encode(string_col)` — base64 encoding
* `base64Decode(encoded_col)` — base64 decoding (alias-on-alias dependency)

### RQ.Ice.HybridAlias.UtilityFunction
version: 1.0

[ClickHouse] SHALL support ALIAS columns that use utility and comparison
functions in Hybrid table segments.

The following cases SHALL be covered:

* `least(val1, val2)` — least of two values
* `least(val1, val2, val3)` — least of three values
* `least(val1, val2, val3, val4)` — least of four values
* `least(str1, str2)` — least of strings
* `least(date1, date2)` — least of dates
* `greatest(val1, val2)` — greatest of two values
* `greatest(val1, val2, val3)` — greatest of three values
* `greatest(val1, val2, val3, val4)` — greatest of four values
* `greatest(str1, str2, str3)` — greatest of strings
* `greatest(date1, date2)` — greatest of dates
* `countDigits(value)` — digit count (Int32)
* `countDigits(big_value)` — digit count (Int64)
* `countDigits(uint_value)` — digit count (UInt32)

## Query Context

### RQ.Ice.HybridAlias.QueryContext
version: 1.0

[ClickHouse] SHALL support ALIAS columns in various SQL query contexts
when querying Hybrid tables.

The following query patterns SHALL be covered:

* BETWEEN and IN predicates in watermarks — `id BETWEEN 10 AND 15`, `value IN (10, 20, 30)`
* String LIKE predicate in watermark — `name LIKE 'A%'`
* Complex AND/OR watermark predicates combining base and alias columns
* HAVING clause filtering on alias column aggregations — `HAVING sum(computed) > 100`
* JOIN operations with alias columns in result set — self-join selecting alias from both sides
* Subqueries selecting and filtering alias columns — `SELECT * FROM (SELECT id, computed FROM ...)`
* ORDER BY alias columns — `ORDER BY computed ASC`, `ORDER BY computed DESC, sum_alias ASC`
* GROUP BY single and multiple alias columns — `GROUP BY year_month`, `GROUP BY year_val, month_val`

## Top-Level Tests

### RQ.Ice.HybridAlias.SimpleArithmeticAlias
version: 1.0

[ClickHouse] SHALL support multiple ALIAS columns (`computed ALIAS value * 2`,
`sum_alias ALIAS id + value`) in a single Hybrid table with both aliases
queryable via SELECT in various combinations (alias only, mix of base and alias).

### RQ.Ice.HybridAlias.AliasColumnInPredicate
version: 1.0

[ClickHouse] SHALL support or explicitly handle ALIAS columns used directly
in watermark predicates for Hybrid tables (`computed >= 20` / `computed < 20`).
If supported, the alias expression SHALL be correctly evaluated during predicate
routing. GROUP BY and aggregations (`max`, `min`) on alias columns SHALL also
be supported.

### RQ.Ice.HybridAlias.LeftAliasRightNormal
version: 1.0

[ClickHouse] SHALL support Hybrid tables where the left segment defines a
column as an ALIAS (`computed ALIAS value * 2`) and the right segment defines
the same column as a regular column (`computed Int64`). The Hybrid table SHALL
correctly return values from both segments.

### RQ.Ice.HybridAlias.LeftAliasRightNormalTypeMismatch
version: 1.0

[ClickHouse] SHALL handle Hybrid tables where the left segment defines a column
as an ALIAS returning Int64 and the right segment defines the same column as a
regular Float64 column. Automatic type casting SHALL be applied when
`hybrid_table_auto_cast_columns = 1` is enabled.

### RQ.Ice.HybridAlias.LeftNormalRightAlias
version: 1.0

[ClickHouse] SHALL support Hybrid tables where the left segment defines a
column as a regular column (`computed Int64`) and the right segment defines
the same column as an ALIAS (`computed ALIAS value * 2`). The Hybrid table
SHALL correctly return values from both segments.

### RQ.Ice.HybridAlias.LeftNormalRightAliasTypeMismatch
version: 1.0

[ClickHouse] SHALL return an error when the left segment defines a column as a
regular Int32 column and the right segment defines the same column as an ALIAS
returning Int64, when the types are incompatible. The error SHALL indicate
a type mismatch between segments.

### RQ.Ice.HybridAlias.DifferentAliasExpressions
version: 1.0

[ClickHouse] SHALL support Hybrid tables where both segments define the same
column as an ALIAS but with different expressions (left: `value * 2`,
right: `value * 3`). Each segment SHALL independently evaluate its own alias
expression.

### RQ.Ice.HybridAlias.AliasMissingInSegment
version: 1.0

[ClickHouse] SHALL return an error when a Hybrid table defines a column that
is present as an ALIAS in one segment but completely missing from the other
segment (neither as alias nor regular column). The error SHALL indicate the
missing column.

[ClickHouse]: https://clickhouse.com
