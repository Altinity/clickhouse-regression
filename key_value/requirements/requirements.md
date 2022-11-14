# SRS ClickHouse Key Value Function
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Requirements](#requirements)
  * 2.1 [Parse Key Value](#parse-key-value)
    * 2.1.1 [RQ.ClickHouse.ParseKeyValue](#rqclickhouseparsekeyvalue)
    * 2.1.2 [RQ.ClickHouse.ParseKeyValue.SupportedDataTypes](#rqclickhouseparsekeyvaluesupporteddatatypes)
    * 2.1.3 [RQ.ClickHouse.ParseKeyValue.UnsupportedDataTypes](#rqclickhouseparsekeyvalueunsupporteddatatypes)

## Introduction

This software requirements specification covers requirements related to [ClickHouse]
[KeyValue] functionality that implements parseKeyValue function.

## Requirements

### Parse Key Value

#### RQ.ClickHouse.ParseKeyValue
version: 1.0

[ClickHouse] SHALL support `parseKeyValue` string function that SHALL have the following syntax:


```sql
parseKeyValue(<column_name>|<constant>|<function_return_value>|<alias>)
```

For example, 

> Insert into the table parsed keys, values from another table

```sql
INSERT INTO table_2 SELECT parseKeyValue(x) FROM table_1;
```

The function SHALL return an `String` that SHALL contain parsed keys, values

#### RQ.ClickHouse.ParseKeyValue.SupportedDataTypes
version: 1.0

[ClickHouse] SHALL support using `parseKeyValue` function for the following data types that SHALL either
be provided as a constant or using a table column:

* `String`

#### RQ.ClickHouse.ParseKeyValue.UnsupportedDataTypes
version: 1.0

[ClickHouse]'s `base58Encode` function SHALL return an error if input data type is not supported.




[KeyValue]: https://github.com/arthurpassos/KeyValuePairFileProcessor
[ClickHouse]: https://clickhouse.tech
