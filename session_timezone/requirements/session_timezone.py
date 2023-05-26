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
        '[ClickHouse] SHALL support `session_timezone` setting.\n'
        '\n'
        '\n'
        '[SRS]: #srs\n'
        '[session_timezone]: https://github.com/ClickHouse/ClickHouse/pull/44149\n'
        '[ClickHouse]: https://clickhouse.com\n'
    ),
    link=None,
    level=2,
    num='6.1'
)

QA_SRS037_ClickHouse_Session_Timezone = Specification(
    name='QA-SRS037 ClickHouse Session Timezone',
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
        ),
    requirements=(
        RQ_SRS_037_ClickHouse_SessionTimezone,
        ),
    content='''
# QA-SRS037 ClickHouse Session Timezone

# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Feature Diagram](#feature-diagram)
* 3 [Related Resources](#related-resources)
* 4 [Terminology](#terminology)
  * 4.1 [SRS](#srs)
* 5 [Requirements](#requirements)
  * 5.1 [RQ.SRS-037.ClickHouse.SessionTimezone](#rqsrs-037clickhousesessiontimezone)

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

[ClickHouse] SHALL support `session_timezone` setting.


[SRS]: #srs
[session_timezone]: https://github.com/ClickHouse/ClickHouse/pull/44149
[ClickHouse]: https://clickhouse.com
'''
)
