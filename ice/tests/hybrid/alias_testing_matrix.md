# ALIAS Columns Testing Matrix for Hybrid Tables

## Overview

This document provides a structured approach to testing ALIAS columns in hybrid table engine segments. It categorizes all possible types of aliases and watermark patterns to ensure comprehensive test coverage.

## Settings

`asterisk_include_alias_columns` — controls whether `SELECT *` includes ALIAS columns.
No dedicated test exists for this setting.

## 1. ALIAS Column Types

### 1.1 Simple Arithmetic Aliases

Aliases that perform basic arithmetic operations on base columns.

**Examples:**
- `computed ALIAS value * 2`
- `sum_alias ALIAS id + value`
- `difference ALIAS value1 - value2`
- `product ALIAS value1 * value2`
- `quotient ALIAS value1 / value2`
- `modulo ALIAS value % 3`
- `intdiv ALIAS intDiv(value, 2)`
- `negative ALIAS abs(value) - abs(value * 2)`
- `multiple ALIAS (value1 * value2 - value3) % (value2 + 1)`
- `scaled ALIAS price * 1.5` (Float32 base column)
- `total ALIAS amount1 + amount2` (Float64 base columns)
- `ratio ALIAS amount1 / amount2` (Float64 base columns)

**Test Coverage:**
- Basic arithmetic operations (+, -, *, /, %)
- Integer division (intDiv)
- Multiple operands in a single expression
- Negative result values
- Division by zero handling
- Division operation explicitly tested
- Arithmetic with Float32 and Float64 base column types
- Alias column used in watermark predicates

### 1.2 Constant Aliases

Aliases that evaluate to constant values.

**Examples:**
- `default_int8 ALIAS -50` (Int8)
- `default_int32 ALIAS toInt32(50000)` (Int32)
- `default_int64 ALIAS toInt64(1000000000)` (Int64)
- `default_int128 ALIAS toInt128(...)` (Int128)
- `default_int256 ALIAS toInt256(...)` (Int256)
- `default_uint256 ALIAS toUInt256(...)` (UInt256)
- `default_float32 ALIAS toFloat32(3.14159)` (Float32)
- `default_float64 ALIAS 2.718281828459045` (Float64)
- `default_decimal32 ALIAS toDecimal32(4.2, 8)` (Decimal32)
- `default_string ALIAS 'hello world'` (String)
- `default_date ALIAS toDate('2025-01-01')` (Date)
- `default_datetime ALIAS toDateTime('2025-01-01 12:00:00')` (DateTime)
- `default_datetime64 ALIAS toDateTime64('2025-01-01 12:00:00', 0)` (DateTime64)
- `default_bool ALIAS true` (Bool)
- `default_bool_false ALIAS false` (Bool)
- `default_array ALIAS array(1, 2, 3)` (Array(UInt8))
- `default_array_string ALIAS array('a', 'b', 'c')` (Array(String))
- `default_tuple ALIAS tuple(1, 'hello', 3.14)` (Tuple)
- `default_nested_tuple ALIAS tuple(1, tuple(2, 3), 4)` (nested Tuple)
- `default_map ALIAS map('key1', 'value1', 'key2', 'value2')` (Map)
- `default_json ALIAS '...'::JSON` (JSON)

**Test Coverage:**
- Numeric constants (Int8, Int32, Int64, Int128, Int256, UInt256, Float32, Float64, Decimal32)
- String constants
- Date and DateTime constants (Date, DateTime, DateTime64)
- Boolean constants (true, false)
- Array constants (numeric and string arrays)
- Tuple constants (flat and nested)
- Map constants
- JSON constants

### 1.3 Boolean/Logical Aliases

Aliases that evaluate to boolean values (UInt8 0/1 in ClickHouse).

**Examples:**
- `is_equal ALIAS value = 42` (=)
- `is_not_equal ALIAS value != 42` (!=)
- `is_less ALIAS value < 100` (<)
- `is_less_equal ALIAS value <= 100` (<=)
- `is_greater ALIAS value > 0` (>)
- `is_greater_equal ALIAS value >= 0` (>=)
- `is_even ALIAS value % 2 = 0` (arithmetic + comparison)
- `is_recent ALIAS date_col >= '2025-01-15'` (date comparison)
- `is_active ALIAS status = 'active'` (string comparison)
- `is_valid ALIAS value > 0 AND value < 100` (AND)
- `is_or_condition ALIAS value < 10 OR value > 90` (OR)
- `is_not_condition ALIAS NOT (value = 0)` (NOT)
- `is_complex_logic ALIAS (value > 0 AND value < 100) OR (value > 200 AND value < 300)` (complex AND/OR)
- `is_xor_condition ALIAS xor(value > 50, value < 100)` (XOR)
- `is_in_range ALIAS value BETWEEN 10 AND 100` (BETWEEN)
- `is_not_in_range ALIAS value NOT BETWEEN 10 AND 100` (NOT BETWEEN)
- `is_in_set ALIAS value IN (1, 2, 3, 4, 5)` (IN)
- `is_not_in_set ALIAS value NOT IN (1, 2, 3, 4, 5)` (NOT IN)
- `is_like ALIAS name LIKE '%test%'` (LIKE)
- `is_not_like ALIAS name NOT LIKE '%test%'` (NOT LIKE)
- `is_ilike ALIAS name ILIKE '%TEST%'` (ILIKE)
- `is_null_check ALIAS isNull(value)` (NULL check)
- `is_not_null_check ALIAS isNotNull(value)` (NOT NULL check)

**Test Coverage:**
- Comparison operators (=, !=, <, <=, >, >=)
- Logical operators (AND, OR, NOT, XOR)
- Complex boolean expressions combining AND/OR
- BETWEEN and NOT BETWEEN range checks
- IN and NOT IN set membership
- LIKE, NOT LIKE, and ILIKE pattern matching
- NULL handling (isNull, isNotNull)

### 1.4 Date/Time Function Aliases

Aliases that use date and time functions.

**Examples:**
- `year ALIAS toYear(date_col)`
- `month ALIAS toMonth(date_col)`
- `day_of_week ALIAS toDayOfWeek(date_col)`
- `day_of_month ALIAS toDayOfMonth(date_col)`
- `quarter ALIAS toQuarter(date_col)`
- `year_month ALIAS toYYYYMM(date_col)`
- `year_month_day ALIAS toYYYYMMDD(date_col)`
- `hour ALIAS toHour(datetime_col)`
- `minute ALIAS toMinute(datetime_col)`
- `second ALIAS toSecond(datetime_col)`
- `start_of_day ALIAS toStartOfDay(datetime_col)`
- `start_of_hour ALIAS toStartOfHour(datetime_col)`
- `start_of_month ALIAS toStartOfMonth(datetime_col)`
- `start_of_quarter ALIAS toStartOfQuarter(datetime_col)`
- `start_of_week ALIAS toStartOfWeek(datetime_col)`
- `start_of_year ALIAS toStartOfYear(datetime_col)`
- `date_string ALIAS toString(date_col)`
- `datetime_string ALIAS toString(datetime_col)`
- `tz_converted ALIAS toTimeZone(datetime_col, 'America/New_York')`
- `timestamp ALIAS toUnixTimestamp(date_col)`
- `date_plus_days ALIAS addDays(date_col, 7)`
- `date_plus_months ALIAS addMonths(date_col, 1)`
- `date_plus_years ALIAS addYears(date_col, 1)`
- `date_minus_days ALIAS subtractDays(date_col, 7)`
- `date_minus_months ALIAS subtractMonths(date_col, 1)`
- `date_minus_years ALIAS subtractYears(date_col, 1)`
- `date_plus_interval ALIAS date_col + INTERVAL 7 DAY`
- `date_minus_interval ALIAS date_col - INTERVAL 1 MONTH`
- `datetime_plus_interval ALIAS datetime_col + INTERVAL 1 HOUR`

**Test Coverage:**
- Date part extraction (toYear, toMonth, toDayOfWeek, toDayOfMonth, toQuarter, toYYYYMM, toYYYYMMDD)
- Time part extraction (toHour, toMinute, toSecond)
- Start-of-period truncation (toStartOfDay, toStartOfHour, toStartOfMonth, toStartOfQuarter, toStartOfWeek, toStartOfYear)
- Date/DateTime formatting (toString)
- Date arithmetic via functions (addDays, addMonths, addYears, subtractDays, subtractMonths, subtractYears)
- Date arithmetic via INTERVAL syntax (date +/- INTERVAL)
- Time zone conversion (toTimeZone)
- Unix timestamp conversion (toUnixTimestamp)

### 1.5 String Function Aliases

Aliases that use string manipulation functions.

**Examples:**
- `upper_name ALIAS upper(name)`
- `lower_name ALIAS lower(name)`
- `name_length ALIAS length(name)`
- `name_length_utf8 ALIAS lengthUTF8(name)`
- `substring_name ALIAS substring(name, 1, 5)`
- `substring_from ALIAS substring(name, 3)`
- `reversed_name ALIAS reverse(name)`
- `concatenated ALIAS concat(first_name, ' ', last_name)`
- `concat_ws ALIAS concatWithSeparator(' ', first_name, last_name)`
- `array_concat ALIAS arrayStringConcat([first, second], ' ')`
- `replaced_all ALIAS replaceAll(name, 'old', 'new')`
- `replaced_one ALIAS replaceOne(name, 'old', 'new')`
- `replaced_regexp ALIAS replaceRegexpOne(name, '\\d+', 'X')`
- `repeated_name ALIAS repeat(name, 3)`
- `left_padded ALIAS leftPad(name, 10, '0')`
- `right_padded ALIAS rightPad(name, 10, '0')`
- `trimmed_name ALIAS trimBoth(name, 'a')`
- `trimmed_left ALIAS trimLeft(name, 'a')`
- `trimmed_right ALIAS trimRight(name, 'a')`
- `position_sub ALIAS position(name, 'test')`
- `position_ci ALIAS positionCaseInsensitive(name, 'TEST')`
- `starts_with ALIAS startsWith(name, 'prefix')`
- `ends_with ALIAS endsWith(name, 'suffix')`
- `is_empty ALIAS empty(name)`
- `is_not_empty ALIAS notEmpty(name)`
- `ascii_code ALIAS ascii(name)`
- `split_by_char ALIAS splitByChar(',', name)`
- `split_by_string ALIAS splitByString('::', name)`
- `formatted ALIAS format('Hello {1}, you are {0} years old', age, name)`
- `extract_groups ALIAS extractAllGroups(name, '(\\w+)=(\\w+)')`

**Test Coverage:**
- Case transformation (upper, lower)
- Length functions (length, lengthUTF8)
- Substring extraction (substring with and without length)
- String reversal (reverse)
- Concatenation (concat, concatWithSeparator, arrayStringConcat)
- Replacement (replaceAll, replaceOne, replaceRegexpOne)
- Repetition (repeat)
- Padding (leftPad, rightPad)
- Trimming (trimBoth, trimLeft, trimRight)
- Search/position (position, positionCaseInsensitive)
- Prefix/suffix checks (startsWith, endsWith)
- Empty checks (empty, notEmpty)
- Character code (ascii)
- Splitting (splitByChar, splitByString)
- Formatting (format)
- Regex extraction (extractAllGroups)

### 1.6 Type Conversion Aliases

Aliases that perform implicit or explicit type conversions.

**Examples:**
- `value_int8 ALIAS toInt8(value)`
- `value_int8 ALIAS toInt8(small_value)` (narrowing from Int16)
- `value_int16 ALIAS toInt16(value)`
- `value_int16 ALIAS toInt16(value)` (narrowing from Int32)
- `value_int32 ALIAS toInt32(value)`
- `value_int32 ALIAS toInt32(big_value)` (narrowing from Int64)
- `value_int64 ALIAS toInt64(value)`
- `value_uint8 ALIAS toUInt8(value)`
- `value_uint8 ALIAS toUInt8(small_value)` (narrowing from UInt16)
- `value_uint16 ALIAS toUInt16(value)`
- `value_uint16 ALIAS toUInt16(value)` (narrowing from UInt32)
- `value_uint32 ALIAS toUInt32(value)`
- `value_uint32 ALIAS toUInt32(big_value)` (narrowing from UInt64)
- `value_uint64 ALIAS toUInt64(value)`
- `value_float32 ALIAS toFloat32(value)`
- `value_float32 ALIAS toFloat32(big_float)` (narrowing from Float64)
- `value_float64 ALIAS toFloat64(value)`
- `value_str ALIAS toString(value)`
- `value_date ALIAS toDate(toString(date_col))`
- `value_datetime ALIAS toDateTime(toString(date_col))`

**Test Coverage:**
- Signed integer conversions (toInt8, toInt16, toInt32, toInt64)
- Unsigned integer conversions (toUInt8, toUInt16, toUInt32, toUInt64)
- Float conversions (toFloat32, toFloat64)
- String conversion (toString)
- Date conversions (toDate, toDateTime)
- Narrowing conversions (larger type to smaller type: Int16→Int8, Int32→Int16, Int64→Int32, UInt16→UInt8, UInt32→UInt16, UInt64→UInt32, Float64→Float32)

### 1.7 Aggregate Function Aliases (if supported)

Aliases that use aggregate functions (may not be supported in all contexts).

**Examples:**
- `avg_value ALIAS avg(value) OVER (PARTITION BY category)`
- `running_total ALIAS sum(value) OVER (ORDER BY date_col)`

**Test Coverage:**
- No dedicated tests exist for aggregate/window function aliases

### 1.8 Conditional Aliases

Aliases that use conditional expressions.

**Examples:**
- `category ALIAS if(value > 50, 'high', 'low')`
- `case_when ALIAS CASE WHEN value > 50 THEN 'high' ELSE 'low' END`
- `case_expr ALIAS CASE value WHEN 1 THEN 'one' WHEN 2 THEN 'two' ELSE 'other' END`
- `status ALIAS multiIf(value < 10, 'low', value < 50, 'medium', 'high')`
- `grade ALIAS multiIf(score >= 90, 'A', score >= 80, 'B', score >= 70, 'C', 'F')`
- `coalesced ALIAS coalesce(value1, value2, 0)`
- `null_if_result ALIAS nullIf(value, 0)`
- `if_null_result ALIAS ifNull(value, 0)`
- `nullable_value ALIAS toNullable(value)`
- `assumed_not_null ALIAS assumeNotNull(nullable_value)`
- `transform_result ALIAS transform(value, [0, -2147483648, 2147483647], ['a', 'b', 'c'], 'default')`

**Test Coverage:**
- if() expressions
- CASE WHEN expressions
- CASE value WHEN expressions
- multiIf expressions (simple and multi-branch grading)
- coalesce for NULL fallback
- NULL-related functions (nullIf, ifNull, toNullable, assumeNotNull)
- transform() value mapping

### 1.9 Nested/Dependent Aliases

Aliases that depend on other alias columns.

**Examples:**
- `computed ALIAS value * 2`, `computed_2 ALIAS computed + 10` (single-level)
- `doubled ALIAS value * 2`, `quadrupled ALIAS doubled * 2` (two-level chain)
- `doubled → quadrupled → octupled ALIAS quadrupled * 2` (three-level chain)
- `doubled → quadrupled → octupled → hexadecupled ALIAS octupled * 2` (four-level chain)
- `sum_all ALIAS id + value + doubled + quadrupled` (depends on multiple aliases)
- `product_all ALIAS doubled * quadrupled` (product of two aliases)
- `percentage ALIAS (doubled * 100) / (value + doubled)` (percentage calculation with alias)
- `nested_math ALIAS (doubled + quadrupled) * 2` (complex arithmetic with aliases)
- `conditional_result ALIAS if(doubled > 100, quadrupled, doubled)` (conditional with aliases)
- `string_combined ALIAS concat(toString(doubled), '-', toString(quadrupled))` (string ops on aliases)

**Test Coverage:**
- Single-level dependency (alias depends on one alias)
- Two-level dependency chain (alias → alias → base)
- Three-level dependency chain (alias → alias → alias → base)
- Four-level dependency chain (alias → alias → alias → alias → base)
- Multiple dependencies (alias depends on multiple aliases simultaneously)
- Complex arithmetic combining multiple aliases
- Conditional expressions referencing aliases
- String operations on alias column values

### 1.10 Complex Expression Aliases

Aliases with complex expressions combining multiple functions and operations.

**Examples:**
- `score ALIAS (value * 2) + (id % 10) - length(name)` (arithmetic + string combined)
- `formatted_date ALIAS concat(toString(toYear(date_col)), '-', toString(toMonth(date_col)))` (nested date/string)
- `normalized_value ALIAS (value - min_value) / (max_value - min_value)` (normalization formula)
- `weighted_sum ALIAS (value1 * 0.3) + (value2 * 0.5) + (value3 * 0.2)` (weighted sum)
- `complex_math ALIAS sqrt(pow(value, 2) + pow(id, 2))` (Pythagorean calculation)
- `complex_round ALIAS round((value * 1.5) / 3.0, 2)` (arithmetic with rounding)
- `conditional_math ALIAS if(value > 0, sqrt(value), abs(value))` (conditional with math)
- `nested_conditional ALIAS multiIf(value < 10, value * 2, value < 50, value * 3, value * 4)` (nested conditional arithmetic)
- `string_transform ALIAS concat(upper(substring(name, 1, 1)), lower(substring(name, 2)))` (string transformation chain)
- `string_math ALIAS length(concat(toString(value), '_', toString(id)))` (string + math combined)

**Test Coverage:**
- Arithmetic combined with string functions
- Nested date and string function calls
- Normalization/scaling formulas
- Weighted sum with float coefficients
- Math functions in complex expressions (sqrt, pow)
- Rounding within arithmetic expressions
- Conditional expressions with math branches
- Nested multiIf with arithmetic
- Chained string transformations
- Cross-domain expressions (string length of numeric concatenation)

### 1.11 Math Function Aliases

Aliases that use mathematical functions.

**Examples:**
- `abs_value ALIAS abs(value)`
- `sqrt_value ALIAS sqrt(value)`
- `cbrt_value ALIAS cbrt(value)`
- `pow_value ALIAS pow(value, 2)`
- `power_value ALIAS power(value, 2)`
- `exp_value ALIAS exp(value)`
- `exp2_value ALIAS exp2(value)`
- `exp10_value ALIAS exp10(value)`
- `ln_value ALIAS ln(value)`
- `log_value ALIAS log(value)`
- `log2_value ALIAS log2(value)`
- `log10_value ALIAS log10(value)`
- `log1p_value ALIAS log1p(value)`
- `sin_value ALIAS sin(value)`
- `cos_value ALIAS cos(value)`
- `tan_value ALIAS tan(value)`
- `asin_value ALIAS asin(value)`
- `acos_value ALIAS acos(value)`
- `atan_value ALIAS atan(value)`
- `atan2_value ALIAS atan2(value, 1)`
- `sinh_value ALIAS sinh(value)`
- `cosh_value ALIAS cosh(value)`
- `tanh_value ALIAS tanh(value)`
- `asinh_value ALIAS asinh(value)`
- `acosh_value ALIAS acosh(value)`
- `atanh_value ALIAS atanh(value)`
- `erf_value ALIAS erf(value)`
- `erfc_value ALIAS erfc(value)`
- `lgamma_value ALIAS lgamma(value)`
- `tgamma_value ALIAS tgamma(value)`
- `sign_value ALIAS sign(value)`

**Test Coverage:**
- Absolute value (abs)
- Roots (sqrt, cbrt)
- Powers and exponents (pow, power, exp, exp2, exp10)
- Logarithms (ln, log, log2, log10, log1p)
- Trigonometric functions (sin, cos, tan, asin, acos, atan, atan2)
- Hyperbolic functions (sinh, cosh, tanh, asinh, acosh, atanh)
- Error functions (erf, erfc)
- Gamma functions (lgamma, tgamma)
- Sign function (sign)

### 1.12 Rounding Function Aliases

Aliases that use rounding functions.

**Examples:**
- `rounded ALIAS round(value)`
- `rounded_precision ALIAS round(value, 2)`
- `ceiled ALIAS ceil(value)`
- `ceiled_precision ALIAS ceil(value, 2)`
- `ceiling_alias ALIAS ceiling(value)`
- `floored ALIAS floor(value)`
- `floored_precision ALIAS floor(value, 2)`
- `truncated ALIAS trunc(value)`
- `truncated_precision ALIAS trunc(value, 2)`
- `truncate_alias ALIAS truncate(value)`
- `bankers_round ALIAS roundBankers(value)`
- `bankers_round_precision ALIAS roundBankers(value, 2)`
- `rounded_down ALIAS roundDown(value, [10, 20, 30, 50])`
- `age_rounded ALIAS roundAge(value)`
- `duration_rounded ALIAS roundDuration(value)`

**Test Coverage:**
- Standard rounding (round, with and without precision)
- Ceiling (ceil, ceiling, with and without precision)
- Floor (floor, with and without precision)
- Truncation (trunc, truncate, with and without precision)
- Banker's rounding (roundBankers, with and without precision)
- Round down to array element (roundDown)
- Domain-specific rounding (roundAge, roundDuration)

### 1.13 Array Function Aliases

Aliases that use array manipulation functions.

**Examples:**
- `array_first ALIAS arrayElement(array_col, 1)`
- `array_last ALIAS arrayElement(array_col, length(array_col))`
- `array_length ALIAS length(array_col)`
- `array_sum ALIAS arraySum(array_col)`
- `array_product ALIAS arrayProduct(array_col)`
- `array_sorted ALIAS arraySort(array_col)`
- `array_reversed ALIAS arrayReverse(array_col)`
- `array_unique ALIAS arrayDistinct(array_col)`
- `array_slice ALIAS arraySlice(array_col, 1, 3)`
- `array_concat ALIAS arrayConcat(array1, array2)`

**Test Coverage:**
- Element access (arrayElement for first and last)
- Array length (length)
- Aggregation (arraySum, arrayProduct)
- Sorting (arraySort)
- Reversal (arrayReverse)
- Deduplication (arrayDistinct)
- Slicing (arraySlice)
- Concatenation (arrayConcat)

### 1.14 Tuple Function Aliases

Aliases that use tuple element access functions.

**Examples:**
- `tuple_first ALIAS tupleElement(tuple_col, 1)`
- `tuple_second ALIAS tupleElement(tuple_col, 2)`

**Test Coverage:**
- Tuple element access by index (tupleElement)

### 1.15 Map Function Aliases

Aliases that use map manipulation functions.

**Examples:**
- `map_get ALIAS map_col['key']`
- `map_keys ALIAS mapKeys(map_col)`
- `map_values ALIAS mapValues(map_col)`
- `map_size ALIAS length(map_col)`

**Test Coverage:**
- Map element access by key (operator[])
- Key extraction (mapKeys)
- Value extraction (mapValues)
- Map size (length)

### 1.16 JSON Function Aliases

Aliases that use JSON extraction functions.

**Examples:**
- `json_extract_int ALIAS JSONExtractInt(toString(json_col), 'key')`
- `json_extract_float ALIAS JSONExtractFloat(toString(json_col), 'key')`
- `json_extract_string ALIAS JSONExtractString(toString(json_col), 'key')`
- `json_has ALIAS JSONHas(toString(json_col), 'key')`

**Test Coverage:**
- JSON integer extraction (JSONExtractInt)
- JSON float extraction (JSONExtractFloat)
- JSON string extraction (JSONExtractString)
- JSON key existence check (JSONHas)

### 1.17 Hash and Encoding Function Aliases

Aliases that use hashing and encoding functions.

**Examples:**
- `hex_encoded ALIAS hex(string_col)`
- `base64_encoded ALIAS base64Encode(string_col)`
- `base64_decoded ALIAS base64Decode(encoded_col)` (depends on alias encoded_col)

**Test Coverage:**
- Hex encoding (hex)
- Base64 encoding (base64Encode)
- Base64 decoding (base64Decode, including alias-on-alias dependency)

### 1.18 Utility Function Aliases

Aliases that use utility/comparison functions.

**Examples:**
- `least_two ALIAS least(val1, val2)`
- `least_three ALIAS least(val1, val2, val3)`
- `least_four ALIAS least(val1, val2, val3, val4)`
- `least_string ALIAS least(str1, str2)`
- `least_date ALIAS least(date1, date2)`
- `greatest_two ALIAS greatest(val1, val2)`
- `greatest_three ALIAS greatest(val1, val2, val3)`
- `greatest_four ALIAS greatest(val1, val2, val3, val4)`
- `greatest_string ALIAS greatest(str1, str2, str3)`
- `greatest_date ALIAS greatest(date1, date2)`
- `digit_count ALIAS countDigits(value)` (Int32)
- `digit_count_int64 ALIAS countDigits(big_value)` (Int64)
- `digit_count_uint32 ALIAS countDigits(uint_value)` (UInt32)

**Test Coverage:**
- least() with 2, 3, and 4 numeric arguments
- least() with string and date types
- greatest() with 2, 3, and 4 numeric arguments
- greatest() with string and date types
- countDigits() with Int32, Int64, and UInt32 types

## 2. Watermark Predicates and Query Patterns

Every test file includes two scenarios: one with a date-based watermark predicate on
a base column, and one with the alias column used directly in the watermark predicate.


### 2.1 Watermark Predicate Patterns Tested

**Date-based direct column predicate (all first scenarios):**
- `date_col >= '2025-01-15'` / `date_col < '2025-01-15'`

**Alias column in predicate (all `_in_watermark` scenarios):**
- Numeric alias: `computed >= 10000`, `sum_alias >= 10000`, `scaled >= 500.0`
- Division alias: `quotient >= 10.0`, `modulo >= 1`
- Boolean alias: `is_even = 1`, `is_valid = 1`
- Date function alias: `year >= 2020`, `year_month >= 202501`
- String function alias: `name_length >= 5`
- Array alias: `array_sum >= 100`, `length(array_sorted) >= 5`
- Nested alias: `quadrupled >= 1000`, `octupled >= 10000`
- Conditional alias: `category = 'high'`, `case_when = 'high'`
- Edge case: `isFinite(div_by_zero) = 0` 

**Overlapping segment predicate:**
- `date_col >= '2013-08-05'` / `date_col < '2025-08-05'` (in `alias_column_in_predicate.py`)

### 2.2 Query Patterns in Test Queries

All test files use a standard set of query patterns via `test_queries`:
- **SELECT**: base columns only, alias columns only, mix of base and alias columns
- **WHERE**: filtering by alias value, filtering by base column value
- **ORDER BY**: ordering by `id` (base column)

**Additional patterns in specific top-level tests:**
- `simple_arithmetic_alias.py` — selects only alias columns, mix of base and alias columns
- `alias_column_in_predicate.py` — `GROUP BY date_col`, `max(computed)`, `min(computed)` aggregations on alias columns

### 2.3 Query Context Tests (query_context/ folder)

Dedicated test files for watermark and query patterns:

- `between_in_watermark.py` — BETWEEN and IN predicates in watermarks
- `string_watermark.py` — String LIKE predicate in watermark
- `complex_watermark.py` — Complex AND/OR watermark predicates combining base and alias columns
- `having_alias.py` — HAVING clause filtering on alias column aggregations
- `join_alias.py` — JOIN operations with alias columns in result set
- `subquery_alias.py` — Subqueries selecting and filtering alias columns
- `order_by_alias.py` — ORDER BY alias columns (ASC, DESC, multiple aliases)
- `group_by_alias.py` — GROUP BY single and multiple alias columns

## 3. Segment Behavior

Segment behavior is tested by dedicated top-level test files.

### 3.1 Tested Scenarios

- **Left alias, right normal**: `left_alias_right_normal.py` — left segment has ALIAS, right has regular column
- **Left normal, right alias**: `left_normal_right_alias.py` — left segment has regular column, right has ALIAS
- **Left alias, right normal with type mismatch**: `left_alias_right_normal_type_mismatch.py` — Float64 regular vs Int64 alias
- **Left normal, right alias with type mismatch**: `left_normal_right_alias_type_mismatch.py` — Int32 regular vs Int64 alias (expects error)

### 3.2 Both Segments Alias with Different Expressions

- `different_alias_expressions.py` — left segment: `computed ALIAS value * 2`, right segment: `computed ALIAS value * 3`

### 3.3 Alias Missing in One Segment

- `alias_missing_in_segment.py` — alias in left, completely absent in right (and vice versa)

## 4. Edge Cases

### 4.1 Tested

- **Division by zero**: `arithmetic/div_by_zero_alias.py` — `value / 0` producing inf
- **NULL-related functions**: `conditional_functions/nullIf_alias.py`, `ifNull_alias.py`, `toNullable_alias.py`, `assumeNotNull_alias.py`
- **NULL checks in boolean**: `boolean_logical/is_null_check_alias.py`, `is_not_null_check_alias.py`
- **Type mismatch across segments**: `left_alias_right_normal_type_mismatch.py`, `left_normal_right_alias_type_mismatch.py`
- **Alias missing in segment**: `alias_missing_in_segment.py` — expects error (exit code 36)
- **Different alias expressions**: `different_alias_expressions.py` — same column name, different expression per segment

### 4.2 Not Tested

- Circular alias dependencies (alias A depends on alias B and vice versa)
- Alias referencing a non-existent or dropped base column
- Invalid type conversions in alias expressions
- `asterisk_include_alias_columns` setting
