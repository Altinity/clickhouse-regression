# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.220712.1163352.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_031_ClickHouse_DNS_Lookup = Requirement(
    name="RQ.SRS-031.ClickHouse.DNS.Lookup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using DNS look up to communicate between different clickhouse instances.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.1",
)

SRS031_ClickHouse_DNS_Lookup = Specification(
    name="SRS031 ClickHouse DNS Lookup",
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
        Heading(name="Revision History", level=1, num="1"),
        Heading(name="Introduction", level=1, num="2"),
        Heading(name="Requirements", level=1, num="3"),
        Heading(name="RQ.SRS-031.ClickHouse.DNS.Lookup", level=2, num="3.1"),
        Heading(name="References", level=1, num="4"),
    ),
    requirements=(RQ_SRS_031_ClickHouse_DNS_Lookup,),
    content="""
# SRS031 ClickHouse DNS Lookup
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Requirements](#requirements)
  * 3.1 [RQ.SRS-031.ClickHouse.DNS.Lookup](#rqsrs-031clickhousednslookup)
* 4 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements related to [ClickHouse]
using DNS.

## Requirements

### RQ.SRS-031.ClickHouse.DNS.Lookup
version: 1.0

[ClickHouse] SHALL support using DNS look up to communicate between different clickhouse instances.

## References

* **ClickHouse:** https://clickhouse.com
* **GitHub Repository**: https://github.com/ClickHouse/ClickHouse/blob/master/tests/testflows/dns_lookup/requirements/requirements.md
* **Revision History**: https://github.com/ClickHouse/ClickHouse/blob/master/tests/testflows/dns_lookup/requirements/requirements.md
* **Git:** https://git-scm.com/

[NDS Lookup]: #dns-lookup
[SRS]: #srs
[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/ClickHouse/ClickHouse/blob/master/tests/testflows/dns_lookup/requirements/requirements.md
[Revision History]: https://github.com/ClickHouse/ClickHouse/blob/master/tests/testflows/dns_lookup/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
""",
)
