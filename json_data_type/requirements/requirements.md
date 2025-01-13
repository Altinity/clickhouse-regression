# SRS-043 JSON Data Type
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Declaring a Column of JSON Type](#declaring-a-column-of-json-type)
    * 2.1 [Parameters](#parameters)
* 3 [Casting to JSON Type ](#casting-to-json-type-)
* 4 [Reading JSON paths as subcolumns](#reading-json-paths-as-subcolumns)
    * 4.1 [Requested Path Does Not Exist](#requested-path-does-not-exist)
    * 4.2 [Data Types of Subcolumns](#data-types-of-subcolumns)
    * 4.3 [Reading JSON sub-objects as subcolumns](#reading-json-sub-objects-as-subcolumns)

## Introduction

This Software Requirements Specification (SRS) defines the requirements for JSON data type support in ClickHouse. This data type stores JavaScript Object Notation (JSON) documents in a single column.


## Declaring a Column of JSON Type

To declare a column of JSON type, use the following syntax:

```sql
<column_name> JSON(max_dynamic_paths=N, max_dynamic_types=M, some.path TypeName, SKIP path.to.skip, SKIP REGEXP 'paths_regexp')
```

### Parameters

- **max_dynamic_paths** is an optional parameter indicating how many paths can be stored separately as subcolumns across single block of data that is stored separately (for example across single data part for MergeTree table). If this limit is exceeded, all other paths will be stored together in a single structure. Default value of max_dynamic_paths is 1024.
- **max_dynamic_types** is an optional parameter between 1 and 255 indicating how many different data types can be stored inside a single path column with type Dynamic across single block of data that is stored separately (for example across single data part for MergeTree table). If this limit is exceeded, all new types will be converted to type String. Default value of max_dynamic_types is 32.
- **some.path TypeName** is an optional type hint for particular path in the JSON. Such paths will be always stored as subcolumns with specified type.
- **SKIP path.to.skip** is an optional hint for particular path that should be skipped during JSON parsing. Such paths will never be stored in the JSON column. If specified path is a nested JSON object, the whole nested object will be skipped.
- **SKIP REGEXP 'path_regexp'** is an optional hint with a regular expression that is used to skip paths during JSON parsing. All paths that match this regular expression will never be stored in the JSON column.

Example:

1. Create a table with a JSON column without specifying any parameters:
```sql
CREATE TABLE test (json JSON) ENGINE = Memory;
INSERT INTO test VALUES ('{"a" : {"b" : 42}, "c" : [1, 2, 3]}'), ('{"f" : "Hello, World!"}'), ('{"a" : {"b" : 43, "e" : 10}, "c" : [4, 5, 6]}');
SELECT json FROM test;
```

```json
{"a":{"b":"42"},"c":["1","2","3"]}
{"f":"Hello, World!"}
{"a":{"b":"43","e":"10"},"c":["4","5","6"]}
```

2. Create a table with a JSON column and with a type hint for a particular path and a path to skip:
```sql
CREATE TABLE test (json JSON(a.b UInt32, SKIP a.e)) ENGINE = Memory;
INSERT INTO test VALUES ('{"a" : {"b" : 42}, "c" : [1, 2, 3]}'), ('{"f" : "Hello, World!"}'), ('{"a" : {"b" : 43, "e" : 10}, "c" : [4, 5, 6]}');
SELECT json FROM test;
```

```json
{"a":{"b":42},"c":["1","2","3"]}
{"a":{"b":0},"f":"Hello, World!"}
{"a":{"b":43},"c":["4","5","6"]}
```

- The second line includes `"a":{"b":0}` because the type hint `a.b UInt32` is specified.
- The third line skips `"a":{"e":10}` due to the `SKIP a.e` directive.

## Casting to JSON Type 

Using CAST from `String`:

```sql
SELECT '{"a" : {"b" : 42},"c" : [1, 2, 3], "d" : "Hello, World!"}'::JSON AS json;
```

```json
{"a":{"b":42},"c":[1,2,3],"d":"Hello, World!"}
```

Using CAST from `Tuple`:

```sql
SET enable_named_columns_in_function_tuple = 1;
SELECT (tuple(42 AS b) AS a, [1, 2, 3] AS c, 'Hello, World!' AS d)::JSON AS json;
```

```json
{"a":{"b":42},"c":[1,2,3],"d":"Hello, World!"}
```

Using CAST from Map:

```sql
SELECT map('a', map('b', 42), 'c', [1,2,3], 'd', 'Hello, World!')::JSON AS json;
```

```json
{"a":{"b":42},"c":[1,2,3],"d":"Hello, World!"}
```

Using CAST from (deprecated) Object('json'):

```sql
SELECT '{"a" : {"b" : 42},"c" : [1, 2, 3], "d" : "Hello, World!"}'::Object('json')::JSON AS json;
```

```json
{"a":{"b":42},"c":[1,2,3],"d":"Hello, World!"}
```


## Reading JSON paths as subcolumns

JSON type supports reading every path as a separate subcolumn. If type of the requested path was not specified in the JSON type declaration, the subcolumn of the path will always have type Dynamic.

```sql
CREATE TABLE test (json JSON(a.b UInt32, SKIP a.e)) ENGINE = Memory;
INSERT INTO test VALUES ('{"a" : {"b" : 42, "g" : 42.42}, "c" : [1, 2, 3], "d" : "2020-01-01"}'), ('{"f" : "Hello, World!", "d" : "2020-01-02"}'), ('{"a" : {"b" : 43, "e" : 10, "g" : 43.43}, "c" : [4, 5, 6]}');
SELECT json FROM test;
```

```json
{"a":{"b":42,"g":42.42},"c":["1","2","3"],"d":"2020-01-01"}
{"a":{"b":0},"d":"2020-01-02","f":"Hello, World!"}
{"a":{"b":43,"g":43.43},"c":["4","5","6"]}
```

```sql
SELECT json.a.b, json.a.g, json.c, json.d FROM test FORMAT Pretty;
```
```
  +----------+----------+---------+------------+
   | json.a.b | json.a.g | json.c  | json.d     |
   +----------+----------+---------+------------+
1. |       42 | 42.42    | [1,2,3] | 2020-01-01 |
   +----------+----------+---------+------------+
2. |        0 | NULL     | NULL    | 2020-01-02 |
   +----------+----------+---------+------------+
3. |       43 | 43.43    | [4,5,6] | NULL       |
   +----------+----------+---------+------------+
```

### Requested Path Does Not Exist

If the requested path wasn't found in the data, it will be filled with NULL values:

```sql
CREATE TABLE test (json JSON()) ENGINE = Memory;
INSERT INTO test VALUES ('{"a" : {"b" : 42, "g" : 42.42}}'), ('{"f" : "Hello, World!", "d" : "2020-01-02"}');
SELECT json.non.existing.path FROM test FORMAT Pretty;
```

```
   +------------------------+
   | json.non.existing.path |
   +------------------------+
1. | NULL                   |
   +------------------------+
2. | NULL                   |
   +------------------------+
```

### Data Types of Subcolumns


### Reading JSON sub-objects as subcolumns

[ClickHouse]: https://clickhouse.com

