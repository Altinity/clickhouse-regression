# Possible Key Column Conversions for Different Parquet File Structures

The following table lists the possible key column conversions for different parquet file structures.

For example,


| Physical Type | Logical Type | Schema Type | File Structure         | Key Column Conversion |
|---------------|--------------|-------------|------------------------|-----------------------|
| BINARY        | UTF8         | optional    | utf8\tNullable(String) | String                |

This line indicates that a Parquet file with a physical type of `BINARY`, a logical type of `UTF8`, and a schema type of 
`optional` was read using ClickHouse. When processed, the structure was interpreted as `utf8\tNullable(String)`, and the key column was converted to `String`.

The `Key Column Conversion` here means that we ran the query as follows:

```sql
SELECT utf8_column FROM file(file.parquet, Parquet, 'utf8_column String')
```

The key column type being 'String'.

## Table

If the combination of `physical type`, `logical type`, and `file structure` is listed in the table, it means that the key column conversion was possible.

You can read more about hte meaning of schema types in [the parquetify wiki](https://github.com/Altinity/parquet-regression/wiki/Schema-Types).

| Physical Type | Logical Type        | Schema Type   | File Structure                                                  | Key Column Conversion           |
|---------------|---------------------|---------------|-----------------------------------------------------------------|---------------------------------|
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | String                          |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | GEOMETRY                        |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | NATIONAL_CHAR_VARYING           |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | BINARY_VARYING                  |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | NCHAR_LARGE_OBJECT              |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | NATIONAL_CHARACTER_VARYING      |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | NATIONAL_CHARACTER              |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | NATIONAL_CHAR                   |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | CHARACTER_VARYING               |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | LONGBLOB                        |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | TINYBLOB                        |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | CLOB                            |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | BLOB                            |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | MEDIUMTEXT                      |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | TEXT                            |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | VARCHAR2                        |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | CHARACTER_LARGE_OBJECT          |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | LONGTEXT                        |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | NVARCHAR                        |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | VARCHAR                         |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | CHAR_VARYING                    |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | MEDIUMBLOB                      |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | NCHAR                           |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | VARBINARY                       |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | CHAR                            |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | TINYTEXT                        |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | BYTEA                           |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | CHARACTER                       |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | CHAR_LARGE_OBJECT               |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | NCHAR_VARYING                   |
| BINARY        | UTF8                | optional      | utf8\tNullable(String)                                          | BINARY_LARGE_OBJECT             |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | String                          |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | GEOMETRY                        |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | NATIONAL_CHAR_VARYING           |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | BINARY_VARYING                  |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | NCHAR_LARGE_OBJECT              |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | NATIONAL_CHARACTER_VARYING      |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | NATIONAL_CHARACTER              |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | NATIONAL_CHAR                   |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | CHARACTER_VARYING               |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | LONGBLOB                        |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | TINYBLOB                        |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | CLOB                            |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | BLOB                            |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | MEDIUMTEXT                      |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | TEXT                            |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | VARCHAR2                        |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | CHARACTER_LARGE_OBJECT          |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | LONGTEXT                        |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | NVARCHAR                        |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | VARCHAR                         |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | CHAR_VARYING                    |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | MEDIUMBLOB                      |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | NCHAR                           |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | VARBINARY                       |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | CHAR                            |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | TINYTEXT                        |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | BYTEA                           |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | CHARACTER                       |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | CHAR_LARGE_OBJECT               |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | NCHAR_VARYING                   |
| BINARY        | UTF8                | required      | utf8\tNullable(String)                                          | BINARY_LARGE_OBJECT             |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | String                          |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | GEOMETRY                        |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | NATIONAL_CHAR_VARYING           |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | BINARY_VARYING                  |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | NCHAR_LARGE_OBJECT              |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | NATIONAL_CHARACTER_VARYING      |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | NATIONAL_CHARACTER              |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | NATIONAL_CHAR                   |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | CHARACTER_VARYING               |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | LONGBLOB                        |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | TINYBLOB                        |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | CLOB                            |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | BLOB                            |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | MEDIUMTEXT                      |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | TEXT                            |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | VARCHAR2                        |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | CHARACTER_LARGE_OBJECT          |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | LONGTEXT                        |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | NVARCHAR                        |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | VARCHAR                         |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | CHAR_VARYING                    |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | MEDIUMBLOB                      |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | NCHAR                           |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | VARBINARY                       |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | CHAR                            |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | TINYTEXT                        |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | BYTEA                           |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | CHARACTER                       |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | CHAR_LARGE_OBJECT               |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | NCHAR_VARYING                   |
| BINARY        | UTF8                | repeated      | utf8\tArray(Nullable(String))                                   | BINARY_LARGE_OBJECT             |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | String                          |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | GEOMETRY                        |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NATIONAL_CHAR_VARYING           |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | BINARY_VARYING                  |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NCHAR_LARGE_OBJECT              |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NATIONAL_CHARACTER_VARYING      |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NATIONAL_CHARACTER              |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NATIONAL_CHAR                   |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CHARACTER_VARYING               |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | LONGBLOB                        |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | TINYBLOB                        |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CLOB                            |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | BLOB                            |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | MEDIUMTEXT                      |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | TEXT                            |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | VARCHAR2                        |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CHARACTER_LARGE_OBJECT          |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | LONGTEXT                        |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NVARCHAR                        |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | VARCHAR                         |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CHAR_VARYING                    |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | MEDIUMBLOB                      |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NCHAR                           |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | VARBINARY                       |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CHAR                            |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | TINYTEXT                        |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | BYTEA                           |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CHARACTER                       |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CHAR_LARGE_OBJECT               |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NCHAR_VARYING                   |
| BINARY        | UTF8                | optionalGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | BINARY_LARGE_OBJECT             |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | String                          |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | GEOMETRY                        |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NATIONAL_CHAR_VARYING           |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | BINARY_VARYING                  |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NCHAR_LARGE_OBJECT              |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NATIONAL_CHARACTER_VARYING      |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NATIONAL_CHARACTER              |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NATIONAL_CHAR                   |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CHARACTER_VARYING               |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | LONGBLOB                        |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | TINYBLOB                        |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CLOB                            |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | BLOB                            |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | MEDIUMTEXT                      |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | TEXT                            |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | VARCHAR2                        |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CHARACTER_LARGE_OBJECT          |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | LONGTEXT                        |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NVARCHAR                        |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | VARCHAR                         |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CHAR_VARYING                    |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | MEDIUMBLOB                      |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NCHAR                           |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | VARBINARY                       |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CHAR                            |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | TINYTEXT                        |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | BYTEA                           |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CHARACTER                       |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | CHAR_LARGE_OBJECT               |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | NCHAR_VARYING                   |
| BINARY        | UTF8                | requiredGroup | utf8\tTuple(\\n    utf8 Array(Nullable(String)))                | BINARY_LARGE_OBJECT             |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | String                          |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | GEOMETRY                        |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | NATIONAL_CHAR_VARYING           |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | BINARY_VARYING                  |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | NCHAR_LARGE_OBJECT              |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | NATIONAL_CHARACTER_VARYING      |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | NATIONAL_CHARACTER              |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | NATIONAL_CHAR                   |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | CHARACTER_VARYING               |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | LONGBLOB                        |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | TINYBLOB                        |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | CLOB                            |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | BLOB                            |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | MEDIUMTEXT                      |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | TEXT                            |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | VARCHAR2                        |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | CHARACTER_LARGE_OBJECT          |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | LONGTEXT                        |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | NVARCHAR                        |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | VARCHAR                         |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | CHAR_VARYING                    |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | MEDIUMBLOB                      |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | NCHAR                           |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | VARBINARY                       |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | CHAR                            |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | TINYTEXT                        |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | BYTEA                           |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | CHARACTER                       |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | CHAR_LARGE_OBJECT               |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | NCHAR_VARYING                   |
| BINARY        | UTF8                | repeatedGroup | utf8\tArray(Tuple(\\n    utf8 Array(Nullable(String))))         | BINARY_LARGE_OBJECT             |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Int64                           |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Int16                           |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UInt256                         |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | String                          |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Int32                           |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UInt8                           |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UInt128                         |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Float64                         |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UInt16                          |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Int128                          |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Int8                            |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Decimal                         |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Int256                          |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UInt64                          |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UInt32                          |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Float32                         |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | GEOMETRY                        |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHAR_VARYING           |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BINARY_VARYING                  |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NCHAR_LARGE_OBJECT              |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHARACTER_VARYING      |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHARACTER              |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHAR                   |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CHARACTER_VARYING               |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | LONGBLOB                        |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TINYBLOB                        |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CLOB                            |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BLOB                            |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | MEDIUMTEXT                      |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TEXT                            |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | VARCHAR2                        |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CHARACTER_LARGE_OBJECT          |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | DOUBLE_PRECISION                |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | LONGTEXT                        |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NVARCHAR                        |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INT1_UNSIGNED                   |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | VARCHAR                         |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CHAR_VARYING                    |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | MEDIUMBLOB                      |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NCHAR                           |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | VARBINARY                       |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CHAR                            |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | SMALLINT_UNSIGNED               |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | FIXED                           |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TINYTEXT                        |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NUMERIC                         |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | DEC                             |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | DOUBLE                          |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BYTEA                           |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INT                             |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | SINGLE                          |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BIT                             |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BIGINT_UNSIGNED                 |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UNSIGNED                        |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TINYINT_UNSIGNED                |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INTEGER_UNSIGNED                |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INT_UNSIGNED                    |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | REAL                            |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CHARACTER                       |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BYTE                            |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | SIGNED                          |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | MEDIUMINT                       |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | YEAR                            |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CHAR_LARGE_OBJECT               |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TINYINT                         |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BIGINT                          |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | SMALLINT                        |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INTEGER_SIGNED                  |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NCHAR_VARYING                   |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INT_SIGNED                      |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BIGINT_SIGNED                   |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BINARY_LARGE_OBJECT             |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | SMALLINT_SIGNED                 |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | FLOAT                           |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | SET                             |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TIME                            |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | MEDIUMINT_SIGNED                |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INT1_SIGNED                     |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INTEGER                         |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | MEDIUMINT_UNSIGNED              |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INT1                            |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TINYINT_SIGNED                  |
| INT32         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | DateTime64                      |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Int64                           |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Int16                           |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UInt256                         |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | String                          |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Int32                           |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UInt8                           |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UInt128                         |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Float64                         |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UInt16                          |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Int128                          |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Int8                            |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Decimal                         |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Int256                          |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | DateTime64                      |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UInt64                          |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UInt32                          |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | Float32                         |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | GEOMETRY                        |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHAR_VARYING           |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BINARY_VARYING                  |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NCHAR_LARGE_OBJECT              |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHARACTER_VARYING      |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHARACTER              |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHAR                   |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CHARACTER_VARYING               |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | LONGBLOB                        |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TINYBLOB                        |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CLOB                            |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BLOB                            |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | MEDIUMTEXT                      |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TEXT                            |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | VARCHAR2                        |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CHARACTER_LARGE_OBJECT          |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | DOUBLE_PRECISION                |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | LONGTEXT                        |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NVARCHAR                        |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INT1_UNSIGNED                   |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | VARCHAR                         |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CHAR_VARYING                    |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | MEDIUMBLOB                      |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NCHAR                           |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | VARBINARY                       |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CHAR                            |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | SMALLINT_UNSIGNED               |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | FIXED                           |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TINYTEXT                        |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NUMERIC                         |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | DEC                             |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | DOUBLE                          |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BYTEA                           |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INT                             |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | SINGLE                          |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BIT                             |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BIGINT_UNSIGNED                 |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | UNSIGNED                        |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TINYINT_UNSIGNED                |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INTEGER_UNSIGNED                |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INT_UNSIGNED                    |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | REAL                            |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CHARACTER                       |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BYTE                            |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | SIGNED                          |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | MEDIUMINT                       |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | YEAR                            |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | CHAR_LARGE_OBJECT               |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TINYINT                         |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BIGINT                          |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | SMALLINT                        |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INTEGER_SIGNED                  |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | NCHAR_VARYING                   |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INT_SIGNED                      |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BIGINT_SIGNED                   |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | BINARY_LARGE_OBJECT             |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | SMALLINT_SIGNED                 |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | FLOAT                           |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | SET                             |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TIME                            |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | MEDIUMINT_SIGNED                |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INT1_SIGNED                     |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INTEGER                         |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | MEDIUMINT_UNSIGNED              |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | INT1                            |
| INT64         | DECIMAL             | optional      | decimal\tNullable(Decimal(3                                     | TINYINT_SIGNED                  |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Int64                           |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Int16                           |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UInt256                         |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | String                          |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Int32                           |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UInt8                           |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UInt128                         |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Float64                         |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UInt16                          |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Int128                          |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Int8                            |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Decimal                         |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Int256                          |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UInt64                          |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UInt32                          |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Float32                         |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | GEOMETRY                        |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHAR_VARYING           |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BINARY_VARYING                  |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NCHAR_LARGE_OBJECT              |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHARACTER_VARYING      |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHARACTER              |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHAR                   |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CHARACTER_VARYING               |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | LONGBLOB                        |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TINYBLOB                        |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CLOB                            |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BLOB                            |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | MEDIUMTEXT                      |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TEXT                            |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | VARCHAR2                        |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CHARACTER_LARGE_OBJECT          |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | DOUBLE_PRECISION                |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | LONGTEXT                        |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NVARCHAR                        |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INT1_UNSIGNED                   |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | VARCHAR                         |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CHAR_VARYING                    |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | MEDIUMBLOB                      |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NCHAR                           |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | VARBINARY                       |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CHAR                            |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | SMALLINT_UNSIGNED               |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | FIXED                           |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TINYTEXT                        |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NUMERIC                         |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | DEC                             |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | DOUBLE                          |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BYTEA                           |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INT                             |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | SINGLE                          |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BIT                             |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BIGINT_UNSIGNED                 |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UNSIGNED                        |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TINYINT_UNSIGNED                |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INTEGER_UNSIGNED                |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INT_UNSIGNED                    |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | REAL                            |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CHARACTER                       |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BYTE                            |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | SIGNED                          |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | MEDIUMINT                       |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | YEAR                            |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CHAR_LARGE_OBJECT               |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TINYINT                         |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BIGINT                          |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | SMALLINT                        |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INTEGER_SIGNED                  |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NCHAR_VARYING                   |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INT_SIGNED                      |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BIGINT_SIGNED                   |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BINARY_LARGE_OBJECT             |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | SMALLINT_SIGNED                 |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | FLOAT                           |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | SET                             |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TIME                            |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | MEDIUMINT_SIGNED                |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INT1_SIGNED                     |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INTEGER                         |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | MEDIUMINT_UNSIGNED              |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INT1                            |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TINYINT_SIGNED                  |
| INT32         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | DateTime64                      |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Int64                           |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Int16                           |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UInt256                         |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | String                          |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Int32                           |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UInt8                           |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UInt128                         |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Float64                         |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UInt16                          |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Int128                          |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Int8                            |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Decimal                         |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Int256                          |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | DateTime64                      |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UInt64                          |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UInt32                          |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | Float32                         |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | GEOMETRY                        |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHAR_VARYING           |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BINARY_VARYING                  |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NCHAR_LARGE_OBJECT              |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHARACTER_VARYING      |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHARACTER              |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NATIONAL_CHAR                   |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CHARACTER_VARYING               |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | LONGBLOB                        |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TINYBLOB                        |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CLOB                            |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BLOB                            |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | MEDIUMTEXT                      |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TEXT                            |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | VARCHAR2                        |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CHARACTER_LARGE_OBJECT          |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | DOUBLE_PRECISION                |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | LONGTEXT                        |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NVARCHAR                        |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INT1_UNSIGNED                   |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | VARCHAR                         |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CHAR_VARYING                    |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | MEDIUMBLOB                      |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NCHAR                           |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | VARBINARY                       |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CHAR                            |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | SMALLINT_UNSIGNED               |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | FIXED                           |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TINYTEXT                        |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NUMERIC                         |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | DEC                             |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | DOUBLE                          |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BYTEA                           |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INT                             |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | SINGLE                          |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BIT                             |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BIGINT_UNSIGNED                 |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | UNSIGNED                        |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TINYINT_UNSIGNED                |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INTEGER_UNSIGNED                |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INT_UNSIGNED                    |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | REAL                            |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CHARACTER                       |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BYTE                            |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | SIGNED                          |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | MEDIUMINT                       |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | YEAR                            |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | CHAR_LARGE_OBJECT               |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TINYINT                         |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BIGINT                          |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | SMALLINT                        |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INTEGER_SIGNED                  |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | NCHAR_VARYING                   |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INT_SIGNED                      |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BIGINT_SIGNED                   |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | BINARY_LARGE_OBJECT             |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | SMALLINT_SIGNED                 |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | FLOAT                           |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | SET                             |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TIME                            |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | MEDIUMINT_SIGNED                |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INT1_SIGNED                     |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INTEGER                         |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | MEDIUMINT_UNSIGNED              |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | INT1                            |
| INT64         | DECIMAL             | required      | decimal\tNullable(Decimal(3                                     | TINYINT_SIGNED                  |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | String                          |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | UInt8                           |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | Int8                            |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | GEOMETRY                        |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NATIONAL_CHAR_VARYING           |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | BINARY_VARYING                  |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NCHAR_LARGE_OBJECT              |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NATIONAL_CHARACTER_VARYING      |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NATIONAL_CHARACTER              |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NATIONAL_CHAR                   |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CHARACTER_VARYING               |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | LONGBLOB                        |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | TINYBLOB                        |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CLOB                            |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | BLOB                            |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | MEDIUMTEXT                      |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | TEXT                            |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | VARCHAR2                        |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CHARACTER_LARGE_OBJECT          |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | LONGTEXT                        |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NVARCHAR                        |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | INT1_UNSIGNED                   |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | VARCHAR                         |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CHAR_VARYING                    |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | MEDIUMBLOB                      |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NCHAR                           |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | VARBINARY                       |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CHAR                            |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | TINYTEXT                        |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | BYTEA                           |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | TINYINT_UNSIGNED                |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CHARACTER                       |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | BYTE                            |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CHAR_LARGE_OBJECT               |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | TINYINT                         |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NCHAR_VARYING                   |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | BINARY_LARGE_OBJECT             |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | INT1_SIGNED                     |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | INT1                            |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | TINYINT_SIGNED                  |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | Int16                           |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | SMALLINT                        |
| INT32         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | SMALLINT_SIGNED                 |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | String                          |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | UInt8                           |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | Int8                            |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | GEOMETRY                        |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NATIONAL_CHAR_VARYING           |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | BINARY_VARYING                  |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NCHAR_LARGE_OBJECT              |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NATIONAL_CHARACTER_VARYING      |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NATIONAL_CHARACTER              |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NATIONAL_CHAR                   |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CHARACTER_VARYING               |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | LONGBLOB                        |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | TINYBLOB                        |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CLOB                            |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | BLOB                            |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | MEDIUMTEXT                      |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | TEXT                            |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | VARCHAR2                        |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CHARACTER_LARGE_OBJECT          |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | LONGTEXT                        |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NVARCHAR                        |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | INT1_UNSIGNED                   |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | VARCHAR                         |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CHAR_VARYING                    |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | MEDIUMBLOB                      |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NCHAR                           |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | VARBINARY                       |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CHAR                            |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | TINYTEXT                        |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | BYTEA                           |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | TINYINT_UNSIGNED                |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CHARACTER                       |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | BYTE                            |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | CHAR_LARGE_OBJECT               |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | TINYINT                         |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | NCHAR_VARYING                   |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | BINARY_LARGE_OBJECT             |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | INT1_SIGNED                     |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | INT1                            |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | TINYINT_SIGNED                  |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | Int16                           |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | SMALLINT                        |
| INT64         | DECIMAL             | repeated      | decimal\tArray(Nullable(Decimal(3                               | SMALLINT_SIGNED                 |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | Int16                           |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | String                          |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | UInt8                           |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | Int8                            |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | GEOMETRY                        |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NATIONAL_CHAR_VARYING           |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | BINARY_VARYING                  |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NCHAR_LARGE_OBJECT              |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NATIONAL_CHARACTER_VARYING      |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NATIONAL_CHARACTER              |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NATIONAL_CHAR                   |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CHARACTER_VARYING               |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | LONGBLOB                        |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | TINYBLOB                        |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CLOB                            |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | BLOB                            |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | MEDIUMTEXT                      |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | TEXT                            |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | VARCHAR2                        |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CHARACTER_LARGE_OBJECT          |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | LONGTEXT                        |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NVARCHAR                        |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | INT1_UNSIGNED                   |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | VARCHAR                         |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CHAR_VARYING                    |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | MEDIUMBLOB                      |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NCHAR                           |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | VARBINARY                       |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CHAR                            |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | TINYTEXT                        |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | BYTEA                           |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | TINYINT_UNSIGNED                |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CHARACTER                       |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | BYTE                            |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CHAR_LARGE_OBJECT               |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | TINYINT                         |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | SMALLINT                        |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NCHAR_VARYING                   |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | BINARY_LARGE_OBJECT             |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | SMALLINT_SIGNED                 |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | INT1_SIGNED                     |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | INT1                            |
| INT32         | DECIMAL             | optionalGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | TINYINT_SIGNED                  |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | String                          |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | UInt8                           |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | Int8                            |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | GEOMETRY                        |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NATIONAL_CHAR_VARYING           |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | BINARY_VARYING                  |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NCHAR_LARGE_OBJECT              |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NATIONAL_CHARACTER_VARYING      |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NATIONAL_CHARACTER              |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NATIONAL_CHAR                   |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CHARACTER_VARYING               |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | LONGBLOB                        |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | TINYBLOB                        |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CLOB                            |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | BLOB                            |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | MEDIUMTEXT                      |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | TEXT                            |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | VARCHAR2                        |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CHARACTER_LARGE_OBJECT          |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | LONGTEXT                        |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NVARCHAR                        |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | INT1_UNSIGNED                   |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | VARCHAR                         |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CHAR_VARYING                    |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | MEDIUMBLOB                      |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NCHAR                           |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | VARBINARY                       |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CHAR                            |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | TINYTEXT                        |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | BYTEA                           |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | TINYINT_UNSIGNED                |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CHARACTER                       |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | BYTE                            |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | CHAR_LARGE_OBJECT               |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | TINYINT                         |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | NCHAR_VARYING                   |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | BINARY_LARGE_OBJECT             |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | INT1_SIGNED                     |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | INT1                            |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | TINYINT_SIGNED                  |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | Int16                           |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | SMALLINT                        |
| INT32         | DECIMAL             | requiredGroup | decimal\tTuple(\\n    decimal Array(Nullable(Decimal(3          | SMALLINT_SIGNED                 |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | String                          |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | UInt8                           |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | Int8                            |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | GEOMETRY                        |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | NATIONAL_CHAR_VARYING           |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | BINARY_VARYING                  |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | NCHAR_LARGE_OBJECT              |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | NATIONAL_CHARACTER_VARYING      |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | NATIONAL_CHARACTER              |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | NATIONAL_CHAR                   |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | CHARACTER_VARYING               |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | LONGBLOB                        |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | TINYBLOB                        |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | CLOB                            |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | BLOB                            |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | MEDIUMTEXT                      |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | TEXT                            |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | VARCHAR2                        |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | CHARACTER_LARGE_OBJECT          |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | LONGTEXT                        |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | NVARCHAR                        |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | INT1_UNSIGNED                   |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | VARCHAR                         |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | CHAR_VARYING                    |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | MEDIUMBLOB                      |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | NCHAR                           |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | VARBINARY                       |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | CHAR                            |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | TINYTEXT                        |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | BYTEA                           |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | TINYINT_UNSIGNED                |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | CHARACTER                       |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | BYTE                            |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | CHAR_LARGE_OBJECT               |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | TINYINT                         |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | NCHAR_VARYING                   |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | BINARY_LARGE_OBJECT             |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | INT1_SIGNED                     |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | INT1                            |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | TINYINT_SIGNED                  |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | Int16                           |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | SMALLINT                        |
| INT32         | DECIMAL             | repeatedGroup | decimal\tArray(Tuple(\\n    decimal Array(Nullable(Decimal(3    | SMALLINT_SIGNED                 |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | String                          |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | GEOMETRY                        |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | NATIONAL_CHAR_VARYING           |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | BINARY_VARYING                  |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | NCHAR_LARGE_OBJECT              |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | NATIONAL_CHARACTER_VARYING      |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | NATIONAL_CHARACTER              |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | NATIONAL_CHAR                   |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | CHARACTER_VARYING               |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | LONGBLOB                        |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | TINYBLOB                        |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | CLOB                            |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | BLOB                            |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | MEDIUMTEXT                      |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | TEXT                            |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | VARCHAR2                        |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | CHARACTER_LARGE_OBJECT          |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | LONGTEXT                        |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | NVARCHAR                        |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | VARCHAR                         |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | CHAR_VARYING                    |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | MEDIUMBLOB                      |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | NCHAR                           |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | VARBINARY                       |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | CHAR                            |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | TINYTEXT                        |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | BYTEA                           |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | CHARACTER                       |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | CHAR_LARGE_OBJECT               |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | NCHAR_VARYING                   |
| BINARY        | ENUM                | optional      | enum\tNullable(String)                                          | BINARY_LARGE_OBJECT             |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | String                          |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | GEOMETRY                        |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | NATIONAL_CHAR_VARYING           |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | BINARY_VARYING                  |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | NCHAR_LARGE_OBJECT              |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | NATIONAL_CHARACTER_VARYING      |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | NATIONAL_CHARACTER              |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | NATIONAL_CHAR                   |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | CHARACTER_VARYING               |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | LONGBLOB                        |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | TINYBLOB                        |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | CLOB                            |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | BLOB                            |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | MEDIUMTEXT                      |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | TEXT                            |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | VARCHAR2                        |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | CHARACTER_LARGE_OBJECT          |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | LONGTEXT                        |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | NVARCHAR                        |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | VARCHAR                         |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | CHAR_VARYING                    |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | MEDIUMBLOB                      |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | NCHAR                           |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | VARBINARY                       |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | CHAR                            |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | TINYTEXT                        |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | BYTEA                           |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | CHARACTER                       |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | CHAR_LARGE_OBJECT               |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | NCHAR_VARYING                   |
| BINARY        | ENUM                | required      | enum\tNullable(String)                                          | BINARY_LARGE_OBJECT             |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | String                          |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | GEOMETRY                        |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | NATIONAL_CHAR_VARYING           |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | BINARY_VARYING                  |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | NCHAR_LARGE_OBJECT              |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | NATIONAL_CHARACTER_VARYING      |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | NATIONAL_CHARACTER              |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | NATIONAL_CHAR                   |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | CHARACTER_VARYING               |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | LONGBLOB                        |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | TINYBLOB                        |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | CLOB                            |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | BLOB                            |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | MEDIUMTEXT                      |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | TEXT                            |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | VARCHAR2                        |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | CHARACTER_LARGE_OBJECT          |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | LONGTEXT                        |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | NVARCHAR                        |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | VARCHAR                         |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | CHAR_VARYING                    |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | MEDIUMBLOB                      |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | NCHAR                           |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | VARBINARY                       |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | CHAR                            |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | TINYTEXT                        |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | BYTEA                           |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | CHARACTER                       |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | CHAR_LARGE_OBJECT               |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | NCHAR_VARYING                   |
| BINARY        | ENUM                | repeated      | enum\tArray(Nullable(String))                                   | BINARY_LARGE_OBJECT             |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | String                          |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | GEOMETRY                        |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NATIONAL_CHAR_VARYING           |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | BINARY_VARYING                  |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NCHAR_LARGE_OBJECT              |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NATIONAL_CHARACTER_VARYING      |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NATIONAL_CHARACTER              |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NATIONAL_CHAR                   |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CHARACTER_VARYING               |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | LONGBLOB                        |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | TINYBLOB                        |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CLOB                            |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | BLOB                            |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | MEDIUMTEXT                      |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | TEXT                            |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | VARCHAR2                        |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CHARACTER_LARGE_OBJECT          |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | LONGTEXT                        |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NVARCHAR                        |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | VARCHAR                         |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CHAR_VARYING                    |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | MEDIUMBLOB                      |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NCHAR                           |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | VARBINARY                       |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CHAR                            |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | TINYTEXT                        |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | BYTEA                           |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CHARACTER                       |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CHAR_LARGE_OBJECT               |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NCHAR_VARYING                   |
| BINARY        | ENUM                | optionalGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | BINARY_LARGE_OBJECT             |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | String                          |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | GEOMETRY                        |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NATIONAL_CHAR_VARYING           |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | BINARY_VARYING                  |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NCHAR_LARGE_OBJECT              |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NATIONAL_CHARACTER_VARYING      |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NATIONAL_CHARACTER              |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NATIONAL_CHAR                   |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CHARACTER_VARYING               |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | LONGBLOB                        |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | TINYBLOB                        |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CLOB                            |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | BLOB                            |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | MEDIUMTEXT                      |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | TEXT                            |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | VARCHAR2                        |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CHARACTER_LARGE_OBJECT          |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | LONGTEXT                        |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NVARCHAR                        |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | VARCHAR                         |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CHAR_VARYING                    |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | MEDIUMBLOB                      |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NCHAR                           |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | VARBINARY                       |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CHAR                            |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | TINYTEXT                        |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | BYTEA                           |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CHARACTER                       |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | CHAR_LARGE_OBJECT               |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | NCHAR_VARYING                   |
| BINARY        | ENUM                | requiredGroup | enum\tTuple(\\n    enum Array(Nullable(String)))                | BINARY_LARGE_OBJECT             |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | String                          |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | GEOMETRY                        |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | NATIONAL_CHAR_VARYING           |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | BINARY_VARYING                  |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | NCHAR_LARGE_OBJECT              |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | NATIONAL_CHARACTER_VARYING      |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | NATIONAL_CHARACTER              |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | NATIONAL_CHAR                   |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | CHARACTER_VARYING               |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | LONGBLOB                        |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | TINYBLOB                        |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | CLOB                            |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | BLOB                            |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | MEDIUMTEXT                      |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | TEXT                            |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | VARCHAR2                        |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | CHARACTER_LARGE_OBJECT          |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | LONGTEXT                        |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | NVARCHAR                        |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | VARCHAR                         |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | CHAR_VARYING                    |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | MEDIUMBLOB                      |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | NCHAR                           |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | VARBINARY                       |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | CHAR                            |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | TINYTEXT                        |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | BYTEA                           |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | CHARACTER                       |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | CHAR_LARGE_OBJECT               |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | NCHAR_VARYING                   |
| BINARY        | ENUM                | repeatedGroup | enum\tArray(Tuple(\\n    enum Array(Nullable(String))))         | BINARY_LARGE_OBJECT             |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | String                          |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | GEOMETRY                        |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | NATIONAL_CHAR_VARYING           |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | BINARY_VARYING                  |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | NCHAR_LARGE_OBJECT              |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | NATIONAL_CHARACTER_VARYING      |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | NATIONAL_CHARACTER              |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | NATIONAL_CHAR                   |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | CHARACTER_VARYING               |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | LONGBLOB                        |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | TINYBLOB                        |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | CLOB                            |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | BLOB                            |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | MEDIUMTEXT                      |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | TEXT                            |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | VARCHAR2                        |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | CHARACTER_LARGE_OBJECT          |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | LONGTEXT                        |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | NVARCHAR                        |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | VARCHAR                         |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | CHAR_VARYING                    |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | MEDIUMBLOB                      |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | NCHAR                           |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | VARBINARY                       |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | CHAR                            |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | TINYTEXT                        |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | BYTEA                           |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | CHARACTER                       |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | CHAR_LARGE_OBJECT               |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | NCHAR_VARYING                   |
| BINARY        | STRING              | optional      | string\tNullable(String)                                        | BINARY_LARGE_OBJECT             |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | String                          |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | GEOMETRY                        |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | NATIONAL_CHAR_VARYING           |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | BINARY_VARYING                  |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | NCHAR_LARGE_OBJECT              |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | NATIONAL_CHARACTER_VARYING      |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | NATIONAL_CHARACTER              |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | NATIONAL_CHAR                   |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | CHARACTER_VARYING               |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | LONGBLOB                        |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | TINYBLOB                        |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | CLOB                            |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | BLOB                            |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | MEDIUMTEXT                      |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | TEXT                            |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | VARCHAR2                        |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | CHARACTER_LARGE_OBJECT          |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | LONGTEXT                        |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | NVARCHAR                        |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | VARCHAR                         |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | CHAR_VARYING                    |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | MEDIUMBLOB                      |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | NCHAR                           |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | VARBINARY                       |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | CHAR                            |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | TINYTEXT                        |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | BYTEA                           |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | CHARACTER                       |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | CHAR_LARGE_OBJECT               |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | NCHAR_VARYING                   |
| BINARY        | STRING              | required      | string\tNullable(String)                                        | BINARY_LARGE_OBJECT             |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | String                          |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | GEOMETRY                        |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | NATIONAL_CHAR_VARYING           |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | BINARY_VARYING                  |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | NCHAR_LARGE_OBJECT              |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | NATIONAL_CHARACTER_VARYING      |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | NATIONAL_CHARACTER              |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | NATIONAL_CHAR                   |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | CHARACTER_VARYING               |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | LONGBLOB                        |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | TINYBLOB                        |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | CLOB                            |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | BLOB                            |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | MEDIUMTEXT                      |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | TEXT                            |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | VARCHAR2                        |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | CHARACTER_LARGE_OBJECT          |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | LONGTEXT                        |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | NVARCHAR                        |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | VARCHAR                         |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | CHAR_VARYING                    |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | MEDIUMBLOB                      |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | NCHAR                           |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | VARBINARY                       |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | CHAR                            |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | TINYTEXT                        |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | BYTEA                           |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | CHARACTER                       |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | CHAR_LARGE_OBJECT               |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | NCHAR_VARYING                   |
| BINARY        | STRING              | repeated      | string\tArray(Nullable(String))                                 | BINARY_LARGE_OBJECT             |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | String                          |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | GEOMETRY                        |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NATIONAL_CHAR_VARYING           |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | BINARY_VARYING                  |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NCHAR_LARGE_OBJECT              |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NATIONAL_CHARACTER_VARYING      |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NATIONAL_CHARACTER              |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NATIONAL_CHAR                   |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CHARACTER_VARYING               |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | LONGBLOB                        |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | TINYBLOB                        |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CLOB                            |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | BLOB                            |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | MEDIUMTEXT                      |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | TEXT                            |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | VARCHAR2                        |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CHARACTER_LARGE_OBJECT          |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | LONGTEXT                        |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NVARCHAR                        |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | VARCHAR                         |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CHAR_VARYING                    |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | MEDIUMBLOB                      |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NCHAR                           |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | VARBINARY                       |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CHAR                            |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | TINYTEXT                        |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | BYTEA                           |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CHARACTER                       |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CHAR_LARGE_OBJECT               |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NCHAR_VARYING                   |
| BINARY        | STRING              | optionalGroup | string\tTuple(\\n    string Array(Nullable(String)))            | BINARY_LARGE_OBJECT             |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | String                          |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | GEOMETRY                        |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NATIONAL_CHAR_VARYING           |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | BINARY_VARYING                  |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NCHAR_LARGE_OBJECT              |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NATIONAL_CHARACTER_VARYING      |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NATIONAL_CHARACTER              |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NATIONAL_CHAR                   |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CHARACTER_VARYING               |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | LONGBLOB                        |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | TINYBLOB                        |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CLOB                            |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | BLOB                            |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | MEDIUMTEXT                      |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | TEXT                            |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | VARCHAR2                        |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CHARACTER_LARGE_OBJECT          |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | LONGTEXT                        |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NVARCHAR                        |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | VARCHAR                         |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CHAR_VARYING                    |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | MEDIUMBLOB                      |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NCHAR                           |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | VARBINARY                       |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CHAR                            |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | TINYTEXT                        |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | BYTEA                           |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CHARACTER                       |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | CHAR_LARGE_OBJECT               |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | NCHAR_VARYING                   |
| BINARY        | STRING              | requiredGroup | string\tTuple(\\n    string Array(Nullable(String)))            | BINARY_LARGE_OBJECT             |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | String                          |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | GEOMETRY                        |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | NATIONAL_CHAR_VARYING           |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | BINARY_VARYING                  |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | NCHAR_LARGE_OBJECT              |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | NATIONAL_CHARACTER_VARYING      |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | NATIONAL_CHARACTER              |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | NATIONAL_CHAR                   |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | CHARACTER_VARYING               |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | LONGBLOB                        |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | TINYBLOB                        |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | CLOB                            |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | BLOB                            |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | MEDIUMTEXT                      |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | TEXT                            |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | VARCHAR2                        |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | CHARACTER_LARGE_OBJECT          |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | LONGTEXT                        |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | NVARCHAR                        |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | VARCHAR                         |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | CHAR_VARYING                    |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | MEDIUMBLOB                      |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | NCHAR                           |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | VARBINARY                       |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | CHAR                            |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | TINYTEXT                        |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | BYTEA                           |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | CHARACTER                       |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | CHAR_LARGE_OBJECT               |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | NCHAR_VARYING                   |
| BINARY        | STRING              | repeatedGroup | string\tArray(Tuple(\\n    string Array(Nullable(String))))     | BINARY_LARGE_OBJECT             |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | String                          |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | GEOMETRY                        |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | NATIONAL_CHAR_VARYING           |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | BINARY_VARYING                  |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | NCHAR_LARGE_OBJECT              |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | NATIONAL_CHARACTER_VARYING      |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | NATIONAL_CHARACTER              |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | NATIONAL_CHAR                   |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | CHARACTER_VARYING               |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | LONGBLOB                        |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | TINYBLOB                        |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | CLOB                            |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | BLOB                            |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | MEDIUMTEXT                      |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | TEXT                            |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | VARCHAR2                        |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | CHARACTER_LARGE_OBJECT          |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | LONGTEXT                        |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | NVARCHAR                        |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | VARCHAR                         |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | CHAR_VARYING                    |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | MEDIUMBLOB                      |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | NCHAR                           |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | VARBINARY                       |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | CHAR                            |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | TINYTEXT                        |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | BYTEA                           |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | CHARACTER                       |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | CHAR_LARGE_OBJECT               |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | NCHAR_VARYING                   |
| BINARY        | JSON                | optional      | json\tNullable(String)                                          | BINARY_LARGE_OBJECT             |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | String                          |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | GEOMETRY                        |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | NATIONAL_CHAR_VARYING           |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | BINARY_VARYING                  |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | NCHAR_LARGE_OBJECT              |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | NATIONAL_CHARACTER_VARYING      |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | NATIONAL_CHARACTER              |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | NATIONAL_CHAR                   |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | CHARACTER_VARYING               |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | LONGBLOB                        |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | TINYBLOB                        |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | CLOB                            |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | BLOB                            |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | MEDIUMTEXT                      |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | TEXT                            |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | VARCHAR2                        |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | CHARACTER_LARGE_OBJECT          |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | LONGTEXT                        |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | NVARCHAR                        |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | VARCHAR                         |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | CHAR_VARYING                    |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | MEDIUMBLOB                      |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | NCHAR                           |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | VARBINARY                       |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | CHAR                            |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | TINYTEXT                        |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | BYTEA                           |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | CHARACTER                       |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | CHAR_LARGE_OBJECT               |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | NCHAR_VARYING                   |
| BINARY        | JSON                | required      | json\tNullable(String)                                          | BINARY_LARGE_OBJECT             |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | String                          |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | GEOMETRY                        |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | NATIONAL_CHAR_VARYING           |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | BINARY_VARYING                  |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | NCHAR_LARGE_OBJECT              |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | NATIONAL_CHARACTER_VARYING      |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | NATIONAL_CHARACTER              |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | NATIONAL_CHAR                   |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | CHARACTER_VARYING               |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | LONGBLOB                        |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | TINYBLOB                        |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | CLOB                            |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | BLOB                            |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | MEDIUMTEXT                      |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | TEXT                            |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | VARCHAR2                        |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | CHARACTER_LARGE_OBJECT          |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | LONGTEXT                        |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | NVARCHAR                        |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | VARCHAR                         |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | CHAR_VARYING                    |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | MEDIUMBLOB                      |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | NCHAR                           |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | VARBINARY                       |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | CHAR                            |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | TINYTEXT                        |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | BYTEA                           |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | CHARACTER                       |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | CHAR_LARGE_OBJECT               |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | NCHAR_VARYING                   |
| BINARY        | JSON                | repeated      | json\tArray(Nullable(String))                                   | BINARY_LARGE_OBJECT             |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | String                          |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | GEOMETRY                        |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NATIONAL_CHAR_VARYING           |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | BINARY_VARYING                  |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NCHAR_LARGE_OBJECT              |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NATIONAL_CHARACTER_VARYING      |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NATIONAL_CHARACTER              |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NATIONAL_CHAR                   |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CHARACTER_VARYING               |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | LONGBLOB                        |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | TINYBLOB                        |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CLOB                            |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | BLOB                            |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | MEDIUMTEXT                      |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | TEXT                            |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | VARCHAR2                        |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CHARACTER_LARGE_OBJECT          |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | LONGTEXT                        |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NVARCHAR                        |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | VARCHAR                         |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CHAR_VARYING                    |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | MEDIUMBLOB                      |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NCHAR                           |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | VARBINARY                       |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CHAR                            |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | TINYTEXT                        |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | BYTEA                           |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CHARACTER                       |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CHAR_LARGE_OBJECT               |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NCHAR_VARYING                   |
| BINARY        | JSON                | optionalGroup | json\tTuple(\\n    json Array(Nullable(String)))                | BINARY_LARGE_OBJECT             |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | String                          |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | GEOMETRY                        |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NATIONAL_CHAR_VARYING           |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | BINARY_VARYING                  |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NCHAR_LARGE_OBJECT              |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NATIONAL_CHARACTER_VARYING      |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NATIONAL_CHARACTER              |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NATIONAL_CHAR                   |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CHARACTER_VARYING               |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | LONGBLOB                        |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | TINYBLOB                        |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CLOB                            |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | BLOB                            |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | MEDIUMTEXT                      |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | TEXT                            |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | VARCHAR2                        |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CHARACTER_LARGE_OBJECT          |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | LONGTEXT                        |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NVARCHAR                        |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | VARCHAR                         |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CHAR_VARYING                    |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | MEDIUMBLOB                      |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NCHAR                           |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | VARBINARY                       |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CHAR                            |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | TINYTEXT                        |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | BYTEA                           |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CHARACTER                       |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | CHAR_LARGE_OBJECT               |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | NCHAR_VARYING                   |
| BINARY        | JSON                | requiredGroup | json\tTuple(\\n    json Array(Nullable(String)))                | BINARY_LARGE_OBJECT             |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | String                          |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | GEOMETRY                        |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | NATIONAL_CHAR_VARYING           |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | BINARY_VARYING                  |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | NCHAR_LARGE_OBJECT              |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | NATIONAL_CHARACTER_VARYING      |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | NATIONAL_CHARACTER              |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | NATIONAL_CHAR                   |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | CHARACTER_VARYING               |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | LONGBLOB                        |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | TINYBLOB                        |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | CLOB                            |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | BLOB                            |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | MEDIUMTEXT                      |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | TEXT                            |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | VARCHAR2                        |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | CHARACTER_LARGE_OBJECT          |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | LONGTEXT                        |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | NVARCHAR                        |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | VARCHAR                         |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | CHAR_VARYING                    |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | MEDIUMBLOB                      |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | NCHAR                           |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | VARBINARY                       |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | CHAR                            |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | TINYTEXT                        |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | BYTEA                           |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | CHARACTER                       |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | CHAR_LARGE_OBJECT               |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | NCHAR_VARYING                   |
| BINARY        | JSON                | repeatedGroup | json\tArray(Tuple(\\n    json Array(Nullable(String))))         | BINARY_LARGE_OBJECT             |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | String                          |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | GEOMETRY                        |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | NATIONAL_CHAR_VARYING           |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | BINARY_VARYING                  |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | NCHAR_LARGE_OBJECT              |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | NATIONAL_CHARACTER_VARYING      |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | NATIONAL_CHARACTER              |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | NATIONAL_CHAR                   |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | CHARACTER_VARYING               |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | LONGBLOB                        |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | TINYBLOB                        |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | CLOB                            |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | BLOB                            |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | MEDIUMTEXT                      |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | TEXT                            |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | VARCHAR2                        |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | CHARACTER_LARGE_OBJECT          |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | LONGTEXT                        |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | NVARCHAR                        |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | VARCHAR                         |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | CHAR_VARYING                    |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | MEDIUMBLOB                      |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | NCHAR                           |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | VARBINARY                       |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | CHAR                            |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | TINYTEXT                        |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | BYTEA                           |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | CHARACTER                       |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | CHAR_LARGE_OBJECT               |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | NCHAR_VARYING                   |
| BINARY        | BSON                | optional      | bson\tNullable(String)                                          | BINARY_LARGE_OBJECT             |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | String                          |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | GEOMETRY                        |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | NATIONAL_CHAR_VARYING           |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | BINARY_VARYING                  |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | NCHAR_LARGE_OBJECT              |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | NATIONAL_CHARACTER_VARYING      |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | NATIONAL_CHARACTER              |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | NATIONAL_CHAR                   |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | CHARACTER_VARYING               |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | LONGBLOB                        |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | TINYBLOB                        |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | CLOB                            |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | BLOB                            |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | MEDIUMTEXT                      |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | TEXT                            |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | VARCHAR2                        |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | CHARACTER_LARGE_OBJECT          |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | LONGTEXT                        |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | NVARCHAR                        |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | VARCHAR                         |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | CHAR_VARYING                    |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | MEDIUMBLOB                      |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | NCHAR                           |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | VARBINARY                       |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | CHAR                            |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | TINYTEXT                        |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | BYTEA                           |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | CHARACTER                       |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | CHAR_LARGE_OBJECT               |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | NCHAR_VARYING                   |
| BINARY        | BSON                | required      | bson\tNullable(String)                                          | BINARY_LARGE_OBJECT             |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | String                          |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | GEOMETRY                        |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | NATIONAL_CHAR_VARYING           |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | BINARY_VARYING                  |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | NCHAR_LARGE_OBJECT              |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | NATIONAL_CHARACTER_VARYING      |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | NATIONAL_CHARACTER              |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | NATIONAL_CHAR                   |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | CHARACTER_VARYING               |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | LONGBLOB                        |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | TINYBLOB                        |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | CLOB                            |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | BLOB                            |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | MEDIUMTEXT                      |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | TEXT                            |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | VARCHAR2                        |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | CHARACTER_LARGE_OBJECT          |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | LONGTEXT                        |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | NVARCHAR                        |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | VARCHAR                         |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | CHAR_VARYING                    |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | MEDIUMBLOB                      |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | NCHAR                           |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | VARBINARY                       |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | CHAR                            |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | TINYTEXT                        |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | BYTEA                           |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | CHARACTER                       |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | CHAR_LARGE_OBJECT               |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | NCHAR_VARYING                   |
| BINARY        | BSON                | repeated      | bson\tArray(Nullable(String))                                   | BINARY_LARGE_OBJECT             |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | String                          |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | GEOMETRY                        |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NATIONAL_CHAR_VARYING           |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | BINARY_VARYING                  |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NCHAR_LARGE_OBJECT              |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NATIONAL_CHARACTER_VARYING      |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NATIONAL_CHARACTER              |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NATIONAL_CHAR                   |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CHARACTER_VARYING               |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | LONGBLOB                        |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | TINYBLOB                        |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CLOB                            |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | BLOB                            |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | MEDIUMTEXT                      |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | TEXT                            |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | VARCHAR2                        |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CHARACTER_LARGE_OBJECT          |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | LONGTEXT                        |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NVARCHAR                        |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | VARCHAR                         |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CHAR_VARYING                    |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | MEDIUMBLOB                      |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NCHAR                           |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | VARBINARY                       |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CHAR                            |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | TINYTEXT                        |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | BYTEA                           |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CHARACTER                       |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CHAR_LARGE_OBJECT               |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NCHAR_VARYING                   |
| BINARY        | BSON                | optionalGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | BINARY_LARGE_OBJECT             |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | String                          |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | GEOMETRY                        |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NATIONAL_CHAR_VARYING           |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | BINARY_VARYING                  |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NCHAR_LARGE_OBJECT              |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NATIONAL_CHARACTER_VARYING      |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NATIONAL_CHARACTER              |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NATIONAL_CHAR                   |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CHARACTER_VARYING               |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | LONGBLOB                        |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | TINYBLOB                        |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CLOB                            |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | BLOB                            |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | MEDIUMTEXT                      |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | TEXT                            |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | VARCHAR2                        |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CHARACTER_LARGE_OBJECT          |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | LONGTEXT                        |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NVARCHAR                        |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | VARCHAR                         |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CHAR_VARYING                    |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | MEDIUMBLOB                      |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NCHAR                           |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | VARBINARY                       |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CHAR                            |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | TINYTEXT                        |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | BYTEA                           |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CHARACTER                       |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | CHAR_LARGE_OBJECT               |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | NCHAR_VARYING                   |
| BINARY        | BSON                | requiredGroup | bson\tTuple(\\n    bson Array(Nullable(String)))                | BINARY_LARGE_OBJECT             |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | String                          |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | GEOMETRY                        |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | NATIONAL_CHAR_VARYING           |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | BINARY_VARYING                  |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | NCHAR_LARGE_OBJECT              |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | NATIONAL_CHARACTER_VARYING      |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | NATIONAL_CHARACTER_LARGE_OBJECT |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | NATIONAL_CHARACTER              |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | NATIONAL_CHAR                   |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | CHARACTER_VARYING               |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | LONGBLOB                        |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | TINYBLOB                        |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | CLOB                            |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | BLOB                            |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | MEDIUMTEXT                      |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | TEXT                            |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | VARCHAR2                        |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | CHARACTER_LARGE_OBJECT          |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | LONGTEXT                        |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | NVARCHAR                        |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | VARCHAR                         |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | CHAR_VARYING                    |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | MEDIUMBLOB                      |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | NCHAR                           |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | VARBINARY                       |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | CHAR                            |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | TINYTEXT                        |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | BYTEA                           |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | CHARACTER                       |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | CHAR_LARGE_OBJECT               |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | NCHAR_VARYING                   |
| BINARY        | BSON                | repeatedGroup | bson\tArray(Tuple(\\n    bson Array(Nullable(String))))         | BINARY_LARGE_OBJECT             |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | Int64                           |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | Int16                           |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | UInt256                         |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | String                          |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | Int32                           |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | UInt8                           |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | UInt128                         |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | Float64                         |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | UInt16                          |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | Int128                          |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | Int8                            |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | Decimal                         |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | Int256                          |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | UInt64                          |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | UInt32                          |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | Float32                         |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | GEOMETRY                        |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | NATIONAL_CHAR_VARYING           |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | BINARY_VARYING                  |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | NCHAR_LARGE_OBJECT              |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | NATIONAL_CHARACTER_VARYING      |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | NATIONAL_CHARACTER              |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | NATIONAL_CHAR                   |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | CHARACTER_VARYING               |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | LONGBLOB                        |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | TINYBLOB                        |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | CLOB                            |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | BLOB                            |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | MEDIUMTEXT                      |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | TEXT                            |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | VARCHAR2                        |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | CHARACTER_LARGE_OBJECT          |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | DOUBLE_PRECISION                |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | LONGTEXT                        |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | NVARCHAR                        |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | INT1_UNSIGNED                   |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | VARCHAR                         |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | CHAR_VARYING                    |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | MEDIUMBLOB                      |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | NCHAR                           |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | VARBINARY                       |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | CHAR                            |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | SMALLINT_UNSIGNED               |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | FIXED                           |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | TINYTEXT                        |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | NUMERIC                         |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | DEC                             |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | DOUBLE                          |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | BYTEA                           |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | INT                             |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | SINGLE                          |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | BIT                             |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | BIGINT_UNSIGNED                 |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | UNSIGNED                        |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | TINYINT_UNSIGNED                |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | INTEGER_UNSIGNED                |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | INT_UNSIGNED                    |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | REAL                            |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | CHARACTER                       |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | BYTE                            |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | SIGNED                          |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | MEDIUMINT                       |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | YEAR                            |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | CHAR_LARGE_OBJECT               |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | TINYINT                         |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | BIGINT                          |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | SMALLINT                        |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | INTEGER_SIGNED                  |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | NCHAR_VARYING                   |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | INT_SIGNED                      |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | BIGINT_SIGNED                   |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | BINARY_LARGE_OBJECT             |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | SMALLINT_SIGNED                 |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | FLOAT                           |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | SET                             |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | TIME                            |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | MEDIUMINT_SIGNED                |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | INT1_SIGNED                     |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | INTEGER                         |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | MEDIUMINT_UNSIGNED              |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | INT1                            |
| INT32         | UINT8               | optional      | uint8\tNullable(UInt8)                                          | TINYINT_SIGNED                  |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | Int64                           |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | Int16                           |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | UInt256                         |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | String                          |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | Int32                           |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | UInt8                           |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | UInt128                         |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | Float64                         |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | UInt16                          |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | Int128                          |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | Int8                            |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | Decimal                         |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | Int256                          |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | UInt64                          |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | UInt32                          |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | Float32                         |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | GEOMETRY                        |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | NATIONAL_CHAR_VARYING           |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | BINARY_VARYING                  |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | NCHAR_LARGE_OBJECT              |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | NATIONAL_CHARACTER_VARYING      |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | NATIONAL_CHARACTER              |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | NATIONAL_CHAR                   |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | CHARACTER_VARYING               |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | LONGBLOB                        |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | TINYBLOB                        |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | CLOB                            |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | BLOB                            |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | MEDIUMTEXT                      |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | TEXT                            |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | VARCHAR2                        |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | CHARACTER_LARGE_OBJECT          |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | DOUBLE_PRECISION                |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | LONGTEXT                        |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | NVARCHAR                        |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | INT1_UNSIGNED                   |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | VARCHAR                         |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | CHAR_VARYING                    |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | MEDIUMBLOB                      |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | NCHAR                           |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | VARBINARY                       |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | CHAR                            |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | SMALLINT_UNSIGNED               |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | FIXED                           |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | TINYTEXT                        |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | NUMERIC                         |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | DEC                             |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | DOUBLE                          |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | BYTEA                           |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | INT                             |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | SINGLE                          |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | BIT                             |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | BIGINT_UNSIGNED                 |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | UNSIGNED                        |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | TINYINT_UNSIGNED                |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | INTEGER_UNSIGNED                |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | INT_UNSIGNED                    |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | REAL                            |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | CHARACTER                       |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | BYTE                            |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | SIGNED                          |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | MEDIUMINT                       |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | YEAR                            |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | CHAR_LARGE_OBJECT               |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | TINYINT                         |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | BIGINT                          |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | SMALLINT                        |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | INTEGER_SIGNED                  |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | NCHAR_VARYING                   |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | INT_SIGNED                      |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | BIGINT_SIGNED                   |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | BINARY_LARGE_OBJECT             |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | SMALLINT_SIGNED                 |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | FLOAT                           |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | SET                             |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | TIME                            |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | MEDIUMINT_SIGNED                |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | INT1_SIGNED                     |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | INTEGER                         |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | MEDIUMINT_UNSIGNED              |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | INT1                            |
| INT32         | UINT8               | required      | uint8\tNullable(UInt8)                                          | TINYINT_SIGNED                  |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | String                          |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | Int8                            |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | GEOMETRY                        |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | NATIONAL_CHAR_VARYING           |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | BINARY_VARYING                  |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | NCHAR_LARGE_OBJECT              |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | NATIONAL_CHARACTER_VARYING      |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | NATIONAL_CHARACTER              |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | NATIONAL_CHAR                   |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | CHARACTER_VARYING               |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | LONGBLOB                        |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | TINYBLOB                        |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | CLOB                            |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | BLOB                            |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | MEDIUMTEXT                      |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | TEXT                            |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | VARCHAR2                        |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | CHARACTER_LARGE_OBJECT          |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | LONGTEXT                        |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | NVARCHAR                        |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | VARCHAR                         |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | CHAR_VARYING                    |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | MEDIUMBLOB                      |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | NCHAR                           |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | VARBINARY                       |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | CHAR                            |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | TINYTEXT                        |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | BYTEA                           |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | CHARACTER                       |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | BYTE                            |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | CHAR_LARGE_OBJECT               |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | TINYINT                         |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | NCHAR_VARYING                   |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | BINARY_LARGE_OBJECT             |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | INT1_SIGNED                     |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | INT1                            |
| INT32         | UINT8               | repeated      | uint8\tArray(Nullable(UInt8))                                   | TINYINT_SIGNED                  |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | String                          |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | GEOMETRY                        |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NATIONAL_CHAR_VARYING           |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | BINARY_VARYING                  |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NCHAR_LARGE_OBJECT              |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NATIONAL_CHARACTER_VARYING      |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NATIONAL_CHARACTER              |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NATIONAL_CHAR                   |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CHARACTER_VARYING               |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | LONGBLOB                        |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | TINYBLOB                        |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CLOB                            |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | BLOB                            |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | MEDIUMTEXT                      |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | TEXT                            |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | VARCHAR2                        |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CHARACTER_LARGE_OBJECT          |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | LONGTEXT                        |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NVARCHAR                        |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | VARCHAR                         |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CHAR_VARYING                    |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | MEDIUMBLOB                      |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NCHAR                           |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | VARBINARY                       |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CHAR                            |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | TINYTEXT                        |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | BYTEA                           |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CHARACTER                       |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CHAR_LARGE_OBJECT               |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NCHAR_VARYING                   |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | BINARY_LARGE_OBJECT             |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | Int8                            |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | BYTE                            |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | TINYINT                         |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | INT1_SIGNED                     |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | INT1                            |
| INT32         | UINT8               | optionalGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | TINYINT_SIGNED                  |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | String                          |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | Int8                            |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | GEOMETRY                        |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NATIONAL_CHAR_VARYING           |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | BINARY_VARYING                  |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NCHAR_LARGE_OBJECT              |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NATIONAL_CHARACTER_VARYING      |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NATIONAL_CHARACTER              |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NATIONAL_CHAR                   |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CHARACTER_VARYING               |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | LONGBLOB                        |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | TINYBLOB                        |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CLOB                            |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | BLOB                            |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | MEDIUMTEXT                      |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | TEXT                            |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | VARCHAR2                        |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CHARACTER_LARGE_OBJECT          |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | LONGTEXT                        |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NVARCHAR                        |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | VARCHAR                         |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CHAR_VARYING                    |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | MEDIUMBLOB                      |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NCHAR                           |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | VARBINARY                       |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CHAR                            |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | TINYTEXT                        |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | BYTEA                           |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CHARACTER                       |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | BYTE                            |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | CHAR_LARGE_OBJECT               |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | TINYINT                         |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | NCHAR_VARYING                   |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | BINARY_LARGE_OBJECT             |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | INT1_SIGNED                     |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | INT1                            |
| INT32         | UINT8               | requiredGroup | uint8\tTuple(\\n    uint8 Array(Nullable(UInt8)))               | TINYINT_SIGNED                  |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | String                          |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | Int8                            |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | GEOMETRY                        |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | NATIONAL_CHAR_VARYING           |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | BINARY_VARYING                  |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | NCHAR_LARGE_OBJECT              |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | NATIONAL_CHARACTER_VARYING      |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | NATIONAL_CHARACTER              |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | NATIONAL_CHAR                   |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | CHARACTER_VARYING               |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | LONGBLOB                        |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | TINYBLOB                        |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | CLOB                            |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | BLOB                            |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | MEDIUMTEXT                      |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | TEXT                            |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | VARCHAR2                        |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | CHARACTER_LARGE_OBJECT          |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | LONGTEXT                        |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | NVARCHAR                        |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | VARCHAR                         |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | CHAR_VARYING                    |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | MEDIUMBLOB                      |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | NCHAR                           |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | VARBINARY                       |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | CHAR                            |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | TINYTEXT                        |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | BYTEA                           |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | CHARACTER                       |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | BYTE                            |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | CHAR_LARGE_OBJECT               |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | TINYINT                         |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | NCHAR_VARYING                   |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | BINARY_LARGE_OBJECT             |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | INT1_SIGNED                     |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | INT1                            |
| INT32         | UINT8               | repeatedGroup | uint8\tArray(Tuple(\\n    uint8 Array(Nullable(UInt8))))        | TINYINT_SIGNED                  |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | Int64                           |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | Int16                           |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | UInt256                         |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | String                          |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | DateTime                        |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | Int32                           |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | UInt8                           |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | UInt128                         |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | Float64                         |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | UInt16                          |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | Int128                          |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | Int8                            |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | Decimal                         |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | Int256                          |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | DateTime64                      |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | DateTime32                      |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | UInt64                          |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | UInt32                          |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | Float32                         |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | GEOMETRY                        |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | NATIONAL_CHAR_VARYING           |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | BINARY_VARYING                  |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | NCHAR_LARGE_OBJECT              |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | NATIONAL_CHARACTER_VARYING      |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | NATIONAL_CHARACTER              |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | NATIONAL_CHAR                   |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | CHARACTER_VARYING               |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | LONGBLOB                        |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | TINYBLOB                        |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | CLOB                            |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | BLOB                            |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | MEDIUMTEXT                      |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | TEXT                            |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | VARCHAR2                        |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | CHARACTER_LARGE_OBJECT          |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | DOUBLE_PRECISION                |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | LONGTEXT                        |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | NVARCHAR                        |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | INT1_UNSIGNED                   |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | VARCHAR                         |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | CHAR_VARYING                    |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | MEDIUMBLOB                      |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | NCHAR                           |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | VARBINARY                       |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | CHAR                            |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | SMALLINT_UNSIGNED               |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | TIMESTAMP                       |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | FIXED                           |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | TINYTEXT                        |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | NUMERIC                         |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | DEC                             |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | DOUBLE                          |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | BYTEA                           |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | INT                             |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | SINGLE                          |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | BIT                             |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | BIGINT_UNSIGNED                 |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | UNSIGNED                        |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | TINYINT_UNSIGNED                |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | INTEGER_UNSIGNED                |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | INT_UNSIGNED                    |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | REAL                            |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | CHARACTER                       |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | BYTE                            |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | SIGNED                          |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | MEDIUMINT                       |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | YEAR                            |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | CHAR_LARGE_OBJECT               |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | TINYINT                         |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | BIGINT                          |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | SMALLINT                        |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | INTEGER_SIGNED                  |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | NCHAR_VARYING                   |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | INT_SIGNED                      |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | BIGINT_SIGNED                   |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | BINARY_LARGE_OBJECT             |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | SMALLINT_SIGNED                 |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | FLOAT                           |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | SET                             |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | TIME                            |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | MEDIUMINT_SIGNED                |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | INT1_SIGNED                     |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | INTEGER                         |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | MEDIUMINT_UNSIGNED              |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | INT1                            |
| INT32         | UINT16              | optional      | uint16\tNullable(UInt16)                                        | TINYINT_SIGNED                  |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | Int64                           |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | Int16                           |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | UInt256                         |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | String                          |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | DateTime                        |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | Int32                           |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | UInt8                           |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | UInt128                         |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | Float64                         |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | UInt16                          |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | Int128                          |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | Int8                            |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | Decimal                         |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | Int256                          |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | DateTime64                      |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | DateTime32                      |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | UInt64                          |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | UInt32                          |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | Float32                         |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | GEOMETRY                        |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | NATIONAL_CHAR_VARYING           |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | BINARY_VARYING                  |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | NCHAR_LARGE_OBJECT              |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | NATIONAL_CHARACTER_VARYING      |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | NATIONAL_CHARACTER              |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | NATIONAL_CHAR                   |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | CHARACTER_VARYING               |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | LONGBLOB                        |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | TINYBLOB                        |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | CLOB                            |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | BLOB                            |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | MEDIUMTEXT                      |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | TEXT                            |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | VARCHAR2                        |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | CHARACTER_LARGE_OBJECT          |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | DOUBLE_PRECISION                |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | LONGTEXT                        |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | NVARCHAR                        |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | INT1_UNSIGNED                   |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | VARCHAR                         |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | CHAR_VARYING                    |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | MEDIUMBLOB                      |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | NCHAR                           |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | VARBINARY                       |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | CHAR                            |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | SMALLINT_UNSIGNED               |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | TIMESTAMP                       |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | FIXED                           |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | TINYTEXT                        |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | NUMERIC                         |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | DEC                             |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | DOUBLE                          |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | BYTEA                           |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | INT                             |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | SINGLE                          |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | BIT                             |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | BIGINT_UNSIGNED                 |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | UNSIGNED                        |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | TINYINT_UNSIGNED                |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | INTEGER_UNSIGNED                |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | INT_UNSIGNED                    |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | REAL                            |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | CHARACTER                       |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | BYTE                            |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | SIGNED                          |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | MEDIUMINT                       |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | YEAR                            |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | CHAR_LARGE_OBJECT               |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | TINYINT                         |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | BIGINT                          |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | SMALLINT                        |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | INTEGER_SIGNED                  |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | NCHAR_VARYING                   |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | INT_SIGNED                      |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | BIGINT_SIGNED                   |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | BINARY_LARGE_OBJECT             |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | SMALLINT_SIGNED                 |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | FLOAT                           |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | SET                             |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | TIME                            |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | MEDIUMINT_SIGNED                |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | INT1_SIGNED                     |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | INTEGER                         |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | MEDIUMINT_UNSIGNED              |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | INT1                            |
| INT32         | UINT16              | required      | uint16\tNullable(UInt16)                                        | TINYINT_SIGNED                  |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | Int16                           |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | String                          |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | UInt8                           |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | Int8                            |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | GEOMETRY                        |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | NATIONAL_CHAR_VARYING           |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | BINARY_VARYING                  |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | NCHAR_LARGE_OBJECT              |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | NATIONAL_CHARACTER_VARYING      |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | NATIONAL_CHARACTER              |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | NATIONAL_CHAR                   |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | CHARACTER_VARYING               |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | LONGBLOB                        |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | TINYBLOB                        |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | CLOB                            |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | BLOB                            |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | MEDIUMTEXT                      |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | TEXT                            |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | VARCHAR2                        |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | CHARACTER_LARGE_OBJECT          |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | LONGTEXT                        |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | NVARCHAR                        |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | INT1_UNSIGNED                   |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | VARCHAR                         |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | CHAR_VARYING                    |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | MEDIUMBLOB                      |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | NCHAR                           |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | VARBINARY                       |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | CHAR                            |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | TINYTEXT                        |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | BYTEA                           |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | TINYINT_UNSIGNED                |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | CHARACTER                       |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | BYTE                            |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | CHAR_LARGE_OBJECT               |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | TINYINT                         |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | SMALLINT                        |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | NCHAR_VARYING                   |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | BINARY_LARGE_OBJECT             |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | SMALLINT_SIGNED                 |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | INT1_SIGNED                     |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | INT1                            |
| INT32         | UINT16              | repeated      | uint16\tArray(Nullable(UInt16))                                 | TINYINT_SIGNED                  |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | Int16                           |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | String                          |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | UInt8                           |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | Int8                            |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | GEOMETRY                        |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NATIONAL_CHAR_VARYING           |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | BINARY_VARYING                  |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NCHAR_LARGE_OBJECT              |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NATIONAL_CHARACTER_VARYING      |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NATIONAL_CHARACTER              |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NATIONAL_CHAR                   |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CHARACTER_VARYING               |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | LONGBLOB                        |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | TINYBLOB                        |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CLOB                            |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | BLOB                            |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | MEDIUMTEXT                      |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | TEXT                            |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | VARCHAR2                        |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CHARACTER_LARGE_OBJECT          |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | LONGTEXT                        |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NVARCHAR                        |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | INT1_UNSIGNED                   |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | VARCHAR                         |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CHAR_VARYING                    |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | MEDIUMBLOB                      |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NCHAR                           |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | VARBINARY                       |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CHAR                            |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | TINYTEXT                        |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | BYTEA                           |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | TINYINT_UNSIGNED                |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CHARACTER                       |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | BYTE                            |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CHAR_LARGE_OBJECT               |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | TINYINT                         |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | SMALLINT                        |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NCHAR_VARYING                   |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | BINARY_LARGE_OBJECT             |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | SMALLINT_SIGNED                 |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | INT1_SIGNED                     |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | INT1                            |
| INT32         | UINT16              | optionalGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | TINYINT_SIGNED                  |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | Int16                           |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | String                          |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | UInt8                           |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | Int8                            |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | GEOMETRY                        |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NATIONAL_CHAR_VARYING           |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | BINARY_VARYING                  |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NCHAR_LARGE_OBJECT              |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NATIONAL_CHARACTER_VARYING      |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NATIONAL_CHARACTER              |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NATIONAL_CHAR                   |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CHARACTER_VARYING               |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | LONGBLOB                        |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | TINYBLOB                        |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CLOB                            |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | BLOB                            |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | MEDIUMTEXT                      |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | TEXT                            |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | VARCHAR2                        |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CHARACTER_LARGE_OBJECT          |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | LONGTEXT                        |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NVARCHAR                        |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | INT1_UNSIGNED                   |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | VARCHAR                         |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CHAR_VARYING                    |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | MEDIUMBLOB                      |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NCHAR                           |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | VARBINARY                       |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CHAR                            |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | TINYTEXT                        |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | BYTEA                           |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | TINYINT_UNSIGNED                |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CHARACTER                       |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | BYTE                            |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | CHAR_LARGE_OBJECT               |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | TINYINT                         |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | SMALLINT                        |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | NCHAR_VARYING                   |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | BINARY_LARGE_OBJECT             |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | SMALLINT_SIGNED                 |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | INT1_SIGNED                     |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | INT1                            |
| INT32         | UINT16              | requiredGroup | uint16\tTuple(\\n    uint16 Array(Nullable(UInt16)))            | TINYINT_SIGNED                  |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | Int16                           |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | String                          |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | UInt8                           |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | Int8                            |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | GEOMETRY                        |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | NATIONAL_CHAR_VARYING           |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | BINARY_VARYING                  |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | NCHAR_LARGE_OBJECT              |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | NATIONAL_CHARACTER_VARYING      |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | NATIONAL_CHARACTER              |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | NATIONAL_CHAR                   |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | CHARACTER_VARYING               |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | LONGBLOB                        |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | TINYBLOB                        |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | CLOB                            |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | BLOB                            |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | MEDIUMTEXT                      |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | TEXT                            |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | VARCHAR2                        |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | CHARACTER_LARGE_OBJECT          |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | LONGTEXT                        |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | NVARCHAR                        |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | INT1_UNSIGNED                   |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | VARCHAR                         |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | CHAR_VARYING                    |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | MEDIUMBLOB                      |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | NCHAR                           |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | VARBINARY                       |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | CHAR                            |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | TINYTEXT                        |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | BYTEA                           |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | TINYINT_UNSIGNED                |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | CHARACTER                       |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | BYTE                            |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | CHAR_LARGE_OBJECT               |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | TINYINT                         |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | SMALLINT                        |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | NCHAR_VARYING                   |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | BINARY_LARGE_OBJECT             |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | SMALLINT_SIGNED                 |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | INT1_SIGNED                     |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | INT1                            |
| INT32         | UINT16              | repeatedGroup | uint16\tArray(Tuple(\\n    uint16 Array(Nullable(UInt16))))     | TINYINT_SIGNED                  |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | Int64                           |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | Int16                           |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | UInt256                         |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | String                          |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | Int32                           |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | UInt8                           |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | UInt128                         |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | Float64                         |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | UInt16                          |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | Int128                          |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | Int8                            |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | Int256                          |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | UInt64                          |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | UInt32                          |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | Float32                         |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | GEOMETRY                        |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | NATIONAL_CHAR_VARYING           |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | BINARY_VARYING                  |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | NCHAR_LARGE_OBJECT              |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | NATIONAL_CHARACTER_VARYING      |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | NATIONAL_CHARACTER              |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | NATIONAL_CHAR                   |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | CHARACTER_VARYING               |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | LONGBLOB                        |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | TINYBLOB                        |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | CLOB                            |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | BLOB                            |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | MEDIUMTEXT                      |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | TEXT                            |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | VARCHAR2                        |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | CHARACTER_LARGE_OBJECT          |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | DOUBLE_PRECISION                |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | LONGTEXT                        |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | NVARCHAR                        |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | INT1_UNSIGNED                   |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | VARCHAR                         |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | CHAR_VARYING                    |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | MEDIUMBLOB                      |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | NCHAR                           |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | VARBINARY                       |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | CHAR                            |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | SMALLINT_UNSIGNED               |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | TINYTEXT                        |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | DOUBLE                          |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | BYTEA                           |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | INT                             |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | SINGLE                          |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | BIT                             |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | BIGINT_UNSIGNED                 |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | UNSIGNED                        |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | TINYINT_UNSIGNED                |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | INTEGER_UNSIGNED                |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | INT_UNSIGNED                    |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | REAL                            |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | CHARACTER                       |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | BYTE                            |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | SIGNED                          |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | MEDIUMINT                       |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | YEAR                            |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | CHAR_LARGE_OBJECT               |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | TINYINT                         |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | BIGINT                          |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | SMALLINT                        |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | INTEGER_SIGNED                  |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | NCHAR_VARYING                   |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | INT_SIGNED                      |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | BIGINT_SIGNED                   |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | BINARY_LARGE_OBJECT             |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | SMALLINT_SIGNED                 |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | FLOAT                           |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | SET                             |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | TIME                            |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | MEDIUMINT_SIGNED                |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | INT1_SIGNED                     |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | INTEGER                         |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | MEDIUMINT_UNSIGNED              |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | INT1                            |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | TINYINT_SIGNED                  |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | DateTime                        |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | DateTime32                      |
| INT64         | UINT64              | optional      | uint64\tNullable(UInt64)                                        | TIMESTAMP                       |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | Int64                           |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | Int16                           |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | UInt256                         |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | String                          |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | Int32                           |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | UInt8                           |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | UInt128                         |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | Float64                         |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | UInt16                          |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | Int128                          |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | Int8                            |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | Int256                          |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | UInt64                          |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | UInt32                          |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | Float32                         |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | GEOMETRY                        |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | NATIONAL_CHAR_VARYING           |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | BINARY_VARYING                  |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | NCHAR_LARGE_OBJECT              |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | NATIONAL_CHARACTER_VARYING      |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | NATIONAL_CHARACTER              |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | NATIONAL_CHAR                   |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | CHARACTER_VARYING               |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | LONGBLOB                        |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | TINYBLOB                        |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | CLOB                            |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | BLOB                            |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | MEDIUMTEXT                      |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | TEXT                            |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | VARCHAR2                        |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | CHARACTER_LARGE_OBJECT          |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | DOUBLE_PRECISION                |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | LONGTEXT                        |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | NVARCHAR                        |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | INT1_UNSIGNED                   |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | VARCHAR                         |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | CHAR_VARYING                    |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | MEDIUMBLOB                      |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | NCHAR                           |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | VARBINARY                       |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | CHAR                            |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | SMALLINT_UNSIGNED               |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | TINYTEXT                        |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | DOUBLE                          |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | BYTEA                           |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | INT                             |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | SINGLE                          |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | BIT                             |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | BIGINT_UNSIGNED                 |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | UNSIGNED                        |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | TINYINT_UNSIGNED                |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | INTEGER_UNSIGNED                |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | INT_UNSIGNED                    |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | REAL                            |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | CHARACTER                       |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | BYTE                            |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | SIGNED                          |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | MEDIUMINT                       |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | YEAR                            |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | CHAR_LARGE_OBJECT               |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | TINYINT                         |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | BIGINT                          |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | SMALLINT                        |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | INTEGER_SIGNED                  |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | NCHAR_VARYING                   |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | INT_SIGNED                      |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | BIGINT_SIGNED                   |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | BINARY_LARGE_OBJECT             |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | SMALLINT_SIGNED                 |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | FLOAT                           |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | SET                             |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | TIME                            |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | MEDIUMINT_SIGNED                |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | INT1_SIGNED                     |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | INTEGER                         |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | MEDIUMINT_UNSIGNED              |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | INT1                            |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | TINYINT_SIGNED                  |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | DateTime                        |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | DateTime32                      |
| INT64         | UINT64              | required      | uint64\tNullable(UInt64)                                        | TIMESTAMP                       |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | Int16                           |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | String                          |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | Int32                           |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | UInt8                           |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | UInt16                          |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | Int8                            |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | UInt32                          |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | GEOMETRY                        |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | NATIONAL_CHAR_VARYING           |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | BINARY_VARYING                  |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | NCHAR_LARGE_OBJECT              |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | NATIONAL_CHARACTER_VARYING      |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | NATIONAL_CHARACTER              |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | NATIONAL_CHAR                   |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | CHARACTER_VARYING               |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | LONGBLOB                        |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | TINYBLOB                        |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | CLOB                            |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | BLOB                            |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | MEDIUMTEXT                      |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | TEXT                            |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | VARCHAR2                        |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | CHARACTER_LARGE_OBJECT          |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | LONGTEXT                        |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | NVARCHAR                        |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | INT1_UNSIGNED                   |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | VARCHAR                         |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | CHAR_VARYING                    |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | MEDIUMBLOB                      |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | NCHAR                           |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | VARBINARY                       |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | CHAR                            |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | SMALLINT_UNSIGNED               |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | TINYTEXT                        |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | BYTEA                           |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | INT                             |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | TINYINT_UNSIGNED                |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | INTEGER_UNSIGNED                |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | INT_UNSIGNED                    |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | CHARACTER                       |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | BYTE                            |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | MEDIUMINT                       |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | YEAR                            |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | CHAR_LARGE_OBJECT               |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | TINYINT                         |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | SMALLINT                        |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | INTEGER_SIGNED                  |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | NCHAR_VARYING                   |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | INT_SIGNED                      |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | BINARY_LARGE_OBJECT             |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | SMALLINT_SIGNED                 |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | MEDIUMINT_SIGNED                |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | INT1_SIGNED                     |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | INTEGER                         |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | MEDIUMINT_UNSIGNED              |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | INT1                            |
| INT64         | UINT64              | repeated      | uint64\tArray(Nullable(UInt64))                                 | TINYINT_SIGNED                  |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | Int64                           |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | Int16                           |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | String                          |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | Int32                           |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | Float64                         |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | Int128                          |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | Int8                            |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | Decimal                         |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | Int256                          |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | DateTime64                      |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | Float32                         |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | GEOMETRY                        |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | NATIONAL_CHAR_VARYING           |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | BINARY_VARYING                  |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | NCHAR_LARGE_OBJECT              |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | NATIONAL_CHARACTER              |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | NATIONAL_CHAR                   |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | CHARACTER_VARYING               |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | LONGBLOB                        |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | TINYBLOB                        |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | CLOB                            |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | BLOB                            |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | MEDIUMTEXT                      |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | TEXT                            |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | VARCHAR2                        |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | CHARACTER_LARGE_OBJECT          |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | DOUBLE_PRECISION                |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | LONGTEXT                        |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | NVARCHAR                        |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | VARCHAR                         |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | CHAR_VARYING                    |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | MEDIUMBLOB                      |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | NCHAR                           |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | VARBINARY                       |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | CHAR                            |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | FIXED                           |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | TINYTEXT                        |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | NUMERIC                         |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | DEC                             |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | DOUBLE                          |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | BYTEA                           |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | INT                             |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | SINGLE                          |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | REAL                            |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | CHARACTER                       |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | BYTE                            |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | SIGNED                          |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | MEDIUMINT                       |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | CHAR_LARGE_OBJECT               |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | TINYINT                         |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | BIGINT                          |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | SMALLINT                        |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | INTEGER_SIGNED                  |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | NCHAR_VARYING                   |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | INT_SIGNED                      |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | BIGINT_SIGNED                   |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | BINARY_LARGE_OBJECT             |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | SMALLINT_SIGNED                 |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | FLOAT                           |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | TIME                            |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | MEDIUMINT_SIGNED                |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | INT1_SIGNED                     |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | INTEGER                         |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | INT1                            |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | TINYINT_SIGNED                  |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | UInt256                         |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | UInt8                           |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | UInt128                         |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | UInt16                          |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | UInt64                          |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | UInt32                          |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | INT1_UNSIGNED                   |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | SMALLINT_UNSIGNED               |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | BIT                             |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | BIGINT_UNSIGNED                 |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | UNSIGNED                        |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | TINYINT_UNSIGNED                |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | INTEGER_UNSIGNED                |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | INT_UNSIGNED                    |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | YEAR                            |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | SET                             |
| INT32         | INT8                | optional      | int8\tNullable(Int8)                                            | MEDIUMINT_UNSIGNED              |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | Int64                           |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | Int16                           |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | String                          |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | Int32                           |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | Float64                         |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | Int128                          |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | Int8                            |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | Decimal                         |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | Int256                          |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | DateTime64                      |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | Float32                         |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | GEOMETRY                        |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | NATIONAL_CHAR_VARYING           |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | BINARY_VARYING                  |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | NCHAR_LARGE_OBJECT              |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | NATIONAL_CHARACTER              |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | NATIONAL_CHAR                   |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | CHARACTER_VARYING               |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | LONGBLOB                        |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | TINYBLOB                        |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | CLOB                            |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | BLOB                            |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | MEDIUMTEXT                      |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | TEXT                            |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | VARCHAR2                        |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | CHARACTER_LARGE_OBJECT          |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | DOUBLE_PRECISION                |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | LONGTEXT                        |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | NVARCHAR                        |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | VARCHAR                         |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | CHAR_VARYING                    |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | MEDIUMBLOB                      |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | NCHAR                           |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | VARBINARY                       |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | CHAR                            |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | FIXED                           |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | TINYTEXT                        |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | NUMERIC                         |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | DEC                             |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | DOUBLE                          |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | BYTEA                           |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | INT                             |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | SINGLE                          |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | REAL                            |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | CHARACTER                       |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | BYTE                            |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | SIGNED                          |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | MEDIUMINT                       |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | CHAR_LARGE_OBJECT               |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | TINYINT                         |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | BIGINT                          |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | SMALLINT                        |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | INTEGER_SIGNED                  |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | NCHAR_VARYING                   |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | INT_SIGNED                      |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | BIGINT_SIGNED                   |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | BINARY_LARGE_OBJECT             |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | SMALLINT_SIGNED                 |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | FLOAT                           |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | TIME                            |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | MEDIUMINT_SIGNED                |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | INT1_SIGNED                     |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | INTEGER                         |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | INT1                            |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | TINYINT_SIGNED                  |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | UInt256                         |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | UInt8                           |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | UInt128                         |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | UInt16                          |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | UInt64                          |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | UInt32                          |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | INT1_UNSIGNED                   |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | SMALLINT_UNSIGNED               |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | BIT                             |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | BIGINT_UNSIGNED                 |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | UNSIGNED                        |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | TINYINT_UNSIGNED                |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | INTEGER_UNSIGNED                |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | INT_UNSIGNED                    |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | YEAR                            |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | SET                             |
| INT32         | INT8                | required      | int8\tNullable(Int8)                                            | MEDIUMINT_UNSIGNED              |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | String                          |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | GEOMETRY                        |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | NATIONAL_CHAR_VARYING           |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | BINARY_VARYING                  |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | NCHAR_LARGE_OBJECT              |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | NATIONAL_CHARACTER              |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | NATIONAL_CHAR                   |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | CHARACTER_VARYING               |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | LONGBLOB                        |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | TINYBLOB                        |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | CLOB                            |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | BLOB                            |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | MEDIUMTEXT                      |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | TEXT                            |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | VARCHAR2                        |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | CHARACTER_LARGE_OBJECT          |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | LONGTEXT                        |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | NVARCHAR                        |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | VARCHAR                         |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | CHAR_VARYING                    |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | MEDIUMBLOB                      |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | NCHAR                           |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | VARBINARY                       |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | CHAR                            |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | TINYTEXT                        |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | BYTEA                           |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | CHARACTER                       |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | CHAR_LARGE_OBJECT               |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | NCHAR_VARYING                   |
| INT32         | INT8                | repeated      | int8\tArray(Nullable(Int8))                                     | BINARY_LARGE_OBJECT             |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | String                          |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | GEOMETRY                        |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NATIONAL_CHAR_VARYING           |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | BINARY_VARYING                  |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NCHAR_LARGE_OBJECT              |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NATIONAL_CHARACTER              |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NATIONAL_CHAR                   |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CHARACTER_VARYING               |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | LONGBLOB                        |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | TINYBLOB                        |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CLOB                            |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | BLOB                            |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | MEDIUMTEXT                      |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | TEXT                            |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | VARCHAR2                        |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CHARACTER_LARGE_OBJECT          |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | LONGTEXT                        |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NVARCHAR                        |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | VARCHAR                         |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CHAR_VARYING                    |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | MEDIUMBLOB                      |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NCHAR                           |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | VARBINARY                       |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CHAR                            |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | TINYTEXT                        |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | BYTEA                           |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CHARACTER                       |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CHAR_LARGE_OBJECT               |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NCHAR_VARYING                   |
| INT32         | INT8                | optionalGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | BINARY_LARGE_OBJECT             |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | String                          |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | GEOMETRY                        |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NATIONAL_CHAR_VARYING           |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | BINARY_VARYING                  |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NCHAR_LARGE_OBJECT              |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NATIONAL_CHARACTER              |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NATIONAL_CHAR                   |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CHARACTER_VARYING               |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | LONGBLOB                        |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | TINYBLOB                        |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CLOB                            |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | BLOB                            |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | MEDIUMTEXT                      |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | TEXT                            |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | VARCHAR2                        |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CHARACTER_LARGE_OBJECT          |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | LONGTEXT                        |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NVARCHAR                        |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | VARCHAR                         |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CHAR_VARYING                    |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | MEDIUMBLOB                      |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NCHAR                           |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | VARBINARY                       |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CHAR                            |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | TINYTEXT                        |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | BYTEA                           |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CHARACTER                       |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | CHAR_LARGE_OBJECT               |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | NCHAR_VARYING                   |
| INT32         | INT8                | requiredGroup | int8\tTuple(\\n    int8 Array(Nullable(Int8)))                  | BINARY_LARGE_OBJECT             |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | String                          |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | GEOMETRY                        |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | NATIONAL_CHAR_VARYING           |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | BINARY_VARYING                  |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | NCHAR_LARGE_OBJECT              |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | NATIONAL_CHARACTER              |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | NATIONAL_CHAR                   |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | CHARACTER_VARYING               |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | LONGBLOB                        |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | TINYBLOB                        |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | CLOB                            |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | BLOB                            |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | MEDIUMTEXT                      |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | TEXT                            |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | VARCHAR2                        |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | CHARACTER_LARGE_OBJECT          |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | LONGTEXT                        |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | NVARCHAR                        |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | VARCHAR                         |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | CHAR_VARYING                    |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | MEDIUMBLOB                      |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | NCHAR                           |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | VARBINARY                       |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | CHAR                            |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | TINYTEXT                        |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | BYTEA                           |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | CHARACTER                       |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | CHAR_LARGE_OBJECT               |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | NCHAR_VARYING                   |
| INT32         | INT8                | repeatedGroup | int8\tArray(Tuple(\\n    int8 Array(Nullable(Int8))))           | BINARY_LARGE_OBJECT             |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | Int64                           |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | Int16                           |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | String                          |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | Int32                           |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | Float64                         |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | Int128                          |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | Int8                            |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | Decimal                         |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | Int256                          |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | DateTime64                      |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | Float32                         |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | GEOMETRY                        |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | NATIONAL_CHAR_VARYING           |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | BINARY_VARYING                  |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | NCHAR_LARGE_OBJECT              |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | NATIONAL_CHARACTER              |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | NATIONAL_CHAR                   |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | CHARACTER_VARYING               |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | LONGBLOB                        |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | TINYBLOB                        |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | CLOB                            |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | BLOB                            |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | MEDIUMTEXT                      |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | TEXT                            |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | VARCHAR2                        |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | CHARACTER_LARGE_OBJECT          |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | DOUBLE_PRECISION                |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | LONGTEXT                        |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | NVARCHAR                        |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | VARCHAR                         |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | CHAR_VARYING                    |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | MEDIUMBLOB                      |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | NCHAR                           |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | VARBINARY                       |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | CHAR                            |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | FIXED                           |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | TINYTEXT                        |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | NUMERIC                         |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | DEC                             |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | DOUBLE                          |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | BYTEA                           |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | INT                             |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | SINGLE                          |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | REAL                            |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | CHARACTER                       |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | BYTE                            |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | SIGNED                          |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | MEDIUMINT                       |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | CHAR_LARGE_OBJECT               |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | TINYINT                         |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | BIGINT                          |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | SMALLINT                        |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | INTEGER_SIGNED                  |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | NCHAR_VARYING                   |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | INT_SIGNED                      |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | BIGINT_SIGNED                   |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | BINARY_LARGE_OBJECT             |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | SMALLINT_SIGNED                 |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | FLOAT                           |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | TIME                            |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | MEDIUMINT_SIGNED                |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | INT1_SIGNED                     |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | INTEGER                         |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | INT1                            |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | TINYINT_SIGNED                  |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | UInt256                         |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | DateTime                        |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | UInt8                           |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | UInt128                         |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | UInt16                          |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | DateTime32                      |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | UInt64                          |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | UInt32                          |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | INT1_UNSIGNED                   |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | SMALLINT_UNSIGNED               |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | TIMESTAMP                       |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | BIT                             |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | BIGINT_UNSIGNED                 |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | UNSIGNED                        |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | TINYINT_UNSIGNED                |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | INTEGER_UNSIGNED                |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | INT_UNSIGNED                    |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | YEAR                            |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | SET                             |
| INT32         | INT16               | optional      | int16\tNullable(Int16)                                          | MEDIUMINT_UNSIGNED              |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | Int64                           |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | Int16                           |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | UInt256                         |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | String                          |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | DateTime                        |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | Int32                           |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | UInt8                           |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | UInt128                         |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | Float64                         |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | UInt16                          |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | Int128                          |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | Int8                            |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | Decimal                         |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | Int256                          |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | DateTime64                      |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | DateTime32                      |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | UInt64                          |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | UInt32                          |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | Float32                         |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | GEOMETRY                        |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | NATIONAL_CHAR_VARYING           |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | BINARY_VARYING                  |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | NCHAR_LARGE_OBJECT              |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | NATIONAL_CHARACTER              |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | NATIONAL_CHAR                   |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | CHARACTER_VARYING               |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | LONGBLOB                        |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | TINYBLOB                        |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | CLOB                            |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | BLOB                            |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | MEDIUMTEXT                      |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | TEXT                            |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | VARCHAR2                        |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | CHARACTER_LARGE_OBJECT          |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | DOUBLE_PRECISION                |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | LONGTEXT                        |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | NVARCHAR                        |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | INT1_UNSIGNED                   |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | VARCHAR                         |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | CHAR_VARYING                    |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | MEDIUMBLOB                      |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | NCHAR                           |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | VARBINARY                       |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | CHAR                            |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | SMALLINT_UNSIGNED               |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | TIMESTAMP                       |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | FIXED                           |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | TINYTEXT                        |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | NUMERIC                         |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | DEC                             |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | DOUBLE                          |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | BYTEA                           |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | INT                             |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | SINGLE                          |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | BIT                             |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | BIGINT_UNSIGNED                 |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | UNSIGNED                        |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | TINYINT_UNSIGNED                |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | INTEGER_UNSIGNED                |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | INT_UNSIGNED                    |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | REAL                            |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | CHARACTER                       |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | BYTE                            |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | SIGNED                          |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | MEDIUMINT                       |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | YEAR                            |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | CHAR_LARGE_OBJECT               |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | TINYINT                         |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | BIGINT                          |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | SMALLINT                        |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | INTEGER_SIGNED                  |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | NCHAR_VARYING                   |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | INT_SIGNED                      |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | BIGINT_SIGNED                   |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | BINARY_LARGE_OBJECT             |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | SMALLINT_SIGNED                 |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | FLOAT                           |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | SET                             |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | TIME                            |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | MEDIUMINT_SIGNED                |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | INT1_SIGNED                     |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | INTEGER                         |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | MEDIUMINT_UNSIGNED              |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | INT1                            |
| INT32         | INT16               | required      | int16\tNullable(Int16)                                          | TINYINT_SIGNED                  |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | String                          |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | Int8                            |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | GEOMETRY                        |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | NATIONAL_CHAR_VARYING           |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | BINARY_VARYING                  |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | NCHAR_LARGE_OBJECT              |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | NATIONAL_CHARACTER              |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | NATIONAL_CHAR                   |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | CHARACTER_VARYING               |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | LONGBLOB                        |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | TINYBLOB                        |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | CLOB                            |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | BLOB                            |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | MEDIUMTEXT                      |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | TEXT                            |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | VARCHAR2                        |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | CHARACTER_LARGE_OBJECT          |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | LONGTEXT                        |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | NVARCHAR                        |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | VARCHAR                         |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | CHAR_VARYING                    |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | MEDIUMBLOB                      |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | NCHAR                           |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | VARBINARY                       |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | CHAR                            |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | TINYTEXT                        |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | BYTEA                           |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | CHARACTER                       |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | BYTE                            |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | CHAR_LARGE_OBJECT               |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | TINYINT                         |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | NCHAR_VARYING                   |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | BINARY_LARGE_OBJECT             |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | INT1_SIGNED                     |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | INT1                            |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | TINYINT_SIGNED                  |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | UInt8                           |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | INT1_UNSIGNED                   |
| INT32         | INT16               | repeated      | int16\tArray(Nullable(Int16))                                   | TINYINT_UNSIGNED                |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | String                          |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | Int8                            |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | GEOMETRY                        |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NATIONAL_CHAR_VARYING           |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | BINARY_VARYING                  |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NCHAR_LARGE_OBJECT              |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NATIONAL_CHARACTER              |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NATIONAL_CHAR                   |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CHARACTER_VARYING               |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | LONGBLOB                        |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | TINYBLOB                        |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CLOB                            |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | BLOB                            |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | MEDIUMTEXT                      |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | TEXT                            |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | VARCHAR2                        |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CHARACTER_LARGE_OBJECT          |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | LONGTEXT                        |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NVARCHAR                        |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | VARCHAR                         |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CHAR_VARYING                    |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | MEDIUMBLOB                      |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NCHAR                           |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | VARBINARY                       |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CHAR                            |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | TINYTEXT                        |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | BYTEA                           |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CHARACTER                       |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | BYTE                            |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CHAR_LARGE_OBJECT               |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | TINYINT                         |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NCHAR_VARYING                   |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | BINARY_LARGE_OBJECT             |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | INT1_SIGNED                     |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | INT1                            |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | TINYINT_SIGNED                  |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | UInt8                           |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | INT1_UNSIGNED                   |
| INT32         | INT16               | optionalGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | TINYINT_UNSIGNED                |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | String                          |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | UInt8                           |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | Int8                            |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | GEOMETRY                        |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NATIONAL_CHAR_VARYING           |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | BINARY_VARYING                  |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NCHAR_LARGE_OBJECT              |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NATIONAL_CHARACTER              |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NATIONAL_CHAR                   |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CHARACTER_VARYING               |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | LONGBLOB                        |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | TINYBLOB                        |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CLOB                            |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | BLOB                            |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | MEDIUMTEXT                      |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | TEXT                            |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | VARCHAR2                        |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CHARACTER_LARGE_OBJECT          |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | LONGTEXT                        |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NVARCHAR                        |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | INT1_UNSIGNED                   |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | VARCHAR                         |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CHAR_VARYING                    |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | MEDIUMBLOB                      |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NCHAR                           |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | VARBINARY                       |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CHAR                            |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | TINYTEXT                        |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | BYTEA                           |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | TINYINT_UNSIGNED                |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CHARACTER                       |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | BYTE                            |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | CHAR_LARGE_OBJECT               |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | TINYINT                         |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | NCHAR_VARYING                   |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | BINARY_LARGE_OBJECT             |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | INT1_SIGNED                     |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | INT1                            |
| INT32         | INT16               | requiredGroup | int16\tTuple(\\n    int16 Array(Nullable(Int16)))               | TINYINT_SIGNED                  |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | String                          |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | Int8                            |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | GEOMETRY                        |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | NATIONAL_CHAR_VARYING           |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | BINARY_VARYING                  |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | NCHAR_LARGE_OBJECT              |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | NATIONAL_CHARACTER              |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | NATIONAL_CHAR                   |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | CHARACTER_VARYING               |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | LONGBLOB                        |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | TINYBLOB                        |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | CLOB                            |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | BLOB                            |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | MEDIUMTEXT                      |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | TEXT                            |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | VARCHAR2                        |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | CHARACTER_LARGE_OBJECT          |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | LONGTEXT                        |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | NVARCHAR                        |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | VARCHAR                         |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | CHAR_VARYING                    |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | MEDIUMBLOB                      |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | NCHAR                           |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | VARBINARY                       |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | CHAR                            |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | TINYTEXT                        |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | BYTEA                           |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | CHARACTER                       |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | BYTE                            |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | CHAR_LARGE_OBJECT               |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | TINYINT                         |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | NCHAR_VARYING                   |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | BINARY_LARGE_OBJECT             |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | INT1_SIGNED                     |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | INT1                            |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | TINYINT_SIGNED                  |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | UInt8                           |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | INT1_UNSIGNED                   |
| INT32         | INT16               | repeatedGroup | int16\tArray(Tuple(\\n    int16 Array(Nullable(Int16))))        | TINYINT_UNSIGNED                |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | Int64                           |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | Int16                           |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | UInt256                         |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | String                          |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | DateTime                        |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | Int32                           |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | UInt8                           |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | UInt128                         |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | Float64                         |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | UInt16                          |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | Int128                          |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | Int8                            |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | Decimal                         |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | Int256                          |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | DateTime64                      |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | DateTime32                      |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | UInt64                          |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | UInt32                          |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | Float32                         |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | GEOMETRY                        |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | NATIONAL_CHAR_VARYING           |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | BINARY_VARYING                  |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | NCHAR_LARGE_OBJECT              |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | NATIONAL_CHARACTER              |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | NATIONAL_CHAR                   |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | CHARACTER_VARYING               |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | LONGBLOB                        |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | TINYBLOB                        |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | CLOB                            |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | BLOB                            |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | MEDIUMTEXT                      |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | TEXT                            |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | VARCHAR2                        |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | CHARACTER_LARGE_OBJECT          |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | DOUBLE_PRECISION                |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | LONGTEXT                        |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | NVARCHAR                        |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | INT1_UNSIGNED                   |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | VARCHAR                         |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | CHAR_VARYING                    |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | MEDIUMBLOB                      |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | NCHAR                           |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | VARBINARY                       |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | CHAR                            |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | SMALLINT_UNSIGNED               |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | TIMESTAMP                       |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | FIXED                           |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | TINYTEXT                        |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | NUMERIC                         |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | DEC                             |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | DOUBLE                          |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | BYTEA                           |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | INT                             |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | SINGLE                          |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | BIT                             |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | BIGINT_UNSIGNED                 |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | UNSIGNED                        |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | TINYINT_UNSIGNED                |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | INTEGER_UNSIGNED                |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | INT_UNSIGNED                    |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | REAL                            |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | CHARACTER                       |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | BYTE                            |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | SIGNED                          |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | MEDIUMINT                       |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | YEAR                            |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | CHAR_LARGE_OBJECT               |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | TINYINT                         |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | BIGINT                          |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | SMALLINT                        |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | INTEGER_SIGNED                  |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | NCHAR_VARYING                   |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | INT_SIGNED                      |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | BIGINT_SIGNED                   |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | BINARY_LARGE_OBJECT             |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | SMALLINT_SIGNED                 |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | FLOAT                           |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | SET                             |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | TIME                            |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | MEDIUMINT_SIGNED                |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | INT1_SIGNED                     |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | INTEGER                         |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | MEDIUMINT_UNSIGNED              |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | INT1                            |
| INT32         | INT32               | optional      | int32\tNullable(Int32)                                          | TINYINT_SIGNED                  |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | Int64                           |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | Int16                           |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | String                          |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | Int32                           |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | Float64                         |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | Int128                          |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | Int8                            |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | Decimal                         |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | Int256                          |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | DateTime64                      |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | Float32                         |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | GEOMETRY                        |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | NATIONAL_CHAR_VARYING           |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | BINARY_VARYING                  |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | NCHAR_LARGE_OBJECT              |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | NATIONAL_CHARACTER              |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | NATIONAL_CHAR                   |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | CHARACTER_VARYING               |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | LONGBLOB                        |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | TINYBLOB                        |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | CLOB                            |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | BLOB                            |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | MEDIUMTEXT                      |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | TEXT                            |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | VARCHAR2                        |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | CHARACTER_LARGE_OBJECT          |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | DOUBLE_PRECISION                |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | LONGTEXT                        |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | NVARCHAR                        |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | VARCHAR                         |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | CHAR_VARYING                    |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | MEDIUMBLOB                      |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | NCHAR                           |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | VARBINARY                       |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | CHAR                            |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | FIXED                           |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | TINYTEXT                        |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | NUMERIC                         |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | DEC                             |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | DOUBLE                          |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | BYTEA                           |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | INT                             |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | SINGLE                          |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | REAL                            |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | CHARACTER                       |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | BYTE                            |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | SIGNED                          |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | MEDIUMINT                       |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | CHAR_LARGE_OBJECT               |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | TINYINT                         |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | BIGINT                          |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | SMALLINT                        |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | INTEGER_SIGNED                  |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | NCHAR_VARYING                   |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | INT_SIGNED                      |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | BIGINT_SIGNED                   |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | BINARY_LARGE_OBJECT             |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | SMALLINT_SIGNED                 |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | FLOAT                           |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | TIME                            |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | MEDIUMINT_SIGNED                |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | INT1_SIGNED                     |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | INTEGER                         |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | INT1                            |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | TINYINT_SIGNED                  |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | UInt256                         |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | DateTime                        |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | UInt8                           |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | UInt128                         |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | UInt16                          |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | DateTime32                      |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | UInt64                          |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | UInt32                          |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | INT1_UNSIGNED                   |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | SMALLINT_UNSIGNED               |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | TIMESTAMP                       |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | BIT                             |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | BIGINT_UNSIGNED                 |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | UNSIGNED                        |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | TINYINT_UNSIGNED                |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | INTEGER_UNSIGNED                |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | INT_UNSIGNED                    |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | YEAR                            |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | SET                             |
| INT32         | INT32               | required      | int32\tNullable(Int32)                                          | MEDIUMINT_UNSIGNED              |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | Int16                           |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | String                          |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | UInt8                           |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | UInt16                          |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | Int8                            |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | GEOMETRY                        |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | NATIONAL_CHAR_VARYING           |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | BINARY_VARYING                  |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | NCHAR_LARGE_OBJECT              |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | NATIONAL_CHARACTER              |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | NATIONAL_CHAR                   |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | CHARACTER_VARYING               |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | LONGBLOB                        |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | TINYBLOB                        |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | CLOB                            |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | BLOB                            |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | MEDIUMTEXT                      |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | TEXT                            |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | VARCHAR2                        |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | CHARACTER_LARGE_OBJECT          |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | LONGTEXT                        |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | NVARCHAR                        |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | INT1_UNSIGNED                   |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | VARCHAR                         |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | CHAR_VARYING                    |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | MEDIUMBLOB                      |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | NCHAR                           |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | VARBINARY                       |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | CHAR                            |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | SMALLINT_UNSIGNED               |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | TINYTEXT                        |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | BYTEA                           |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | TINYINT_UNSIGNED                |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | CHARACTER                       |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | BYTE                            |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | YEAR                            |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | CHAR_LARGE_OBJECT               |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | TINYINT                         |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | SMALLINT                        |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | NCHAR_VARYING                   |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | BINARY_LARGE_OBJECT             |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | SMALLINT_SIGNED                 |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | INT1_SIGNED                     |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | INT1                            |
| INT32         | INT32               | repeated      | int32\tArray(Nullable(Int32))                                   | TINYINT_SIGNED                  |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | Int16                           |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | String                          |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | Int8                            |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | GEOMETRY                        |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NATIONAL_CHAR_VARYING           |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | BINARY_VARYING                  |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NCHAR_LARGE_OBJECT              |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NATIONAL_CHARACTER              |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NATIONAL_CHAR                   |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CHARACTER_VARYING               |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | LONGBLOB                        |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | TINYBLOB                        |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CLOB                            |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | BLOB                            |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | MEDIUMTEXT                      |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | TEXT                            |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | VARCHAR2                        |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CHARACTER_LARGE_OBJECT          |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | LONGTEXT                        |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NVARCHAR                        |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | VARCHAR                         |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CHAR_VARYING                    |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | MEDIUMBLOB                      |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NCHAR                           |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | VARBINARY                       |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CHAR                            |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | TINYTEXT                        |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | BYTEA                           |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CHARACTER                       |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | BYTE                            |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CHAR_LARGE_OBJECT               |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | TINYINT                         |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | SMALLINT                        |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NCHAR_VARYING                   |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | BINARY_LARGE_OBJECT             |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | SMALLINT_SIGNED                 |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | INT1_SIGNED                     |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | INT1                            |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | TINYINT_SIGNED                  |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | UInt8                           |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | UInt16                          |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | INT1_UNSIGNED                   |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | SMALLINT_UNSIGNED               |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | TINYINT_UNSIGNED                |
| INT32         | INT32               | optionalGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | YEAR                            |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | Int16                           |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | String                          |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | Int8                            |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | GEOMETRY                        |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NATIONAL_CHAR_VARYING           |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | BINARY_VARYING                  |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NCHAR_LARGE_OBJECT              |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NATIONAL_CHARACTER              |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NATIONAL_CHAR                   |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CHARACTER_VARYING               |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | LONGBLOB                        |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | TINYBLOB                        |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CLOB                            |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | BLOB                            |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | MEDIUMTEXT                      |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | TEXT                            |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | VARCHAR2                        |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CHARACTER_LARGE_OBJECT          |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | LONGTEXT                        |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NVARCHAR                        |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | VARCHAR                         |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CHAR_VARYING                    |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | MEDIUMBLOB                      |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NCHAR                           |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | VARBINARY                       |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CHAR                            |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | TINYTEXT                        |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | BYTEA                           |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CHARACTER                       |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | BYTE                            |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | CHAR_LARGE_OBJECT               |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | TINYINT                         |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | SMALLINT                        |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | NCHAR_VARYING                   |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | BINARY_LARGE_OBJECT             |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | SMALLINT_SIGNED                 |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | INT1_SIGNED                     |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | INT1                            |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | TINYINT_SIGNED                  |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | UInt8                           |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | UInt16                          |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | INT1_UNSIGNED                   |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | SMALLINT_UNSIGNED               |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | TINYINT_UNSIGNED                |
| INT32         | INT32               | requiredGroup | int32\tTuple(\\n    int32 Array(Nullable(Int32)))               | YEAR                            |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | Int16                           |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | String                          |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | Int8                            |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | GEOMETRY                        |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | NATIONAL_CHAR_VARYING           |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | BINARY_VARYING                  |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | NCHAR_LARGE_OBJECT              |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | NATIONAL_CHARACTER_VARYING      |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | NATIONAL_CHARACTER              |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | NATIONAL_CHAR                   |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | CHARACTER_VARYING               |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | LONGBLOB                        |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | TINYBLOB                        |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | CLOB                            |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | BLOB                            |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | MEDIUMTEXT                      |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | TEXT                            |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | VARCHAR2                        |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | CHARACTER_LARGE_OBJECT          |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | LONGTEXT                        |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | NVARCHAR                        |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | VARCHAR                         |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | CHAR_VARYING                    |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | MEDIUMBLOB                      |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | NCHAR                           |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | VARBINARY                       |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | CHAR                            |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | TINYTEXT                        |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | BYTEA                           |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | CHARACTER                       |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | BYTE                            |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | CHAR_LARGE_OBJECT               |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | TINYINT                         |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | SMALLINT                        |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | NCHAR_VARYING                   |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | BINARY_LARGE_OBJECT             |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | SMALLINT_SIGNED                 |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | INT1_SIGNED                     |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | INT1                            |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | TINYINT_SIGNED                  |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | UInt8                           |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | UInt16                          |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | INT1_UNSIGNED                   |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | SMALLINT_UNSIGNED               |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | TINYINT_UNSIGNED                |
| INT32         | INT32               | repeatedGroup | int32\tArray(Tuple(\\n    int32 Array(Nullable(Int32))))        | YEAR                            |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | Int64                           |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | Int16                           |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | String                          |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | Int32                           |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | Float64                         |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | Int128                          |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | Int8                            |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | Decimal                         |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | Int256                          |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | Float32                         |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | GEOMETRY                        |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | NATIONAL_CHAR_VARYING           |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | BINARY_VARYING                  |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | NCHAR_LARGE_OBJECT              |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | NATIONAL_CHARACTER_VARYING      |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | NATIONAL_CHARACTER              |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | NATIONAL_CHAR                   |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | CHARACTER_VARYING               |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | LONGBLOB                        |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | TINYBLOB                        |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | CLOB                            |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | BLOB                            |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | MEDIUMTEXT                      |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | TEXT                            |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | VARCHAR2                        |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | CHARACTER_LARGE_OBJECT          |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | DOUBLE_PRECISION                |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | LONGTEXT                        |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | NVARCHAR                        |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | VARCHAR                         |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | CHAR_VARYING                    |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | MEDIUMBLOB                      |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | NCHAR                           |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | VARBINARY                       |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | CHAR                            |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | FIXED                           |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | TINYTEXT                        |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | NUMERIC                         |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | DEC                             |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | DOUBLE                          |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | BYTEA                           |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | INT                             |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | SINGLE                          |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | REAL                            |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | CHARACTER                       |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | BYTE                            |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | SIGNED                          |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | MEDIUMINT                       |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | CHAR_LARGE_OBJECT               |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | TINYINT                         |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | BIGINT                          |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | SMALLINT                        |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | INTEGER_SIGNED                  |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | NCHAR_VARYING                   |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | INT_SIGNED                      |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | BIGINT_SIGNED                   |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | BINARY_LARGE_OBJECT             |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | SMALLINT_SIGNED                 |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | FLOAT                           |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | TIME                            |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | MEDIUMINT_SIGNED                |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | INT1_SIGNED                     |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | INTEGER                         |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | INT1                            |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | TINYINT_SIGNED                  |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | UInt256                         |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | DateTime                        |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | UInt8                           |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | UInt128                         |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | UInt16                          |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | DateTime64                      |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | DateTime32                      |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | UInt64                          |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | UInt32                          |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | INT1_UNSIGNED                   |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | SMALLINT_UNSIGNED               |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | TIMESTAMP                       |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | BIT                             |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | BIGINT_UNSIGNED                 |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | UNSIGNED                        |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | TINYINT_UNSIGNED                |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | INTEGER_UNSIGNED                |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | INT_UNSIGNED                    |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | YEAR                            |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | SET                             |
| INT64         | INT64               | optional      | int64\tNullable(Int64)                                          | MEDIUMINT_UNSIGNED              |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | Int64                           |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | Int16                           |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | UInt256                         |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | String                          |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | DateTime                        |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | Int32                           |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | UInt8                           |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | UInt128                         |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | Float64                         |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | UInt16                          |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | Int128                          |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | Int8                            |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | Decimal                         |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | Int256                          |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | DateTime64                      |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | DateTime32                      |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | UInt64                          |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | UInt32                          |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | Float32                         |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | GEOMETRY                        |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | NATIONAL_CHAR_VARYING           |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | BINARY_VARYING                  |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | NCHAR_LARGE_OBJECT              |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | NATIONAL_CHARACTER_VARYING      |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | NATIONAL_CHARACTER              |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | NATIONAL_CHAR                   |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | CHARACTER_VARYING               |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | LONGBLOB                        |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | TINYBLOB                        |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | CLOB                            |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | BLOB                            |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | MEDIUMTEXT                      |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | TEXT                            |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | VARCHAR2                        |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | CHARACTER_LARGE_OBJECT          |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | DOUBLE_PRECISION                |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | LONGTEXT                        |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | NVARCHAR                        |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | INT1_UNSIGNED                   |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | VARCHAR                         |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | CHAR_VARYING                    |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | MEDIUMBLOB                      |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | NCHAR                           |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | VARBINARY                       |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | CHAR                            |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | SMALLINT_UNSIGNED               |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | TIMESTAMP                       |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | FIXED                           |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | TINYTEXT                        |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | NUMERIC                         |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | DEC                             |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | DOUBLE                          |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | BYTEA                           |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | INT                             |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | SINGLE                          |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | BIT                             |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | BIGINT_UNSIGNED                 |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | UNSIGNED                        |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | TINYINT_UNSIGNED                |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | INTEGER_UNSIGNED                |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | INT_UNSIGNED                    |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | REAL                            |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | CHARACTER                       |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | BYTE                            |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | SIGNED                          |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | MEDIUMINT                       |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | YEAR                            |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | CHAR_LARGE_OBJECT               |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | TINYINT                         |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | BIGINT                          |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | SMALLINT                        |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | INTEGER_SIGNED                  |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | NCHAR_VARYING                   |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | INT_SIGNED                      |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | BIGINT_SIGNED                   |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | BINARY_LARGE_OBJECT             |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | SMALLINT_SIGNED                 |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | FLOAT                           |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | SET                             |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | TIME                            |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | MEDIUMINT_SIGNED                |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | INT1_SIGNED                     |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | INTEGER                         |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | MEDIUMINT_UNSIGNED              |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | INT1                            |
| INT64         | INT64               | required      | int64\tNullable(Int64)                                          | TINYINT_SIGNED                  |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | Int16                           |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | String                          |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | Int32                           |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | UInt8                           |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | UInt16                          |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | Int8                            |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | UInt32                          |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | GEOMETRY                        |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | NATIONAL_CHAR_VARYING           |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | BINARY_VARYING                  |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | NCHAR_LARGE_OBJECT              |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | NATIONAL_CHARACTER_VARYING      |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | NATIONAL_CHARACTER              |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | NATIONAL_CHAR                   |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | CHARACTER_VARYING               |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | LONGBLOB                        |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | TINYBLOB                        |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | CLOB                            |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | BLOB                            |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | MEDIUMTEXT                      |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | TEXT                            |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | VARCHAR2                        |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | CHARACTER_LARGE_OBJECT          |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | LONGTEXT                        |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | NVARCHAR                        |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | INT1_UNSIGNED                   |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | VARCHAR                         |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | CHAR_VARYING                    |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | MEDIUMBLOB                      |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | NCHAR                           |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | VARBINARY                       |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | CHAR                            |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | SMALLINT_UNSIGNED               |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | TINYTEXT                        |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | BYTEA                           |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | INT                             |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | TINYINT_UNSIGNED                |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | INTEGER_UNSIGNED                |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | INT_UNSIGNED                    |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | CHARACTER                       |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | BYTE                            |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | MEDIUMINT                       |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | YEAR                            |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | CHAR_LARGE_OBJECT               |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | TINYINT                         |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | SMALLINT                        |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | INTEGER_SIGNED                  |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | NCHAR_VARYING                   |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | INT_SIGNED                      |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | BINARY_LARGE_OBJECT             |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | SMALLINT_SIGNED                 |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | MEDIUMINT_SIGNED                |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | INT1_SIGNED                     |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | INTEGER                         |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | MEDIUMINT_UNSIGNED              |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | INT1                            |
| INT64         | INT64               | repeated      | int64\tArray(Nullable(Int64))                                   | TINYINT_SIGNED                  |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | Int16                           |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | String                          |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | Int32                           |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | UInt8                           |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | UInt16                          |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | Int8                            |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | UInt32                          |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | GEOMETRY                        |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NATIONAL_CHAR_VARYING           |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | BINARY_VARYING                  |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NCHAR_LARGE_OBJECT              |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NATIONAL_CHARACTER_VARYING      |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NATIONAL_CHARACTER              |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NATIONAL_CHAR                   |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CHARACTER_VARYING               |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | LONGBLOB                        |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | TINYBLOB                        |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CLOB                            |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | BLOB                            |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | MEDIUMTEXT                      |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | TEXT                            |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | VARCHAR2                        |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CHARACTER_LARGE_OBJECT          |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | LONGTEXT                        |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NVARCHAR                        |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INT1_UNSIGNED                   |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | VARCHAR                         |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CHAR_VARYING                    |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | MEDIUMBLOB                      |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NCHAR                           |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | VARBINARY                       |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CHAR                            |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | SMALLINT_UNSIGNED               |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | TINYTEXT                        |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | BYTEA                           |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INT                             |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | TINYINT_UNSIGNED                |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INTEGER_UNSIGNED                |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INT_UNSIGNED                    |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CHARACTER                       |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | BYTE                            |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | MEDIUMINT                       |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | YEAR                            |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CHAR_LARGE_OBJECT               |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | TINYINT                         |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | SMALLINT                        |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INTEGER_SIGNED                  |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NCHAR_VARYING                   |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INT_SIGNED                      |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | BINARY_LARGE_OBJECT             |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | SMALLINT_SIGNED                 |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | MEDIUMINT_SIGNED                |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INT1_SIGNED                     |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INTEGER                         |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | MEDIUMINT_UNSIGNED              |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INT1                            |
| INT64         | INT64               | optionalGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | TINYINT_SIGNED                  |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | Int16                           |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | String                          |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | Int32                           |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | Int8                            |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | GEOMETRY                        |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NATIONAL_CHAR_VARYING           |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | BINARY_VARYING                  |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NCHAR_LARGE_OBJECT              |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NATIONAL_CHARACTER_VARYING      |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NATIONAL_CHARACTER              |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NATIONAL_CHAR                   |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CHARACTER_VARYING               |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | LONGBLOB                        |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | TINYBLOB                        |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CLOB                            |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | BLOB                            |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | MEDIUMTEXT                      |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | TEXT                            |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | VARCHAR2                        |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CHARACTER_LARGE_OBJECT          |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | LONGTEXT                        |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NVARCHAR                        |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | VARCHAR                         |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CHAR_VARYING                    |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | MEDIUMBLOB                      |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NCHAR                           |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | VARBINARY                       |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CHAR                            |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | TINYTEXT                        |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | BYTEA                           |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INT                             |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CHARACTER                       |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | BYTE                            |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | MEDIUMINT                       |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | CHAR_LARGE_OBJECT               |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | TINYINT                         |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | SMALLINT                        |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INTEGER_SIGNED                  |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | NCHAR_VARYING                   |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INT_SIGNED                      |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | BINARY_LARGE_OBJECT             |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | SMALLINT_SIGNED                 |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | MEDIUMINT_SIGNED                |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INT1_SIGNED                     |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INTEGER                         |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INT1                            |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | TINYINT_SIGNED                  |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | UInt8                           |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | UInt16                          |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | UInt32                          |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INT1_UNSIGNED                   |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | SMALLINT_UNSIGNED               |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | TINYINT_UNSIGNED                |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INTEGER_UNSIGNED                |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | INT_UNSIGNED                    |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | YEAR                            |
| INT64         | INT64               | requiredGroup | int64\tTuple(\\n    int64 Array(Nullable(Int64)))               | MEDIUMINT_UNSIGNED              |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | Int16                           |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | String                          |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | Int32                           |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | UInt8                           |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | UInt16                          |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | Int8                            |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | UInt32                          |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | GEOMETRY                        |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | NATIONAL_CHAR_VARYING           |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | BINARY_VARYING                  |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | NCHAR_LARGE_OBJECT              |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | NATIONAL_CHARACTER_VARYING      |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | NATIONAL_CHARACTER              |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | NATIONAL_CHAR                   |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | CHARACTER_VARYING               |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | LONGBLOB                        |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | TINYBLOB                        |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | CLOB                            |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | BLOB                            |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | MEDIUMTEXT                      |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | TEXT                            |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | VARCHAR2                        |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | CHARACTER_LARGE_OBJECT          |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | LONGTEXT                        |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | NVARCHAR                        |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | INT1_UNSIGNED                   |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | VARCHAR                         |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | CHAR_VARYING                    |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | MEDIUMBLOB                      |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | NCHAR                           |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | VARBINARY                       |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | CHAR                            |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | SMALLINT_UNSIGNED               |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | TINYTEXT                        |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | BYTEA                           |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | INT                             |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | TINYINT_UNSIGNED                |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | INTEGER_UNSIGNED                |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | INT_UNSIGNED                    |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | CHARACTER                       |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | BYTE                            |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | MEDIUMINT                       |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | YEAR                            |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | CHAR_LARGE_OBJECT               |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | TINYINT                         |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | SMALLINT                        |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | INTEGER_SIGNED                  |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | NCHAR_VARYING                   |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | INT_SIGNED                      |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | BINARY_LARGE_OBJECT             |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | SMALLINT_SIGNED                 |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | MEDIUMINT_SIGNED                |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | INT1_SIGNED                     |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | INTEGER                         |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | MEDIUMINT_UNSIGNED              |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | INT1                            |
| INT64         | INT64               | repeatedGroup | int64\tArray(Tuple(\\n    int64 Array(Nullable(Int64))))        | TINYINT_SIGNED                  |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | Int64                           |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | Int16                           |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | String                          |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | Int32                           |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | Float64                         |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | Int128                          |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | Int8                            |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | Decimal                         |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | Int256                          |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | DateTime64                      |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | Float32                         |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | GEOMETRY                        |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | NATIONAL_CHAR_VARYING           |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | BINARY_VARYING                  |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | NCHAR_LARGE_OBJECT              |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | NATIONAL_CHARACTER_VARYING      |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | NATIONAL_CHARACTER              |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | NATIONAL_CHAR                   |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | CHARACTER_VARYING               |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | LONGBLOB                        |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | TINYBLOB                        |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | CLOB                            |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | BLOB                            |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | MEDIUMTEXT                      |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | TEXT                            |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | VARCHAR2                        |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | CHARACTER_LARGE_OBJECT          |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | DOUBLE_PRECISION                |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | LONGTEXT                        |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | NVARCHAR                        |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | VARCHAR                         |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | CHAR_VARYING                    |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | MEDIUMBLOB                      |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | NCHAR                           |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | VARBINARY                       |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | CHAR                            |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | FIXED                           |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | TINYTEXT                        |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | NUMERIC                         |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | DEC                             |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | DOUBLE                          |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | BYTEA                           |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | INT                             |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | SINGLE                          |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | REAL                            |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | CHARACTER                       |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | BYTE                            |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | SIGNED                          |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | MEDIUMINT                       |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | CHAR_LARGE_OBJECT               |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | TINYINT                         |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | BIGINT                          |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | SMALLINT                        |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | INTEGER_SIGNED                  |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | NCHAR_VARYING                   |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | INT_SIGNED                      |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | BIGINT_SIGNED                   |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | BINARY_LARGE_OBJECT             |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | SMALLINT_SIGNED                 |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | FLOAT                           |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | TIME                            |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | MEDIUMINT_SIGNED                |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | INT1_SIGNED                     |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | INTEGER                         |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | INT1                            |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | TINYINT_SIGNED                  |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | UInt256                         |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | DateTime                        |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | UInt8                           |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | UInt128                         |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | UInt16                          |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | DateTime32                      |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | UInt64                          |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | UInt32                          |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | INT1_UNSIGNED                   |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | SMALLINT_UNSIGNED               |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | TIMESTAMP                       |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | BIT                             |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | BIGINT_UNSIGNED                 |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | UNSIGNED                        |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | TINYINT_UNSIGNED                |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | INTEGER_UNSIGNED                |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | INT_UNSIGNED                    |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | YEAR                            |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | SET                             |
| INT32         | NONE                | optional      | none\tNullable(Int32)                                           | MEDIUMINT_UNSIGNED              |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | Int64                           |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | Int16                           |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | UInt256                         |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | String                          |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | DateTime                        |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | Int32                           |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | UInt8                           |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | UInt128                         |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | Float64                         |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | UInt16                          |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | Int128                          |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | Int8                            |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | Decimal                         |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | Int256                          |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | DateTime64                      |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | DateTime32                      |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | UInt64                          |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | UInt32                          |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | Float32                         |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | GEOMETRY                        |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | NATIONAL_CHAR_VARYING           |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | BINARY_VARYING                  |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | NCHAR_LARGE_OBJECT              |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | NATIONAL_CHARACTER_VARYING      |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | NATIONAL_CHARACTER              |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | NATIONAL_CHAR                   |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | CHARACTER_VARYING               |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | LONGBLOB                        |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | TINYBLOB                        |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | CLOB                            |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | BLOB                            |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | MEDIUMTEXT                      |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | TEXT                            |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | VARCHAR2                        |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | CHARACTER_LARGE_OBJECT          |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | DOUBLE_PRECISION                |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | LONGTEXT                        |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | NVARCHAR                        |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | INT1_UNSIGNED                   |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | VARCHAR                         |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | CHAR_VARYING                    |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | MEDIUMBLOB                      |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | NCHAR                           |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | VARBINARY                       |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | CHAR                            |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | SMALLINT_UNSIGNED               |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | TIMESTAMP                       |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | FIXED                           |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | TINYTEXT                        |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | NUMERIC                         |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | DEC                             |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | DOUBLE                          |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | BYTEA                           |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | INT                             |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | SINGLE                          |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | BIT                             |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | BIGINT_UNSIGNED                 |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | UNSIGNED                        |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | TINYINT_UNSIGNED                |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | INTEGER_UNSIGNED                |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | INT_UNSIGNED                    |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | REAL                            |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | CHARACTER                       |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | BYTE                            |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | SIGNED                          |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | MEDIUMINT                       |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | YEAR                            |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | CHAR_LARGE_OBJECT               |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | TINYINT                         |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | BIGINT                          |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | SMALLINT                        |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | INTEGER_SIGNED                  |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | NCHAR_VARYING                   |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | INT_SIGNED                      |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | BIGINT_SIGNED                   |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | BINARY_LARGE_OBJECT             |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | SMALLINT_SIGNED                 |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | FLOAT                           |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | SET                             |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | TIME                            |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | MEDIUMINT_SIGNED                |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | INT1_SIGNED                     |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | INTEGER                         |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | MEDIUMINT_UNSIGNED              |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | INT1                            |
| INT64         | NONE                | optional      | none\tNullable(Int64)                                           | TINYINT_SIGNED                  |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | Bool                            |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | String                          |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | bool                            |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | GEOMETRY                        |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | NATIONAL_CHAR_VARYING           |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | BINARY_VARYING                  |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | NCHAR_LARGE_OBJECT              |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | NATIONAL_CHARACTER_VARYING      |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | boolean                         |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | NATIONAL_CHARACTER_LARGE_OBJECT |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | NATIONAL_CHARACTER              |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | NATIONAL_CHAR                   |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | CHARACTER_VARYING               |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | LONGBLOB                        |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | TINYBLOB                        |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | CLOB                            |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | BLOB                            |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | MEDIUMTEXT                      |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | TEXT                            |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | VARCHAR2                        |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | CHARACTER_LARGE_OBJECT          |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | LONGTEXT                        |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | NVARCHAR                        |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | VARCHAR                         |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | CHAR_VARYING                    |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | MEDIUMBLOB                      |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | NCHAR                           |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | VARBINARY                       |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | CHAR                            |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | TINYTEXT                        |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | BYTEA                           |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | CHARACTER                       |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | CHAR_LARGE_OBJECT               |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | NCHAR_VARYING                   |
| BOOLEAN       | NONE                | optional      | none\tNullable(Bool)                                            | BINARY_LARGE_OBJECT             |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | String                          |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | GEOMETRY                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | NATIONAL_CHAR_VARYING           |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | BINARY_VARYING                  |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | NCHAR_LARGE_OBJECT              |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | NATIONAL_CHARACTER_VARYING      |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | NATIONAL_CHARACTER_LARGE_OBJECT |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | NATIONAL_CHARACTER              |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | NATIONAL_CHAR                   |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | CHARACTER_VARYING               |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | LONGBLOB                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | TINYBLOB                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | CLOB                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | BLOB                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | MEDIUMTEXT                      |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | TEXT                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | VARCHAR2                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | CHARACTER_LARGE_OBJECT          |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | LONGTEXT                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | NVARCHAR                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | VARCHAR                         |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | CHAR_VARYING                    |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | MEDIUMBLOB                      |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | NCHAR                           |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | VARBINARY                       |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | CHAR                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | TINYTEXT                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | BYTEA                           |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | CHARACTER                       |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | CHAR_LARGE_OBJECT               |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | NCHAR_VARYING                   |
| FIXED         | LEN_BYTE_ARRAY_NONE | optional      | none\tNullable(FixedString(3))                                  | BINARY_LARGE_OBJECT             |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | Int64                           |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | Int16                           |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | UInt256                         |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | String                          |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | DateTime                        |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | Int32                           |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | UInt8                           |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | Date                            |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | UInt128                         |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | Float64                         |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | UInt16                          |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | Int128                          |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | Int8                            |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | Decimal                         |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | Int256                          |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | DateTime64                      |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | DateTime32                      |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | Date32                          |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | UInt64                          |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | UInt32                          |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | Float32                         |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | GEOMETRY                        |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | NATIONAL_CHAR_VARYING           |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | BINARY_VARYING                  |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | NCHAR_LARGE_OBJECT              |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | NATIONAL_CHARACTER_VARYING      |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | NATIONAL_CHARACTER              |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | NATIONAL_CHAR                   |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | CHARACTER_VARYING               |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | LONGBLOB                        |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | TINYBLOB                        |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | CLOB                            |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | BLOB                            |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | MEDIUMTEXT                      |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | TEXT                            |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | VARCHAR2                        |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | CHARACTER_LARGE_OBJECT          |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | DOUBLE_PRECISION                |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | LONGTEXT                        |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | NVARCHAR                        |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | INT1_UNSIGNED                   |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | VARCHAR                         |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | CHAR_VARYING                    |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | MEDIUMBLOB                      |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | NCHAR                           |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | VARBINARY                       |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | CHAR                            |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | SMALLINT_UNSIGNED               |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | TIMESTAMP                       |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | FIXED                           |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | TINYTEXT                        |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | NUMERIC                         |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | DEC                             |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | DOUBLE                          |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | BYTEA                           |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | INT                             |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | SINGLE                          |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | BIT                             |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | BIGINT_UNSIGNED                 |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | UNSIGNED                        |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | TINYINT_UNSIGNED                |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | INTEGER_UNSIGNED                |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | INT_UNSIGNED                    |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | REAL                            |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | CHARACTER                       |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | BYTE                            |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | SIGNED                          |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | MEDIUMINT                       |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | YEAR                            |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | CHAR_LARGE_OBJECT               |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | TINYINT                         |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | BIGINT                          |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | SMALLINT                        |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | INTEGER_SIGNED                  |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | NCHAR_VARYING                   |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | INT_SIGNED                      |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | BIGINT_SIGNED                   |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | BINARY_LARGE_OBJECT             |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | SMALLINT_SIGNED                 |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | FLOAT                           |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | SET                             |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | TIME                            |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | MEDIUMINT_SIGNED                |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | INT1_SIGNED                     |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | INTEGER                         |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | MEDIUMINT_UNSIGNED              |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | INT1                            |
| INT32         | NONE                | required      | none\tNullable(Int32)                                           | TINYINT_SIGNED                  |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | Int64                           |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | Int16                           |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | UInt256                         |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | String                          |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | DateTime                        |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | Int32                           |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | UInt8                           |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | UInt128                         |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | Float64                         |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | UInt16                          |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | Int128                          |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | Int8                            |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | Decimal                         |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | Int256                          |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | DateTime64                      |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | DateTime32                      |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | UInt64                          |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | UInt32                          |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | Float32                         |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | GEOMETRY                        |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | NATIONAL_CHAR_VARYING           |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | BINARY_VARYING                  |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | NCHAR_LARGE_OBJECT              |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | NATIONAL_CHARACTER_VARYING      |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | NATIONAL_CHARACTER              |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | NATIONAL_CHAR                   |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | CHARACTER_VARYING               |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | LONGBLOB                        |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | TINYBLOB                        |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | CLOB                            |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | BLOB                            |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | MEDIUMTEXT                      |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | TEXT                            |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | VARCHAR2                        |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | CHARACTER_LARGE_OBJECT          |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | DOUBLE_PRECISION                |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | LONGTEXT                        |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | NVARCHAR                        |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | INT1_UNSIGNED                   |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | VARCHAR                         |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | CHAR_VARYING                    |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | MEDIUMBLOB                      |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | NCHAR                           |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | VARBINARY                       |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | CHAR                            |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | SMALLINT_UNSIGNED               |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | TIMESTAMP                       |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | FIXED                           |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | TINYTEXT                        |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | NUMERIC                         |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | DEC                             |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | DOUBLE                          |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | BYTEA                           |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | INT                             |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | SINGLE                          |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | BIT                             |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | BIGINT_UNSIGNED                 |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | UNSIGNED                        |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | TINYINT_UNSIGNED                |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | INTEGER_UNSIGNED                |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | INT_UNSIGNED                    |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | REAL                            |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | CHARACTER                       |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | BYTE                            |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | SIGNED                          |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | MEDIUMINT                       |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | YEAR                            |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | CHAR_LARGE_OBJECT               |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | TINYINT                         |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | BIGINT                          |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | SMALLINT                        |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | INTEGER_SIGNED                  |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | NCHAR_VARYING                   |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | INT_SIGNED                      |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | BIGINT_SIGNED                   |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | BINARY_LARGE_OBJECT             |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | SMALLINT_SIGNED                 |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | FLOAT                           |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | SET                             |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | TIME                            |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | MEDIUMINT_SIGNED                |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | INT1_SIGNED                     |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | INTEGER                         |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | MEDIUMINT_UNSIGNED              |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | INT1                            |
| INT64         | NONE                | required      | none\tNullable(Int64)                                           | TINYINT_SIGNED                  |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | Bool                            |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | String                          |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | bool                            |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | GEOMETRY                        |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | NATIONAL_CHAR_VARYING           |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | BINARY_VARYING                  |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | NCHAR_LARGE_OBJECT              |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | NATIONAL_CHARACTER_VARYING      |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | boolean                         |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | NATIONAL_CHARACTER_LARGE_OBJECT |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | NATIONAL_CHARACTER              |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | NATIONAL_CHAR                   |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | CHARACTER_VARYING               |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | LONGBLOB                        |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | TINYBLOB                        |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | CLOB                            |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | BLOB                            |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | MEDIUMTEXT                      |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | TEXT                            |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | VARCHAR2                        |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | CHARACTER_LARGE_OBJECT          |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | LONGTEXT                        |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | NVARCHAR                        |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | VARCHAR                         |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | CHAR_VARYING                    |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | MEDIUMBLOB                      |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | NCHAR                           |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | VARBINARY                       |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | CHAR                            |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | TINYTEXT                        |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | BYTEA                           |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | CHARACTER                       |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | CHAR_LARGE_OBJECT               |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | NCHAR_VARYING                   |
| BOOLEAN       | NONE                | required      | none\tNullable(Bool)                                            | BINARY_LARGE_OBJECT             |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | String                          |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | GEOMETRY                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | NATIONAL_CHAR_VARYING           |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | BINARY_VARYING                  |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | NCHAR_LARGE_OBJECT              |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | NATIONAL_CHARACTER_VARYING      |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | NATIONAL_CHARACTER_LARGE_OBJECT |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | NATIONAL_CHARACTER              |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | NATIONAL_CHAR                   |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | CHARACTER_VARYING               |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | LONGBLOB                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | TINYBLOB                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | CLOB                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | BLOB                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | MEDIUMTEXT                      |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | TEXT                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | VARCHAR2                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | CHARACTER_LARGE_OBJECT          |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | LONGTEXT                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | NVARCHAR                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | VARCHAR                         |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | CHAR_VARYING                    |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | MEDIUMBLOB                      |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | NCHAR                           |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | VARBINARY                       |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | CHAR                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | TINYTEXT                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | BYTEA                           |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | CHARACTER                       |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | CHAR_LARGE_OBJECT               |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | NCHAR_VARYING                   |
| FIXED         | LEN_BYTE_ARRAY_NONE | required      | none\tNullable(FixedString(3))                                  | BINARY_LARGE_OBJECT             |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | Int64                           |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | Int16                           |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | String                          |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | Int32                           |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | Float64                         |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | Int128                          |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | Int8                            |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | Decimal                         |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | Int256                          |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | DateTime64                      |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | Float32                         |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | GEOMETRY                        |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | NATIONAL_CHAR_VARYING           |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | BINARY_VARYING                  |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | NCHAR_LARGE_OBJECT              |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | NATIONAL_CHARACTER_VARYING      |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | NATIONAL_CHARACTER              |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | NATIONAL_CHAR                   |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | CHARACTER_VARYING               |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | LONGBLOB                        |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | TINYBLOB                        |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | CLOB                            |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | BLOB                            |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | MEDIUMTEXT                      |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | TEXT                            |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | VARCHAR2                        |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | CHARACTER_LARGE_OBJECT          |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | DOUBLE_PRECISION                |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | LONGTEXT                        |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | NVARCHAR                        |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | VARCHAR                         |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | CHAR_VARYING                    |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | MEDIUMBLOB                      |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | NCHAR                           |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | VARBINARY                       |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | CHAR                            |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | FIXED                           |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | TINYTEXT                        |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | NUMERIC                         |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | DEC                             |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | DOUBLE                          |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | BYTEA                           |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | INT                             |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | SINGLE                          |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | REAL                            |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | CHARACTER                       |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | BYTE                            |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | SIGNED                          |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | MEDIUMINT                       |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | CHAR_LARGE_OBJECT               |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | TINYINT                         |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | BIGINT                          |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | SMALLINT                        |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | INTEGER_SIGNED                  |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | NCHAR_VARYING                   |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | INT_SIGNED                      |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | BIGINT_SIGNED                   |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | BINARY_LARGE_OBJECT             |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | SMALLINT_SIGNED                 |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | FLOAT                           |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | TIME                            |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | MEDIUMINT_SIGNED                |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | INT1_SIGNED                     |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | INTEGER                         |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | INT1                            |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | TINYINT_SIGNED                  |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | UInt256                         |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | DateTime                        |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | UInt8                           |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | UInt128                         |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | UInt16                          |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | DateTime32                      |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | UInt64                          |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | UInt32                          |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | INT1_UNSIGNED                   |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | SMALLINT_UNSIGNED               |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | TIMESTAMP                       |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | BIT                             |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | BIGINT_UNSIGNED                 |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | UNSIGNED                        |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | TINYINT_UNSIGNED                |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | INTEGER_UNSIGNED                |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | INT_UNSIGNED                    |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | YEAR                            |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | SET                             |
| INT32         | NONE                | repeated      | none\tArray(Nullable(Int32))                                    | MEDIUMINT_UNSIGNED              |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | Int64                           |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | Int16                           |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | UInt256                         |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | String                          |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | DateTime                        |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | Int32                           |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | UInt8                           |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | UInt128                         |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | Float64                         |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | UInt16                          |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | Int128                          |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | Int8                            |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | Decimal                         |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | Int256                          |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | DateTime64                      |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | DateTime32                      |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | UInt64                          |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | UInt32                          |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | Float32                         |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | GEOMETRY                        |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | NATIONAL_CHAR_VARYING           |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | BINARY_VARYING                  |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | NCHAR_LARGE_OBJECT              |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | NATIONAL_CHARACTER_VARYING      |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | NATIONAL_CHARACTER              |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | NATIONAL_CHAR                   |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | CHARACTER_VARYING               |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | LONGBLOB                        |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | TINYBLOB                        |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | CLOB                            |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | BLOB                            |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | MEDIUMTEXT                      |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | TEXT                            |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | VARCHAR2                        |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | CHARACTER_LARGE_OBJECT          |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | DOUBLE_PRECISION                |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | LONGTEXT                        |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | NVARCHAR                        |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | INT1_UNSIGNED                   |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | VARCHAR                         |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | CHAR_VARYING                    |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | MEDIUMBLOB                      |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | NCHAR                           |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | VARBINARY                       |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | CHAR                            |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | SMALLINT_UNSIGNED               |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | TIMESTAMP                       |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | FIXED                           |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | TINYTEXT                        |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | NUMERIC                         |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | DEC                             |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | DOUBLE                          |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | BYTEA                           |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | INT                             |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | SINGLE                          |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | BIT                             |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | BIGINT_UNSIGNED                 |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | UNSIGNED                        |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | TINYINT_UNSIGNED                |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | INTEGER_UNSIGNED                |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | INT_UNSIGNED                    |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | REAL                            |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | CHARACTER                       |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | BYTE                            |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | SIGNED                          |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | MEDIUMINT                       |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | YEAR                            |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | CHAR_LARGE_OBJECT               |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | TINYINT                         |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | BIGINT                          |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | SMALLINT                        |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | INTEGER_SIGNED                  |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | NCHAR_VARYING                   |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | INT_SIGNED                      |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | BIGINT_SIGNED                   |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | BINARY_LARGE_OBJECT             |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | SMALLINT_SIGNED                 |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | FLOAT                           |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | SET                             |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | TIME                            |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | MEDIUMINT_SIGNED                |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | INT1_SIGNED                     |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | INTEGER                         |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | MEDIUMINT_UNSIGNED              |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | INT1                            |
| INT64         | NONE                | repeated      | none\tArray(Nullable(Int64))                                    | TINYINT_SIGNED                  |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | Bool                            |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | String                          |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | bool                            |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | GEOMETRY                        |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | NATIONAL_CHAR_VARYING           |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | BINARY_VARYING                  |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | NCHAR_LARGE_OBJECT              |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | NATIONAL_CHARACTER_VARYING      |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | boolean                         |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | NATIONAL_CHARACTER_LARGE_OBJECT |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | NATIONAL_CHARACTER              |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | NATIONAL_CHAR                   |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | CHARACTER_VARYING               |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | LONGBLOB                        |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | TINYBLOB                        |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | CLOB                            |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | BLOB                            |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | MEDIUMTEXT                      |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | TEXT                            |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | VARCHAR2                        |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | CHARACTER_LARGE_OBJECT          |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | LONGTEXT                        |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | NVARCHAR                        |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | VARCHAR                         |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | CHAR_VARYING                    |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | MEDIUMBLOB                      |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | NCHAR                           |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | VARBINARY                       |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | CHAR                            |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | TINYTEXT                        |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | BYTEA                           |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | CHARACTER                       |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | CHAR_LARGE_OBJECT               |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | NCHAR_VARYING                   |
| BOOLEAN       | NONE                | repeated      | none\tArray(Nullable(Bool))                                     | BINARY_LARGE_OBJECT             |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | String                          |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | GEOMETRY                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | NATIONAL_CHAR_VARYING           |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | BINARY_VARYING                  |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | NCHAR_LARGE_OBJECT              |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | NATIONAL_CHARACTER_VARYING      |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | NATIONAL_CHARACTER_LARGE_OBJECT |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | NATIONAL_CHARACTER              |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | NATIONAL_CHAR                   |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | CHARACTER_VARYING               |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | LONGBLOB                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | TINYBLOB                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | CLOB                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | BLOB                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | MEDIUMTEXT                      |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | TEXT                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | VARCHAR2                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | CHARACTER_LARGE_OBJECT          |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | LONGTEXT                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | NVARCHAR                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | VARCHAR                         |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | CHAR_VARYING                    |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | MEDIUMBLOB                      |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | NCHAR                           |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | VARBINARY                       |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | CHAR                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | TINYTEXT                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | BYTEA                           |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | CHARACTER                       |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | CHAR_LARGE_OBJECT               |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | NCHAR_VARYING                   |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeated      | none\tArray(Nullable(FixedString(3)))                           | BINARY_LARGE_OBJECT             |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Int64                           |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Int16                           |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UInt256                         |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | String                          |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | DateTime                        |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Int32                           |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UInt8                           |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Date                            |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UInt128                         |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Float64                         |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UInt16                          |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Int128                          |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Int8                            |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Decimal                         |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Int256                          |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | DateTime64                      |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | DateTime32                      |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Date32                          |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UInt64                          |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UInt32                          |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Float32                         |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | GEOMETRY                        |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NATIONAL_CHAR_VARYING           |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BINARY_VARYING                  |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NCHAR_LARGE_OBJECT              |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NATIONAL_CHARACTER_VARYING      |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NATIONAL_CHARACTER              |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NATIONAL_CHAR                   |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CHARACTER_VARYING               |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | LONGBLOB                        |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TINYBLOB                        |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CLOB                            |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BLOB                            |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | MEDIUMTEXT                      |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TEXT                            |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | VARCHAR2                        |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CHARACTER_LARGE_OBJECT          |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | DOUBLE_PRECISION                |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | LONGTEXT                        |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NVARCHAR                        |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INT1_UNSIGNED                   |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | VARCHAR                         |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CHAR_VARYING                    |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | MEDIUMBLOB                      |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NCHAR                           |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | VARBINARY                       |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CHAR                            |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | SMALLINT_UNSIGNED               |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TIMESTAMP                       |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | FIXED                           |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TINYTEXT                        |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NUMERIC                         |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | DEC                             |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | DOUBLE                          |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BYTEA                           |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INT                             |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | SINGLE                          |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BIT                             |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BIGINT_UNSIGNED                 |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UNSIGNED                        |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TINYINT_UNSIGNED                |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INTEGER_UNSIGNED                |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INT_UNSIGNED                    |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | REAL                            |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CHARACTER                       |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BYTE                            |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | SIGNED                          |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | MEDIUMINT                       |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | YEAR                            |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CHAR_LARGE_OBJECT               |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TINYINT                         |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BIGINT                          |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | SMALLINT                        |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INTEGER_SIGNED                  |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NCHAR_VARYING                   |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INT_SIGNED                      |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BIGINT_SIGNED                   |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BINARY_LARGE_OBJECT             |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | SMALLINT_SIGNED                 |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | FLOAT                           |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | SET                             |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TIME                            |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | MEDIUMINT_SIGNED                |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INT1_SIGNED                     |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INTEGER                         |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | MEDIUMINT_UNSIGNED              |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INT1                            |
| INT32         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TINYINT_SIGNED                  |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Int64                           |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Int16                           |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UInt256                         |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | String                          |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | DateTime                        |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Int32                           |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UInt8                           |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UInt128                         |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Float64                         |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UInt16                          |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Int128                          |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Int8                            |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Decimal                         |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Int256                          |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | DateTime64                      |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | DateTime32                      |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UInt64                          |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UInt32                          |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Float32                         |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | GEOMETRY                        |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NATIONAL_CHAR_VARYING           |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BINARY_VARYING                  |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NCHAR_LARGE_OBJECT              |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NATIONAL_CHARACTER_VARYING      |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NATIONAL_CHARACTER              |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NATIONAL_CHAR                   |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CHARACTER_VARYING               |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | LONGBLOB                        |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TINYBLOB                        |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CLOB                            |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BLOB                            |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | MEDIUMTEXT                      |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TEXT                            |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | VARCHAR2                        |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CHARACTER_LARGE_OBJECT          |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | DOUBLE_PRECISION                |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | LONGTEXT                        |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NVARCHAR                        |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INT1_UNSIGNED                   |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | VARCHAR                         |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CHAR_VARYING                    |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | MEDIUMBLOB                      |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NCHAR                           |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | VARBINARY                       |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CHAR                            |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | SMALLINT_UNSIGNED               |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TIMESTAMP                       |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | FIXED                           |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TINYTEXT                        |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NUMERIC                         |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | DEC                             |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | DOUBLE                          |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BYTEA                           |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INT                             |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | SINGLE                          |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BIT                             |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BIGINT_UNSIGNED                 |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UNSIGNED                        |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TINYINT_UNSIGNED                |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INTEGER_UNSIGNED                |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INT_UNSIGNED                    |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | REAL                            |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CHARACTER                       |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BYTE                            |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | SIGNED                          |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | MEDIUMINT                       |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | YEAR                            |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CHAR_LARGE_OBJECT               |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TINYINT                         |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BIGINT                          |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | SMALLINT                        |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INTEGER_SIGNED                  |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NCHAR_VARYING                   |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INT_SIGNED                      |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BIGINT_SIGNED                   |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BINARY_LARGE_OBJECT             |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | SMALLINT_SIGNED                 |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | FLOAT                           |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | SET                             |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TIME                            |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | MEDIUMINT_SIGNED                |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INT1_SIGNED                     |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INTEGER                         |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | MEDIUMINT_UNSIGNED              |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INT1                            |
| INT64         | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TINYINT_SIGNED                  |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | Bool                            |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | String                          |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | bool                            |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | GEOMETRY                        |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NATIONAL_CHAR_VARYING           |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | BINARY_VARYING                  |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NCHAR_LARGE_OBJECT              |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NATIONAL_CHARACTER_VARYING      |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | boolean                         |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NATIONAL_CHARACTER_LARGE_OBJECT |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NATIONAL_CHARACTER              |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NATIONAL_CHAR                   |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CHARACTER_VARYING               |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | LONGBLOB                        |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | TINYBLOB                        |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CLOB                            |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | BLOB                            |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | MEDIUMTEXT                      |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | TEXT                            |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | VARCHAR2                        |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CHARACTER_LARGE_OBJECT          |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | LONGTEXT                        |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NVARCHAR                        |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | VARCHAR                         |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CHAR_VARYING                    |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | MEDIUMBLOB                      |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NCHAR                           |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | VARBINARY                       |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CHAR                            |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | TINYTEXT                        |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | BYTEA                           |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CHARACTER                       |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CHAR_LARGE_OBJECT               |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NCHAR_VARYING                   |
| BOOLEAN       | NONE                | optionalGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | BINARY_LARGE_OBJECT             |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | String                          |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | GEOMETRY                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NATIONAL_CHAR_VARYING           |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | BINARY_VARYING                  |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NCHAR_LARGE_OBJECT              |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NATIONAL_CHARACTER_VARYING      |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NATIONAL_CHARACTER_LARGE_OBJECT |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NATIONAL_CHARACTER              |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NATIONAL_CHAR                   |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CHARACTER_VARYING               |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | LONGBLOB                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | TINYBLOB                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CLOB                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | BLOB                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | MEDIUMTEXT                      |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | TEXT                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | VARCHAR2                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CHARACTER_LARGE_OBJECT          |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | LONGTEXT                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NVARCHAR                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | VARCHAR                         |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CHAR_VARYING                    |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | MEDIUMBLOB                      |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NCHAR                           |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | VARBINARY                       |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CHAR                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | TINYTEXT                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | BYTEA                           |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CHARACTER                       |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CHAR_LARGE_OBJECT               |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NCHAR_VARYING                   |
| FIXED         | LEN_BYTE_ARRAY_NONE | optionalGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | BINARY_LARGE_OBJECT             |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Int64                           |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Int16                           |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | String                          |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Int32                           |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Float64                         |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Int128                          |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Int8                            |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Decimal                         |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Int256                          |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | DateTime64                      |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | Float32                         |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | GEOMETRY                        |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NATIONAL_CHAR_VARYING           |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BINARY_VARYING                  |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NCHAR_LARGE_OBJECT              |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NATIONAL_CHARACTER_VARYING      |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NATIONAL_CHARACTER              |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NATIONAL_CHAR                   |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CHARACTER_VARYING               |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | LONGBLOB                        |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TINYBLOB                        |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CLOB                            |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BLOB                            |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | MEDIUMTEXT                      |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TEXT                            |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | VARCHAR2                        |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CHARACTER_LARGE_OBJECT          |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | DOUBLE_PRECISION                |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | LONGTEXT                        |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NVARCHAR                        |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | VARCHAR                         |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CHAR_VARYING                    |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | MEDIUMBLOB                      |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NCHAR                           |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | VARBINARY                       |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CHAR                            |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | FIXED                           |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TINYTEXT                        |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NUMERIC                         |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | DEC                             |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | DOUBLE                          |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BYTEA                           |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INT                             |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | SINGLE                          |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | REAL                            |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CHARACTER                       |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BYTE                            |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | SIGNED                          |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | MEDIUMINT                       |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | CHAR_LARGE_OBJECT               |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TINYINT                         |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BIGINT                          |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | SMALLINT                        |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INTEGER_SIGNED                  |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | NCHAR_VARYING                   |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INT_SIGNED                      |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BIGINT_SIGNED                   |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BINARY_LARGE_OBJECT             |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | SMALLINT_SIGNED                 |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | FLOAT                           |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TIME                            |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | MEDIUMINT_SIGNED                |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INT1_SIGNED                     |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INTEGER                         |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INT1                            |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TINYINT_SIGNED                  |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UInt256                         |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | DateTime                        |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UInt8                           |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UInt128                         |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UInt16                          |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | DateTime32                      |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UInt64                          |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UInt32                          |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INT1_UNSIGNED                   |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | SMALLINT_UNSIGNED               |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TIMESTAMP                       |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BIT                             |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | BIGINT_UNSIGNED                 |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | UNSIGNED                        |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | TINYINT_UNSIGNED                |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INTEGER_UNSIGNED                |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | INT_UNSIGNED                    |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | YEAR                            |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | SET                             |
| INT32         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int32)))                 | MEDIUMINT_UNSIGNED              |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Int64                           |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Int16                           |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | String                          |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Int32                           |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Float64                         |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Int128                          |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Int8                            |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Decimal                         |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Int256                          |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | Float32                         |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | GEOMETRY                        |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NATIONAL_CHAR_VARYING           |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BINARY_VARYING                  |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NCHAR_LARGE_OBJECT              |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NATIONAL_CHARACTER_VARYING      |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NATIONAL_CHARACTER              |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NATIONAL_CHAR                   |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CHARACTER_VARYING               |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | LONGBLOB                        |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TINYBLOB                        |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CLOB                            |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BLOB                            |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | MEDIUMTEXT                      |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TEXT                            |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | VARCHAR2                        |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CHARACTER_LARGE_OBJECT          |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | DOUBLE_PRECISION                |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | LONGTEXT                        |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NVARCHAR                        |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | VARCHAR                         |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CHAR_VARYING                    |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | MEDIUMBLOB                      |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NCHAR                           |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | VARBINARY                       |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CHAR                            |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | FIXED                           |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TINYTEXT                        |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NUMERIC                         |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | DEC                             |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | DOUBLE                          |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BYTEA                           |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INT                             |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | SINGLE                          |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | REAL                            |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CHARACTER                       |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BYTE                            |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | SIGNED                          |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | MEDIUMINT                       |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | CHAR_LARGE_OBJECT               |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TINYINT                         |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BIGINT                          |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | SMALLINT                        |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INTEGER_SIGNED                  |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | NCHAR_VARYING                   |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INT_SIGNED                      |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BIGINT_SIGNED                   |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BINARY_LARGE_OBJECT             |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | SMALLINT_SIGNED                 |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | FLOAT                           |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TIME                            |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | MEDIUMINT_SIGNED                |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INT1_SIGNED                     |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INTEGER                         |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INT1                            |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TINYINT_SIGNED                  |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UInt256                         |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | DateTime                        |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UInt8                           |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UInt128                         |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UInt16                          |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | DateTime64                      |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | DateTime32                      |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UInt64                          |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UInt32                          |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INT1_UNSIGNED                   |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | SMALLINT_UNSIGNED               |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TIMESTAMP                       |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BIT                             |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | BIGINT_UNSIGNED                 |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | UNSIGNED                        |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | TINYINT_UNSIGNED                |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INTEGER_UNSIGNED                |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | INT_UNSIGNED                    |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | YEAR                            |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | SET                             |
| INT64         | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Int64)))                 | MEDIUMINT_UNSIGNED              |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | Bool                            |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | String                          |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | bool                            |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | GEOMETRY                        |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NATIONAL_CHAR_VARYING           |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | BINARY_VARYING                  |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NCHAR_LARGE_OBJECT              |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NATIONAL_CHARACTER_VARYING      |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | boolean                         |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NATIONAL_CHARACTER_LARGE_OBJECT |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NATIONAL_CHARACTER              |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NATIONAL_CHAR                   |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CHARACTER_VARYING               |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | LONGBLOB                        |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | TINYBLOB                        |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CLOB                            |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | BLOB                            |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | MEDIUMTEXT                      |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | TEXT                            |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | VARCHAR2                        |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CHARACTER_LARGE_OBJECT          |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | LONGTEXT                        |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NVARCHAR                        |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | VARCHAR                         |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CHAR_VARYING                    |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | MEDIUMBLOB                      |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NCHAR                           |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | VARBINARY                       |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CHAR                            |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | TINYTEXT                        |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | BYTEA                           |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CHARACTER                       |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | CHAR_LARGE_OBJECT               |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | NCHAR_VARYING                   |
| BOOLEAN       | NONE                | requiredGroup | none\tTuple(\\n    none Array(Nullable(Bool)))                  | BINARY_LARGE_OBJECT             |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | String                          |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | GEOMETRY                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NATIONAL_CHAR_VARYING           |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | BINARY_VARYING                  |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NCHAR_LARGE_OBJECT              |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NATIONAL_CHARACTER_VARYING      |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NATIONAL_CHARACTER_LARGE_OBJECT |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NATIONAL_CHARACTER              |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NATIONAL_CHAR                   |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CHARACTER_VARYING               |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | LONGBLOB                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | TINYBLOB                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CLOB                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | BLOB                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | MEDIUMTEXT                      |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | TEXT                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | VARCHAR2                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CHARACTER_LARGE_OBJECT          |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | LONGTEXT                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NVARCHAR                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | VARCHAR                         |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CHAR_VARYING                    |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | MEDIUMBLOB                      |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NCHAR                           |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | VARBINARY                       |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CHAR                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | TINYTEXT                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | BYTEA                           |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CHARACTER                       |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | CHAR_LARGE_OBJECT               |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | NCHAR_VARYING                   |
| FIXED         | LEN_BYTE_ARRAY_NONE | requiredGroup | none\tTuple(\\n    none Array(Nullable(FixedString(3))))        | BINARY_LARGE_OBJECT             |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | Int64                           |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | Int16                           |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | UInt256                         |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | String                          |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | DateTime                        |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | Int32                           |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | UInt8                           |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | UInt128                         |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | Float64                         |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | UInt16                          |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | Int128                          |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | Int8                            |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | Decimal                         |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | Int256                          |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | DateTime64                      |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | DateTime32                      |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | UInt64                          |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | UInt32                          |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | Float32                         |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | GEOMETRY                        |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | NATIONAL_CHAR_VARYING           |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | BINARY_VARYING                  |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | NCHAR_LARGE_OBJECT              |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | NATIONAL_CHARACTER_VARYING      |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | NATIONAL_CHARACTER              |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | NATIONAL_CHAR                   |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | CHARACTER_VARYING               |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | LONGBLOB                        |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | TINYBLOB                        |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | CLOB                            |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | BLOB                            |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | MEDIUMTEXT                      |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | TEXT                            |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | VARCHAR2                        |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | CHARACTER_LARGE_OBJECT          |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | DOUBLE_PRECISION                |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | LONGTEXT                        |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | NVARCHAR                        |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | INT1_UNSIGNED                   |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | VARCHAR                         |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | CHAR_VARYING                    |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | MEDIUMBLOB                      |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | NCHAR                           |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | VARBINARY                       |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | CHAR                            |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | SMALLINT_UNSIGNED               |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | TIMESTAMP                       |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | FIXED                           |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | TINYTEXT                        |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | NUMERIC                         |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | DEC                             |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | DOUBLE                          |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | BYTEA                           |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | INT                             |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | SINGLE                          |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | BIT                             |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | BIGINT_UNSIGNED                 |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | UNSIGNED                        |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | TINYINT_UNSIGNED                |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | INTEGER_UNSIGNED                |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | INT_UNSIGNED                    |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | REAL                            |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | CHARACTER                       |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | BYTE                            |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | SIGNED                          |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | MEDIUMINT                       |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | YEAR                            |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | CHAR_LARGE_OBJECT               |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | TINYINT                         |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | BIGINT                          |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | SMALLINT                        |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | INTEGER_SIGNED                  |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | NCHAR_VARYING                   |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | INT_SIGNED                      |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | BIGINT_SIGNED                   |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | BINARY_LARGE_OBJECT             |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | SMALLINT_SIGNED                 |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | FLOAT                           |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | SET                             |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | TIME                            |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | MEDIUMINT_SIGNED                |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | INT1_SIGNED                     |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | INTEGER                         |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | MEDIUMINT_UNSIGNED              |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | INT1                            |
| INT32         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int32))))          | TINYINT_SIGNED                  |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | Int64                           |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | Int16                           |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | UInt256                         |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | String                          |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | DateTime                        |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | Int32                           |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | UInt8                           |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | UInt128                         |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | Float64                         |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | UInt16                          |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | Int128                          |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | Int8                            |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | Decimal                         |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | Int256                          |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | DateTime64                      |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | DateTime32                      |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | UInt64                          |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | UInt32                          |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | Float32                         |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | GEOMETRY                        |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | NATIONAL_CHAR_VARYING           |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | BINARY_VARYING                  |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | NCHAR_LARGE_OBJECT              |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | NATIONAL_CHARACTER_VARYING      |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | NATIONAL_CHARACTER_LARGE_OBJECT |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | NATIONAL_CHARACTER              |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | NATIONAL_CHAR                   |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | CHARACTER_VARYING               |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | LONGBLOB                        |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | TINYBLOB                        |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | CLOB                            |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | BLOB                            |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | MEDIUMTEXT                      |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | TEXT                            |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | VARCHAR2                        |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | CHARACTER_LARGE_OBJECT          |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | DOUBLE_PRECISION                |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | LONGTEXT                        |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | NVARCHAR                        |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | INT1_UNSIGNED                   |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | VARCHAR                         |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | CHAR_VARYING                    |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | MEDIUMBLOB                      |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | NCHAR                           |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | VARBINARY                       |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | CHAR                            |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | SMALLINT_UNSIGNED               |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | TIMESTAMP                       |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | FIXED                           |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | TINYTEXT                        |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | NUMERIC                         |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | DEC                             |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | DOUBLE                          |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | BYTEA                           |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | INT                             |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | SINGLE                          |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | BIT                             |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | BIGINT_UNSIGNED                 |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | UNSIGNED                        |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | TINYINT_UNSIGNED                |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | INTEGER_UNSIGNED                |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | INT_UNSIGNED                    |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | REAL                            |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | CHARACTER                       |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | BYTE                            |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | SIGNED                          |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | MEDIUMINT                       |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | YEAR                            |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | CHAR_LARGE_OBJECT               |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | TINYINT                         |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | BIGINT                          |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | SMALLINT                        |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | INTEGER_SIGNED                  |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | NCHAR_VARYING                   |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | INT_SIGNED                      |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | BIGINT_SIGNED                   |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | BINARY_LARGE_OBJECT             |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | SMALLINT_SIGNED                 |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | FLOAT                           |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | SET                             |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | TIME                            |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | MEDIUMINT_SIGNED                |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | INT1_SIGNED                     |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | INTEGER                         |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | MEDIUMINT_UNSIGNED              |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | INT1                            |
| INT64         | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Int64))))          | TINYINT_SIGNED                  |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | Bool                            |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | String                          |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | bool                            |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | GEOMETRY                        |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | NATIONAL_CHAR_VARYING           |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | BINARY_VARYING                  |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | NCHAR_LARGE_OBJECT              |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | NATIONAL_CHARACTER_VARYING      |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | boolean                         |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | NATIONAL_CHARACTER_LARGE_OBJECT |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | NATIONAL_CHARACTER              |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | NATIONAL_CHAR                   |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | CHARACTER_VARYING               |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | LONGBLOB                        |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | TINYBLOB                        |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | CLOB                            |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | BLOB                            |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | MEDIUMTEXT                      |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | TEXT                            |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | VARCHAR2                        |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | CHARACTER_LARGE_OBJECT          |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | LONGTEXT                        |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | NVARCHAR                        |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | VARCHAR                         |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | CHAR_VARYING                    |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | MEDIUMBLOB                      |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | NCHAR                           |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | VARBINARY                       |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | CHAR                            |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | TINYTEXT                        |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | BYTEA                           |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | CHARACTER                       |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | CHAR_LARGE_OBJECT               |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | NCHAR_VARYING                   |
| BOOLEAN       | NONE                | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(Bool))))           | BINARY_LARGE_OBJECT             |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | String                          |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | GEOMETRY                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | NATIONAL_CHAR_VARYING           |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | BINARY_VARYING                  |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | NCHAR_LARGE_OBJECT              |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | NATIONAL_CHARACTER_VARYING      |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | NATIONAL_CHARACTER_LARGE_OBJECT |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | NATIONAL_CHARACTER              |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | NATIONAL_CHAR                   |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | CHARACTER_VARYING               |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | LONGBLOB                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | TINYBLOB                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | CLOB                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | BLOB                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | MEDIUMTEXT                      |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | TEXT                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | VARCHAR2                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | CHARACTER_LARGE_OBJECT          |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | LONGTEXT                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | NVARCHAR                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | VARCHAR                         |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | CHAR_VARYING                    |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | MEDIUMBLOB                      |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | NCHAR                           |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | VARBINARY                       |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | CHAR                            |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | TINYTEXT                        |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | BYTEA                           |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | CHARACTER                       |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | CHAR_LARGE_OBJECT               |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | NCHAR_VARYING                   |
| FIXED         | LEN_BYTE_ARRAY_NONE | repeatedGroup | none\tArray(Tuple(\\n    none Array(Nullable(FixedString(3))))) | BINARY_LARGE_OBJECT             |
