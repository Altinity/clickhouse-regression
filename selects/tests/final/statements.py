from selects.tests.steps import *

select_count_query = define(
    "count()", "SELECT count() FROM {name} {final} FORMAT JSONEachRow;"
)

select_limit_query = define(
    "LIMIT 1",
    "SELECT * FROM {name} {final} ORDER BY (id, x, someCol) LIMIT 1 FORMAT JSONEachRow;",
)

select_limit_by_query = define(
    "LIMIT BY",
    "SELECT * FROM {name} {final} ORDER BY (id, x, someCol)"
    " LIMIT 1 BY id FORMAT JSONEachRow;",
)

select_group_by_query = define(
    "GROUP BY",
    "SELECT id, count(x) as cx FROM {name} {final} "
    "GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
)

select_distinct_query = define(
    "DISTINCT",
    "SELECT DISTINCT * FROM {name} {final} ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
)

select_where_query = define(
    "WHERE",
    "SELECT * FROM {name} {final} WHERE x > 3 "
    "ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
)
