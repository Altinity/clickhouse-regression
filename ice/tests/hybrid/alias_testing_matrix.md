# ALIAS Columns Testing Matrix for Hybrid Tables

## Overview

This document provides a structured approach to testing ALIAS columns in hybrid table engine segments. It categorizes all possible types of aliases and watermark patterns to ensure comprehensive test coverage.

## Settings

asterisk_include_alias_columns

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

**Test Coverage:**
- Basic arithmetic operations (+, -, *, /, %)
- Multiple operands
- Negative numbers
- Zero values
- Division by zero handling
- Different numeric base column types (Int8, Int16, Int32, Int64, UInt8, UInt16, UInt32, UInt64, Float32, Float64)
- Division operation explicitly tested
- Arithmetic with Float types

### 1.2 Constant Aliases

Aliases that evaluate to constant values.

**Examples:**
- `threshold ALIAS 50`
- `max_value ALIAS 1000`
- `default_date ALIAS '2025-01-01'`

**Test Coverage:**
- Numeric constants (Int8, Int16, Int32, Int64, UInt8, UInt16, UInt32, UInt64, Float32, Float64)
- String constants
- Date constants (toDate('2025-01-01'))
- Boolean constants (true, false, 1, 0)
- NULL constants

### 1.3 Boolean/Logical Aliases

Aliases that evaluate to boolean values (UInt8 0/1 in ClickHouse).

**Examples:**
- `is_even ALIAS value % 2 = 0`
- `is_recent ALIAS date_col >= '2025-01-15'`
- `is_valid ALIAS value > 0 AND value < 100`
- `is_active ALIAS status = 'active'`

**Test Coverage:**
- Comparison operators (=, !=, <, <=, >, >=)
- Logical operators (AND, OR, NOT)
- Complex boolean expressions
- NULL handling in comparisons

### 1.4 Date/Time Function Aliases

Aliases that use date and time functions.

**Examples:**
- `year_month ALIAS toYYYYMM(date_col)`
- `year ALIAS toYear(date_col)`
- `day_of_week ALIAS toDayOfWeek(date_col)`
- `timestamp ALIAS toUnixTimestamp(date_col)`
- `date_string ALIAS toString(date_col)`

**Test Coverage:**
- Date extraction functions (toYear, toMonth, toDayOfWeek, toDayOfMonth, toYYYYMM)
- Date formatting functions (toString(date_col))
- Date arithmetic (date + interval, date - interval)
- Time zone conversions (toTimeZone, convertTimeZone)
- Date comparisons
- toUnixTimestamp() function

### 1.5 String Function Aliases

Aliases that use string manipulation functions.

**Examples:**
- `upper_name ALIAS upper(name)`
- `lower_name ALIAS lower(name)`
- `name_length ALIAS length(name)`
- `substring_name ALIAS substring(name, 1, 5)`
- `concatenated ALIAS concat(first_name, ' ', last_name)`

**Test Coverage:**
- String transformation functions (upper, lower)
- String extraction functions (substring)
- String concatenation (concat)
- Pattern matching (LIKE in expressions)
- NULL string handling
- String length (length)

### 1.6 Type Conversion Aliases

Aliases that perform implicit or explicit type conversions.

**Examples:**
- `value_str ALIAS toString(value)`
- `value_int ALIAS toInt32(value_str)`
- `value_float ALIAS toFloat64(value)`
- `value_date ALIAS toDate(value_str)`

**Test Coverage:**
- Numeric type conversions (toInt8, toInt16, toInt32, toInt64, toUInt8, toUInt16, toUInt32, toUInt64, toFloat32, toFloat64)
- String conversions (toString)
- Date conversions (toDate, toDateTime)
- Type casting edge cases
- Invalid conversion handling

### 1.7 Aggregate Function Aliases (if supported)

Aliases that use aggregate functions (may not be supported in all contexts).

**Examples:**
- `avg_value ALIAS avg(value) OVER (PARTITION BY category)`
- `running_total ALIAS sum(value) OVER (ORDER BY date_col)`

**Test Coverage:**
- Window functions
- Aggregate functions in aliases
- Partitioning and ordering

### 1.8 Conditional Aliases

Aliases that use conditional expressions.

**Examples:**
- `category ALIAS if(value > 50, 'high', 'low')`
- `status ALIAS multiIf(value < 10, 'low', value < 50, 'medium', 'high')`
- `coalesced ALIAS coalesce(value1, value2, 0)`

**Test Coverage:**
- IF expressions
- MultiIf expressions
- Coalesce
- NULL handling

### 1.9 Nested/Dependent Aliases

Aliases that depend on other alias columns.

**Examples:**
- `computed ALIAS value * 2`
- `computed_2 ALIAS computed + 10`
- `doubled ALIAS value * 2`
- `quadrupled ALIAS doubled * 2`
- `sum_all ALIAS id + value + doubled + quadrupled`

**Test Coverage:**
- Single-level dependency (alias depends on one alias)
- Multi-level dependency chains (alias depends on alias that depends on alias)
- 3+ level dependency chains (alias -> alias -> alias -> alias)
- Multiple dependencies (alias depends on multiple aliases)
- Circular dependency detection (should fail)
- Dependency resolution order

### 1.10 Complex Expression Aliases

Aliases with complex expressions combining multiple functions and operations.

**Examples:**
- `score ALIAS (value * 2) + (id % 10) - length(name)`
- `formatted_date ALIAS concat(toString(toYear(date_col)), '-', toString(toMonth(date_col)))`
- `normalized_value ALIAS (value - min_value) / (max_value - min_value)`

**Test Coverage:**
- Nested function calls
- Multiple operations in single expression
- Operator precedence
- Expression evaluation order

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
| Constant | ✓ | ✓ | ✓ | ✓ | ✓ |
| Boolean | ✓ | ✓ | ✓ | ✓ | ✓ |
| Date/Time Function | ✓ | ✓ | ✓ | ✓ | ✓ |
| String Function | ✓ | ✓ | ✓ | ✓ | ✓ |
| Type Conversion | ✓ | ✓ | ✓ | ✓ | ✓ |
| Conditional | ✓ | ✓ | ✓ | ✓ | ✓ |
| Nested/Dependent | ✓ | ✓ | ✓ | ✓ | ✓ |
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
