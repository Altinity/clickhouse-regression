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

JSON type supports reading every path as a separate subcolumn. 

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

If type of the requested path was not specified in the JSON type declaration, the subcolumn of the path will always have type Dynamic.

```sql
CREATE TABLE test (json JSON(a.b UInt32, SKIP a.e)) ENGINE = Memory;
INSERT INTO test VALUES ('{"a" : {"b" : 42, "g" : 42.42}, "c" : [1, 2, 3], "d" : "2020-01-01"}'), ('{"f" : "Hello, World!", "d" : "2020-01-02"}'), ('{"a" : {"b" : 43, "e" : 10, "g" : 43.43}, "c" : [4, 5, 6]}');

SELECT toTypeName(json.a.b), toTypeName(json.a.g), toTypeName(json.c), toTypeName(json.d) FROM test FORMAT Pretty;
```
```
   +----------------------+----------------------+--------------------+--------------------+
   | toTypeName(json.a.b) | toTypeName(json.a.g) | toTypeName(json.c) | toTypeName(json.d) |
   +----------------------+----------------------+--------------------+--------------------+
1. | UInt32               | Dynamic              | Dynamic            | Dynamic            |
   +----------------------+----------------------+--------------------+--------------------+
2. | UInt32               | Dynamic              | Dynamic            | Dynamic            |
   +----------------------+----------------------+--------------------+--------------------+
3. | UInt32               | Dynamic              | Dynamic            | Dynamic            |
   +----------------------+----------------------+--------------------+--------------------+
```

`a.b` has type UInt32 because it was specified in the JSON type declaration. `a.g`, `c`, and `d` have type Dynamic because they were not specified in the JSON type declaration.


It is also possible to read subcolumns of a Dynamic type using special syntax json.some.path.:TypeName:

```sql
select json.a.g.:Float64, dynamicType(json.a.g), json.d.:Date, dynamicType(json.d) FROM test FORMAT Pretty;
```

```
   +---------------------+-----------------------+----------------+---------------------+
   | json.a.g.:`Float64` | dynamicType(json.a.g) | json.d.:`Date` | dynamicType(json.d) |
   +---------------------+-----------------------+----------------+---------------------+
1. |               42.42 | Float64               |     2020-01-01 | Date                |
   +---------------------+-----------------------+----------------+---------------------+
2. |                NULL | None                  |     2020-01-02 | Date                |
   +---------------------+-----------------------+----------------+---------------------+
3. |               43.43 | Float64               |           NULL | None                |
   +---------------------+-----------------------+----------------+---------------------+
```

### Casting Dynamic subcolumns to other types

Dynamic subcolumns can be cast to any data type. However, if the internal type of the subcolumn cannot be cast to the requested type, an exception will be thrown.

```sql
select json.a.g::UInt64 as uint FROM test FORMAT Pretty;
```

```
   +------+
   | uint |
   +------+
1. |   42 |
   +------+
2. |    0 |
   +------+
3. |   43 |
   +------+

```

```sql
select json.a.g::UUID as float FROM test;
```

```
Code: 48. DB::Exception: Received from localhost:9000. DB::Exception: Conversion between numeric types and UUID is not supported. Probably the passed UUID is unquoted: while executing 'FUNCTION CAST(__table1.json.a.g :: 2, 'UUID'_String :: 1) -> CAST(__table1.json.a.g, 'UUID'_String) UUID : 0'. (NOT_IMPLEMENTED)
```
### Reading JSON sub-objects as subcolumns

JSON type supports reading nested objects as subcolumns with type `JSON` using special syntax `json.^some.path`:

```sql
CREATE TABLE test (json JSON) ENGINE = Memory;
INSERT INTO test VALUES ('{"a" : {"b" : {"c" : 42, "g" : 42.42}}, "c" : [1, 2, 3], "d" : {"e" : {"f" : {"g" : "Hello, World", "h" : [1, 2, 3]}}}}'), ('{"f" : "Hello, World!", "d" : {"e" : {"f" : {"h" : [4, 5, 6]}}}}'), ('{"a" : {"b" : {"c" : 43, "e" : 10, "g" : 43.43}}, "c" : [4, 5, 6]}');
SELECT json FROM test;
```

```json
{"a":{"b":{"c":"42","g":42.42}},"c":["1","2","3"],"d":{"e":{"f":{"g":"Hello, World","h":["1","2","3"]}}}}
{"d":{"e":{"f":{"h":["4","5","6"]}}},"f":"Hello, World!"}
{"a":{"b":{"c":"43","e":"10","g":43.43}},"c":["4","5","6"]}
```

```sql
SELECT json.^a.b, json.^d.e.f FROM test;
```

```
   +-------------------------------+----------------------------------------+
   | json.^`a`.b                   | json.^`d`.e.f                          |
   +-------------------------------+----------------------------------------+
1. | {"c":"42","g":42.42}          | {"g":"Hello, World","h":["1","2","3"]} |
   +-------------------------------+----------------------------------------+
2. | {}                            | {"h":["4","5","6"]}                    |
   +-------------------------------+----------------------------------------+
3. | {"c":"43","e":"10","g":43.43} | {}                                     |
   +-------------------------------+----------------------------------------+

```


### Types inference for paths

During JSON parsing ClickHouse tries to detect the most appropriate data type for each JSON path. 

```sql
SELECT JSONAllPathsWithTypes('{"a" : "2020-01-01", "b" : "2020-01-01 10:00:00"}'::JSON) AS paths_with_types settings input_format_try_infer_dates=1, input_format_try_infer_datetimes=1;
```

https://github.com/ClickHouse/ClickHouse/issues/74586
```
┌─paths_with_types─────────────────┐
│ {'a':'Date','b':'DateTime64(9)'} │
└──────────────────────────────────┘
```

```sql
SELECT JSONAllPathsWithTypes('{"a" : "2020-01-01", "b" : "2020-01-01 10:00:00"}'::JSON) AS paths_with_types settings input_format_try_infer_dates=0, input_format_try_infer_datetimes=0;
```

```
┌─paths_with_types────────────┐
│ {'a':'String','b':'String'} │
└─────────────────────────────┘
```

```sql
SELECT JSONAllPathsWithTypes('{"a" : [1, 2, 3]}'::JSON) AS paths_with_types settings schema_inference_make_columns_nullable=1;
```

```
┌─paths_with_types───────────────┐
│ {'a':'Array(Nullable(Int64))'} │
└────────────────────────────────┘
```

```sql
SELECT JSONAllPathsWithTypes('{"a" : [1, 2, 3]}'::JSON) AS paths_with_types settings schema_inference_make_columns_nullable=0;
```

```
┌─paths_with_types─────┐
│ {'a':'Array(Int64)'} │
└──────────────────────┘
```

### Handling arrays of JSON objects

JSON paths that contains an array of objects are parsed as type Array(JSON) and inserted into Dynamic column for this path. To read an array of objects you can extract it from Dynamic column as a subcolumn:

```sql
CREATE TABLE test (json JSON) ENGINE = Memory;
INSERT INTO test VALUES
('{"a" : {"b" : [{"c" : 42, "d" : "Hello", "f" : [[{"g" : 42.42}]], "k" : {"j" : 1000}}, {"c" : 43}, {"e" : [1, 2, 3], "d" : "My", "f" : [[{"g" : 43.43, "h" : "2020-01-01"}]],  "k" : {"j" : 2000}}]}}'),
('{"a" : {"b" : [1, 2, 3]}}'),
('{"a" : {"b" : [{"c" : 44, "f" : [[{"h" : "2020-01-02"}]]}, {"e" : [4, 5, 6], "d" : "World", "f" : [[{"g" : 44.44}]],  "k" : {"j" : 3000}}]}}');
SELECT json FROM test;
```

```
┌─json────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ {"a":{"b":[{"c":"42","d":"Hello","f":[[{"g":42.42}]],"k":{"j":"1000"}},{"c":"43"},{"d":"My","e":["1","2","3"],"f":[[{"g":43.43,"h":"2020-01-01"}]],"k":{"j":"2000"}}]}} │
│ {"a":{"b":["1","2","3"]}}                                                                                                                                               │
│ {"a":{"b":[{"c":"44","f":[[{"h":"2020-01-02"}]]},{"d":"World","e":["4","5","6"],"f":[[{"g":44.44}]],"k":{"j":"3000"}}]}}                                                │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

```sql
SELECT json.a.b, dynamicType(json.a.b) FROM test;
```

| json.a.b | dynamicType(json.a.b) |
|:-|:-|
| ['{"c":"42","d":"Hello","f":[[{"g":42.42}]],"k":{"j":"1000"}}','{"c":"43"}','{"d":"My","e":["1","2","3"],"f":[[{"g":43.43,"h":"2020-01-01"}]],"k":{"j":"2000"}}'] | Array(JSON(max_dynamic_types=16, max_dynamic_paths=256)) |
| [1,2,3] | Array(Nullable(Int64)) |
| ['{"c":"44","f":[[{"h":"2020-01-02"}]]}','{"d":"World","e":["4","5","6"],"f":[[{"g":44.44}]],"k":{"j":"3000"}}'] | Array(JSON(max_dynamic_types=16, max_dynamic_paths=256)) |


As you can notice, the max_dynamic_types/max_dynamic_paths parameters of the nested JSON type were reduced compared to the default values. It's needed to avoid number of subcolumns to grow uncontrolled on nested arrays of JSON objects.

Let's try to read subcolumns from this nested JSON column:

```sql
SELECT json.a.b.:`Array(JSON)`.c, json.a.b.:`Array(JSON)`.f, json.a.b.:`Array(JSON)`.d FROM test; 
```

```
┌─json.a.b.:`Array(JSON)`.c─┬─json.a.b.:`Array(JSON)`.f───────────────────────────────────┬─json.a.b.:`Array(JSON)`.d─┐
│ [42,43,NULL]              │ [[['{"g":42.42}']],NULL,[['{"g":43.43,"h":"2020-01-01"}']]] │ ['Hello',NULL,'My']       │
│ []                        │ []                                                          │ []                        │
│ [44,NULL]                 │ [[['{"h":"2020-01-02"}']],[['{"g":44.44}']]]                │ [NULL,'World']            │
└───────────────────────────┴─────────────────────────────────────────────────────────────┴───────────────────────────┘
```

#### Special syntax for arrays of JSON objects

We can avoid writing Array(JSON) subcolumn name using special syntax:

```sql
SELECT json.a.b[].c, json.a.b[].f, json.a.b[].d FROM test;
```

```
┌─json.a.b.:`Array(JSON)`.c─┬─json.a.b.:`Array(JSON)`.f───────────────────────────────────┬─json.a.b.:`Array(JSON)`.d─┐
│ [42,43,NULL]              │ [[['{"g":42.42}']],NULL,[['{"g":43.43,"h":"2020-01-01"}']]] │ ['Hello',NULL,'My']       │
│ []                        │ []                                                          │ []                        │
│ [44,NULL]                 │ [[['{"h":"2020-01-02"}']],[['{"g":44.44}']]]                │ [NULL,'World']            │
└───────────────────────────┴─────────────────────────────────────────────────────────────┴───────────────────────────┘
```

The number of [] after path indicates the array level. json.path[][] will be transformed to json.path.:Array(Array(JSON)).


Let's check the paths and types inside our Array(JSON):

```sql
SELECT DISTINCT arrayJoin(JSONAllPathsWithTypes(arrayJoin(json.a.b[]))) FROM test;
```

```
┌─arrayJoin(JSONAllPathsWithTypes(arrayJoin(json.a.b.:`Array(JSON)`)))──┐
│ ('c','Int64')                                                         │
│ ('d','String')                                                        │
│ ('f','Array(Array(JSON(max_dynamic_types=8, max_dynamic_paths=64)))') │
│ ('k.j','Int64')                                                       │
│ ('e','Array(Nullable(Int64))')                                        │
└───────────────────────────────────────────────────────────────────────┘
```

Let's read subcolumns from Array(JSON) column:

```sql
SELECT json.a.b[].c.:Int64, json.a.b[].f[][].g.:Float64, json.a.b[].f[][].h.:Date FROM test;
```

```
┌─json.a.b.:`Array(JSON)`.c.:`Int64`─┬─json.a.b.:`Array(JSON)`.f.:`Array(Array(JSON))`.g.:`Float64`─┬─json.a.b.:`Array(JSON)`.f.:`Array(Array(JSON))`.h.:`Date`─┐
│ [42,43,NULL]                       │ [[[42.42]],[],[[43.43]]]                                     │ [[[NULL]],[],[['2020-01-01']]]                            │
│ []                                 │ []                                                           │ []                                                        │
│ [44,NULL]                          │ [[[NULL]],[[44.44]]]                                         │ [[['2020-01-02']],[[NULL]]]                               │
└────────────────────────────────────┴──────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────┘
```

We can also read sub-object subcolumns from nested JSON column:

```sql
SELECT json.a.b[].^k FROM test
```

```
['{"j":"1000"}','{}','{"j":"2000"}']
[]
['{}','{"j":"3000"}']
```

### Reading JSON type from the data

All text formats (JSONEachRow, TSV, CSV, CustomSeparated, Values, etc) supports reading JSON type.

Examples:

```sql
SELECT json FROM format(JSONEachRow, 'json JSON(a.b.c UInt32, SKIP a.b.d, SKIP d.e, SKIP REGEXP \'b.*\')', '
{"json" : {"a" : {"b" : {"c" : 1, "d" : [0, 1]}}, "b" : "2020-01-01", "c" : 42, "d" : {"e" : {"f" : ["s1", "s2"]}, "i" : [1, 2, 3]}}}
{"json" : {"a" : {"b" : {"c" : 2, "d" : [2, 3]}}, "b" : [1, 2, 3], "c" : null, "d" : {"e" : {"g" : 43}, "i" : [4, 5, 6]}}}
{"json" : {"a" : {"b" : {"c" : 3, "d" : [4, 5]}}, "b" : {"c" : 10}, "e" : "Hello, World!"}}
{"json" : {"a" : {"b" : {"c" : 4, "d" : [6, 7]}}, "c" : 43}}
{"json" : {"a" : {"b" : {"c" : 5, "d" : [8, 9]}}, "b" : {"c" : 11, "j" : [1, 2, 3]}, "d" : {"e" : {"f" : ["s3", "s4"], "g" : 44}, "h" : "2020-02-02 10:00:00"}}}
')
```

```
{"a":{"b":{"c":1}},"c":"42","d":{"i":["1","2","3"]}}
{"a":{"b":{"c":2}},"d":{"i":["4","5","6"]}}
{"a":{"b":{"c":3}},"e":"Hello, World!"}
{"a":{"b":{"c":4}},"c":"43"}
{"a":{"b":{"c":5}},"d":{"h":"2020-02-02 10:00:00"}}
```

For text formats like CSV/TSV/etc JSON is parsed from a string containing JSON object.

```sql
SELECT json FROM format(TSV, 'json JSON(a.b.c UInt32, SKIP a.b.d, SKIP REGEXP \'b.*\')',
'{"a" : {"b" : {"c" : 1, "d" : [0, 1]}}, "b" : "2020-01-01", "c" : 42, "d" : {"e" : {"f" : ["s1", "s2"]}, "i" : [1, 2, 3]}}
{"a" : {"b" : {"c" : 2, "d" : [2, 3]}}, "b" : [1, 2, 3], "c" : null, "d" : {"e" : {"g" : 43}, "i" : [4, 5, 6]}}
{"a" : {"b" : {"c" : 3, "d" : [4, 5]}}, "b" : {"c" : 10}, "e" : "Hello, World!"}
{"a" : {"b" : {"c" : 4, "d" : [6, 7]}}, "c" : 43}
{"a" : {"b" : {"c" : 5, "d" : [8, 9]}}, "b" : {"c" : 11, "j" : [1, 2, 3]}, "d" : {"e" : {"f" : ["s3", "s4"], "g" : 44}, "h" : "2020-02-02 10:00:00"}}')
```

```
{"a":{"b":{"c":1}},"c":"42","d":{"e":{"f":["s1","s2"]},"i":["1","2","3"]}}
{"a":{"b":{"c":2}},"d":{"e":{"g":"43"},"i":["4","5","6"]}}
{"a":{"b":{"c":3}},"e":"Hello, World!"}
{"a":{"b":{"c":4}},"c":"43"}
{"a":{"b":{"c":5}},"d":{"e":{"f":["s3","s4"],"g":"44"},"h":"2020-02-02 10:00:00"}}
```

### Reaching the limit of dynamic paths inside JSON

JSON data type can store only limited number of paths as separate subcolumns inside. By default, this limit is 1024, but you can change it in type declaration using parameter max_dynamic_paths. When the limit is reached, all new paths inserted to JSON column will be stored in a single shared data structure. It's still possible to read such paths as subcolumns, but it will require reading the whole shared data structure to extract the values of this path. This limit is needed to avoid the enormous number of different subcolumns that can make the table unusable.

#### Reaching the limit during data parsing

During parsing of JSON object from the data, when the limit is reached for current block of data, all new paths will be stored in a shared data structure. We can check it using introspection functions JSONDynamicPaths, JSONSharedDataPaths:

```sql
SELECT json, JSONDynamicPaths(json), JSONSharedDataPaths(json) FROM format(JSONEachRow, 'json JSON(max_dynamic_paths=3)', '
{"json" : {"a" : {"b" : 42}, "c" : [1, 2, 3]}}
{"json" : {"a" : {"b" : 43}, "d" : "2020-01-01"}}
{"json" : {"a" : {"b" : 44}, "c" : [4, 5, 6]}}
{"json" : {"a" : {"b" : 43}, "d" : "2020-01-02", "e" : "Hello", "f" : {"g" : 42.42}}}
{"json" : {"a" : {"b" : 43}, "c" : [7, 8, 9], "f" : {"g" : 43.43}, "h" : "World"}}
')
```

```
┌─json───────────────────────────────────────────────────────────┬─JSONDynamicPaths(json)─┬─JSONSharedDataPaths(json)─┐
│ {"a":{"b":"42"},"c":["1","2","3"]}                             │ ['a.b','c','d']        │ []                        │
│ {"a":{"b":"43"},"d":"2020-01-01"}                              │ ['a.b','c','d']        │ []                        │
│ {"a":{"b":"44"},"c":["4","5","6"]}                             │ ['a.b','c','d']        │ []                        │
│ {"a":{"b":"43"},"d":"2020-01-02","e":"Hello","f":{"g":42.42}}  │ ['a.b','c','d']        │ ['e','f.g']               │
│ {"a":{"b":"43"},"c":["7","8","9"],"f":{"g":43.43},"h":"World"} │ ['a.b','c','d']        │ ['f.g','h']               │
└────────────────────────────────────────────────────────────────┴────────────────────────┴───────────────────────────┘
```

As we can see, after inserting paths e and f.g the limit was reached and we inserted them into shared data structure.


#### During merges of data parts in MergeTree table engines

During merge of several data parts in MergeTree table the JSON column in the resulting data part can reach the limit of dynamic paths and won't be able to store all paths from source parts as subcolumns. In this case ClickHouse chooses what paths will remain as subcolumns after merge and what paths will be stored in the shared data structure. In most cases ClickHouse tries to keep paths that contain the largest number of non-null values and move the rarest paths to the shared data structure, but it depends on the implementation.

Let's see an example of such merge. First, let's create a table with `JSON` column, set the limit of dynamic paths to 3 and insert values with 5 different paths:

```sql
CREATE TABLE test (id UInt64, json JSON(max_dynamic_paths=3)) engine=MergeTree ORDER BY id;
SYSTEM STOP MERGES test;
INSERT INTO test SELECT number, formatRow('JSONEachRow', number as a) FROM numbers(5);
INSERT INTO test SELECT number, formatRow('JSONEachRow', number as b) FROM numbers(4);
INSERT INTO test SELECT number, formatRow('JSONEachRow', number as c) FROM numbers(3);
INSERT INTO test SELECT number, formatRow('JSONEachRow', number as d) FROM numbers(2);
INSERT INTO test SELECT number, formatRow('JSONEachRow', number as e)  FROM numbers(1);
```

Each insert will create a separate data pert with `JSON` column containing single path:

```sql
SELECT count(), JSONDynamicPaths(json) AS dynamic_paths, JSONSharedDataPaths(json) AS shared_data_paths, _part FROM test GROUP BY _part, dynamic_paths, shared_data_paths ORDER BY _part ASC
```

```
┌─count()─┬─dynamic_paths─┬─shared_data_paths─┬─_part─────┐
│       5 │ ['a']         │ []                │ all_1_1_0 │
│       4 │ ['b']         │ []                │ all_2_2_0 │
│       3 │ ['c']         │ []                │ all_3_3_0 │
│       2 │ ['d']         │ []                │ all_4_4_0 │
│       1 │ ['e']         │ []                │ all_5_5_0 │
└─────────┴───────────────┴───────────────────┴───────────┘
```

Now, let's merge all parts into one and see what will happen:

```sql
SYSTEM START MERGES test;
OPTIMIZE TABLE test FINAL;
SELECT count(), dynamicType(d), _part FROM test GROUP BY _part, dynamicType(d) ORDER BY _part;
```

```
┌─count()─┬─dynamic_paths─┬─shared_data_paths─┬─_part─────┐
│       1 │ ['a','b','c'] │ ['e']             │ all_1_5_2 │
│       2 │ ['a','b','c'] │ ['d']             │ all_1_5_2 │
│      12 │ ['a','b','c'] │ []                │ all_1_5_2 │
└─────────┴───────────────┴───────────────────┴───────────┘
```


[ClickHouse]: https://clickhouse.com

