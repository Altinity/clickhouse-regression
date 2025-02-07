# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.241127.1225014.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_043_JSON_DeclareColumn = Requirement(
    name="RQ.SRS-043.JSON.DeclareColumn",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support declaring a column of JSON type using the following syntax:\n"
        "\n"
        "```sql\n"
        "<column_name> JSON(max_dynamic_paths=N, max_dynamic_types=M, some.path TypeName, SKIP path.to.skip, SKIP REGEXP 'paths_regexp')\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.1",
)

RQ_SRS_043_JSON_Parameters_max_dynamic_paths = Requirement(
    name="RQ.SRS-043.JSON.Parameters.max_dynamic_paths",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support optional `max_dynamic_paths` parameter in the JSON type declaration which indicates how many paths can be stored separately as subcolumns across a single block of data that is stored separately (for example, across a single data part for a MergeTree table). \n"
        "If this limit is exceeded, all other paths will be stored together in a single structure. The default value of `max_dynamic_paths` is 1024.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.1",
)

RQ_SRS_043_JSON_Parameters_max_dynamic_types = Requirement(
    name="RQ.SRS-043.JSON.Parameters.max_dynamic_types",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support optional `max_dynamic_types` parameter in the JSON type declaration which indicates how many different data types can be stored inside a single path column with type Dynamic across a single block of data that is stored separately (for example, across a single data part for a MergeTree table). If this limit is exceeded, all new types will be converted to type String. The default value of `max_dynamic_types` is 32.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.2",
)

RQ_SRS_043_JSON_Parameters_Hints_TypeHint = Requirement(
    name="RQ.SRS-043.JSON.Parameters.Hints.TypeHint",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support optional type hint `some.path TypeName` for particular path in the JSON. Such paths will be always stored as subcolumns with specified type.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.1",
)

RQ_SRS_043_JSON_Parameters_Hints_SkipHint = Requirement(
    name="RQ.SRS-043.JSON.Parameters.Hints.SkipHint",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support optional hint `SKIP path.to.skip` for particular path that should be skipped during JSON parsing. Such paths will never be stored in the JSON column.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.2",
)

RQ_SRS_043_JSON_Parameters_Hints_SkipRegexpHint = Requirement(
    name="RQ.SRS-043.JSON.Parameters.Hints.SkipRegexpHint",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support optional hint `SKIP REGEXP 'path_regexp'` with a regular expression that is used to skip paths during JSON parsing. All paths that match this regular expression will never be stored in the JSON column.\n"
        "\n"
        "\n"
        "\n"
        "Examples:\n"
        "\n"
        "1. Create a table with a JSON column without specifying any parameters:\n"
        "```sql\n"
        "CREATE TABLE test (json JSON) ENGINE = Memory;\n"
        'INSERT INTO test VALUES (\'{"a" : {"b" : 42}, "c" : [1, 2, 3]}\'), (\'{"f" : "Hello, World!"}\'), (\'{"a" : {"b" : 43, "e" : 10}, "c" : [4, 5, 6]}\');\n'
        "SELECT json FROM test;\n"
        "```\n"
        "\n"
        "```json\n"
        '{"a":{"b":"42"},"c":["1","2","3"]}\n'
        '{"f":"Hello, World!"}\n'
        '{"a":{"b":"43","e":"10"},"c":["4","5","6"]}\n'
        "```\n"
        "\n"
        "2. Create a table with a JSON column and with a **type hint** for a particular path and a **path to skip**:\n"
        "```sql\n"
        "CREATE TABLE test (json JSON(a.b UInt32, SKIP a.e)) ENGINE = Memory;\n"
        'INSERT INTO test VALUES (\'{"a" : {"b" : 42}, "c" : [1, 2, 3]}\'), (\'{"f" : "Hello, World!"}\'), (\'{"a" : {"b" : 43, "e" : 10}, "c" : [4, 5, 6]}\');\n'
        "SELECT json FROM test;\n"
        "```\n"
        "\n"
        "```json\n"
        '{"a":{"b":42},"c":["1","2","3"]}\n'
        '{"a":{"b":0},"f":"Hello, World!"}\n'
        '{"a":{"b":43},"c":["4","5","6"]}\n'
        "```\n"
        "\n"
        '- The second line includes `"a":{"b":0}` because the type hint `a.b UInt32` is specified.\n'
        '- The third line skips `"a":{"e":10}` due to the `SKIP a.e` directive.\n'
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.3",
)

RQ_SRS_043_JSON_Casting_CastFromString = Requirement(
    name="RQ.SRS-043.JSON.Casting.CastFromString",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support casting from `String` to `JSON` type.\n"
        "\n"
        "```sql\n"
        'SELECT \'{"a" : {"b" : 42},"c" : [1, 2, 3], "d" : "Hello, World!"}\'::JSON AS json;\n'
        "```\n"
        "Result:  \n"
        "```json\n"
        '{"a":{"b":42},"c":[1,2,3],"d":"Hello, World!"}\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.1",
)

RQ_SRS_043_JSON_Casting_CastFromTuple = Requirement(
    name="RQ.SRS-043.JSON.Casting.CastFromTuple",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support casting from `Tuple` to `JSON` type.\n"
        "\n"
        "```sql\n"
        "SET enable_named_columns_in_function_tuple = 1;\n"
        "SELECT (tuple(42 AS b) AS a, [1, 2, 3] AS c, 'Hello, World!' AS d)::JSON AS json;\n"
        "```\n"
        "Result:  \n"
        "```json\n"
        '{"a":{"b":42},"c":[1,2,3],"d":"Hello, World!"}\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.2",
)

RQ_SRS_043_JSON_Casting_CastFromMap = Requirement(
    name="RQ.SRS-043.JSON.Casting.CastFromMap",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support casting from `Map` to `JSON` type.\n"
        "\n"
        "```sql\n"
        "SET use_variant_as_common_type = 1, enable_variant_type = 1;\n"
        "SELECT map('a', map('b', 42), 'c', [1,2,3], 'd', 'Hello, World!')::JSON AS json;\n"
        "```\n"
        "Result:\n"
        "```json\n"
        '{"a":{"b":42},"c":[1,2,3],"d":"Hello, World!"}\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.3",
)

RQ_SRS_043_JSON_Casting_CastFromObjectJson = Requirement(
    name="RQ.SRS-043.JSON.Casting.CastFromObjectJson",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support casting from (deprecated) `Object('json')` to `JSON` type.\n"
        "\n"
        "```sql\n"
        'SELECT \'{"a" : {"b" : 42},"c" : [1, 2, 3], "d" : "Hello, World!"}\'::Object(\'json\')::JSON AS json;\n'
        "```\n"
        "Result:\n"
        "```json\n"
        '{"a":{"b":42},"c":[1,2,3],"d":"Hello, World!"}\n'
        "```\n"
        "\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.4",
)

RQ_SRS_043_JSON_ReadingPaths = Requirement(
    name="RQ.SRS-043.JSON.ReadingPaths",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support reading JSON paths as separate subcolumns using syntax `json.some.path`.\n"
        "\n"
        "**Example:**  \n"
        "\n"
        "```sql\n"
        "CREATE TABLE test (json JSON(a.b UInt32, SKIP a.e)) ENGINE = Memory;\n"
        'INSERT INTO test VALUES (\'{"a" : {"b" : 42, "g" : 42.42}, "c" : [1, 2, 3], "d" : "2020-01-01"}\'), (\'{"f" : "Hello, World!", "d" : "2020-01-02"}\'), (\'{"a" : {"b" : 43, "e" : 10, "g" : 43.43}, "c" : [4, 5, 6]}\');\n'
        "SELECT json FROM test;\n"
        "```\n"
        "\n"
        "```json\n"
        '{"a":{"b":42,"g":42.42},"c":["1","2","3"],"d":"2020-01-01"}\n'
        '{"a":{"b":0},"d":"2020-01-02","f":"Hello, World!"}\n'
        '{"a":{"b":43,"g":43.43},"c":["4","5","6"]}\n'
        "```\n"
        "\n"
        "```sql\n"
        "SELECT json.a.b, json.a.g, json.c, json.d FROM test FORMAT Pretty;\n"
        "```\n"
        "```\n"
        "  +----------+----------+---------+------------+\n"
        "   | json.a.b | json.a.g | json.c  | json.d     |\n"
        "   +----------+----------+---------+------------+\n"
        "1. |       42 | 42.42    | [1,2,3] | 2020-01-01 |\n"
        "   +----------+----------+---------+------------+\n"
        "2. |        0 | NULL     | NULL    | 2020-01-02 |\n"
        "   +----------+----------+---------+------------+\n"
        "3. |       43 | 43.43    | [4,5,6] | NULL       |\n"
        "   +----------+----------+---------+------------+\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_SRS_043_JSON_ReadingPaths_RequestedPathDoesNotExist = Requirement(
    name="RQ.SRS-043.JSON.ReadingPaths.RequestedPathDoesNotExist",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL fill the subcolumn with NULL values if the requested path was not found in the data.\n"
        "\n"
        "**Example:**  \n"
        "\n"
        "```sql\n"
        "CREATE TABLE test (json JSON()) ENGINE = Memory;\n"
        'INSERT INTO test VALUES (\'{"a" : {"b" : 42, "g" : 42.42}}\'), (\'{"f" : "Hello, World!", "d" : "2020-01-02"}\');\n'
        "SELECT json.non.existing.path FROM test FORMAT Pretty;\n"
        "```\n"
        "\n"
        "```\n"
        "   +------------------------+\n"
        "   | json.non.existing.path |\n"
        "   +------------------------+\n"
        "1. | NULL                   |\n"
        "   +------------------------+\n"
        "2. | NULL                   |\n"
        "   +------------------------+\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.1",
)

RQ_SRS_043_JSON_ReadingPaths_DataTypes = Requirement(
    name="RQ.SRS-043.JSON.ReadingPaths.DataTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL determine the data type of the subcolumn based on the JSON type declaration. If the type of the requested path was not specified in the JSON type declaration, the subcolumn of the path will always have type `Dynamic`.\n"
        "\n"
        "**Example:**  \n"
        "\n"
        "```sql\n"
        "CREATE TABLE test (json JSON(a.b UInt32, SKIP a.e)) ENGINE = Memory;\n"
        'INSERT INTO test VALUES (\'{"a" : {"b" : 42, "g" : 42.42}, "c" : [1, 2, 3], "d" : "2020-01-01"}\'), (\'{"f" : "Hello, World!", "d" : "2020-01-02"}\'), (\'{"a" : {"b" : 43, "e" : 10, "g" : 43.43}, "c" : [4, 5, 6]}\');\n'
        "\n"
        "SELECT toTypeName(json.a.b), toTypeName(json.a.g), toTypeName(json.c), toTypeName(json.d) FROM test FORMAT Pretty;\n"
        "```\n"
        "```\n"
        "   +----------------------+----------------------+--------------------+--------------------+\n"
        "   | toTypeName(json.a.b) | toTypeName(json.a.g) | toTypeName(json.c) | toTypeName(json.d) |\n"
        "   +----------------------+----------------------+--------------------+--------------------+\n"
        "1. | UInt32               | Dynamic              | Dynamic            | Dynamic            |\n"
        "   +----------------------+----------------------+--------------------+--------------------+\n"
        "2. | UInt32               | Dynamic              | Dynamic            | Dynamic            |\n"
        "   +----------------------+----------------------+--------------------+--------------------+\n"
        "3. | UInt32               | Dynamic              | Dynamic            | Dynamic            |\n"
        "   +----------------------+----------------------+--------------------+--------------------+\n"
        "```\n"
        "\n"
        "`a.b` has type UInt32 because it was specified in the JSON type declaration. `a.g`, `c`, and `d` have type Dynamic because they were not specified in the JSON type declaration.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.3.1",
)

RQ_SRS_043_JSON_ReadingPaths_CastingDynamicSubcolumns = Requirement(
    name="RQ.SRS-043.JSON.ReadingPaths.CastingDynamicSubcolumns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support casting Dynamic subcolumns to other types using special syntax json.some.path.:TypeName. If the internal type of the subcolumn cannot be cast to the requested type, an exception will be thrown.\n"
        "\n"
        "Examples:  \n"
        "\n"
        "```sql\n"
        "select json.a.g.:Float64, dynamicType(json.a.g), json.d.:Date, dynamicType(json.d) FROM test FORMAT Pretty;\n"
        "```\n"
        "\n"
        "```\n"
        "   +---------------------+-----------------------+----------------+---------------------+\n"
        "   | json.a.g.:`Float64` | dynamicType(json.a.g) | json.d.:`Date` | dynamicType(json.d) |\n"
        "   +---------------------+-----------------------+----------------+---------------------+\n"
        "1. |               42.42 | Float64               |     2020-01-01 | Date                |\n"
        "   +---------------------+-----------------------+----------------+---------------------+\n"
        "2. |                NULL | None                  |     2020-01-02 | Date                |\n"
        "   +---------------------+-----------------------+----------------+---------------------+\n"
        "3. |               43.43 | Float64               |           NULL | None                |\n"
        "   +---------------------+-----------------------+----------------+---------------------+\n"
        "```\n"
        "\n"
        "```sql\n"
        "select json.a.g::UInt64 as uint FROM test FORMAT Pretty;\n"
        "```\n"
        "\n"
        "```\n"
        "   +------+\n"
        "   | uint |\n"
        "   +------+\n"
        "1. |   42 |\n"
        "   +------+\n"
        "2. |    0 |\n"
        "   +------+\n"
        "3. |   43 |\n"
        "   +------+\n"
        "\n"
        "```\n"
        "\n"
        "```sql\n"
        "select json.a.g::UUID as float FROM test;\n"
        "```\n"
        "\n"
        "```\n"
        "Code: 48. DB::Exception: Received from localhost:9000. DB::Exception: Conversion between numeric types and UUID is not supported. Probably the passed UUID is unquoted: while executing 'FUNCTION CAST(__table1.json.a.g :: 2, 'UUID'_String :: 1) -> CAST(__table1.json.a.g, 'UUID'_String) UUID : 0'. (NOT_IMPLEMENTED)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.3.2",
)

RQ_SRS_043_JSON_ReadingSubObjects = Requirement(
    name="RQ.SRS-043.JSON.ReadingSubObjects",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support reading nested objects as subcolumns with type `JSON` using special syntax `json.^some.path`.\n"
        "\n"
        "**Example:**  \n"
        "\n"
        "```sql\n"
        "CREATE TABLE test (json JSON) ENGINE = Memory;\n"
        'INSERT INTO test VALUES (\'{"a" : {"b" : {"c" : 42, "g" : 42.42}}, "c" : [1, 2, 3], "d" : {"e" : {"f" : {"g" : "Hello, World", "h" : [1, 2, 3]}}}}\'), (\'{"f" : "Hello, World!", "d" : {"e" : {"f" : {"h" : [4, 5, 6]}}}}\'), (\'{"a" : {"b" : {"c" : 43, "e" : 10, "g" : 43.43}}, "c" : [4, 5, 6]}\');\n'
        "SELECT json FROM test;\n"
        "```\n"
        "\n"
        "```json\n"
        '{"a":{"b":{"c":"42","g":42.42}},"c":["1","2","3"],"d":{"e":{"f":{"g":"Hello, World","h":["1","2","3"]}}}}\n'
        '{"d":{"e":{"f":{"h":["4","5","6"]}}},"f":"Hello, World!"}\n'
        '{"a":{"b":{"c":"43","e":"10","g":43.43}},"c":["4","5","6"]}\n'
        "```\n"
        "\n"
        "```sql\n"
        "SELECT json.^a.b, json.^d.e.f FROM test;\n"
        "```\n"
        "\n"
        "```\n"
        "   +-------------------------------+----------------------------------------+\n"
        "   | json.^`a`.b                   | json.^`d`.e.f                          |\n"
        "   +-------------------------------+----------------------------------------+\n"
        '1. | {"c":"42","g":42.42}          | {"g":"Hello, World","h":["1","2","3"]} |\n'
        "   +-------------------------------+----------------------------------------+\n"
        '2. | {}                            | {"h":["4","5","6"]}                    |\n'
        "   +-------------------------------+----------------------------------------+\n"
        '3. | {"c":"43","e":"10","g":43.43} | {}                                     |\n'
        "   +-------------------------------+----------------------------------------+\n"
        "\n"
        "```\n"
        "\n"
        "Note: Reading sub-objects as subcolumns may be inefficient, as this may require almost full scan of the JSON data.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.1",
)

RQ_SRS_043_JSON_TypesInference = Requirement(
    name="RQ.SRS-043.JSON.TypesInference",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support inferring the types of JSON paths during JSON parsing. ClickHouse tries to detect the most appropriate data type for each JSON path.\n"
        "\n"
        "Examples:\n"
        "\n"
        "```sql\n"
        'SELECT JSONAllPathsWithTypes(\'{"a" : "2020-01-01", "b" : "2020-01-01 10:00:00"}\'::JSON) AS paths_with_types settings input_format_try_infer_dates=1, input_format_try_infer_datetimes=1;\n'
        "```\n"
        "k\n"
        "```\n"
        "┌─paths_with_types─────────────────┐\n"
        "│ {'a':'Date','b':'DateTime64(9)'} │\n"
        "└──────────────────────────────────┘\n"
        "```\n"
        "\n"
        "```sql\n"
        'SELECT JSONAllPathsWithTypes(\'{"a" : "2020-01-01", "b" : "2020-01-01 10:00:00"}\'::JSON) AS paths_with_types settings input_format_try_infer_dates=0, input_format_try_infer_datetimes=0;\n'
        "```\n"
        "\n"
        "```\n"
        "┌─paths_with_types────────────┐\n"
        "│ {'a':'String','b':'String'} │\n"
        "└─────────────────────────────┘\n"
        "```\n"
        "\n"
        "```sql\n"
        "SELECT JSONAllPathsWithTypes('{\"a\" : [1, 2, 3]}'::JSON) AS paths_with_types settings schema_inference_make_columns_nullable=1;\n"
        "```\n"
        "\n"
        "```\n"
        "┌─paths_with_types───────────────┐\n"
        "│ {'a':'Array(Nullable(Int64))'} │\n"
        "└────────────────────────────────┘\n"
        "```\n"
        "\n"
        "```sql\n"
        "SELECT JSONAllPathsWithTypes('{\"a\" : [1, 2, 3]}'::JSON) AS paths_with_types settings schema_inference_make_columns_nullable=0;\n"
        "```\n"
        "\n"
        "```\n"
        "┌─paths_with_types─────┐\n"
        "│ {'a':'Array(Int64)'} │\n"
        "└──────────────────────┘\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_SRS_043_JSON_ArraysOfJsonObjects = Requirement(
    name="RQ.SRS-043.JSON.ArraysOfJsonObjects",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support parsing arrays of JSON objects as type `Array(JSON)` and inserting them into a Dynamic column for this path. To read an array of objects, it SHALL be possible to extract it from the Dynamic column as a subcolumn.\n"
        "\n"
        "**Example:**\n"
        "\n"
        "```sql\n"
        "CREATE TABLE test (json JSON) ENGINE = Memory;\n"
        "INSERT INTO test VALUES\n"
        '(\'{"a" : {"b" : [{"c" : 42, "d" : "Hello", "f" : [[{"g" : 42.42}]], "k" : {"j" : 1000}}, {"c" : 43}, {"e" : [1, 2, 3], "d" : "My", "f" : [[{"g" : 43.43, "h" : "2020-01-01"}]],  "k" : {"j" : 2000}}]}}\'),\n'
        '(\'{"a" : {"b" : [1, 2, 3]}}\'),\n'
        '(\'{"a" : {"b" : [{"c" : 44, "f" : [[{"h" : "2020-01-02"}]]}, {"e" : [4, 5, 6], "d" : "World", "f" : [[{"g" : 44.44}]],  "k" : {"j" : 3000}}]}}\');\n'
        "SELECT json FROM test;\n"
        "```\n"
        "\n"
        "```\n"
        "┌─json────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐\n"
        '│ {"a":{"b":[{"c":"42","d":"Hello","f":[[{"g":42.42}]],"k":{"j":"1000"}},{"c":"43"},{"d":"My","e":["1","2","3"],"f":[[{"g":43.43,"h":"2020-01-01"}]],"k":{"j":"2000"}}]}} │\n'
        '│ {"a":{"b":["1","2","3"]}}                                                                                                                                               │\n'
        '│ {"a":{"b":[{"c":"44","f":[[{"h":"2020-01-02"}]]},{"d":"World","e":["4","5","6"],"f":[[{"g":44.44}]],"k":{"j":"3000"}}]}}                                                │\n'
        "└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘\n"
        "```\n"
        "\n"
        "```sql\n"
        "SELECT json.a.b, dynamicType(json.a.b) FROM test;\n"
        "```\n"
        "\n"
        "| json.a.b | dynamicType(json.a.b) |\n"
        "|:-|:-|\n"
        '| [\'{"c":"42","d":"Hello","f":[[{"g":42.42}]],"k":{"j":"1000"}}\',\'{"c":"43"}\',\'{"d":"My","e":["1","2","3"],"f":[[{"g":43.43,"h":"2020-01-01"}]],"k":{"j":"2000"}}\'] | Array(JSON(max_dynamic_types=16, max_dynamic_paths=256)) |\n'
        "| [1,2,3] | Array(Nullable(Int64)) |\n"
        '| [\'{"c":"44","f":[[{"h":"2020-01-02"}]]}\',\'{"d":"World","e":["4","5","6"],"f":[[{"g":44.44}]],"k":{"j":"3000"}}\'] | Array(JSON(max_dynamic_types=16, max_dynamic_paths=256)) |\n'
        "\n"
        "\n"
        "The max_dynamic_types/max_dynamic_paths parameters of the nested JSON type were reduced compared to the default values. It's needed to avoid number of subcolumns to grow uncontrolled on nested arrays of JSON objects.\n"
        "\n"
        "Reading subcolumns from this nested JSON column:\n"
        "\n"
        "```sql\n"
        "SELECT json.a.b.:`Array(JSON)`.c, json.a.b.:`Array(JSON)`.f, json.a.b.:`Array(JSON)`.d FROM test; \n"
        "```\n"
        "\n"
        "```\n"
        "┌─json.a.b.:`Array(JSON)`.c─┬─json.a.b.:`Array(JSON)`.f───────────────────────────────────┬─json.a.b.:`Array(JSON)`.d─┐\n"
        "│ [42,43,NULL]              │ [[['{\"g\":42.42}']],NULL,[['{\"g\":43.43,\"h\":\"2020-01-01\"}']]] │ ['Hello',NULL,'My']       │\n"
        "│ []                        │ []                                                          │ []                        │\n"
        "│ [44,NULL]                 │ [[['{\"h\":\"2020-01-02\"}']],[['{\"g\":44.44}']]]                │ [NULL,'World']            │\n"
        "└───────────────────────────┴─────────────────────────────────────────────────────────────┴───────────────────────────┘\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_SRS_043_JSON_ArraysOfJsonObjects_SpecialSyntax = Requirement(
    name="RQ.SRS-043.JSON.ArraysOfJsonObjects.SpecialSyntax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support special syntax for reading subcolumns from arrays of JSON objects. The number of [] after the path indicates the array level. For example `json.path[][]` SHALL be transformed to `json.path.:Array(Array(JSON))`.\n"
        "\n"
        "**Example:**  \n"
        "\n"
        "```sql\n"
        "SELECT json.a.b[].c, json.a.b[].f, json.a.b[].d FROM test;\n"
        "```\n"
        "\n"
        "```\n"
        "┌─json.a.b.:`Array(JSON)`.c─┬─json.a.b.:`Array(JSON)`.f───────────────────────────────────┬─json.a.b.:`Array(JSON)`.d─┐\n"
        "│ [42,43,NULL]              │ [[['{\"g\":42.42}']],NULL,[['{\"g\":43.43,\"h\":\"2020-01-01\"}']]] │ ['Hello',NULL,'My']       │\n"
        "│ []                        │ []                                                          │ []                        │\n"
        "│ [44,NULL]                 │ [[['{\"h\":\"2020-01-02\"}']],[['{\"g\":44.44}']]]                │ [NULL,'World']            │\n"
        "└───────────────────────────┴─────────────────────────────────────────────────────────────┴───────────────────────────┘\n"
        "```\n"
        "\n"
        "\n"
        "\n"
        "Checking the paths and types inside our Array(JSON):\n"
        "\n"
        "```sql\n"
        "SELECT DISTINCT arrayJoin(JSONAllPathsWithTypes(arrayJoin(json.a.b[]))) FROM test;\n"
        "```\n"
        "\n"
        "```\n"
        "┌─arrayJoin(JSONAllPathsWithTypes(arrayJoin(json.a.b.:`Array(JSON)`)))──┐\n"
        "│ ('c','Int64')                                                         │\n"
        "│ ('d','String')                                                        │\n"
        "│ ('f','Array(Array(JSON(max_dynamic_types=8, max_dynamic_paths=64)))') │\n"
        "│ ('k.j','Int64')                                                       │\n"
        "│ ('e','Array(Nullable(Int64))')                                        │\n"
        "└───────────────────────────────────────────────────────────────────────┘\n"
        "```\n"
        "\n"
        "Reading subcolumns from Array(JSON) column:\n"
        "\n"
        "```sql\n"
        "SELECT json.a.b[].c.:Int64, json.a.b[].f[][].g.:Float64, json.a.b[].f[][].h.:Date FROM test;\n"
        "```\n"
        "\n"
        "```\n"
        "┌─json.a.b.:`Array(JSON)`.c.:`Int64`─┬─json.a.b.:`Array(JSON)`.f.:`Array(Array(JSON))`.g.:`Float64`─┬─json.a.b.:`Array(JSON)`.f.:`Array(Array(JSON))`.h.:`Date`─┐\n"
        "│ [42,43,NULL]                       │ [[[42.42]],[],[[43.43]]]                                     │ [[[NULL]],[],[['2020-01-01']]]                            │\n"
        "│ []                                 │ []                                                           │ []                                                        │\n"
        "│ [44,NULL]                          │ [[[NULL]],[[44.44]]]                                         │ [[['2020-01-02']],[[NULL]]]                               │\n"
        "└────────────────────────────────────┴──────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────┘\n"
        "```\n"
        "\n"
        "Reading sub-object subcolumns from nested JSON column:\n"
        "\n"
        "```sql\n"
        "SELECT json.a.b[].^k FROM test\n"
        "```\n"
        "\n"
        "```\n"
        '[\'{"j":"1000"}\',\'{}\',\'{"j":"2000"}\']\n'
        "[]\n"
        "['{}','{\"j\":\"3000\"}']\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.2.1",
)

RQ_SRS_043_JSON_ReadingJsonFromData = Requirement(
    name="RQ.SRS-043.JSON.ReadingJsonFromData",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support reading JSON type from the data using the `format` function.\n"
        "\n"
        "Examples:\n"
        "\n"
        "```sql\n"
        "SELECT json FROM format(JSONEachRow, 'json JSON(a.b.c UInt32, SKIP a.b.d, SKIP d.e, SKIP REGEXP \\'b.*\\')', '\n"
        '{"json" : {"a" : {"b" : {"c" : 1, "d" : [0, 1]}}, "b" : "2020-01-01", "c" : 42, "d" : {"e" : {"f" : ["s1", "s2"]}, "i" : [1, 2, 3]}}}\n'
        '{"json" : {"a" : {"b" : {"c" : 2, "d" : [2, 3]}}, "b" : [1, 2, 3], "c" : null, "d" : {"e" : {"g" : 43}, "i" : [4, 5, 6]}}}\n'
        '{"json" : {"a" : {"b" : {"c" : 3, "d" : [4, 5]}}, "b" : {"c" : 10}, "e" : "Hello, World!"}}\n'
        '{"json" : {"a" : {"b" : {"c" : 4, "d" : [6, 7]}}, "c" : 43}}\n'
        '{"json" : {"a" : {"b" : {"c" : 5, "d" : [8, 9]}}, "b" : {"c" : 11, "j" : [1, 2, 3]}, "d" : {"e" : {"f" : ["s3", "s4"], "g" : 44}, "h" : "2020-02-02 10:00:00"}}}\n'
        "')\n"
        "```\n"
        "\n"
        "```\n"
        '{"a":{"b":{"c":1}},"c":"42","d":{"i":["1","2","3"]}}\n'
        '{"a":{"b":{"c":2}},"d":{"i":["4","5","6"]}}\n'
        '{"a":{"b":{"c":3}},"e":"Hello, World!"}\n'
        '{"a":{"b":{"c":4}},"c":"43"}\n'
        '{"a":{"b":{"c":5}},"d":{"h":"2020-02-02 10:00:00"}}\n'
        "```\n"
        "\n"
        "For text formats like CSV/TSV/etc JSON is parsed from a string containing JSON object.\n"
        "\n"
        "```sql\n"
        "SELECT json FROM format(TSV, 'json JSON(a.b.c UInt32, SKIP a.b.d, SKIP REGEXP \\'b.*\\')',\n"
        '\'{"a" : {"b" : {"c" : 1, "d" : [0, 1]}}, "b" : "2020-01-01", "c" : 42, "d" : {"e" : {"f" : ["s1", "s2"]}, "i" : [1, 2, 3]}}\n'
        '{"a" : {"b" : {"c" : 2, "d" : [2, 3]}}, "b" : [1, 2, 3], "c" : null, "d" : {"e" : {"g" : 43}, "i" : [4, 5, 6]}}\n'
        '{"a" : {"b" : {"c" : 3, "d" : [4, 5]}}, "b" : {"c" : 10}, "e" : "Hello, World!"}\n'
        '{"a" : {"b" : {"c" : 4, "d" : [6, 7]}}, "c" : 43}\n'
        '{"a" : {"b" : {"c" : 5, "d" : [8, 9]}}, "b" : {"c" : 11, "j" : [1, 2, 3]}, "d" : {"e" : {"f" : ["s3", "s4"], "g" : 44}, "h" : "2020-02-02 10:00:00"}}\')\n'
        "```\n"
        "\n"
        "```\n"
        '{"a":{"b":{"c":1}},"c":"42","d":{"e":{"f":["s1","s2"]},"i":["1","2","3"]}}\n'
        '{"a":{"b":{"c":2}},"d":{"e":{"g":"43"},"i":["4","5","6"]}}\n'
        '{"a":{"b":{"c":3}},"e":"Hello, World!"}\n'
        '{"a":{"b":{"c":4}},"c":"43"}\n'
        '{"a":{"b":{"c":5}},"d":{"e":{"f":["s3","s4"],"g":"44"},"h":"2020-02-02 10:00:00"}}\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.1",
)

RQ_SRS_043_JSON_ReachingLimitOfDynamicPaths = Requirement(
    name="RQ.SRS-043.JSON.ReachingLimitOfDynamicPaths",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support limiting the number of dynamic paths that can be stored inside a JSON column. When the limit is reached, all new paths SHALL be stored in a shared data structure. \n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.1",
)

RQ_SRS_043_JSON_ReachingLimitOfDynamicPaths_DataParsing = Requirement(
    name="RQ.SRS-043.JSON.ReachingLimitOfDynamicPaths.DataParsing",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "During parsing of JSON object from the data, when the limit is reached for current block of data, [Clickhouse] SHALL store all new paths in a shared data structure.\n"
        "\n"
        "**Example:**  \n"
        "We can check it using introspection functions JSONDynamicPaths, JSONSharedDataPaths:\n"
        "\n"
        "```sql\n"
        "SELECT json, JSONDynamicPaths(json), JSONSharedDataPaths(json) FROM format(JSONEachRow, 'json JSON(max_dynamic_paths=3)', '\n"
        '{"json" : {"a" : {"b" : 42}, "c" : [1, 2, 3]}}\n'
        '{"json" : {"a" : {"b" : 43}, "d" : "2020-01-01"}}\n'
        '{"json" : {"a" : {"b" : 44}, "c" : [4, 5, 6]}}\n'
        '{"json" : {"a" : {"b" : 43}, "d" : "2020-01-02", "e" : "Hello", "f" : {"g" : 42.42}}}\n'
        '{"json" : {"a" : {"b" : 43}, "c" : [7, 8, 9], "f" : {"g" : 43.43}, "h" : "World"}}\n'
        "')\n"
        "```\n"
        "\n"
        "```\n"
        "┌─json───────────────────────────────────────────────────────────┬─JSONDynamicPaths(json)─┬─JSONSharedDataPaths(json)─┐\n"
        '│ {"a":{"b":"42"},"c":["1","2","3"]}                             │ [\'a.b\',\'c\',\'d\']        │ []                        │\n'
        '│ {"a":{"b":"43"},"d":"2020-01-01"}                              │ [\'a.b\',\'c\',\'d\']        │ []                        │\n'
        '│ {"a":{"b":"44"},"c":["4","5","6"]}                             │ [\'a.b\',\'c\',\'d\']        │ []                        │\n'
        '│ {"a":{"b":"43"},"d":"2020-01-02","e":"Hello","f":{"g":42.42}}  │ [\'a.b\',\'c\',\'d\']        │ [\'e\',\'f.g\']               │\n'
        '│ {"a":{"b":"43"},"c":["7","8","9"],"f":{"g":43.43},"h":"World"} │ [\'a.b\',\'c\',\'d\']        │ [\'f.g\',\'h\']               │\n'
        "└────────────────────────────────────────────────────────────────┴────────────────────────┴───────────────────────────┘\n"
        "```\n"
        "\n"
        "After inserting paths e and f.g the limit was reached and we inserted them into shared data structure.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.3.1",
)

RQ_SRS_043_JSON_ReachingLimitDuringMerge = Requirement(
    name="RQ.SRS-043.JSON.ReachingLimitDuringMerge",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "If the limit of dynamic paths is reached during the merge of data parts in a MergeTree table, [ClickHouse] SHALL decide which paths will remain as subcolumns after the merge and which will be stored in the shared data structure and prioritize paths with the highest number of non-null values.\n"
        "\n"
        "**Example:**  \n"
        "\n"
        "Setting the limit of dynamic paths to 3 and insert values with 5 different paths:\n"
        "\n"
        "```sql\n"
        "CREATE TABLE test (id UInt64, json JSON(max_dynamic_paths=3)) engine=MergeTree ORDER BY id;\n"
        "SYSTEM STOP MERGES test;\n"
        "INSERT INTO test SELECT number, formatRow('JSONEachRow', number as a) FROM numbers(5);\n"
        "INSERT INTO test SELECT number, formatRow('JSONEachRow', number as b) FROM numbers(4);\n"
        "INSERT INTO test SELECT number, formatRow('JSONEachRow', number as c) FROM numbers(3);\n"
        "INSERT INTO test SELECT number, formatRow('JSONEachRow', number as d) FROM numbers(2);\n"
        "INSERT INTO test SELECT number, formatRow('JSONEachRow', number as e)  FROM numbers(1);\n"
        "```\n"
        "\n"
        "Each insert will create a separate data pert with `JSON` column containing single path:\n"
        "\n"
        "```sql\n"
        "SELECT count(), JSONDynamicPaths(json) AS dynamic_paths, JSONSharedDataPaths(json) AS shared_data_paths, _part FROM test GROUP BY _part, dynamic_paths, shared_data_paths ORDER BY _part ASC\n"
        "```\n"
        "\n"
        "```\n"
        "┌─count()─┬─dynamic_paths─┬─shared_data_paths─┬─_part─────┐\n"
        "│       5 │ ['a']         │ []                │ all_1_1_0 │\n"
        "│       4 │ ['b']         │ []                │ all_2_2_0 │\n"
        "│       3 │ ['c']         │ []                │ all_3_3_0 │\n"
        "│       2 │ ['d']         │ []                │ all_4_4_0 │\n"
        "│       1 │ ['e']         │ []                │ all_5_5_0 │\n"
        "└─────────┴───────────────┴───────────────────┴───────────┘\n"
        "```\n"
        "\n"
        "Now, let's merge all parts into one and see what will happen:\n"
        "\n"
        "```sql\n"
        "SYSTEM START MERGES test;\n"
        "OPTIMIZE TABLE test FINAL;\n"
        "SELECT count(), dynamicType(d), _part FROM test GROUP BY _part, dynamicType(d) ORDER BY _part;\n"
        "```\n"
        "\n"
        "```\n"
        "┌─count()─┬─dynamic_paths─┬─shared_data_paths─┬─_part─────┐\n"
        "│       1 │ ['a','b','c'] │ ['e']             │ all_1_5_2 │\n"
        "│       2 │ ['a','b','c'] │ ['d']             │ all_1_5_2 │\n"
        "│      12 │ ['a','b','c'] │ []                │ all_1_5_2 │\n"
        "└─────────┴───────────────┴───────────────────┴───────────┘\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.4.1",
)

RQ_SRS_043_JSON_IntrospectionFunctions = Requirement(
    name="RQ.SRS-043.JSON.IntrospectionFunctions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support the following introspection functions for inspecting the content of the JSON column:\n"
        "\n"
        "- JSONAllPaths\n"
        "- JSONAllPathsWithTypes\n"
        "- JSONDynamicPaths\n"
        "- JSONDynamicPathsWithTypes\n"
        "- JSONSharedDataPaths\n"
        "- JSONSharedDataPathsWithTypes\n"
        "- distinctDynamicTypes\n"
        "- distinctJSONPaths\n"
        "- distinctJSONPathsAndTypes\n"
        "\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.1",
)

RQ_SRS_043_JSON_ModifyColumn = Requirement(
    name="RQ.SRS-043.JSON.ModifyColumn",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support changing the type of the column to the `JSON` type using the `ALTER TABLE ... MODIFY COLUMN ... JSON` syntax.\n"
        "\n"
        "\n"
        "**Example:**\n"
        "```sql\n"
        "CREATE TABLE test (json String) ENGINE=MergeTree ORDeR BY tuple();\n"
        'INSERT INTO test VALUES (\'{"a" : 42}\'), (\'{"a" : 43, "b" : "Hello"}\'), (\'{"a" : 44, "b" : [1, 2, 3]}\'), (\'{"c" : "2020-01-01"}\');\n'
        "ALTER TABLE test MODIFY COLUMN json JSON;\n"
        "SELECT json, json.a, json.b, json.c FROM test;\n"
        "```\n"
        "\n"
        "```\n"
        "┌─json─────────────────────────┬─json.a─┬─json.b──┬─json.c─────┐\n"
        '│ {"a":"42"}                   │ 42     │ ᴺᵁᴸᴸ    │ ᴺᵁᴸᴸ       │\n'
        '│ {"a":"43","b":"Hello"}       │ 43     │ Hello   │ ᴺᵁᴸᴸ       │\n'
        '│ {"a":"44","b":["1","2","3"]} │ 44     │ [1,2,3] │ ᴺᵁᴸᴸ       │\n'
        '│ {"c":"2020-01-01"}           │ ᴺᵁᴸᴸ   │ ᴺᵁᴸᴸ    │ 2020-01-01 │\n'
        "└──────────────────────────────┴────────┴─────────┴────────────┘\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.1",
)

RQ_SRS_043_JSON_Comparison = Requirement(
    name="RQ.SRS-043.JSON.Comparison",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support comparing values of the `JSON` type using the `==` operator. Two JSON objects SHALL be considered equal when they have the same set of paths and the value of each path has the same type and value in both objects.\n"
        "\n"
        "**Example:**\n"
        "```sql\n"
        "CREATE TABLE test (json1 JSON(a UInt32), json2 JSON(a UInt32)) ENGINE=Memory;\n"
        "INSERT INTO test FORMAT JSONEachRow\n"
        '{"json1" : {"a" : 42, "b" : 42, "c" : "Hello"}, "json2" : {"a" : 42, "b" : 42, "c" : "Hello"}}\n'
        '{"json1" : {"a" : 42, "b" : 42, "c" : "Hello"}, "json2" : {"a" : 43, "b" : 42, "c" : "Hello"}}\n'
        '{"json1" : {"a" : 42, "b" : 42, "c" : "Hello"}, "json2" : {"a" : 43, "b" : 42, "c" : "Hello"}}\n'
        '{"json1" : {"a" : 42, "b" : 42, "c" : "Hello"}, "json2" : {"a" : 42, "b" : 42, "c" : "World"}}\n'
        '{"json1" : {"a" : 42, "b" : [1, 2, 3], "c" : "Hello"}, "json2" : {"a" : 42, "b" : 42, "c" : "Hello"}}\n'
        '{"json1" : {"a" : 42, "b" : 42.0, "c" : "Hello"}, "json2" : {"a" : 42, "b" : 42, "c" : "Hello"}}\n'
        '{"json1" : {"a" : 42, "b" : "42", "c" : "Hello"}, "json2" : {"a" : 42, "b" : 42, "c" : "Hello"}};\n'
        "\n"
        "SELECT json1, json2, json1 == json2 FROM test;\n"
        "```\n"
        "\n"
        "```\n"
        "┌─json1──────────────────────────────────┬─json2─────────────────────────┬─equals(json1, json2)─┐\n"
        '│ {"a":42,"b":"42","c":"Hello"}          │ {"a":42,"b":"42","c":"Hello"} │                    1 │\n'
        '│ {"a":42,"b":"42","c":"Hello"}          │ {"a":43,"b":"42","c":"Hello"} │                    0 │\n'
        '│ {"a":42,"b":"42","c":"Hello"}          │ {"a":43,"b":"42","c":"Hello"} │                    0 │\n'
        '│ {"a":42,"b":"42","c":"Hello"}          │ {"a":42,"b":"42","c":"World"} │                    0 │\n'
        '│ {"a":42,"b":["1","2","3"],"c":"Hello"} │ {"a":42,"b":"42","c":"Hello"} │                    0 │\n'
        '│ {"a":42,"b":42,"c":"Hello"}            │ {"a":42,"b":"42","c":"Hello"} │                    0 │\n'
        '│ {"a":42,"b":"42","c":"Hello"}          │ {"a":42,"b":"42","c":"Hello"} │                    0 │\n'
        "└────────────────────────────────────────┴───────────────────────────────┴──────────────────────┘\n"
        "```\n"
        "\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.1",
)

SRS_043_JSON_Data_Type = Specification(
    name="SRS-043 JSON Data Type",
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
        Heading(name="Introduction", level=1, num="1"),
        Heading(name="Declaring a Column of JSON Type", level=1, num="2"),
        Heading(name="RQ.SRS-043.JSON.DeclareColumn", level=2, num="2.1"),
        Heading(name="Parameters", level=1, num="3"),
        Heading(
            name="RQ.SRS-043.JSON.Parameters.max_dynamic_paths", level=2, num="3.1"
        ),
        Heading(
            name="RQ.SRS-043.JSON.Parameters.max_dynamic_types", level=2, num="3.2"
        ),
        Heading(name="Hints", level=2, num="3.3"),
        Heading(name="RQ.SRS-043.JSON.Parameters.Hints.TypeHint", level=3, num="3.3.1"),
        Heading(name="RQ.SRS-043.JSON.Parameters.Hints.SkipHint", level=3, num="3.3.2"),
        Heading(
            name="RQ.SRS-043.JSON.Parameters.Hints.SkipRegexpHint", level=3, num="3.3.3"
        ),
        Heading(name="Casting to JSON Type ", level=1, num="4"),
        Heading(name="RQ.SRS-043.JSON.Casting.CastFromString", level=2, num="4.1"),
        Heading(name="RQ.SRS-043.JSON.Casting.CastFromTuple", level=2, num="4.2"),
        Heading(name="RQ.SRS-043.JSON.Casting.CastFromMap", level=2, num="4.3"),
        Heading(name="RQ.SRS-043.JSON.Casting.CastFromObjectJson", level=2, num="4.4"),
        Heading(name="Reading JSON paths as subcolumns", level=1, num="5"),
        Heading(name="RQ.SRS-043.JSON.ReadingPaths", level=2, num="5.1"),
        Heading(name="Requested Path Does Not Exist", level=2, num="5.2"),
        Heading(
            name="RQ.SRS-043.JSON.ReadingPaths.RequestedPathDoesNotExist",
            level=3,
            num="5.2.1",
        ),
        Heading(name="Data Types of Subcolumns", level=2, num="5.3"),
        Heading(name="RQ.SRS-043.JSON.ReadingPaths.DataTypes", level=3, num="5.3.1"),
        Heading(
            name="RQ.SRS-043.JSON.ReadingPaths.CastingDynamicSubcolumns",
            level=3,
            num="5.3.2",
        ),
        Heading(name="Reading JSON sub-objects as subcolumns", level=1, num="6"),
        Heading(name="RQ.SRS-043.JSON.ReadingSubObjects", level=2, num="6.1"),
        Heading(name="Types inference for paths", level=1, num="7"),
        Heading(name="RQ.SRS-043.JSON.TypesInference", level=2, num="7.1"),
        Heading(name="Handling arrays of JSON objects", level=1, num="8"),
        Heading(name="RQ.SRS-043.JSON.ArraysOfJsonObjects", level=2, num="8.1"),
        Heading(name="Special syntax for arrays of JSON objects", level=2, num="8.2"),
        Heading(
            name="RQ.SRS-043.JSON.ArraysOfJsonObjects.SpecialSyntax",
            level=3,
            num="8.2.1",
        ),
        Heading(name="Reading JSON type from the data", level=1, num="9"),
        Heading(name="RQ.SRS-043.JSON.ReadingJsonFromData", level=2, num="9.1"),
        Heading(
            name="Reaching the limit of dynamic paths inside JSON", level=1, num="10"
        ),
        Heading(
            name="RQ.SRS-043.JSON.ReachingLimitOfDynamicPaths", level=2, num="10.1"
        ),
        Heading(
            name="RQ.SRS-043.JSON.ReachingLimitOfDynamicPaths.ReadingPaths",
            level=2,
            num="10.2",
        ),
        Heading(name="Reaching the limit during data parsing", level=2, num="10.3"),
        Heading(
            name="RQ.SRS-043.JSON.ReachingLimitOfDynamicPaths.DataParsing",
            level=3,
            num="10.3.1",
        ),
        Heading(
            name="During merges of data parts in MergeTree table engines",
            level=2,
            num="10.4",
        ),
        Heading(name="RQ.SRS-043.JSON.ReachingLimitDuringMerge", level=3, num="10.4.1"),
        Heading(name="Introspection functions", level=1, num="11"),
        Heading(name="RQ.SRS-043.JSON.IntrospectionFunctions", level=2, num="11.1"),
        Heading(name="ALTER MODIFY COLUMN to JSON type", level=1, num="12"),
        Heading(name="RQ.SRS-043.JSON.ModifyColumn", level=2, num="12.1"),
        Heading(name="Comparison between values of the JSON type", level=1, num="13"),
        Heading(name="RQ.SRS-043.JSON.Comparison", level=2, num="13.1"),
    ),
    requirements=(
        RQ_SRS_043_JSON_DeclareColumn,
        RQ_SRS_043_JSON_Parameters_max_dynamic_paths,
        RQ_SRS_043_JSON_Parameters_max_dynamic_types,
        RQ_SRS_043_JSON_Parameters_Hints_TypeHint,
        RQ_SRS_043_JSON_Parameters_Hints_SkipHint,
        RQ_SRS_043_JSON_Parameters_Hints_SkipRegexpHint,
        RQ_SRS_043_JSON_Casting_CastFromString,
        RQ_SRS_043_JSON_Casting_CastFromTuple,
        RQ_SRS_043_JSON_Casting_CastFromMap,
        RQ_SRS_043_JSON_Casting_CastFromObjectJson,
        RQ_SRS_043_JSON_ReadingPaths,
        RQ_SRS_043_JSON_ReadingPaths_RequestedPathDoesNotExist,
        RQ_SRS_043_JSON_ReadingPaths_DataTypes,
        RQ_SRS_043_JSON_ReadingPaths_CastingDynamicSubcolumns,
        RQ_SRS_043_JSON_ReadingSubObjects,
        RQ_SRS_043_JSON_TypesInference,
        RQ_SRS_043_JSON_ArraysOfJsonObjects,
        RQ_SRS_043_JSON_ArraysOfJsonObjects_SpecialSyntax,
        RQ_SRS_043_JSON_ReadingJsonFromData,
        RQ_SRS_043_JSON_ReachingLimitOfDynamicPaths,
        RQ_SRS_043_JSON_ReachingLimitOfDynamicPaths_DataParsing,
        RQ_SRS_043_JSON_ReachingLimitDuringMerge,
        RQ_SRS_043_JSON_IntrospectionFunctions,
        RQ_SRS_043_JSON_ModifyColumn,
        RQ_SRS_043_JSON_Comparison,
    ),
    content=r"""
# SRS-043 JSON Data Type
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Declaring a Column of JSON Type](#declaring-a-column-of-json-type)
    * 2.1 [RQ.SRS-043.JSON.DeclareColumn](#rqsrs-043jsondeclarecolumn)
* 3 [Parameters](#parameters)
    * 3.1 [RQ.SRS-043.JSON.Parameters.max_dynamic_paths](#rqsrs-043jsonparametersmax_dynamic_paths)
    * 3.2 [RQ.SRS-043.JSON.Parameters.max_dynamic_types](#rqsrs-043jsonparametersmax_dynamic_types)
    * 3.3 [Hints](#hints)
        * 3.3.1 [RQ.SRS-043.JSON.Parameters.Hints.TypeHint](#rqsrs-043jsonparametershintstypehint)
        * 3.3.2 [RQ.SRS-043.JSON.Parameters.Hints.SkipHint](#rqsrs-043jsonparametershintsskiphint)
        * 3.3.3 [RQ.SRS-043.JSON.Parameters.Hints.SkipRegexpHint](#rqsrs-043jsonparametershintsskipregexphint)
* 4 [Casting to JSON Type ](#casting-to-json-type-)
    * 4.1 [RQ.SRS-043.JSON.Casting.CastFromString](#rqsrs-043jsoncastingcastfromstring)
    * 4.2 [RQ.SRS-043.JSON.Casting.CastFromTuple](#rqsrs-043jsoncastingcastfromtuple)
    * 4.3 [RQ.SRS-043.JSON.Casting.CastFromMap](#rqsrs-043jsoncastingcastfrommap)
    * 4.4 [RQ.SRS-043.JSON.Casting.CastFromObjectJson](#rqsrs-043jsoncastingcastfromobjectjson)
* 5 [Reading JSON paths as subcolumns](#reading-json-paths-as-subcolumns)
    * 5.1 [RQ.SRS-043.JSON.ReadingPaths](#rqsrs-043jsonreadingpaths)
    * 5.2 [Requested Path Does Not Exist](#requested-path-does-not-exist)
        * 5.2.1 [RQ.SRS-043.JSON.ReadingPaths.RequestedPathDoesNotExist](#rqsrs-043jsonreadingpathsrequestedpathdoesnotexist)
    * 5.3 [Data Types of Subcolumns](#data-types-of-subcolumns)
        * 5.3.1 [RQ.SRS-043.JSON.ReadingPaths.DataTypes](#rqsrs-043jsonreadingpathsdatatypes)
        * 5.3.2 [RQ.SRS-043.JSON.ReadingPaths.CastingDynamicSubcolumns](#rqsrs-043jsonreadingpathscastingdynamicsubcolumns)
* 6 [Reading JSON sub-objects as subcolumns](#reading-json-sub-objects-as-subcolumns)
    * 6.1 [RQ.SRS-043.JSON.ReadingSubObjects](#rqsrs-043jsonreadingsubobjects)
* 7 [Types inference for paths](#types-inference-for-paths)
    * 7.1 [RQ.SRS-043.JSON.TypesInference](#rqsrs-043jsontypesinference)
* 8 [Handling arrays of JSON objects](#handling-arrays-of-json-objects)
    * 8.1 [RQ.SRS-043.JSON.ArraysOfJsonObjects](#rqsrs-043jsonarraysofjsonobjects)
    * 8.2 [Special syntax for arrays of JSON objects](#special-syntax-for-arrays-of-json-objects)
        * 8.2.1 [RQ.SRS-043.JSON.ArraysOfJsonObjects.SpecialSyntax](#rqsrs-043jsonarraysofjsonobjectsspecialsyntax)
* 9 [Reading JSON type from the data](#reading-json-type-from-the-data)
    * 9.1 [RQ.SRS-043.JSON.ReadingJsonFromData](#rqsrs-043jsonreadingjsonfromdata)
* 10 [Reaching the limit of dynamic paths inside JSON](#reaching-the-limit-of-dynamic-paths-inside-json)
    * 10.1 [RQ.SRS-043.JSON.ReachingLimitOfDynamicPaths](#rqsrs-043jsonreachinglimitofdynamicpaths)
    * 10.2 [RQ.SRS-043.JSON.ReachingLimitOfDynamicPaths.ReadingPaths](#rqsrs-043jsonreachinglimitofdynamicpathsreadingpaths)
    * 10.3 [Reaching the limit during data parsing](#reaching-the-limit-during-data-parsing)
        * 10.3.1 [RQ.SRS-043.JSON.ReachingLimitOfDynamicPaths.DataParsing](#rqsrs-043jsonreachinglimitofdynamicpathsdataparsing)
    * 10.4 [During merges of data parts in MergeTree table engines](#during-merges-of-data-parts-in-mergetree-table-engines)
        * 10.4.1 [RQ.SRS-043.JSON.ReachingLimitDuringMerge](#rqsrs-043jsonreachinglimitduringmerge)
* 11 [Introspection functions](#introspection-functions)
    * 11.1 [RQ.SRS-043.JSON.IntrospectionFunctions](#rqsrs-043jsonintrospectionfunctions)
* 12 [ALTER MODIFY COLUMN to JSON type](#alter-modify-column-to-json-type)
    * 12.1 [RQ.SRS-043.JSON.ModifyColumn](#rqsrs-043jsonmodifycolumn)
* 13 [Comparison between values of the JSON type](#comparison-between-values-of-the-json-type)
    * 13.1 [RQ.SRS-043.JSON.Comparison](#rqsrs-043jsoncomparison)

## Introduction

This Software Requirements Specification (SRS) defines the requirements for JSON data type support in ClickHouse. This data type stores JavaScript Object Notation (JSON) documents in a single column.


## Declaring a Column of JSON Type

### RQ.SRS-043.JSON.DeclareColumn
version: 1.0  

[ClickHouse] SHALL support declaring a column of JSON type using the following syntax:

```sql
<column_name> JSON(max_dynamic_paths=N, max_dynamic_types=M, some.path TypeName, SKIP path.to.skip, SKIP REGEXP 'paths_regexp')
```

## Parameters

### RQ.SRS-043.JSON.Parameters.max_dynamic_paths
version: 1.0  

[ClickHouse] SHALL support optional `max_dynamic_paths` parameter in the JSON type declaration which indicates how many paths can be stored separately as subcolumns across a single block of data that is stored separately (for example, across a single data part for a MergeTree table). 
If this limit is exceeded, all other paths will be stored together in a single structure. The default value of `max_dynamic_paths` is 1024.

### RQ.SRS-043.JSON.Parameters.max_dynamic_types
version: 1.0  

[ClickHouse] SHALL support optional `max_dynamic_types` parameter in the JSON type declaration which indicates how many different data types can be stored inside a single path column with type Dynamic across a single block of data that is stored separately (for example, across a single data part for a MergeTree table). If this limit is exceeded, all new types will be converted to type String. The default value of `max_dynamic_types` is 32.

### Hints

#### RQ.SRS-043.JSON.Parameters.Hints.TypeHint
version: 1.0  

[ClickHouse] SHALL support optional type hint `some.path TypeName` for particular path in the JSON. Such paths will be always stored as subcolumns with specified type.

#### RQ.SRS-043.JSON.Parameters.Hints.SkipHint
version: 1.0  

[ClickHouse] SHALL support optional hint `SKIP path.to.skip` for particular path that should be skipped during JSON parsing. Such paths will never be stored in the JSON column.

#### RQ.SRS-043.JSON.Parameters.Hints.SkipRegexpHint
version: 1.0  

[ClickHouse] SHALL support optional hint `SKIP REGEXP 'path_regexp'` with a regular expression that is used to skip paths during JSON parsing. All paths that match this regular expression will never be stored in the JSON column.



Examples:

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

2. Create a table with a JSON column and with a **type hint** for a particular path and a **path to skip**:
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

### RQ.SRS-043.JSON.Casting.CastFromString
version: 1.0  

[ClickHouse] SHALL support casting from `String` to `JSON` type.

```sql
SELECT '{"a" : {"b" : 42},"c" : [1, 2, 3], "d" : "Hello, World!"}'::JSON AS json;
```
Result:  
```json
{"a":{"b":42},"c":[1,2,3],"d":"Hello, World!"}
```

### RQ.SRS-043.JSON.Casting.CastFromTuple
version: 1.0  

[ClickHouse] SHALL support casting from `Tuple` to `JSON` type.

```sql
SET enable_named_columns_in_function_tuple = 1;
SELECT (tuple(42 AS b) AS a, [1, 2, 3] AS c, 'Hello, World!' AS d)::JSON AS json;
```
Result:  
```json
{"a":{"b":42},"c":[1,2,3],"d":"Hello, World!"}
```

### RQ.SRS-043.JSON.Casting.CastFromMap
version: 1.0  

[ClickHouse] SHALL support casting from `Map` to `JSON` type.

```sql
SET use_variant_as_common_type = 1, enable_variant_type = 1;
SELECT map('a', map('b', 42), 'c', [1,2,3], 'd', 'Hello, World!')::JSON AS json;
```
Result:
```json
{"a":{"b":42},"c":[1,2,3],"d":"Hello, World!"}
```

### RQ.SRS-043.JSON.Casting.CastFromObjectJson
version: 1.0  

[ClickHouse] SHALL support casting from (deprecated) `Object('json')` to `JSON` type.

```sql
SELECT '{"a" : {"b" : 42},"c" : [1, 2, 3], "d" : "Hello, World!"}'::Object('json')::JSON AS json;
```
Result:
```json
{"a":{"b":42},"c":[1,2,3],"d":"Hello, World!"}
```


## Reading JSON paths as subcolumns

### RQ.SRS-043.JSON.ReadingPaths
version: 1.0  

[ClickHouse] SHALL support reading JSON paths as separate subcolumns using syntax `json.some.path`.

**Example:**  

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

#### RQ.SRS-043.JSON.ReadingPaths.RequestedPathDoesNotExist
version: 1.0  

[ClickHouse] SHALL fill the subcolumn with NULL values if the requested path was not found in the data.

**Example:**  

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

#### RQ.SRS-043.JSON.ReadingPaths.DataTypes
version: 1.0  

[ClickHouse] SHALL determine the data type of the subcolumn based on the JSON type declaration. If the type of the requested path was not specified in the JSON type declaration, the subcolumn of the path will always have type `Dynamic`.

**Example:**  

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


#### RQ.SRS-043.JSON.ReadingPaths.CastingDynamicSubcolumns
version: 1.0  

[ClickHouse] SHALL support casting Dynamic subcolumns to other types using special syntax json.some.path.:TypeName. If the internal type of the subcolumn cannot be cast to the requested type, an exception will be thrown.

Examples:  

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

## Reading JSON sub-objects as subcolumns

### RQ.SRS-043.JSON.ReadingSubObjects
version: 1.0  

[ClickHouse] SHALL support reading nested objects as subcolumns with type `JSON` using special syntax `json.^some.path`.

**Example:**  

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

Note: Reading sub-objects as subcolumns may be inefficient, as this may require almost full scan of the JSON data.

## Types inference for paths

### RQ.SRS-043.JSON.TypesInference
version: 1.0  

[ClickHouse] SHALL support inferring the types of JSON paths during JSON parsing. ClickHouse tries to detect the most appropriate data type for each JSON path.

Examples:

```sql
SELECT JSONAllPathsWithTypes('{"a" : "2020-01-01", "b" : "2020-01-01 10:00:00"}'::JSON) AS paths_with_types settings input_format_try_infer_dates=1, input_format_try_infer_datetimes=1;
```
k
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

## Handling arrays of JSON objects

### RQ.SRS-043.JSON.ArraysOfJsonObjects
version: 1.0  

[ClickHouse] SHALL support parsing arrays of JSON objects as type `Array(JSON)` and inserting them into a Dynamic column for this path. To read an array of objects, it SHALL be possible to extract it from the Dynamic column as a subcolumn.

**Example:**

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


The max_dynamic_types/max_dynamic_paths parameters of the nested JSON type were reduced compared to the default values. It's needed to avoid number of subcolumns to grow uncontrolled on nested arrays of JSON objects.

Reading subcolumns from this nested JSON column:

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

### Special syntax for arrays of JSON objects

#### RQ.SRS-043.JSON.ArraysOfJsonObjects.SpecialSyntax
version: 1.0  

[ClickHouse] SHALL support special syntax for reading subcolumns from arrays of JSON objects. The number of [] after the path indicates the array level. For example `json.path[][]` SHALL be transformed to `json.path.:Array(Array(JSON))`.

**Example:**  

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



Checking the paths and types inside our Array(JSON):

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

Reading subcolumns from Array(JSON) column:

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

Reading sub-object subcolumns from nested JSON column:

```sql
SELECT json.a.b[].^k FROM test
```

```
['{"j":"1000"}','{}','{"j":"2000"}']
[]
['{}','{"j":"3000"}']
```

## Reading JSON type from the data

### RQ.SRS-043.JSON.ReadingJsonFromData
version: 1.0  

[ClickHouse] SHALL support reading JSON type from the data using the `format` function.

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

## Reaching the limit of dynamic paths inside JSON

JSON data type can store only limited number of paths as separate subcolumns inside. By default, this limit is 1024, but you can change it in type declaration using parameter max_dynamic_paths. When the limit is reached, all new paths inserted to JSON column will be stored in a single shared data structure. It's still possible to read such paths as subcolumns, but it will require reading the whole shared data structure to extract the values of this path. This limit is needed to avoid the enormous number of different subcolumns that can make the table unusable.

### RQ.SRS-043.JSON.ReachingLimitOfDynamicPaths
version: 1.0  

[ClickHouse] SHALL support limiting the number of dynamic paths that can be stored inside a JSON column. When the limit is reached, all new paths SHALL be stored in a shared data structure. 

### RQ.SRS-043.JSON.ReachingLimitOfDynamicPaths.ReadingPaths

[ClickHouse] SHALL support reading paths from the shared data structure as subcolumns.


### Reaching the limit during data parsing

#### RQ.SRS-043.JSON.ReachingLimitOfDynamicPaths.DataParsing
version: 1.0  

During parsing of JSON object from the data, when the limit is reached for current block of data, [Clickhouse] SHALL store all new paths in a shared data structure.

**Example:**  
We can check it using introspection functions JSONDynamicPaths, JSONSharedDataPaths:

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

After inserting paths e and f.g the limit was reached and we inserted them into shared data structure.


### During merges of data parts in MergeTree table engines

During the merge of multiple data parts in a MergeTree table, the JSON column in the resulting data part may reach the limit of dynamic paths, preventing it from storing all paths from the source parts as subcolumns. In such cases, ClickHouse decides which paths will remain as subcolumns after the merge and which will be stored in the shared data structure. Generally, ClickHouse prioritizes keeping paths with the highest number of non-null values and moves the rarest paths to the shared data structure, but the exact behavior depends on the implementation.

#### RQ.SRS-043.JSON.ReachingLimitDuringMerge
version: 1.0  

If the limit of dynamic paths is reached during the merge of data parts in a MergeTree table, [ClickHouse] SHALL decide which paths will remain as subcolumns after the merge and which will be stored in the shared data structure and prioritize paths with the highest number of non-null values.

**Example:**  

Setting the limit of dynamic paths to 3 and insert values with 5 different paths:

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

## Introspection functions

### RQ.SRS-043.JSON.IntrospectionFunctions
version: 1.0  

[ClickHouse] SHALL support the following introspection functions for inspecting the content of the JSON column:

- JSONAllPaths
- JSONAllPathsWithTypes
- JSONDynamicPaths
- JSONDynamicPathsWithTypes
- JSONSharedDataPaths
- JSONSharedDataPathsWithTypes
- distinctDynamicTypes
- distinctJSONPaths
- distinctJSONPathsAndTypes


## ALTER MODIFY COLUMN to JSON type

It's possible to alter an existing table and change the type of the column to the new `JSON` type. Right now only alter from `String` type is supported.

### RQ.SRS-043.JSON.ModifyColumn
version: 1.0  

[ClickHouse] SHALL support changing the type of the column to the `JSON` type using the `ALTER TABLE ... MODIFY COLUMN ... JSON` syntax.


**Example:**
```sql
CREATE TABLE test (json String) ENGINE=MergeTree ORDeR BY tuple();
INSERT INTO test VALUES ('{"a" : 42}'), ('{"a" : 43, "b" : "Hello"}'), ('{"a" : 44, "b" : [1, 2, 3]}'), ('{"c" : "2020-01-01"}');
ALTER TABLE test MODIFY COLUMN json JSON;
SELECT json, json.a, json.b, json.c FROM test;
```

```
┌─json─────────────────────────┬─json.a─┬─json.b──┬─json.c─────┐
│ {"a":"42"}                   │ 42     │ ᴺᵁᴸᴸ    │ ᴺᵁᴸᴸ       │
│ {"a":"43","b":"Hello"}       │ 43     │ Hello   │ ᴺᵁᴸᴸ       │
│ {"a":"44","b":["1","2","3"]} │ 44     │ [1,2,3] │ ᴺᵁᴸᴸ       │
│ {"c":"2020-01-01"}           │ ᴺᵁᴸᴸ   │ ᴺᵁᴸᴸ    │ 2020-01-01 │
└──────────────────────────────┴────────┴─────────┴────────────┘
```

## Comparison between values of the JSON type

Values of the `JSON` column cannot be compared by `less/greater` functions, but can be compared using `equal` function. Two JSON objects considered equal when they have the same set of paths and value of each path have the same type and value in both objects.

### RQ.SRS-043.JSON.Comparison
version: 1.0  

[ClickHouse] SHALL support comparing values of the `JSON` type using the `==` operator. Two JSON objects SHALL be considered equal when they have the same set of paths and the value of each path has the same type and value in both objects.

**Example:**
```sql
CREATE TABLE test (json1 JSON(a UInt32), json2 JSON(a UInt32)) ENGINE=Memory;
INSERT INTO test FORMAT JSONEachRow
{"json1" : {"a" : 42, "b" : 42, "c" : "Hello"}, "json2" : {"a" : 42, "b" : 42, "c" : "Hello"}}
{"json1" : {"a" : 42, "b" : 42, "c" : "Hello"}, "json2" : {"a" : 43, "b" : 42, "c" : "Hello"}}
{"json1" : {"a" : 42, "b" : 42, "c" : "Hello"}, "json2" : {"a" : 43, "b" : 42, "c" : "Hello"}}
{"json1" : {"a" : 42, "b" : 42, "c" : "Hello"}, "json2" : {"a" : 42, "b" : 42, "c" : "World"}}
{"json1" : {"a" : 42, "b" : [1, 2, 3], "c" : "Hello"}, "json2" : {"a" : 42, "b" : 42, "c" : "Hello"}}
{"json1" : {"a" : 42, "b" : 42.0, "c" : "Hello"}, "json2" : {"a" : 42, "b" : 42, "c" : "Hello"}}
{"json1" : {"a" : 42, "b" : "42", "c" : "Hello"}, "json2" : {"a" : 42, "b" : 42, "c" : "Hello"}};

SELECT json1, json2, json1 == json2 FROM test;
```

```
┌─json1──────────────────────────────────┬─json2─────────────────────────┬─equals(json1, json2)─┐
│ {"a":42,"b":"42","c":"Hello"}          │ {"a":42,"b":"42","c":"Hello"} │                    1 │
│ {"a":42,"b":"42","c":"Hello"}          │ {"a":43,"b":"42","c":"Hello"} │                    0 │
│ {"a":42,"b":"42","c":"Hello"}          │ {"a":43,"b":"42","c":"Hello"} │                    0 │
│ {"a":42,"b":"42","c":"Hello"}          │ {"a":42,"b":"42","c":"World"} │                    0 │
│ {"a":42,"b":["1","2","3"],"c":"Hello"} │ {"a":42,"b":"42","c":"Hello"} │                    0 │
│ {"a":42,"b":42,"c":"Hello"}            │ {"a":42,"b":"42","c":"Hello"} │                    0 │
│ {"a":42,"b":"42","c":"Hello"}          │ {"a":42,"b":"42","c":"Hello"} │                    0 │
└────────────────────────────────────────┴───────────────────────────────┴──────────────────────┘
```


[ClickHouse]: https://clickhouse.com
""",
)
