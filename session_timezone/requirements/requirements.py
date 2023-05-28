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
        '[ClickHouse] SHALL support the `session_timezone` setting in ClickHouse. The `session_timezone` setting allows the \n'
        'specification of an implicit timezone, which overrides the default timezone for all DateTime/DateTime64 values and \n'
        "function results that do not have an explicit timezone specified. An empty string ('') as the value configures the \n"
        "session timezone to the server's default timezone.\n"
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
        '[ClickHouse] SHALL support  the `session_timezone` setting is not specified, and the default timezones are used for the \n'
        'session and server.\n'
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
        '[ClickHouse] SHALL support the `session_timezone` setting overriding the default session timezone while keeping the server\n'
        'timezone unchanged.\n'
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

RQ_SRS_037_ClickHouse_SessionTimezone_DateTime = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.DateTime',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the `session_timezone` setting affects the conversion of DateTime values, \n'
        'resulting in the output being adjusted according to the specified session timezone.\n'
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
    num='6.4'
)

RQ_SRS_037_ClickHouse_SessionTimezone_ParsingOfDateOrDateTimeTypes = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.ParsingOfDateOrDateTimeTypes',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the `session_timezone` setting on the parsing of Date or DateTime types, \n'
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
    num='6.5'
)

RQ_SRS_037_ClickHouse_SessionTimezone_PossibleValues = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.PossibleValues',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the possible values for the `session_timezone` setting:\n'
        '  * Europe/Berlin\n'
        '  * UTC\n'
        '  * Zulu\n'
        '\n'
    ),
    link=None,
    level=2,
    num='6.6'
)

RQ_SRS_037_ClickHouse_SessionTimezone_DefaultValue = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.DefaultValue',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support an empty string ('') as the `session_timezone` setting default value.\n"
        '\n'
    ),
    link=None,
    level=2,
    num='6.7'
)

RQ_SRS_037_ClickHouse_SessionTimezone_WrongSettingValue = Requirement(
    name='RQ.SRS-037.ClickHouse.SessionTimezone.WrongSettingValue',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL provide exception with wrong `session_timezone` setting value:\n'
        '\n'
        '```CMD\n'
        'Code: 36. DB::Exception: Received from localhost:9000. DB::Exception: Exception: Invalid time zone...\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=2,
    num='6.8'
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
    num='6.9.2'
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
        '[SRS]: #srs\n'
        '[session_timezone]: https://github.com/ClickHouse/ClickHouse/pull/44149\n'
        '[ClickHouse]: https://clickhouse.com\n'
        '[timezone]:https://clickhouse.com/docs/en/operations/server-configuration-parameters/settings#server_configuration_parameters-timezone\n'
    ),
    link=None,
    level=3,
    num='6.9.4'
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
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.DateTime', level=2, num='6.4'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.ParsingOfDateOrDateTimeTypes', level=2, num='6.5'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.PossibleValues', level=2, num='6.6'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.DefaultValue', level=2, num='6.7'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.WrongSettingValue', level=2, num='6.8'),
        Heading(name='Non-Functional Requirements', level=2, num='6.9'),
        Heading(name='Performance', level=3, num='6.9.1'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.Performance', level=3, num='6.9.2'),
        Heading(name='Reliability', level=3, num='6.9.3'),
        Heading(name='RQ.SRS-037.ClickHouse.SessionTimezone.Reliability', level=3, num='6.9.4'),
        ),
    requirements=(
        RQ_SRS_037_ClickHouse_SessionTimezone,
        RQ_SRS_037_ClickHouse_SessionTimezone_ServerDefault,
        RQ_SRS_037_ClickHouse_SessionTimezone_ServerSession,
        RQ_SRS_037_ClickHouse_SessionTimezone_DateTime,
        RQ_SRS_037_ClickHouse_SessionTimezone_ParsingOfDateOrDateTimeTypes,
        RQ_SRS_037_ClickHouse_SessionTimezone_PossibleValues,
        RQ_SRS_037_ClickHouse_SessionTimezone_DefaultValue,
        RQ_SRS_037_ClickHouse_SessionTimezone_WrongSettingValue,
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
  * 5.4 [RQ.SRS-037.ClickHouse.SessionTimezone.DateTime](#rqsrs-037clickhousesessiontimezonedatetime)
  * 5.5 [RQ.SRS-037.ClickHouse.SessionTimezone.ParsingOfDateOrDateTimeTypes](#rqsrs-037clickhousesessiontimezoneparsingofdateordatetimetypes)
  * 5.6 [RQ.SRS-037.ClickHouse.SessionTimezone.PossibleValues](#rqsrs-037clickhousesessiontimezonepossiblevalues)
  * 5.7 [RQ.SRS-037.ClickHouse.SessionTimezone.DefaultValue](#rqsrs-037clickhousesessiontimezonedefaultvalue)
  * 5.8 [RQ.SRS-037.ClickHouse.SessionTimezone.WrongSettingValue](#rqsrs-037clickhousesessiontimezonewrongsettingvalue)
  * 5.9 [Non-Functional Requirements](#non-functional-requirements)
    * 5.9.1 [Performance](#performance)
    * 5.9.2 [RQ.SRS-037.ClickHouse.SessionTimezone.Performance](#rqsrs-037clickhousesessiontimezoneperformance)
    * 5.9.3 [Reliability](#reliability)
    * 5.9.4 [RQ.SRS-037.ClickHouse.SessionTimezone.Reliability](#rqsrs-037clickhousesessiontimezonereliability)

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
  
  A-->"SETTING"-->D

  1A---2A---3A---4A
  1D---2D---3D---4D
  
    subgraph A["SELECT"]

        1A["timeZone()"]:::green
        2A["serverTimezone()"]:::green
        3A["DateTime"]:::green
        4A["DateTime64"]:::green
        
    end
    
    subgraph D["Session Timezone"]
        1D["default"]:::green
        2D["wrong"]:::green
        3D["Europe/Berlin"]:::red
        4D["Zulu"]:::red
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

[ClickHouse] SHALL support the `session_timezone` setting in ClickHouse. The `session_timezone` setting allows the 
specification of an implicit timezone, which overrides the default timezone for all DateTime/DateTime64 values and 
function results that do not have an explicit timezone specified. An empty string ('') as the value configures the 
session timezone to the server's default timezone.

### RQ.SRS-037.ClickHouse.SessionTimezone.ServerDefault
version: 1.0

[ClickHouse] SHALL support  the `session_timezone` setting is not specified, and the default timezones are used for the 
session and server.

Example:
```sql
> SELECT timeZone(), serverTimezone() FORMAT TSV

> Europe/Berlin	Europe/Berlin
```

### RQ.SRS-037.ClickHouse.SessionTimezone.ServerSession
version: 1.0

[ClickHouse] SHALL support the `session_timezone` setting overriding the default session timezone while keeping the server
timezone unchanged.

Example:

```sql
> SELECT timeZone(), serverTimezone() SETTINGS session_timezone = 'Asia/Novosibirsk' FORMAT TSV

> Asia/Novosibirsk	Europe/Berlin
```

### RQ.SRS-037.ClickHouse.SessionTimezone.DateTime
version: 1.0

[ClickHouse] SHALL support the `session_timezone` setting affects the conversion of DateTime values, 
resulting in the output being adjusted according to the specified session timezone.

```sql
> SELECT toDateTime64(toDateTime64('1999-12-12 23:23:23.123', 3), 3, 'Europe/Zurich') SETTINGS 
session_timezone = 'America/Denver' FORMAT TSV

> 1999-12-13 07:23:23.123
```

### RQ.SRS-037.ClickHouse.SessionTimezone.ParsingOfDateOrDateTimeTypes
version: 1.0

[ClickHouse] SHALL support the `session_timezone` setting on the parsing of Date or DateTime types, 
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

### RQ.SRS-037.ClickHouse.SessionTimezone.PossibleValues
version: 1.0

[ClickHouse] SHALL support the possible values for the `session_timezone` setting:
  * Europe/Berlin
  * UTC
  * Zulu

### RQ.SRS-037.ClickHouse.SessionTimezone.DefaultValue
version: 1.0

[ClickHouse] SHALL support an empty string ('') as the `session_timezone` setting default value.

### RQ.SRS-037.ClickHouse.SessionTimezone.WrongSettingValue
version: 1.0

[ClickHouse] SHALL provide exception with wrong `session_timezone` setting value:

```CMD
Code: 36. DB::Exception: Received from localhost:9000. DB::Exception: Exception: Invalid time zone...
```

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
'''
)
