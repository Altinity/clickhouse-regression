# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_107_DBeaver_UI_Startup = Requirement(
    name='RQ.SRS-107.DBeaver.UI.Startup',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'DBeaver SHALL start with a new workspace and show its main window, titled\n'
        '`DBeaver <version>`, after its first-run Product Configuration wizard is\n'
        'accepted.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.1.1'
)

RQ_SRS_107_DBeaver_UI_Connection = Requirement(
    name='RQ.SRS-107.DBeaver.UI.Connection',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'A connection to the local ClickHouse server SHALL be created with Database >\n'
        'New Database Connection, the `ClickHouse` driver (not `ClickHouse (Legacy)`),\n'
        'host `localhost`, port `8123` and user `default`. Test Connection SHALL report\n'
        '`Connected` and show the server version that `SELECT version()` returns, and\n'
        'the connection SHALL show in the navigator after Finish.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.1'
)

RQ_SRS_107_DBeaver_UI_Dataset = Requirement(
    name='RQ.SRS-107.DBeaver.UI.Dataset',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'A script run from the SQL editor with Alt+X SHALL create the database\n'
        '`lts_dbeaver_ui`, the MergeTree table `events` and its 100 rows, and the server\n'
        'SHALL then return `count()` 100 for the table.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.1'
)

RQ_SRS_107_DBeaver_UI_Queries = Requirement(
    name='RQ.SRS-107.DBeaver.UI.Queries',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'Queries run from the SQL editor with Ctrl+Enter SHALL show exactly the expected\n'
        'rows in the result grid for:\n'
        '\n'
        '* `count()` and `count(score)`\n'
        '* `sum`, `min`, `max` and `uniqExact`\n'
        '* `WHERE score IS NULL`\n'
        '* `GROUP BY id % 5`\n'
        '* `ORDER BY id DESC LIMIT 3`\n'
        '* `ARRAY JOIN` on the `tags` array\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.1'
)

RQ_SRS_107_DBeaver_UI_Navigator = Requirement(
    name='RQ.SRS-107.DBeaver.UI.Navigator',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'After a refresh, the navigator SHALL show the database `lts_dbeaver_ui`, its\n'
        "table `events` and the table's columns with their types: `id (UInt64)`,\n"
        '`name (String)`, `created (DateTime)`, `score (Nullable(Float64))` and\n'
        '`tags (Array(String))`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.1'
)

RQ_SRS_107_DBeaver_UI_Screenshots = Requirement(
    name='RQ.SRS-107.DBeaver.UI.Screenshots',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'Each step SHALL save a numbered screenshot of the screen under\n'
        '`lts/_instances/dbeaver_ui/screenshots/`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.1'
)

RQ_SRS_107_DBeaver_UI_Compatibility_LTS = Requirement(
    name='RQ.SRS-107.DBeaver.UI.Compatibility.LTS',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'DBeaver Community Edition SHALL be verified to connect to, create data in and\n'
        'query the current Altinity ClickHouse LTS build through its user interface.\n'
        '\n'
        '[DBeaver]: https://github.com/dbeaver/dbeaver\n'
    ),
    link=None,
    level=3,
    num='4.7.1'
)

SRS_107_DBeaver_UI_Smoke_Testing = Specification(
    name='SRS-107 DBeaver UI Smoke Testing',
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
        Heading(name='Introduction', level=1, num='1'),
        Heading(name='Terminology', level=1, num='2'),
        Heading(name='How the Tests Work', level=1, num='3'),
        Heading(name='Environment', level=2, num='3.1'),
        Heading(name='Finding Widgets', level=2, num='3.2'),
        Heading(name='Expected Results', level=2, num='3.3'),
        Heading(name='Evidence', level=2, num='3.4'),
        Heading(name='Requirements', level=1, num='4'),
        Heading(name='Startup', level=2, num='4.1'),
        Heading(name='RQ.SRS-107.DBeaver.UI.Startup', level=3, num='4.1.1'),
        Heading(name='Connection', level=2, num='4.2'),
        Heading(name='RQ.SRS-107.DBeaver.UI.Connection', level=3, num='4.2.1'),
        Heading(name='Dataset', level=2, num='4.3'),
        Heading(name='RQ.SRS-107.DBeaver.UI.Dataset', level=3, num='4.3.1'),
        Heading(name='Queries', level=2, num='4.4'),
        Heading(name='RQ.SRS-107.DBeaver.UI.Queries', level=3, num='4.4.1'),
        Heading(name='Navigator', level=2, num='4.5'),
        Heading(name='RQ.SRS-107.DBeaver.UI.Navigator', level=3, num='4.5.1'),
        Heading(name='Screenshots', level=2, num='4.6'),
        Heading(name='RQ.SRS-107.DBeaver.UI.Screenshots', level=3, num='4.6.1'),
        Heading(name='Compatibility', level=2, num='4.7'),
        Heading(name='RQ.SRS-107.DBeaver.UI.Compatibility.LTS', level=3, num='4.7.1'),
        ),
    requirements=(
        RQ_SRS_107_DBeaver_UI_Startup,
        RQ_SRS_107_DBeaver_UI_Connection,
        RQ_SRS_107_DBeaver_UI_Dataset,
        RQ_SRS_107_DBeaver_UI_Queries,
        RQ_SRS_107_DBeaver_UI_Navigator,
        RQ_SRS_107_DBeaver_UI_Screenshots,
        RQ_SRS_107_DBeaver_UI_Compatibility_LTS,
        ),
    content=r'''
# SRS-107 DBeaver UI Smoke Testing
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Terminology](#terminology)
* 3 [How the Tests Work](#how-the-tests-work)
    * 3.1 [Environment](#environment)
    * 3.2 [Finding Widgets](#finding-widgets)
    * 3.3 [Expected Results](#expected-results)
    * 3.4 [Evidence](#evidence)
* 4 [Requirements](#requirements)
    * 4.1 [Startup](#startup)
        * 4.1.1 [RQ.SRS-107.DBeaver.UI.Startup](#rqsrs-107dbeaveruistartup)
    * 4.2 [Connection](#connection)
        * 4.2.1 [RQ.SRS-107.DBeaver.UI.Connection](#rqsrs-107dbeaveruiconnection)
    * 4.3 [Dataset](#dataset)
        * 4.3.1 [RQ.SRS-107.DBeaver.UI.Dataset](#rqsrs-107dbeaveruidataset)
    * 4.4 [Queries](#queries)
        * 4.4.1 [RQ.SRS-107.DBeaver.UI.Queries](#rqsrs-107dbeaveruiqueries)
    * 4.5 [Navigator](#navigator)
        * 4.5.1 [RQ.SRS-107.DBeaver.UI.Navigator](#rqsrs-107dbeaveruinavigator)
    * 4.6 [Screenshots](#screenshots)
        * 4.6.1 [RQ.SRS-107.DBeaver.UI.Screenshots](#rqsrs-107dbeaveruiscreenshots)
    * 4.7 [Compatibility](#compatibility)
        * 4.7.1 [RQ.SRS-107.DBeaver.UI.Compatibility.LTS](#rqsrs-107dbeaveruicompatibilitylts)

## Introduction

This SRS covers an automated version of the manual [DBeaver] check of a
ClickHouse LTS build: start DBeaver Community Edition, create a connection to
a local ClickHouse server, create a dataset and run check queries from the SQL
editor, with a screenshot of each step.

Unlike SRS-106, which replays DBeaver's SQL through its JDBC driver, this suite
runs DBeaver itself and drives its user interface.

## Terminology

- **LTS** — Long-Term Support ClickHouse release.
- **AT-SPI** — the Linux accessibility interface. DBeaver reports its windows
  and widgets through it, with their role, name and position on the screen.
- **Navigator** — the DBeaver tree of connections, databases, tables and columns.

## How the Tests Work

### Environment

One container, built from the ClickHouse image under test, runs the ClickHouse
server through the image's `/entrypoint.sh`, a virtual X display (Xvfb,
1920x1080) with the openbox window manager, and DBeaver CE at the release given
by `--dbeaver-version` (default `26.2.1`), started with a new workspace.

DBeaver downloads the ClickHouse JDBC driver from Maven Central when the
connection is first tested, as it does for a user, so the run needs internet
access.

### Finding Widgets

The tests find each widget by its AT-SPI role and name, for example the push
button `Test Connection ...` in the window `Connect to a database`, and click
the centre of its current position. No coordinates are fixed in the tests.
Input fields have no name, so a field is found as the one right of its label.

Two parts of DBeaver are drawn by DBeaver itself and are not reported through
AT-SPI:

- the driver gallery of the New Database Connection wizard: the tests type the
  driver name into its search box and move the focus to the gallery, which
  selects the first match, then check the `Driver name` the next page shows;
- the result grid: the tests copy the grid with Ctrl+A, Ctrl+C and compare the
  clipboard. Each query is tagged with `SETTINGS log_comment`, and the tests
  wait until the server's `system.query_log` shows it finished before reading
  the grid, so a query DBeaver never sent cannot pass.

Keys are pressed and text is typed with xdotool. SQL is pasted rather than
typed, because typing goes through the editor's autocomplete.

### Expected Results

The dataset is the one of SRS-106: database `lts_dbeaver_ui`, MergeTree table
`events` with 100 rows, `id` from 0 to 99, `score` NULL for every fifth row
and two tags per row, so `count()` must be 100, `count(score)` 80 and
`sum(id)` 4950. Every query is compared with its exact rows.

The scenarios share one DBeaver session and run in order. A failed scenario
stops the session.

### Evidence

`lts/_instances/dbeaver_ui/`: `screenshots/` with a numbered screenshot of each
step, and `logs/` with `build.log`, `clickhouse-server.log`, `dbeaver.log`,
`dbeaver-debug.log` and `container.log`.

## Requirements

### Startup

#### RQ.SRS-107.DBeaver.UI.Startup
version: 1.0

DBeaver SHALL start with a new workspace and show its main window, titled
`DBeaver <version>`, after its first-run Product Configuration wizard is
accepted.

### Connection

#### RQ.SRS-107.DBeaver.UI.Connection
version: 1.0

A connection to the local ClickHouse server SHALL be created with Database >
New Database Connection, the `ClickHouse` driver (not `ClickHouse (Legacy)`),
host `localhost`, port `8123` and user `default`. Test Connection SHALL report
`Connected` and show the server version that `SELECT version()` returns, and
the connection SHALL show in the navigator after Finish.

### Dataset

#### RQ.SRS-107.DBeaver.UI.Dataset
version: 1.0

A script run from the SQL editor with Alt+X SHALL create the database
`lts_dbeaver_ui`, the MergeTree table `events` and its 100 rows, and the server
SHALL then return `count()` 100 for the table.

### Queries

#### RQ.SRS-107.DBeaver.UI.Queries
version: 1.0

Queries run from the SQL editor with Ctrl+Enter SHALL show exactly the expected
rows in the result grid for:

* `count()` and `count(score)`
* `sum`, `min`, `max` and `uniqExact`
* `WHERE score IS NULL`
* `GROUP BY id % 5`
* `ORDER BY id DESC LIMIT 3`
* `ARRAY JOIN` on the `tags` array

### Navigator

#### RQ.SRS-107.DBeaver.UI.Navigator
version: 1.0

After a refresh, the navigator SHALL show the database `lts_dbeaver_ui`, its
table `events` and the table's columns with their types: `id (UInt64)`,
`name (String)`, `created (DateTime)`, `score (Nullable(Float64))` and
`tags (Array(String))`.

### Screenshots

#### RQ.SRS-107.DBeaver.UI.Screenshots
version: 1.0

Each step SHALL save a numbered screenshot of the screen under
`lts/_instances/dbeaver_ui/screenshots/`.

### Compatibility

#### RQ.SRS-107.DBeaver.UI.Compatibility.LTS
version: 1.0

DBeaver Community Edition SHALL be verified to connect to, create data in and
query the current Altinity ClickHouse LTS build through its user interface.

[DBeaver]: https://github.com/dbeaver/dbeaver
'''
)
