# SRS033 ClickHouse Key Value Function
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Test Feature Diagram](#test-feature-diagram)
* 3 [Requirements](#requirements)
  * 3.1 [extractKeyValuePairs Function](#extractkeyvaluepairs-function)
    * 3.1.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function](#rqsrs-033clickhouseextractkeyvaluepairsfunction)
    * 3.1.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.SupportedDataTypes](#rqsrs-033clickhouseextractkeyvaluepairsfunctionsupporteddatatypes)
    * 3.1.3 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.UnsupportedDataTypes](#rqsrs-033clickhouseextractkeyvaluepairsfunctionunsupporteddatatypes)
  * 3.2 [Input Data Source](#input-data-source)
    * 3.2.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Constant](#rqsrs-033clickhouseextractkeyvaluepairsinputdatasourceconstant)
    * 3.2.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Column](#rqsrs-033clickhouseextractkeyvaluepairsinputdatasourcecolumn)
    * 3.2.3 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Array](#rqsrs-033clickhouseextractkeyvaluepairsinputdatasourcearray)
    * 3.2.4 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Map](#rqsrs-033clickhouseextractkeyvaluepairsinputdatasourcemap)
    * 3.2.5 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Alias](#rqsrs-033clickhouseextractkeyvaluepairsinputdatasourcealias)
  * 3.3 [Parsing](#parsing)
    * 3.3.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.Noise](#rqsrs-033clickhouseextractkeyvaluepairsparsingnoise)
    * 3.3.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.IdenticalKeys](#rqsrs-033clickhouseextractkeyvaluepairsparsingidenticalkeys)
  * 3.4 [Format](#format)
    * 3.4.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Input](#rqsrs-033clickhouseextractkeyvaluepairsformatinput)
  * 3.5 [Key](#key)
    * 3.5.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Key.Format](#rqsrs-033clickhouseextractkeyvaluepairskeyformat)
  * 3.6 [Value](#value)
    * 3.6.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Value.Format](#rqsrs-033clickhouseextractkeyvaluepairsvalueformat)
  * 3.7 [Parameters](#parameters)
    * 3.7.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters](#rqsrs-033clickhouseextractkeyvaluepairsparameters)
    * 3.7.2 [Key Value Pair Delimiter](#key-value-pair-delimiter)
      * 3.7.2.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.KeyValuePairDelimiter](#rqsrs-033clickhouseextractkeyvaluepairsparameterskeyvaluepairdelimiter)
      * 3.7.2.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.KeyValuePairDelimiter.Format](#rqsrs-033clickhouseextractkeyvaluepairsparameterskeyvaluepairdelimiterformat)
    * 3.7.3 [Pair Delimiter](#pair-delimiter)
      * 3.7.3.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.PairDelimiters](#rqsrs-033clickhouseextractkeyvaluepairsparameterspairdelimiters)
      * 3.7.3.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.PairDelimiters.Format](#rqsrs-033clickhouseextractkeyvaluepairsparameterspairdelimitersformat)
    * 3.7.4 [Quoting Character](#quoting-character)
      * 3.7.4.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.QuotingCharacter](#rqsrs-033clickhouseextractkeyvaluepairsparametersquotingcharacter)
      * 3.7.4.2 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.QuotingCharacter.Format](#rqsrs-033clickhouseextractkeyvaluepairsparametersquotingcharacterformat)
      * 3.7.4.3 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.ExtractKeyValuePairsWithEscaping](#rqsrs-033clickhouseextractkeyvaluepairsparametersextractkeyvaluepairswithescaping)
    * 3.7.5 [Special Characters Conflict](#special-characters-conflict)
      * 3.7.5.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.SpecialCharactersConflict](#rqsrs-033clickhouseextractkeyvaluepairsparametersspecialcharactersconflict)
  * 3.8 [Default Parameters Values](#default-parameters-values)
    * 3.8.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.KeyValuePairDelimiter](#rqsrs-033clickhouseextractkeyvaluepairsdefaultkeyvaluepairdelimiter)
  * 3.9 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.PairDelimiters](#rqsrs-033clickhouseextractkeyvaluepairsdefaultpairdelimiters)
    * 3.9.1 [RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.QuotingCharacter](#rqsrs-033clickhouseextractkeyvaluepairsdefaultquotingcharacter)

## Introduction

This software requirements specification covers requirements related to [ClickHouse]
[extractKeyValuePairs] function.

## Test Feature Diagram

```mermaid
flowchart LR
  subgraph Key Value
    direction LR
    subgraph A[extractKeyValuePairs]
        A1[remove all noise not related to the key or value]
        A2[output any values that are recognized as a key-value pair]
    end
    subgraph E[Format]
        direction TB
        subgraph E1[input format]
            direction LR
            E11[Any string]
            E12["extractKeyValuePairs(string[, key_value_pair_delimiter[, pair_delimiters[, quoting_character]]])"]
        endutput forma
        subgraph E2[ot]
            direction LR 
            E21["String in format {'key': 'value', ...}"]
        end
    end  
    subgraph Z[Separator]
        direction TB
        subgraph Z1[Key]
            direction LR
            Z12[can't contain control symbols]
            Z13[can't be an empty string]
            Z14[it accepts anything if it is between the enclosing character]
        end
        subgraph Z2[Value]
            direction LR
            Z22[can be empty string]
            Z23[can't contain control symbols]
            Z24[it accepts anything if it is between the enclosing character]
        end
    end
    subgraph Q[Parameters]
        direction TB
        Q1[key_value_pair_delimiter, default ':']
        Q2["pair_delimiters, default ' ,;'"]
        Q3[quoting_character, default double quotes]
        Q5[extractKeyValuePairsWithEscaping]
    end
  end
```

## Requirements

### extractKeyValuePairs Function

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function
version: 1.0

[ClickHouse] SHALL support `extractKeyValuePairs` function that SHALL have the following syntax:


```sql
extractKeyValuePairs(<column_name>|<constant>|<function_return_value>|<alias>[, key_value_pair_delimiter[, pair_delimiters[, quoting_character]]]])
```

For example, 

> Insert into the table parsed key-values from another table

```sql
INSERT INTO table_2 SELECT extractKeyValuePairs(x) FROM table_1;
```

The function SHALL return a `map` object containing all recognized parsed keys and values. 

`{'key': 'value', ...}`

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.SupportedDataTypes
version: 1.0

[ClickHouse] SHALL support using the [extractKeyValuePairs] function with the following data types:

* [String]
* [LowCardinality]
* [FixedString]

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Function.UnsupportedDataTypes
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if input data type is not supported. 
Nullable types are not supported.

### Input Data Source

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Constant
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as a constant string.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Column
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as a string column.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Array
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as the value that
returned from the array.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Map
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as 
value that returned from the map.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.InputDataSource.Alias
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept input as alias expression.

### Parsing

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.Noise
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL remove all noise that is not related to the key or value.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parsing.IdenticalKeys
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return the all key value pairs
for key value pairs with the same key.

For example:

`SELECT extractKeyValuePairs('a:a, a:b')`

### Format

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Format.Input
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL accept any string as input.

### Key

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Key.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL recognize the key in the input string
if it satisfies the following conditions:

* Key can't contain symbols that defined in parameters.
* Key can't be an empty string.
* If a key is enclosed, value can contain any symbols.
* If `extractKeyValuePairsWithEscaping` is used, key shall accept control symbols.

### Value

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Value.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL recognize the value in the input string
if it satisfies the following conditions:

* Value can't contain symbols that defined in parameters except `key_value_pair_delimiter`.
* Value can be an empty string.
* If a value is enclosed, value can contain any symbols.
* If `extractKeyValuePairsWithEscaping` is used, value shall accept control symbols.
* Value can contain `key_value_pair_delimiter`, For example:

`SELECT extractKeyValuePairs('a:a:a', ':', ';')`

returns

`{'a':'a:a'}`

### Parameters

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying following parameters:
`key_value_pair_delimiter`, `pair_delimiters`, `quoting_character`.

#### Key Value Pair Delimiter

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.KeyValuePairDelimiter
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `key_value_pair_delimiter`
which SHALL divide key value pairs among themselves.

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.KeyValuePairDelimiter.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if `key_value_pair_delimiter` 
parameter specified with non-string value or string value with more than one symbol.

#### Pair Delimiter

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.PairDelimiters
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `pair_delimiters`
which SHALL divide key value pairs in input string.

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.PairDelimiters.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if `pair_delimiters` 
parameter specified with non-string value.

#### Quoting Character

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.QuotingCharacter
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL support specifying `quoting_character`,
which allows using unsupported characters in a key or value if they are enclosed.

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.QuotingCharacter.Format
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if `quoting_character` 
parameter specified with non-string value or string value with more than one symbol.

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.ExtractKeyValuePairsWithEscaping
version: 1.0

[ClickHouse] SHALL support `extractKeyValuePairsWithEscaping` function that SHALL
allow using control symbols in keys and values and allow specifying symbols in hexadecimal format.

For example:

`SELECT extractKeyValuePairsWithEscaping('a:\\x0A', ':', ',', '\"')`

SHALL return

`{'a':'\n'}`

#### Special Characters Conflict

##### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Parameters.SpecialCharactersConflict
version: 1.0

[ClickHouse]'s [extractKeyValuePairs] function SHALL return an error if
either `key_value_pair_delimiter`, `pair_delimiter`, or `quoting_character`
parameters use the same symbol.

For example:

`SELECT extractKeyValuePairs('a=a', '=', '=', '=')`

### Default Parameters Values

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.KeyValuePairDelimiter
version: 1.0

By default, [ClickHouse]'s [extractKeyValuePairs] function SHALL 
specify `key_value_pair_delimiter` using `':'`.

### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.PairDelimiters
version: 1.0

By default, [ClickHouse]'s [extractKeyValuePairs] function SHALL 
specify `pair_delimiters` using `' ,;'`.

#### RQ.SRS-033.ClickHouse.ExtractKeyValuePairs.Default.QuotingCharacter
version: 1.0

By default, [ClickHouse]'s [extractKeyValuePairs] function SHALL
specify `quoting_character` using `'"'`.


[String]: https://clickhouse.com/docs/en/sql-reference/data-types/string
[FixedString]: https://clickhouse.com/docs/en/sql-reference/data-types/fixedstring
[LowCardinality]: https://clickhouse.com/docs/en/sql-reference/data-types/lowcardinality
[extractKeyValuePairs]: https://github.com/arthurpassos/KeyValuePairFileProcessor
[ClickHouse]: https://clickhouse.tech
