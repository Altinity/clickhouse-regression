# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230125.1024636.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_037_ClickHouse_SessionTimezone = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the `session_timezone` setting in ClickHouse. The `session_timezone` setting SHALL allow the \n'
        'specification of an implicit timezone, which overrides the default timezone for all DateTime/DateTime64 values and \n'
        'function results that do not have an explicit timezone specified. An empty string as the value SHALL configure the \n'
        "session timezone to be set to the server's default timezone.\n"
        '\n'
    ),
    link=None,
    level=2,
    num='6.1'
)

RQ_SRS_037_ClickHouse_SessionTimezone_ServerDefault = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.ServerDefault',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL use the default server timezone when `session_timezone` setting is not specified. \n'
        '\n'
        'Example:\n'
        '```sql\n'
        '> SELECT timeZone(), serverTimezone() FORMAT TSV\n'
        '\n'
        '> Europe/Berlin\tEurope/Berlin\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=2,
    num='6.2'
)

RQ_SRS_037_ClickHouse_SessionTimezone_ServerSession = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.ServerSession',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL override the default session timezone when `session_timezone` setting is specified while\n'
        'keeping the server timezone unchanged.\n'
        '\n'
        'Example:\n'
        '\n'
        '```sql\n'
        "> SELECT timeZone(), serverTimezone() SETTINGS session_timezone = 'Asia/Novosibirsk' FORMAT TSV\n"
        '\n'
        '> Asia/Novosibirsk\tEurope/Berlin\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=2,
    num='6.3'
)

RQ_SRS_037_ClickHouse_SessionTimezone_SettingsPriority = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.SettingsPriority',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL override session's `session_timezone` setting value when `SETTINGS session_timezone` inline clause is specified for a given query.\n"
        '\n'
    ),
    link=None,
    level=2,
    num='6.4'
)

RQ_SRS_037_ClickHouse_SessionTimezone_DateTime = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.DateTime',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL use the timezone specified by the `session_timezone` setting for all `DateTime` or `DateTime64` value conversions.\n'
        '\n'
        '```sql\n'
        "> SELECT toDateTime64(toDateTime64('1999-12-12 23:23:23.123', 3), 3, 'Europe/Zurich') SETTINGS \n"
        "session_timezone = 'America/Denver' FORMAT TSV\n"
        '\n'
        '> 1999-12-13 07:23:23.123\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=2,
    num='6.5'
)

RQ_SRS_037_ClickHouse_SessionTimezone_ParsingOfDateTimeTypes = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.ParsingOfDateTimeTypes',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL use timezone specified by the `session_timezone` setting when parsing of DateTime or DateTime64 types, \n'
        'as illustrated in the following example:\n'
        '\n'
        '```sql\n'
        "CREATE TABLE test_tz (`d` DateTime('UTC')) ENGINE = Memory AS SELECT toDateTime('2000-01-01 00:00:00', 'UTC');\n"
        "SELECT *, timezone() FROM test_tz WHERE d = toDateTime('2000-01-01 00:00:00') SETTINGS session_timezone = 'Asia/Novosibirsk'\n"
        '0 rows in set.\n'
        "SELECT *, timezone() FROM test_tz WHERE d = '2000-01-01 00:00:00' SETTINGS session_timezone = 'Asia/Novosibirsk'\n"
        '┌───────────────────d─┬─timezone()───────┐\n'
        '│ 2000-01-01 00:00:00 │ Asia/Novosibirsk │\n'
        '└─────────────────────┴──────────────────┘\n'
        '```\n'
        '\n'
        'The parsing behavior differs based on the approach used:\n'
        "  * toDateTime('2000-01-01 00:00:00') creates a new DateTime with the specified `session_timezone`.\n"
        "  * '2000-01-01 00:00:00' is parsed based on the DateTime column's inherited type, including its timezone.\n"
        '  The `session_timezone` setting does not affect this value.\n'
        '\n'
    ),
    link=None,
    level=2,
    num='6.6'
)

RQ_SRS_037_ClickHouse_SessionTimezone_ParsingOfDateTimeTypes_Insert = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.ParsingOfDateTimeTypes.Insert',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL insert data with timezone specified by the `session_timezone` setting into DateTime type column.\n'
        '\n'
        '* Date\n'
        '* DateTime\n'
        '* DateTime64\n'
        '\n'
    ),
    link=None,
    level=3,
    num='6.6.1'
)

RQ_SRS_037_ClickHouse_SessionTimezone_DateTypes = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.DateTypes',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support all Date types with `session_timezone` setting.\n'
        '\n'
        '* Date\n'
        '* DateTime\n'
        '* DateTime64\n'
        '\n'
    ),
    link=None,
    level=2,
    num='6.8'
)

RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support all Date functions with `session_timezone` setting.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='6.9.1'
)

RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDate = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDate',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support all `toDate` functions with `session_timezone` setting and return correct values.\n'
        '\n'
        '* toDate\n'
        '* toDate32\n'
        '* toDateTime\n'
        '* toDateTime64\n'
        '\n'
    ),
    link=None,
    level=4,
    num='6.9.1.1'
)

RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDateOrDefault = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDateOrDefault',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support all `toDateOrDefault` functions with `session_timezone` setting and return correct default\n'
        'values.\n'
        '\n'
        '* toDateOrDefault\n'
        '* toDate32OrDefault\n'
        '* toDateTimeOrDefault\n'
        '* toDateTime64OrDefault\n'
        '\n'
    ),
    link=None,
    level=4,
    num='6.9.1.2'
)

RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDateOrNull = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDateOrNull',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support all `toDateOrNull` functions with `session_timezone` setting and return null value.\n'
        '\n'
        '* toDateOrNull\n'
        '* toDate32OrNull\n'
        '* toDateTimeOrNull\n'
        '* toDateTime64OrNull\n'
        '\n'
    ),
    link=None,
    level=4,
    num='6.9.1.3'
)

RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDateOrZero = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDateOrZero',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support all `toDateOrZero` functions with `session_timezone` setting and return minimum possible\n'
        'value.\n'
        '\n'
        '* toDateOrZero\n'
        '* toDate32OrZero\n'
        '* toDateTimeOrZero\n'
        '* toDateTime64OrZero\n'
        '\n'
    ),
    link=None,
    level=4,
    num='6.9.1.4'
)

RQ_SRS_037_ClickHouse_SessionTimezone_PossibleValues = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.PossibleValues',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support any value from `system.time_zones`.\n'
        '\n'
    ),
    link=None,
    level=2,
    num='6.10'
)

RQ_SRS_037_ClickHouse_SessionTimezone_DefaultValue = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.DefaultValue',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use default server timezone if the `session_timezone` value is an empty string `''`.\n"
        '\n'
    ),
    link=None,
    level=2,
    num='6.11'
)

RQ_SRS_037_ClickHouse_SessionTimezone_WrongSettingValue = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.WrongSettingValue',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL throw an exception when invalid setting is applied:\n'
        '\n'
        '```CMD\n'
        'Code: 36. DB::Exception: Received from localhost:9000. DB::Exception: Exception: Invalid time zone...\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=2,
    num='6.12'
)

RQ_SRS_037_ClickHouse_SessionTimezone_ClickhouseLocal = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.ClickhouseLocal',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the `session_timezone` setting for [clickhouse local] in the same way as \n'
        'for `clickhouse client`.\n'
        '\n'
    ),
    link=None,
    level=2,
    num='6.13'
)

RQ_SRS_037_ClickHouse_SessionTimezone_Performance = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.Performance',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL allow handle large volumes of data efficiently with the `session_timezone` setting.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='6.14.2'
)

RQ_SRS_037_ClickHouse_SessionTimezone_Reliability = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.Reliability',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL be reliable and not lose any data with the `session_timezone` setting.\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '[SRS]: #srs\n'
        '[session_timezone]: https://github.com/ClickHouse/ClickHouse/pull/44149\n'
        '[ClickHouse]: https://clickhouse.com\n'
        '[timezone]:https://clickhouse.com/docs/en/operations/server-configuration-parameters/settings#server_configuration_parameters-timezone\n'
        '[clickhouse local]:https://clickhouse.com/docs/en/operations/utilities/clickhouse-local\n'
    ),
    link=None,
    level=3,
    num='6.14.4'
)

SRS037_ClickHouse_Session_Timezone = Specification(
    name='SRS037 ClickHouse Session Timezone',
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
        Heading(name='Software Requirements Specification', level=0, num=''),
        Heading(name='Table of Contents', level=1, num='1'),
        Heading(name='Introduction', level=1, num='2'),
        Heading(name='Feature Diagram', level=1, num='3'),
        Heading(name='Related Resources', level=1, num='4'),
        Heading(name='Terminology', level=1, num='5'),
        Heading(name='SRS', level=2, num='5.1'),
        Heading(name='Requirements', level=1, num='6'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone', level=2, num='6.1'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.ServerDefault', level=2, num='6.2'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.ServerSession', level=2, num='6.3'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.SettingsPriority', level=2, num='6.4'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.DateTime', level=2, num='6.5'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.ParsingOfDateTimeTypes', level=2, num='6.6'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.ParsingOfDateTimeTypes.Insert', level=3, num='6.6.1'),
        Heading(name='Date Types', level=2, num='6.7'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.DateTypes', level=2, num='6.8'),
        Heading(name='Date Functions', level=2, num='6.9'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions', level=3, num='6.9.1'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDate', level=4, num='6.9.1.1'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDateOrDefault', level=4, num='6.9.1.2'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDateOrNull', level=4, num='6.9.1.3'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDateOrZero', level=4, num='6.9.1.4'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.PossibleValues', level=2, num='6.10'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.DefaultValue', level=2, num='6.11'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.WrongSettingValue', level=2, num='6.12'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.ClickhouseLocal', level=2, num='6.13'),
        Heading(name='Non-Functional Requirements', level=2, num='6.14'),
        Heading(name='Performance', level=3, num='6.14.1'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.Performance', level=3, num='6.14.2'),
        Heading(name='Reliability', level=3, num='6.14.3'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.Reliability', level=3, num='6.14.4'),
        ),
    requirements=(
        RQ_SRS_037_ClickHouse_SessionTimezone,
        RQ_SRS_037_ClickHouse_SessionTimezone_ServerDefault,
        RQ_SRS_037_ClickHouse_SessionTimezone_ServerSession,
        RQ_SRS_037_ClickHouse_SessionTimezone_SettingsPriority,
        RQ_SRS_037_ClickHouse_SessionTimezone_DateTime,
        RQ_SRS_037_ClickHouse_SessionTimezone_ParsingOfDateTimeTypes,
        RQ_SRS_037_ClickHouse_SessionTimezone_ParsingOfDateTimeTypes_Insert,
        RQ_SRS_037_ClickHouse_SessionTimezone_DateTypes,
        RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions,
        RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDate,
        RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDateOrDefault,
        RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDateOrNull,
        RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDateOrZero,
        RQ_SRS_037_ClickHouse_SessionTimezone_PossibleValues,
        RQ_SRS_037_ClickHouse_SessionTimezone_DefaultValue,
        RQ_SRS_037_ClickHouse_SessionTimezone_WrongSettingValue,
        RQ_SRS_037_ClickHouse_SessionTimezone_ClickhouseLocal,
        RQ_SRS_037_ClickHouse_SessionTimezone_Performance,
        RQ_SRS_037_ClickHouse_SessionTimezone_Reliability,
        ),
    content='''
# SRS037 ClickHouse Session Timezone

# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Feature Diagram](#feature-diagram)
* 3 [Related Resources](#related-resources)
* 4 [Terminology](#terminology)
  * 4.1 [SRS](#srs)
* 5 [Requirements](#requirements)
  * 5.1 [RQ.SRS-037.ClickHouse.SessionTimezone](#rqsrs-037clickhousesessiontimezone)
  * 5.2 [RQ.SRS-037.ClickHouse.SessionTimezone.ServerDefault](#rqsrs-037clickhousesessiontimezoneserverdefault)
  * 5.3 [RQ.SRS-037.ClickHouse.SessionTimezone.ServerSession](#rqsrs-037clickhousesessiontimezoneserversession)
  * 5.4 [RQ.SRS-037.ClickHouse.SessionTimezone.SettingsPriority](#rqsrs-037clickhousesessiontimezonesettingspriority)
  * 5.5 [RQ.SRS-037.ClickHouse.SessionTimezone.DateTime](#rqsrs-037clickhousesessiontimezonedatetime)
  * 5.6 [RQ.SRS-037.ClickHouse.SessionTimezone.ParsingOfDateTimeTypes](#rqsrs-037clickhousesessiontimezoneparsingofdatetimetypes)
    * 5.6.1 [RQ.SRS-037.ClickHouse.SessionTimezone.ParsingOfDateTimeTypes.Insert](#rqsrs-037clickhousesessiontimezoneparsingofdatetimetypesinsert)
  * 5.7 [Date Types](#date-types)
  * 5.8 [RQ.SRS-037.ClickHouse.SessionTimezone.DateTypes](#rqsrs-037clickhousesessiontimezonedatetypes)
  * 5.9 [Date Functions](#date-functions)
    * 5.9.1 [RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions](#rqsrs-037clickhousesessiontimezonedatefunctions)
      * 5.9.1.1 [RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDate](#rqsrs-037clickhousesessiontimezonedatefunctionstodate)
      * 5.9.1.2 [RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDateOrDefault](#rqsrs-037clickhousesessiontimezonedatefunctionstodateordefault)
      * 5.9.1.3 [RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDateOrNull](#rqsrs-037clickhousesessiontimezonedatefunctionstodateornull)
      * 5.9.1.4 [RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDateOrZero](#rqsrs-037clickhousesessiontimezonedatefunctionstodateorzero)
  * 5.10 [RQ.SRS-037.ClickHouse.SessionTimezone.PossibleValues](#rqsrs-037clickhousesessiontimezonepossiblevalues)
  * 5.11 [RQ.SRS-037.ClickHouse.SessionTimezone.DefaultValue](#rqsrs-037clickhousesessiontimezonedefaultvalue)
  * 5.12 [RQ.SRS-037.ClickHouse.SessionTimezone.WrongSettingValue](#rqsrs-037clickhousesessiontimezonewrongsettingvalue)
  * 5.13 [RQ.SRS-037.ClickHouse.SessionTimezone.ClickhouseLocal](#rqsrs-037clickhousesessiontimezoneclickhouselocal)
  * 5.14 [Non-Functional Requirements](#non-functional-requirements)
    * 5.14.1 [Performance](#performance)
    * 5.14.2 [RQ.SRS-037.ClickHouse.SessionTimezone.Performance](#rqsrs-037clickhousesessiontimezoneperformance)
    * 5.14.3 [Reliability](#reliability)
    * 5.14.4 [RQ.SRS-037.ClickHouse.SessionTimezone.Reliability](#rqsrs-037clickhousesessiontimezonereliability)

## Introduction

This software requirements specification covers requirements related to [ClickHouse] support of changing
default timezone with [session_timezone] setting.

## Feature Diagram

Test feature diagram.

```mermaid
flowchart TB;

  classDef yellow fill:#ffff32,stroke:#323,stroke-width:4px,color:black;
  classDef yellow2 fill:#ffff32,stroke:#323,stroke-width:4px,color:red;
  classDef green fill:#00ff32,stroke:#323,stroke-width:4px,color:black;
  classDef red fill:red,stroke:#323,stroke-width:4px,color:black;
  classDef blue fill:blue,stroke:#323,stroke-width:4px,color:white;
  
  subgraph O["'Session Timezone' Test Feature Diagram"]
  
  C-->E-->A--"SETTING"-->D
  C-->A

  1A---2A---3A---4A---5A---6A---7A---8A---9A---10A---11A---12A
  13
  1D---2D---3D
  
    subgraph E["SET"]

        1E["session_timezone"]:::green
 
    end
  
    subgraph C["Clickhouse"]

        1C["client"]:::green
        2C["local"]:::green
 
    end
  
    subgraph A["SELECT"]

        1A["FUNCTIONS"]:::yellow
        2A["timeZone()"]:::green
        3A["serverTimezone()"]:::green
        4A["now()"]:::green
        5A["toDate()"]:::green
        6A["toDate32()"]:::green
        7A["toDateTime()"]:::green
        8A["toDateTime64()"]:::green
        9A["toDateOrDefault()"]:::green
        10A["toDate32OrDefault()"]:::green
        11A["toDateTimeOrDefault()"]:::green
        12A["toDateTime64OrDefault()"]:::green
        
        13A["FUNCTIONS"]:::yellow
        14A["toDateOrNull()"]:::green
        15A["toDate32OrNull()"]:::green
        16A["toDateTimeOrNull()"]:::green
        17A["toDateTime64OrNull()"]:::green
        18A["toDateOrZero()"]:::green
        19A["toDate32OrZero()"]:::green
        20A["toDateTimeOrZerol()"]:::green
        21A["toDateTime64OrZero()"]:::green
        
    end
    
    subgraph D["session_timezone"]
        1D["default"]:::green
        2D["wrong"]:::green
        3D["any timezone"]:::green
    end
  end
```
## Related Resources

**Pull Requests**

* https://github.com/ClickHouse/ClickHouse/pull/44149

## Terminology

### SRS

Software Requirements Specification

## Requirements

### RQ.SRS-037.ClickHouse.SessionTimezone
version: 1.0

[ClickHouse] SHALL support the `session_timezone` setting in ClickHouse. The `session_timezone` setting SHALL allow the 
specification of an implicit timezone, which overrides the default timezone for all DateTime/DateTime64 values and 
function results that do not have an explicit timezone specified. An empty string as the value SHALL configure the 
session timezone to be set to the server's default timezone.

### RQ.SRS-037.ClickHouse.SessionTimezone.ServerDefault
version: 1.0

[ClickHouse] SHALL use the default server timezone when `session_timezone` setting is not specified. 

Example:
```sql
> SELECT timeZone(), serverTimezone() FORMAT TSV

> Europe/Berlin	Europe/Berlin
```

### RQ.SRS-037.ClickHouse.SessionTimezone.ServerSession
version: 1.0

[ClickHouse] SHALL override the default session timezone when `session_timezone` setting is specified while
keeping the server timezone unchanged.

Example:

```sql
> SELECT timeZone(), serverTimezone() SETTINGS session_timezone = 'Asia/Novosibirsk' FORMAT TSV

> Asia/Novosibirsk	Europe/Berlin
```

### RQ.SRS-037.ClickHouse.SessionTimezone.SettingsPriority
version: 1.0

[ClickHouse] SHALL override session's `session_timezone` setting value when `SETTINGS session_timezone` inline clause is specified for a given query.

### RQ.SRS-037.ClickHouse.SessionTimezone.DateTime
version: 1.0

[ClickHouse] SHALL use the timezone specified by the `session_timezone` setting for all `DateTime` or `DateTime64` value conversions.

```sql
> SELECT toDateTime64(toDateTime64('1999-12-12 23:23:23.123', 3), 3, 'Europe/Zurich') SETTINGS 
session_timezone = 'America/Denver' FORMAT TSV

> 1999-12-13 07:23:23.123
```

### RQ.SRS-037.ClickHouse.SessionTimezone.ParsingOfDateTimeTypes
version: 1.0

[ClickHouse] SHALL use timezone specified by the `session_timezone` setting when parsing of DateTime or DateTime64 types, 
as illustrated in the following example:

```sql
CREATE TABLE test_tz (`d` DateTime('UTC')) ENGINE = Memory AS SELECT toDateTime('2000-01-01 00:00:00', 'UTC');
SELECT *, timezone() FROM test_tz WHERE d = toDateTime('2000-01-01 00:00:00') SETTINGS session_timezone = 'Asia/Novosibirsk'
0 rows in set.
SELECT *, timezone() FROM test_tz WHERE d = '2000-01-01 00:00:00' SETTINGS session_timezone = 'Asia/Novosibirsk'
┌───────────────────d─┬─timezone()───────┐
│ 2000-01-01 00:00:00 │ Asia/Novosibirsk │
└─────────────────────┴──────────────────┘
```

The parsing behavior differs based on the approach used:
  * toDateTime('2000-01-01 00:00:00') creates a new DateTime with the specified `session_timezone`.
  * '2000-01-01 00:00:00' is parsed based on the DateTime column's inherited type, including its timezone.
  The `session_timezone` setting does not affect this value.

#### RQ.SRS-037.ClickHouse.SessionTimezone.ParsingOfDateTimeTypes.Insert
version: 1.0

[ClickHouse] SHALL insert data with timezone specified by the `session_timezone` setting into DateTime type column.

* Date
* DateTime
* DateTime64

### Date Types

### RQ.SRS-037.ClickHouse.SessionTimezone.DateTypes
version: 1.0

[ClickHouse] SHALL support all Date types with `session_timezone` setting.

* Date
* DateTime
* DateTime64

### Date Functions

#### RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions
version: 1.0

[ClickHouse] SHALL support all Date functions with `session_timezone` setting.

##### RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDate
version: 1.0

[ClickHouse] SHALL support all `toDate` functions with `session_timezone` setting and return correct values.

* toDate
* toDate32
* toDateTime
* toDateTime64

##### RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDateOrDefault
version: 1.0

[ClickHouse] SHALL support all `toDateOrDefault` functions with `session_timezone` setting and return correct default
values.

* toDateOrDefault
* toDate32OrDefault
* toDateTimeOrDefault
* toDateTime64OrDefault

##### RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDateOrNull
version: 1.0

[ClickHouse] SHALL support all `toDateOrNull` functions with `session_timezone` setting and return null value.

* toDateOrNull
* toDate32OrNull
* toDateTimeOrNull
* toDateTime64OrNull

##### RQ.SRS-037.ClickHouse.SessionTimezone.DateFunctions.ToDateOrZero
version: 1.0

[ClickHouse] SHALL support all `toDateOrZero` functions with `session_timezone` setting and return minimum possible
value.

* toDateOrZero
* toDate32OrZero
* toDateTimeOrZero
* toDateTime64OrZero

### RQ.SRS-037.ClickHouse.SessionTimezone.PossibleValues
version: 1.0

[ClickHouse] SHALL support any value from `system.time_zones`.

### RQ.SRS-037.ClickHouse.SessionTimezone.DefaultValue
version: 1.0

[ClickHouse] SHALL use default server timezone if the `session_timezone` value is an empty string `''`.

### RQ.SRS-037.ClickHouse.SessionTimezone.WrongSettingValue
version: 1.0

[ClickHouse] SHALL throw an exception when invalid setting is applied:

```CMD
Code: 36. DB::Exception: Received from localhost:9000. DB::Exception: Exception: Invalid time zone...
```

### RQ.SRS-037.ClickHouse.SessionTimezone.ClickhouseLocal
version: 1.0

[ClickHouse] SHALL support the `session_timezone` setting for [clickhouse local] in the same way as 
for `clickhouse client`.

### Non-Functional Requirements

#### Performance

#### RQ.SRS-037.ClickHouse.SessionTimezone.Performance
version: 1.0

[ClickHouse] SHALL allow handle large volumes of data efficiently with the `session_timezone` setting.

#### Reliability

#### RQ.SRS-037.ClickHouse.SessionTimezone.Reliability
version: 1.0

[ClickHouse] SHALL be reliable and not lose any data with the `session_timezone` setting.





[SRS]: #srs
[session_timezone]: https://github.com/ClickHouse/ClickHouse/pull/44149
[ClickHouse]: https://clickhouse.com
[timezone]:https://clickhouse.com/docs/en/operations/server-configuration-parameters/settings#server_configuration_parameters-timezone
[clickhouse local]:https://clickhouse.com/docs/en/operations/utilities/clickhouse-local
'''
)
