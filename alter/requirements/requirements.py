# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.231001.1175523.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_032_ClickHouse_Alter = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "* [`REPLACE PARTITION`](https://github.com/Altinity/clickhouse-regression/blob/main/alter/table/replace_partition/requirements/requirements.md)                                                                                                                        |\n"
        "* `ATTACH PARTITION`\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/alter/requirements/requirements.md\n"
        "[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/alter/requirements/requirements.md\n"
        "[Git]: https://git-scm.com/\n"
        "[GitHub]: https://github.com\n"
    ),
    link=None,
    level=2,
    num="4.1",
)

SRS032_ClickHouse_Alter = Specification(
    name="SRS032 ClickHouse Alter",
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
        Heading(name="Software Requirements Specification", level=0, num=""),
        Heading(name="Table of Contents", level=1, num="1"),
        Heading(name="Revision History", level=1, num="2"),
        Heading(name="Introduction", level=1, num="3"),
        Heading(name="The List of ALTER Statements Covered by Tests", level=1, num="4"),
        Heading(name="RQ.SRS-032.ClickHouse.Alter", level=2, num="4.1"),
    ),
    requirements=(RQ_SRS_032_ClickHouse_Alter,),
    content="""
# SRS032 ClickHouse Alter

# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [The List of ALTER Statements Covered by Tests](#the-list-of-alter-statements-covered-by-tests)
    * 3.1 [RQ.SRS-032.ClickHouse.Alter](#rqsrs-032clickhousealter)




## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].


## Introduction

This software requirements specification covers requirements for `ALTER` in [ClickHouse].

The documentation used:

- https://clickhouse.com/docs/en/sql-reference/statements/alter


## The List of ALTER Statements Covered by Tests

### RQ.SRS-032.ClickHouse.Alter
version: 1.0

* [`REPLACE PARTITION`](https://github.com/Altinity/clickhouse-regression/blob/main/alter/table/replace_partition/requirements/requirements.md)                                                                                                                        |
* `ATTACH PARTITION`





[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/alter/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/alter/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
""",
)
