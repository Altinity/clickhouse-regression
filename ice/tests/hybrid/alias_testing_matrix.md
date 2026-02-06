# ALIAS Columns Testing Matrix for Hybrid Tables

## Overview

This document provides a structured approach to testing ALIAS columns in hybrid table engine segments. It categorizes all possible types of aliases and watermark patterns to ensure comprehensive test coverage.

## Settings

asterisk_include_alias_columns

## 1. ALIAS Column Types

### 1.1 Simple Arithmetic Aliases

Aliases that perform basic arithmetic operations on base columns.

**Examples:**
    1. `computed ALIAS value * 2`
    2. `sum_alias ALIAS id + value`
    3. `difference ALIAS value1 - value2`
    4. `product ALIAS value1 * value2`
    5. `quotient ALIAS value1 / value2`
    6. `modulo ALIAS value % 3`
    7. `intdiv ALIAS intDiv(value, 2)`
    8. `multiple ALIAS (value1 * value2 - value3) % value2`
    9. `div_by_zero ALIAS value / 0`
    10. `negative abs(value)-abs(value*2)`

**Test Coverage:**
- Basic arithmetic operations (+, -, *, /, %)
- Multiple operands
- Integer division (intDiv)
- Zero values
- Division by zero handling
- Negative numbers
- Different numeric base column types (Int8, Int16, Int32, Int64, UInt8, UInt16, UInt32, UInt64, Float32, Float64)

### 1.2 Constant Aliases

Aliases that evaluate to constant values.

**Examples:**
    1. `default_int8 ALIAS 50`
    2. `default_int32 ALIAS 50000`
    3. `default_int64 ALIAS 1000000000`
    4. `default_int128 ALIAS 170141183460469231731687303715884105727`
    5. `default_int256 ALIAS 57896044618658097711785492504343953926634992332820282019728792003956564819967`
    6. `default_uint256 ALIAS 115792089237316195423570985008687907853269984665640564039457584007913129639935`
    7. `default_float32 ALIAS 3.14159`
    8. `default_float64 ALIAS 2.718281828459045`
    9. `default_decimal32 ALIAS toDecimal32(4.2, 8)`
    10. `default_date ALIAS toDate('2025-01-01')`
    11. `default_datetime ALIAS '2025-01-01 12:00:00'`
    12. `default_datetime64 ALIAS toDateTime('2025-01-01 12:00:00')`
    13. `default_string ALIAS 'hello world'`
    14. `default_bool ALIAS true`
    15. `default_bool_false ALIAS false`
    16. `default_array ALIAS array(1, 2, 3)`
    17. `default_array_string ALIAS array('a', 'b', 'c')`
    18. `default_tuple ALIAS tuple(1, 'hello', 3.14)`
    19. `default_map ALIAS map('key1', 'value1', 'key2', 'value2')`
    20. `default_json '{"a" : {"b" : 42}, "c" : [1, 2, 3]}'::JSON`
    21. `default_nested map('key1', map('key2', 1))`
    22. `default_nested_tuple ALIAS tuple(1, tuple(2, 3), 4)`


**Test Coverage:**
- Integer constants
- Float constants
- Decimal constants
- Date/Time constants
- String constants
- Boolean constants
- Array constants
- Tuple constants
- Map constants
- JSON constant
- Nested datatypes

### 1.3 Mathematical Function Aliases

Aliases that use mathematical functions.

**Examples:**
1. `abs_value ALIAS abs(value)`
2. `sqrt_value ALIAS sqrt(value)`
3. `cbrt_value ALIAS cbrt(value)`
4. `power_value ALIAS pow(value, 2)`
5. `power_alt_value ALIAS power(value, 2)`
6. `exp_value ALIAS exp(value)`
7. `exp2_value ALIAS exp2(value)`
8. `exp10_value ALIAS exp10(value)`
9. `log_value ALIAS log(value)`
10. `ln_value ALIAS ln(value)`
11. `log2_value ALIAS log2(value)`
12. `log10_value ALIAS log10(value)`
13. `log1p_value ALIAS log1p(value)`
14. `sin_value ALIAS sin(value)`
15. `cos_value ALIAS cos(value)`
16. `tan_value ALIAS tan(value)`
17. `asin_value ALIAS asin(value)`
18. `acos_value ALIAS acos(value)`
19. `atan_value ALIAS atan(value)`
20. `atan2_value ALIAS atan2(value, 1)`
21. `sinh_value ALIAS sinh(value)`
22. `cosh_value ALIAS cosh(value)`
23. `tanh_value ALIAS tanh(value)`
24. `asinh_value ALIAS asinh(value)`
25. `acosh_value ALIAS acosh(value)`
26. `atanh_value ALIAS atanh(value)`
27. `sign_value ALIAS sign(value)`
28. `erf_value ALIAS erf(value)`
29. `erfc_value ALIAS erfc(value)`
30. `lgamma_value ALIAS lgamma(value)`
31. `tgamma_value ALIAS tgamma(value)`

**Test Coverage:**
- Absolute value (abs)
- Square root and cubic root (sqrt, cbrt)
- Power functions (pow, power, exp, exp2, exp10)
- Logarithmic functions (log, ln, log2, log10, log1p)
- Trigonometric functions (sin, cos, tan, asin, acos, atan, atan2)
- Hyperbolic functions (sinh, cosh, tanh, asinh, acosh, atanh)
- Sign function (sign)
- Special functions (erf, erfc, lgamma, tgamma)
- Different numeric input types (Int*, UInt*, Float*, Decimal*)
- Edge cases (negative values, zero, infinity, NaN)

### 1.4 Rounding Function Aliases

Aliases that use rounding functions.

**Examples:**
1. `rounded ALIAS round(value)`
2. `rounded_precision ALIAS round(value, 2)`
3. `floored ALIAS floor(value)`
4. `floored_precision ALIAS floor(value, 2)`
5. `ceiled ALIAS ceil(value)`
6. `ceiling_alias ALIAS ceiling(value)`
7. `ceiled_precision ALIAS ceil(value, 2)`
8. `truncated ALIAS trunc(value)`
9. `truncate_alias ALIAS truncate(value)`
10. `truncated_precision ALIAS trunc(value, 2)`
11. `bankers_round ALIAS roundBankers(value)`
12. `bankers_round_precision ALIAS roundBankers(value, 2)`
13. `duration_rounded ALIAS roundDuration(value)`
14. `age_rounded ALIAS roundAge(value)`
15. `rounded_down ALIAS roundDown(value, [10, 20, 30, 50])`

**Test Coverage:**
- Round functions (round, roundBankers, roundDuration, roundAge)
- Floor function (with and without precision)
- Ceil/Ceiling functions (with and without precision)
- Truncate/Trunc functions (with and without precision)
- RoundDown function (with array parameters)
- Different precision levels (N parameter)
- Negative numbers
- Float and Decimal types
- Different numeric input types (Int*, UInt*, Float*, Decimal*)

### 1.5 Bitwise Operation Aliases

Aliases that use bitwise operations.

**Examples:**
- `bit_and ALIAS bitAnd(value1, value2)`
- `bit_or ALIAS bitOr(value1, value2)`
- `bit_xor ALIAS bitXor(value1, value2)`
- `bit_not ALIAS bitNot(value)`
- `bit_shift_left ALIAS bitShiftLeft(value, 2)`
- `bit_shift_right ALIAS bitShiftRight(value, 2)`

**Test Coverage:**
- Bitwise AND (bitAnd)
- Bitwise OR (bitOr)
- Bitwise XOR (bitXor)
- Bitwise NOT (bitNot)
- Bitwise shift operations (bitShiftLeft, bitShiftRight)
- Integer types only
- Different integer sizes

### 1.6 Boolean/Logical Aliases

Aliases that evaluate to boolean values (UInt8 0/1 in ClickHouse).

**Examples:**
1. `is_even ALIAS value % 2 = 0`
2. `is_equal ALIAS value = 42`
3. `is_not_equal ALIAS value != 42`
4. `is_less ALIAS value < 100`
5. `is_less_equal ALIAS value <= 100`
6. `is_greater ALIAS value > 0`
7. `is_greater_equal ALIAS value >= 0`
8. `is_recent ALIAS date_col >= '2025-01-15'`
9. `is_valid ALIAS value > 0 AND value < 100`
10. `is_in_range ALIAS value BETWEEN 10 AND 100`
11. `is_not_in_range ALIAS value NOT BETWEEN 10 AND 100`
12. `is_active ALIAS status = 'active'`
13. `is_like ALIAS name LIKE '%test%'`
14. `is_not_like ALIAS name NOT LIKE '%test%'`
15. `is_ilike ALIAS name ILIKE '%TEST%'`
16. `is_in_set ALIAS value IN (1, 2, 3, 4, 5)`
17. `is_not_in_set ALIAS value NOT IN (1, 2, 3, 4, 5)`
18. `is_or_condition ALIAS value < 10 OR value > 90`
19. `is_not_condition ALIAS NOT (value = 0)`
20. `is_xor_condition ALIAS xor(value > 50, value < 100)`
21. `is_null_check ALIAS isNull(value)`
22. `is_not_null_check ALIAS isNotNull(value)`
23. `is_complex_logic ALIAS (value > 0 AND value < 100) OR (value > 200 AND value < 300)`

**Test Coverage:**
- Comparison operators (=, !=, <, <=, >, >=)
- Logical operators (AND, OR, NOT, XOR)
- XOR function (xor)
- BETWEEN and NOT BETWEEN operators
- LIKE, NOT LIKE, ILIKE pattern matching
- IN and NOT IN set operators
- NULL handling functions (isNull, isNotNull)
- Complex boolean expressions with multiple conditions
- Different numeric and string input types

### 1.7 Date/Time Function Aliases

Aliases that use date and time functions.

**Examples:**
1. `year ALIAS toYear(date_col)`
2. `month ALIAS toMonth(date_col)`
3. `quarter ALIAS toQuarter(date_col)`
4. `day_of_week ALIAS toDayOfWeek(date_col)`
5. `day_of_month ALIAS toDayOfMonth(date_col)`
6. `hour ALIAS toHour(datetime_col)`
7. `minute ALIAS toMinute(datetime_col)`
8. `second ALIAS toSecond(datetime_col)`
9. `year_month ALIAS toYYYYMM(date_col)`
10. `year_month_day ALIAS toYYYYMMDD(date_col)`
11. `start_of_year ALIAS toStartOfYear(datetime_col)`
12. `start_of_quarter ALIAS toStartOfQuarter(datetime_col)`
13. `start_of_month ALIAS toStartOfMonth(datetime_col)`
14. `start_of_week ALIAS toStartOfWeek(datetime_col)`
15. `start_of_day ALIAS toStartOfDay(datetime_col)`
16. `start_of_hour ALIAS toStartOfHour(datetime_col)`
17. `timestamp ALIAS toUnixTimestamp(date_col)`
18. `date_string ALIAS toString(date_col)`
19. `datetime_string ALIAS toString(datetime_col)`
20. `date_plus_days ALIAS addDays(date_col, 7)`
21. `date_plus_months ALIAS addMonths(date_col, 1)`
22. `date_plus_years ALIAS addYears(date_col, 1)`
23. `date_minus_days ALIAS subtractDays(date_col, 7)`
24. `date_minus_months ALIAS subtractMonths(date_col, 1)`
25. `date_minus_years ALIAS subtractYears(date_col, 1)`
26. `date_plus_interval ALIAS date_col + INTERVAL 7 DAY`
27. `date_minus_interval ALIAS date_col - INTERVAL 1 MONTH`
28. `datetime_plus_interval ALIAS datetime_col + INTERVAL 1 HOUR`
29. `to_timezone ALIAS toTimeZone(datetime_col, 'America/New_York')`


**Test Coverage:**
- Date extraction functions (toYear, toMonth, toQuarter, toDayOfWeek, toDayOfMonth, toHour, toMinute, toSecond)
- Date format functions (toYYYYMM, toYYYYMMDD)
- Period start functions (toStartOfYear, toStartOfQuarter, toStartOfMonth, toStartOfWeek, toStartOfDay, toStartOfHour)
- Date arithmetic functions (addDays, addMonths, addYears, subtractDays, subtractMonths, subtractYears)
- Date arithmetic with INTERVAL (date + INTERVAL, date - INTERVAL)
- Time zone conversions (toTimeZone)
- Conversion functions (toUnixTimestamp, toString)
- Different date/datetime input types (Date, Date32, DateTime, DateTime64)

### 1.8 String Function Aliases

Aliases that use string manipulation functions.

**Examples:**
1. `upper_name ALIAS upper(name)`
2. `lower_name ALIAS lower(name)`
3. `name_length ALIAS length(name)`
4. `name_length_utf8 ALIAS lengthUTF8(name)`
5. `substring_name ALIAS substring(name, 1, 5)`
6. `substring_from ALIAS substring(name, 3)`
7. `position_sub ALIAS position(name, 'test')`
8. `position_case_insensitive ALIAS positionCaseInsensitive(name, 'TEST')`
9. `concatenated ALIAS concat(first_name, ' ', last_name)`
10. `concatenated_ws ALIAS concat(first_name, last_name)`
11. `reversed_name ALIAS reverse(name)`
12. `replaced_all ALIAS replaceAll(name, 'old', 'new')`
13. `replaced_one ALIAS replaceOne(name, 'old', 'new')`
14. `replaced_regexp ALIAS replaceRegexpOne(name, '\\d+', 'X')`
15. `starts_with ALIAS startsWith(name, 'prefix')`
16. `ends_with ALIAS endsWith(name, 'suffix')`
17. `is_empty ALIAS empty(name)`
18. `is_not_empty ALIAS notEmpty(name)`
19. `left_padded ALIAS leftPad(name, 10, '0')`
20. `right_padded ALIAS rightPad(name, 10, '0')`
21. `formatted_string ALIAS format('Hello {1}, you are {0} years old', age, name)`
22. `repeated_name ALIAS repeat(name, 3)`
23. `trimmed_name ALIAS trimBoth(name)`
24. `trimmed_left ALIAS trimLeft(name)`
25. `trimmed_right ALIAS trimRight(name)`
26. `split_by_char ALIAS splitByChar(',', name)`
27. `split_by_string ALIAS splitByString('::', name)`
28. `array_string_concat ALIAS arrayStringConcat([first, second], ' ')`
29. `extract_all_groups ALIAS extractAllGroups(name, '(\\w+)=(\\w+)')`
30. `ascii_code ALIAS ascii(name)`

**Test Coverage:**
- String transformation functions (upper, lower, reverse)
- String extraction functions (substring, position, positionCaseInsensitive)
- String concatenation (concat, arrayStringConcat)
- String replacement (replaceAll, replaceOne, replaceRegexpOne)
- String padding (leftPad, rightPad)
- String trimming (trimBoth, trimLeft, trimRight)
- String checking (empty, notEmpty, startsWith, endsWith)
- String splitting (splitByChar, splitByString)
- String formatting (format)
- String repetition (repeat)
- Pattern extraction (extractAllGroups)
- ASCII functions (ascii)
- String length (length, lengthUTF8)
- Different string input types and edge cases

### 1.9 Type Conversion Aliases

Aliases that perform implicit or explicit type conversions.

**Examples:**
1. `value_str ALIAS toString(value)` - Convert integer to string
2. `value_int8 ALIAS toInt8(value)` - Convert Int32 to Int8
3. `value_int16 ALIAS toInt16(value)` - Convert Int32 to Int16
4. `value_int32 ALIAS toInt32(value)` - Convert Int32 to Int32
5. `value_int64 ALIAS toInt64(value)` - Convert Int32 to Int64
6. `value_uint8 ALIAS toUInt8(value)` - Convert Int32 to UInt8
7. `value_uint16 ALIAS toUInt16(value)` - Convert Int32 to UInt16
8. `value_uint32 ALIAS toUInt32(value)` - Convert Int32 to UInt32
9. `value_uint64 ALIAS toUInt64(value)` - Convert Int32 to UInt64
10. `value_float32 ALIAS toFloat32(value)` - Convert Int32 to Float32
11. `value_float64 ALIAS toFloat64(value)` - Convert Int32 to Float64
12. `value_date ALIAS toDate(toString(date_col))` - Convert date to string then back to Date
13. `value_datetime ALIAS toDateTime(toString(date_col))` - Convert date to string then to DateTime

**Shrinking Conversions (larger to smaller types):**
14. `value_int32 ALIAS toInt32(big_value)` - Shrinking: Int64 to Int32
15. `value_int16 ALIAS toInt16(value)` - Shrinking: Int32 to Int16
16. `value_int8 ALIAS toInt8(small_value)` - Shrinking: Int16 to Int8
17. `value_uint32 ALIAS toUInt32(big_value)` - Shrinking: UInt64 to UInt32
18. `value_uint16 ALIAS toUInt16(value)` - Shrinking: UInt32 to UInt16
19. `value_uint8 ALIAS toUInt8(small_value)` - Shrinking: UInt16 to UInt8
20. `value_float32 ALIAS toFloat32(big_float)` - Shrinking: Float64 to Float32

**Test Coverage:**
- Numeric type conversions (toInt8, toInt16, toInt32, toInt64, toUInt8, toUInt16, toUInt32, toUInt64, toFloat32, toFloat64)
- String conversions (toString)
- Date conversions (toDate, toDateTime)
- Type casting edge cases
- Invalid conversion handling



### 1.10 Conditional Aliases

Aliases that use conditional expressions.

**Examples:**
1. `category ALIAS if(value > 50, 'high', 'low')` - Basic IF expression
2. `status ALIAS multiIf(value < 10, 'low', value < 50, 'medium', 'high')` - MultiIf with multiple conditions
3. `grade ALIAS multiIf(score >= 90, 'A', score >= 80, 'B', score >= 70, 'C', 'F')` - MultiIf with numeric conditions
4. `case_when ALIAS CASE WHEN value > 50 THEN 'high' ELSE 'low' END` - CASE WHEN expression
5. `case_expr ALIAS CASE value WHEN 1 THEN 'one' WHEN 2 THEN 'two' ELSE 'other' END` - CASE with expression
6. `coalesced ALIAS coalesce(value1, value2, 0)` - Coalesce returns first non-NULL
7. `transformed ALIAS transform(value, [1, 2, 3], ['a', 'b', 'c'], 'default')` - Transform maps values
8. `if_null_result ALIAS ifNull(value, 0)` - Returns default if value is NULL
9. `null_if_result ALIAS nullIf(value, 0)` - Returns NULL if value equals specified value
10. `nullable_value ALIAS toNullable(value)` - Converts value to nullable type
11. `assumed_not_null ALIAS assumeNotNull(nullable_value)` - Assumes value is not NULL

**Test Coverage:**
- IF expressions (if)
- MultiIf expressions (multiIf)
- CASE expressions (CASE WHEN ... THEN ... ELSE ... END)
- CASE with expression (CASE expr WHEN val1 THEN ... ELSE ... END)
- Coalesce function (coalesce)
- Transform function (transform)
- NULL handling functions (ifNull, nullIf, toNullable, assumeNotNull)
- Note: isNull and isNotNull are covered in section 1.6 (Boolean/Logical Aliases)

### 1.11 Nested/Dependent Aliases

Aliases that depend on other alias columns.

**Examples:**
1. `computed ALIAS value * 2` - Base alias (no dependency)
2. `computed_2 ALIAS computed + 10` - Single-level dependency (depends on one alias)
3. `doubled ALIAS value * 2` - Base alias
4. `quadrupled ALIAS doubled * 2` - Two-level dependency chain
5. `octupled ALIAS quadrupled * 2` - Three-level dependency chain
6. `hexadecupled ALIAS octupled * 2` - Four-level dependency chain
7. `sum_all ALIAS id + value + doubled + quadrupled` - Multiple dependencies (depends on multiple aliases)
8. `product_all ALIAS doubled * quadrupled` - Multiple dependencies (product of two aliases)
9. `combined ALIAS concat(toString(doubled), '-', toString(quadrupled))` - String operations with multiple aliases
10. `conditional_result ALIAS if(doubled > 100, quadrupled, doubled)` - Conditional with aliases
11. `nested_math ALIAS (doubled + quadrupled) * 2` - Complex arithmetic with aliases
12. `percentage ALIAS (doubled * 100) / (value + doubled)` - Percentage calculation with aliases

**Test Coverage:**
- Single-level dependency (alias depends on one alias)
- Two-level dependency chains (alias -> alias)
- Three-level dependency chains (alias -> alias -> alias)
- Four-level dependency chains (alias -> alias -> alias -> alias)
- Multiple dependencies (alias depends on multiple aliases)
- Complex expressions combining multiple aliases
- Different operation types (arithmetic, string, conditional)
- Circular dependency detection (should fail)
- Dependency resolution order

### 1.12 Additional Utility Function Aliases

Aliases that use utility functions.

**Examples:**
1. `digit_count ALIAS countDigits(value)` - Count digits in Int32 value
2. `digit_count_int64 ALIAS countDigits(big_value)` - Count digits in Int64 value
3. `digit_count_uint32 ALIAS countDigits(uint_value)` - Count digits in UInt32 value
4. `greatest_two ALIAS greatest(val1, val2)` - Greatest of two values
5. `greatest_three ALIAS greatest(val1, val2, val3)` - Greatest of three values
6. `greatest_four ALIAS greatest(val1, val2, val3, val4)` - Greatest of four values
7. `least_two ALIAS least(val1, val2)` - Least of two values
8. `least_three ALIAS least(val1, val2, val3)` - Least of three values
9. `least_four ALIAS least(val1, val2, val3, val4)` - Least of four values
10. `greatest_string ALIAS greatest(str1, str2, str3)` - Greatest of string values
11. `least_string ALIAS least(str1, str2)` - Least of string values
12. `greatest_date ALIAS greatest(date1, date2)` - Greatest of date values
13. `least_date ALIAS least(date1, date2)` - Least of date values

**Test Coverage:**
- Count digits function (countDigits) with different numeric types (Int32, Int64, UInt32)
- Greatest function with 2, 3, 4+ arguments
- Least function with 2, 3, 4+ arguments
- Greatest/least with numeric types
- Greatest/least with string types
- Greatest/least with date types
- Multiple argument handling

### 1.13 Complex Expression Aliases

Aliases with complex expressions combining multiple functions and operations.

**Examples:**
1. `score ALIAS (value * 2) + (id % 10) - length(name)` - Arithmetic with string function
2. `formatted_date ALIAS concat(toString(toYear(date_col)), '-', toString(toMonth(date_col)))` - Nested date and string functions
3. `normalized_value ALIAS (value - min_value) / (max_value - min_value)` - Normalization formula
4. `complex_math ALIAS sqrt(pow(value, 2) + pow(id, 2))` - Pythagorean calculation
5. `weighted_sum ALIAS (value1 * 0.3) + (value2 * 0.5) + (value3 * 0.2)` - Weighted average components
6. `formatted_string ALIAS concat(upper(substring(name, 1, 1)), lower(substring(name, 2)))` - String transformation chain
7. `date_range_days ALIAS toDayOfYear(date_col) - toDayOfYear('2025-01-01')` - Date difference calculation
8. `conditional_math ALIAS if(value > 0, sqrt(value), abs(value))` - Conditional with math function
9. `log_normalized ALIAS log(value + 1) / log(max_value + 1)` - Logarithmic normalization
10. `string_math ALIAS length(concat(toString(value), '_', toString(id)))` - String concatenation with length
11. `nested_conditional ALIAS multiIf(value < 10, value * 2, value < 50, value * 3, value * 4)` - MultiIf with arithmetic
12. `complex_round ALIAS round((value * 1.5) / 3.0, 2)` - Arithmetic with rounding
13. `date_string_combined ALIAS concat(toString(toYear(date_col)), '-', toString(toMonth(date_col)), '-', toString(toDayOfMonth(date_col)))` - Full date formatting
14. `percentage_string ALIAS concat(toString(round((value * 100.0) / total, 2)), '%')` - Percentage with formatting
15. `abs_normalized ALIAS abs(value - avg_value) / stddev_value` - Statistical normalization

**Test Coverage:**
- Nested function calls (functions within functions)
- Multiple operations in single expression (arithmetic, string, date)
- Operator precedence (parentheses, multiplication before addition)
- Expression evaluation order (left-to-right, function arguments)
- Mixed data types in expressions
- Complex conditional expressions with functions
- Statistical calculations (normalization, weighted sums)
- String formatting with numeric conversions
- Date arithmetic with formatting

### 1.14 Array Function Aliases

Aliases that use array manipulation functions.

**Examples:**
1. `array_length ALIAS length(array_col)` - Length of array
2. `array_sum ALIAS arraySum(array_col)` - Sum of array elements
3. `array_product ALIAS arrayProduct(array_col)` - Product of array elements
4. `array_first ALIAS arrayElement(array_col, 1)` - First element of array
5. `array_last ALIAS arrayElement(array_col, length(array_col))` - Last element of array
6. `array_sorted ALIAS arraySort(array_col)` - Sorted array
7. `array_reversed ALIAS arrayReverse(array_col)` - Reversed array
8. `array_unique ALIAS arrayDistinct(array_col)` - Unique elements in array
9. `array_concat ALIAS arrayConcat(array1, array2)` - Concatenate two arrays
10. `array_slice ALIAS arraySlice(array_col, 1, 3)` - Slice of array

**Test Coverage:**
- Array access functions (arrayElement)
- Array manipulation (arraySort, arrayReverse, arrayDistinct)
- Array aggregation (arraySum, arrayProduct)
- Array combination (arrayConcat)
- Array slicing (arraySlice)
- Array length operations

### 1.15 Tuple Function Aliases

Aliases that use tuple manipulation functions.

**Examples:**
1. `tuple_first ALIAS tupleElement(tuple_col, 1)` - First element of tuple
2. `tuple_second ALIAS tupleElement(tuple_col, 2)` - Second element of tuple
3. `tuple_named ALIAS tupleElement(tuple_col, 'name')` - Named tuple element

**Test Coverage:**
- Tuple element access by index (tupleElement with number)
- Tuple element access by name (tupleElement with string)
- Tuple creation and manipulation

### 1.16 Map Function Aliases

Aliases that use map manipulation functions.

**Examples:**
1. `map_keys ALIAS mapKeys(map_col)` - Keys of map
2. `map_values ALIAS mapValues(map_col)` - Values of map
3. `map_size ALIAS length(map_col)` - Size of map
4. `map_get ALIAS map_col['key']` - Get value by key

**Test Coverage:**
- Map key extraction (mapKeys)
- Map value extraction (mapValues)
- Map size operations
- Map element access

### 1.17 JSON Function Aliases

Aliases that use JSON manipulation functions.

**Examples:**
1. `json_extract_string ALIAS JSONExtractString(json_col, 'key')` - Extract string from JSON
2. `json_extract_int ALIAS JSONExtractInt(json_col, 'key')` - Extract integer from JSON
3. `json_extract_float ALIAS JSONExtractFloat(json_col, 'key')` - Extract float from JSON
4. `json_has ALIAS JSONHas(json_col, 'key')` - Check if key exists

**Test Coverage:**
- JSON extraction functions (JSONExtractString, JSONExtractInt, JSONExtractFloat)
- JSON existence checks (JSONHas)
- JSON path navigation

### 1.18 Encoding Function Aliases

Aliases that use encoding functions.

**Examples:**
1. `base64_encoded ALIAS base64Encode(string_col)` - Base64 encoding
2. `base64_decoded ALIAS base64Decode(encoded_col)` - Base64 decoding
3. `hex_encoded ALIAS hex(string_col)` - Hexadecimal encoding

**Test Coverage:**
- Encoding functions (base64Encode, base64Decode)
- Hexadecimal encoding (hex)

## 2. Watermark/Predicate Types

### 2.1 Direct Column Predicates

Watermarks that use base columns directly (not aliases).

**Examples:**
- `date_col >= '2025-01-15'`
- `date_col < '2025-01-15'`
- `id BETWEEN 10 AND 15`
- `value > 100`
- `status = 'active'`

**Test Coverage:**
- Date column predicates
- Numeric column predicates
- String column predicates
- Boolean column predicates
- Range predicates (BETWEEN)
- Multiple condition predicates (AND, OR)

### 2.2 Alias Column Predicates

Watermarks that use alias columns directly in predicates.

**Examples:**
- `computed >= threshold`
- `computed < threshold`
- `is_even = 1`
- `year_month >= 202501`

**Test Coverage:**
- Simple alias predicates
- Alias predicates with constants
- Alias predicates with other aliases
- Boolean alias predicates
- Date function alias predicates
- Expected behavior (may be unsupported or have limitations)

### 2.3 Predicates on Columns That Aliases Depend On

Watermarks that use base columns that are referenced by alias columns.

**Examples:**
- Base column: `value`
- Alias: `computed ALIAS value * 2`
- Predicate: `value >= 50` (indirectly affects alias)

**Test Coverage:**
- Predicates on source columns of aliases
- Predicates that affect alias evaluation
- Predicates that don't affect alias evaluation
- Multiple aliases depending on same base column

### 2.4 Predicates on Columns That Aliases Don't Depend On

Watermarks that use columns unrelated to alias definitions.

**Examples:**
- Base columns: `id`, `value`, `date_col`
- Alias: `computed ALIAS value * 2`
- Predicate: `date_col >= '2025-01-15'` (unrelated to alias)

**Test Coverage:**
- Independent column predicates
- Predicates that don't affect alias values
- Multiple independent predicates

### 2.5 Complex Predicates with Aliases

Watermarks that combine base columns and aliases in complex expressions.

**Examples:**
- `date_col >= '2025-01-15' AND computed > 100`
- `value > 50 OR is_even = 1`
- `(date_col >= '2025-01-15') AND (computed >= threshold)`

**Test Coverage:**
- Mixed base column and alias predicates
- Logical operators in predicates
- Nested predicate expressions
- Predicate evaluation order

### 2.6 Date-Based Predicates

Watermarks that use date columns or date functions.

**Examples:**
- `date_col >= '2025-01-15'`
- `date_col < '2025-01-15'`
- `toYYYYMM(date_col) >= 202501`
- `toYear(date_col) = 2025`

**Test Coverage:**
- Direct date column comparisons
- Date function predicates
- Date range predicates
- Time zone considerations
- Date alias predicates

### 2.7 Numeric Range Predicates

Watermarks that use numeric ranges.

**Examples:**
- `value BETWEEN 10 AND 100`
- `id >= 1 AND id <= 1000`
- `value IN (10, 20, 30)`

**Test Coverage:**
- BETWEEN predicates
- Range predicates with AND
- IN predicates
- Numeric alias predicates in ranges

### 2.8 String Predicates

Watermarks that use string comparisons.

**Examples:**
- `name = 'test'`
- `status IN ('active', 'pending')`
- `name LIKE 'test%'`

**Test Coverage:**
- Equality predicates
- IN predicates with strings
- LIKE predicates
- String alias predicates

## 3. Query Context Testing

### 3.1 SELECT Clause

**Test Coverage:**
- Selecting only alias columns
- Selecting mix of base and alias columns
- Selecting nested/dependent aliases
- Selecting aliases in expressions
- Selecting aliases with type conversions

### 3.2 WHERE Clause

**Test Coverage:**
- Filtering by alias columns
- Filtering by base columns with aliases in SELECT
- Complex WHERE conditions with aliases
- WHERE with dependent aliases
- WHERE with boolean aliases

### 3.3 GROUP BY Clause

**Test Coverage:**
- Grouping by alias columns
- Grouping by base columns with alias aggregations
- Grouping by nested aliases
- Grouping by date function aliases
- Multiple alias columns in GROUP BY

### 3.4 ORDER BY Clause

**Test Coverage:**
- Ordering by alias columns
- Ordering by base columns with alias in SELECT
- Ordering by nested aliases
- Multiple alias columns in ORDER BY
- ASC/DESC with aliases

### 3.5 HAVING Clause

**Test Coverage:**
- HAVING with alias aggregations
- HAVING with alias columns from GROUP BY
- Complex HAVING conditions with aliases

### 3.6 JOIN Operations

**Test Coverage:**
- JOIN conditions with alias columns
- JOIN conditions with base columns when aliases exist
- Aliases in JOIN result sets

### 3.7 Subqueries

**Test Coverage:**
- Aliases in subquery SELECT
- Aliases in subquery WHERE
- Aliases in correlated subqueries

## 4. Type Compatibility Testing

### 4.1 Type Mismatch Scenarios

**Test Coverage:**
- Alias returns Int16, hybrid table expects Int32
- Alias returns Int64, hybrid table expects Int32
- Alias returns String, hybrid table expects numeric
- Alias returns Date, hybrid table expects String
- Type coercion behavior
- Type conversion errors

### 4.2 Type Alignment

**Test Coverage:**
- Automatic type casting
- Explicit type casting in hybrid table definition
- Type compatibility across segments
- Type mismatch error handling

## 5. Edge Cases and Error Scenarios

### 5.1 Missing Dependencies

**Test Coverage:**
- Alias depends on non-existent column
- Alias depends on dropped column
- Circular alias dependencies

### 5.2 NULL Handling

**Test Coverage:**
- Aliases with NULL base column values
- Aliases that produce NULL
- NULL in alias predicates
- NULL in alias aggregations

### 5.3 Invalid Expressions

**Test Coverage:**
- Division by zero in aliases
- Invalid type conversions
- Invalid function calls
- Syntax errors in alias definitions

### 5.4 Segment Mismatches

**Test Coverage:**
- Different alias definitions in left/right segments
- Missing aliases in one segment
- Type mismatches between segments
- Incompatible alias expressions between segments

## 6. Performance Considerations

### 6.1 Alias Evaluation

**Test Coverage:**
- Alias evaluation during query execution
- Alias evaluation in predicates
- Alias evaluation in aggregations
- Caching of alias values

### 6.2 Predicate Pushdown

**Test Coverage:**
- Predicate pushdown with alias columns
- Predicate pushdown with base columns when aliases exist
- Predicate pushdown optimization

## 7. Test Matrix Summary

### 7.1 Alias Types vs Query Contexts

| Alias Type | SELECT | WHERE | GROUP BY | ORDER BY | HAVING |
|------------|--------|-------|----------|----------|--------|
| Simple Arithmetic | ✓ | ✓ | ✓ | ✓ | ✓ |
| Mathematical Functions | ✓ | ✓ | ✓ | ✓ | ✓ |
| Rounding Functions | ✓ | ✓ | ✓ | ✓ | ✓ |
| Bitwise Operations | ✓ | ✓ | ✓ | ✓ | ✓ |
| Constant | ✓ | ✓ | ✓ | ✓ | ✓ |
| Boolean | ✓ | ✓ | ✓ | ✓ | ✓ |
| Date/Time Function | ✓ | ✓ | ✓ | ✓ | ✓ |
| String Function | ✓ | ✓ | ✓ | ✓ | ✓ |
| Type Conversion | ✓ | ✓ | ✓ | ✓ | ✓ |
| Conditional | ✓ | ✓ | ✓ | ✓ | ✓ |
| Nested/Dependent | ✓ | ✓ | ✓ | ✓ | ✓ |
| Utility Functions | ✓ | ✓ | ✓ | ✓ | ✓ |
| Complex Expression | ✓ | ✓ | ✓ | ✓ | ✓ |

### 7.2 Watermark Types vs Alias Types

| Watermark Type | Simple Alias | Nested Alias | Boolean Alias | Date Alias |
|----------------|--------------|--------------|--------------|------------|
| Direct Column | ✓ | ✓ | ✓ | ✓ |
| Alias Column | ? | ? | ? | ? |
| Base Column (alias depends on) | ✓ | ✓ | ✓ | ✓ |
| Base Column (alias independent) | ✓ | ✓ | ✓ | ✓ |
| Complex Predicate | ✓ | ✓ | ✓ | ✓ |

Legend:
- ✓ = Should be tested
- ? = May have limitations, needs verification

## 8. Recommended Test Scenarios

### 8.1 Basic Functionality
1. Simple alias in SELECT
2. Alias in WHERE clause
3. Alias in GROUP BY
4. Alias in ORDER BY
5. Multiple aliases in single query

### 8.2 Dependency Chains
1. Single-level alias dependency
2. Multi-level alias dependency
3. Multiple aliases depending on same base column
4. Alias depending on multiple other aliases

### 8.3 Watermark Combinations
1. Watermark on base column with aliases present
2. Watermark on alias column (if supported)
3. Watermark on column that alias depends on
4. Complex watermark with aliases

### 8.4 Type Scenarios
1. Type matching between alias and hybrid table definition
2. Type mismatches and conversions
3. Type compatibility across segments

### 8.5 Error Cases
1. Invalid alias expressions
2. Missing dependencies
3. Circular dependencies
4. Segment mismatches

## 9. Implementation Notes

### 9.1 Current Limitations
- Alias columns in watermark predicates may have limitations (see test_alias_columns_in_predicates)
- Type mismatches may require explicit handling
- Some alias types may not be supported in all contexts

### 9.2 Best Practices
- Use base columns in watermark predicates when possible
- Ensure alias definitions are consistent across segments
- Match alias return types with hybrid table column definitions
- Test type conversions explicitly

### 9.3 Future Considerations
- Support for aggregate functions in aliases
- Enhanced type coercion
- Alias evaluation optimization
- Predicate pushdown with aliases
