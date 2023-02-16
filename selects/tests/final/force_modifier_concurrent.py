from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *
from helpers.common import check_clickhouse_version
from selects.tests.select_steps import *
from selects.tests.concurrent_query_steps import *


@TestOutline
def parallel(self, tables, selects, inserts, updates, deletes, iterations=10):
    """Execute specified selects, inserts, updates, and deletes in parallel."""  
    for table in tables:
        with Scenario(f"{table.name}"):
            for i in range(iterations):
                for select in selects:
                    By(f"{select.name}", test=select, parallel=True)(name=table.name)

                for insert in inserts:
                    By(f"{insert.name}", test=insert, parallel=True)(name=table.name)

                for update in updates:
                    By(f"{update.name}", test=update, parallel=True)(name=table.name)

                for delete in deletes:
                    By(f"{delete.name}", test=delete, parallel=True)(name=table.name)    

#FIXME: add all scenarios
# same query runs in parallel
# all queries in parallel
# same query runs in parallel with inserts, updates and delete
# ...
                    
                                      
@TestModule
@Requirements()
@Name("force modifier ")
def feature(self):
    """Parallel queries tests for force select final."""
    if check_clickhouse_version("<22.11")(self):
        skip(
            reason="force_select_final is only supported on ClickHouse version >= 22.11"
        )

    for scenario in loads(current_module(), Scenario):
        scenario()
